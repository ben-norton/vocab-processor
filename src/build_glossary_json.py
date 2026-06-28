"""Build a glossary JSON file from CSV/JSONC sources.

Reads the four conventional files under ``sources/glossaries/<slug>/``:

    glossary-config-entry.jsonc   (required)  top-level glossary metadata
    glossary-meta.csv             (optional)  fallback metadata + term URI base
    glossary-terms.csv            (required)  the term rows
    glossary-sources.csv          (optional)  bibliographic source rows

and writes the canonical glossary JSON to::

    data/glossaries/<slug>/glossary.json

The schema mirrors what the vocab-publisher app expects (see
``vocab-publisher/scripts/csv-to-glossary.js`` for the JavaScript equivalent
that drives the live site build) and matches the existing
``data/glossaries/collections-digitization/glossary.json`` reference output.

Field mapping (terms CSV column -> glossary term JSON):

    resource_id || id || kebab(label) -> id
    label                             -> label
    definition                        -> definition
    category                          -> category   (kebab-cased id form)
    prov_class                        -> provClass
    source                            -> source
    usage_note                        -> scopeNote  (skos:scopeNote)
    url                               -> seeAlso    (rdfs:seeAlso)
    examples                          -> example    (skos:example)
    alt_label                         -> altLabel   (skos:altLabel; pipe/semicolon-delimited list)
    last_modified (YYYYMMDD)          -> modified   (dcterms:modified)

Tolerated quirks in the source CSVs:

  * The terms CSV may use either ``glossary-terms.csv`` or a prefixed name like
    ``<slug>-glossary-terms.csv`` (same for ``glossary-sources.csv``).
  * Some terms CSVs declare two ``source`` header columns where the second is
    really the URL; the duplicate is silently re-keyed to ``url``.
  * Some terms CSVs use ``id`` for the term slug while others use it for a
    sequential row number; numeric ``id`` values are ignored.

Usage::

    python utils/build_glossary_json.py <slug>
    python utils/build_glossary_json.py collections-digitization
    python utils/build_glossary_json.py kos-terms --output some/other/path.json
    python utils/build_glossary_json.py --all
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

ROOT          = Path(__file__).resolve().parents[1]
GLOSS_SRC_DIR = ROOT / "sources" / "glossaries"
GLOSS_OUT_DIR = ROOT / "data"    / "glossaries"


# ── JSONC helpers ───────────────────────────────────────────────────────

_JSONC_RE = re.compile(
    r"""
        "(?:\\.|[^"\\])*"          | # double-quoted strings (preserve as-is)
        /\*.*?\*/                  | # /* block comment */
        //[^\n]*                     # // line comment
    """,
    re.VERBOSE | re.DOTALL,
)


def _strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments from a JSONC document, preserving strings."""
    def repl(m: re.Match[str]) -> str:
        s = m.group(0)
        if s.startswith('"'):
            return s
        return ""
    return _JSONC_RE.sub(repl, text)


def load_jsonc(path: Path) -> dict[str, Any]:
    """Load a JSON-with-comments file. Tolerates // and /* */ comments and
    a single trailing comma before } or ]."""
    raw = _strip_jsonc(path.read_text(encoding="utf-8"))
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: cannot parse {path}: {e}")


# ── CSV helpers ─────────────────────────────────────────────────────────

# Header aliases applied to the *second* (and later) occurrence of a duplicate
# column name. Some authoring tools emit two ``source`` columns where the second
# is actually the URL — we silently re-key it.
_DUPLICATE_HEADER_REKEY = {
    "source": "url",
}


def _disambiguate_headers(headers: list[str]) -> list[str]:
    """Return headers with duplicate names re-keyed via ``_DUPLICATE_HEADER_REKEY``,
    or with a numeric suffix appended if no specific alias is configured."""
    seen: dict[str, int] = {}
    out: list[str] = []
    for h in headers:
        if h not in seen:
            seen[h] = 1
            out.append(h)
            continue
        seen[h] += 1
        alias = _DUPLICATE_HEADER_REKEY.get(h)
        out.append(alias if alias and alias not in seen else f"{h}_{seen[h]}")
        seen[out[-1]] = 1
    return out


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file as a list of dicts (header-row keyed). Returns [] if missing."""
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            headers = _disambiguate_headers([h.strip() for h in next(reader)])
        except StopIteration:
            return []
        rows: list[dict[str, str]] = []
        for raw in reader:
            if not any(c.strip() for c in raw):
                continue
            row: dict[str, str] = {}
            for i, h in enumerate(headers):
                row[h] = (raw[i] if i < len(raw) else "").strip()
            rows.append(row)
        return rows


# ── Misc helpers ────────────────────────────────────────────────────────

def kebab(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def format_date(yyyymmdd: str) -> str | None:
    if not yyyymmdd:
        return None
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", yyyymmdd.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", yyyymmdd.strip()):
        return yyyymmdd.strip()
    return yyyymmdd.strip() or None


def first_nonempty(*values: Any) -> Any:
    for v in values:
        if v not in (None, "", [], {}):
            return v
    return None


# ── Term ordering ───────────────────────────────────────────────────────

_TERM_KEY_ORDER = (
    "id", "label", "definition", "category", "provClass", "altLabel",
    "source", "scopeNote", "seeAlso", "example", "modified", "uri",
)


def _find_csv(src_dir: Path, slug: str, basename: str) -> Path:
    """Locate a CSV under ``src_dir`` accepting either ``<basename>`` or
    ``<slug>-<basename>``. Falls back to the un-prefixed path if neither
    exists, so the caller can still report a missing-file error."""
    direct = src_dir / basename
    if direct.is_file():
        return direct
    prefixed = src_dir / f"{slug}-{basename}"
    if prefixed.is_file():
        return prefixed
    return direct


def _split_alt_labels(s: str) -> list[str]:
    """Split a delimited alt-label cell into individual labels.
    Accepts ``|``, ``;`` or newline as delimiter."""
    if not s:
        return []
    parts = re.split(r"[|;\n]", s)
    return [p.strip() for p in parts if p.strip()]


def _ordered_term(term: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in _TERM_KEY_ORDER:
        if k in term and term[k] not in (None, "", []):
            out[k] = term[k]
    for k, v in term.items():
        if k not in out and v not in (None, "", []):
            out[k] = v
    return out


# ── Core build ──────────────────────────────────────────────────────────

def build_glossary(slug: str, *, output: Path | None = None,
                   include_term_uris: bool = False) -> Path:
    src_dir = GLOSS_SRC_DIR / slug
    if not src_dir.is_dir():
        raise SystemExit(f"ERROR: source folder not found: {src_dir}")

    cfg_path     = _find_csv(src_dir, slug, "glossary-config-entry.jsonc")
    meta_path    = _find_csv(src_dir, slug, "glossary-meta.csv")
    terms_path   = _find_csv(src_dir, slug, "glossary-terms.csv")
    sources_path = _find_csv(src_dir, slug, "glossary-sources.csv")

    if not cfg_path.is_file():
        raise SystemExit(f"ERROR: missing {cfg_path}")
    if not terms_path.is_file():
        raise SystemExit(f"ERROR: missing {terms_path}")

    cfg         = load_jsonc(cfg_path)
    meta_rows   = read_csv_rows(meta_path)
    term_rows   = read_csv_rows(terms_path)
    source_rows = read_csv_rows(sources_path)

    meta = next((r for r in meta_rows if any(r.values())), {}) if meta_rows else {}
    meta_uri = (meta.get("uri") or "").rstrip("/") or None

    print(f"[{slug}] config:  {cfg_path.name}")
    if meta:
        print(f"[{slug}] meta:    {meta_path.name} (uri={meta_uri or '-'})")
    print(f"[{slug}] terms:   {len(term_rows)} row(s) in {terms_path.name}")
    if source_rows:
        print(f"[{slug}] sources: {len(source_rows)} row(s) in {sources_path.name}")

    # ── Categories: unique values from terms, sorted by label ──────────
    category_seen: dict[str, dict[str, str]] = {}
    for r in term_rows:
        label = (r.get("category") or "").strip()
        if not label:
            continue
        cid = kebab(label)
        if cid and cid not in category_seen:
            category_seen[cid] = {"id": cid, "label": label}
    categories = sorted(category_seen.values(), key=lambda c: c["label"].lower())

    # ── Terms ──────────────────────────────────────────────────────────
    terms: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    skipped = 0
    latest_date: str | None = None

    for r in term_rows:
        label = (r.get("label") or "").strip()
        definition = (r.get("definition") or "").strip()
        if not label:
            skipped += 1
            continue
        if not definition:
            print(f"  WARN: skipping {label!r} - no definition")
            skipped += 1
            continue

        resource_id = (r.get("resource_id") or "").strip()
        raw_id      = (r.get("id") or "").strip()
        # The ``id`` column is sometimes a sequential row counter (0, 1, 2, …)
        # and sometimes the term slug itself. Prefer ``resource_id`` when set;
        # otherwise fall back to ``id`` only when it isn't purely numeric.
        if resource_id:
            tid = kebab(resource_id)
        elif raw_id and not raw_id.isdigit():
            tid = kebab(raw_id)
        else:
            tid = kebab(label)
        if not tid:
            print(f"  WARN: cannot derive id for {label!r}")
            skipped += 1
            continue
        if tid in seen_ids:
            print(f"  WARN: duplicate id {tid!r}")
        seen_ids.add(tid)

        term: dict[str, Any] = {"id": tid, "label": label, "definition": definition}

        category = (r.get("category") or "").strip()
        if category:
            term["category"] = kebab(category)

        prov_class = (r.get("prov_class") or "").strip()
        if prov_class:
            term["provClass"] = prov_class

        source = (r.get("source") or "").strip()
        if source:
            term["source"] = source

        usage = (r.get("usage_note") or "").strip()
        if usage:
            term["scopeNote"] = usage

        url = (r.get("url") or "").strip()
        if url:
            term["seeAlso"] = url

        examples = (r.get("examples") or "").strip()
        if examples:
            term["example"] = examples

        alt_labels = _split_alt_labels(r.get("alt_label") or r.get("altLabel") or "")
        if alt_labels:
            term["altLabel"] = alt_labels

        modified = format_date(r.get("last_modified") or "")
        if modified:
            term["modified"] = modified
            if latest_date is None or modified > latest_date:
                latest_date = modified

        if include_term_uris and meta_uri and resource_id:
            term["uri"] = f"{meta_uri}/{resource_id}"
        else:
            identifier = (r.get("identifier") or "").strip()
            if include_term_uris and identifier:
                term["uri"] = identifier

        terms.append(_ordered_term(term))

    # ── Sources ────────────────────────────────────────────────────────
    sources_out: list[dict[str, Any]] = []
    for s in source_rows:
        title = (s.get("title") or "").strip()
        if not title:
            continue
        sources_out.append({
            "title":       title,
            "notation":    (s.get("notation") or "").strip() or None,
            "description": (s.get("description") or "").strip() or None,
            "url":         (s.get("url") or "").strip() or None,
        })

    # ── Compose top-level glossary ─────────────────────────────────────
    def cfg_or_meta(*keys: str) -> Any:
        return first_nonempty(*[cfg.get(k) for k in keys],
                              *[meta.get(k) for k in keys])

    glossary: dict[str, Any] = {}
    glossary["id"]          = cfg.get("id") or slug
    glossary["title"]       = cfg_or_meta("title") or glossary["id"]
    desc = cfg_or_meta("description")
    if desc:
        glossary["description"] = desc
    uri = cfg_or_meta("uri")
    if uri:
        glossary["uri"] = uri

    version  = cfg_or_meta("version") or latest_date or date.today().isoformat()
    created  = cfg_or_meta("created")
    modified = cfg_or_meta("modified")
    license_ = cfg_or_meta("license", "rights")

    glossary["version"] = version
    if created:  glossary["created"]  = created
    if modified: glossary["modified"] = modified
    if license_: glossary["license"]  = license_

    glossary["categories"] = categories

    if cfg.get("scopeNote"):   glossary["scopeNote"]   = cfg["scopeNote"]
    if cfg.get("changeNote"):  glossary["changeNote"]  = cfg["changeNote"]
    if cfg.get("historyNote"): glossary["historyNote"] = cfg["historyNote"]

    ext = cfg.get("externalLinks") or []
    ext_clean = [
        {"label": (l.get("label") or l.get("url")), "url": l["url"]}
        for l in ext if isinstance(l, dict) and l.get("url")
    ]
    if ext_clean:
        glossary["externalLinks"] = ext_clean

    glossary["terms"] = terms
    if sources_out:
        glossary["sources"] = sources_out

    # ── Write output ──────────────────────────────────────────────────
    out_path = output or (GLOSS_OUT_DIR / slug / "glossary.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(glossary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    cat_word = "category" if len(categories) == 1 else "categories"
    try:
        display_path: Path | str = out_path.relative_to(ROOT)
    except ValueError:
        display_path = out_path
    print(f"[{slug}] wrote {display_path}")
    print(f"           {len(terms)} term(s) in {len(categories)} {cat_word}")
    if skipped:
        print(f"           {skipped} row(s) skipped")
    if sources_out:
        print(f"           {len(sources_out)} source citation(s)")
    return out_path


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a glossary JSON file from CSV/JSONC sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "slug",
        nargs="?",
        help="Glossary folder name under sources/glossaries/ "
             "(omit when --all is given).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process every subfolder of sources/glossaries/ that contains "
             "a glossary-terms.csv file.",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Override the output JSON path (only valid with a single slug).",
    )
    parser.add_argument(
        "--include-term-uris",
        action="store_true",
        help="Emit a per-term `uri` field (derived from glossary-meta.csv's "
             "uri + resource_id, or from the terms CSV's identifier column). "
             "Off by default to match the canonical reference output.",
    )
    args = parser.parse_args()

    if not args.all and not args.slug:
        parser.error("either a slug positional argument or --all is required")
    if args.all and args.output:
        parser.error("--output cannot be combined with --all")

    if args.all:
        skip = {"templates", "schemes"}
        slugs: list[str] = []
        for p in sorted(GLOSS_SRC_DIR.iterdir()):
            if not p.is_dir() or p.name in skip:
                continue
            if (p / "glossary-terms.csv").is_file() \
                    or (p / f"{p.name}-glossary-terms.csv").is_file():
                slugs.append(p.name)
        if not slugs:
            print(f"ERROR: no glossaries found under {GLOSS_SRC_DIR}", file=sys.stderr)
            sys.exit(1)
        for s in slugs:
            print(f"\n=== {s} ===")
            build_glossary(s, include_term_uris=args.include_term_uris)
    else:
        out_override = Path(args.output) if args.output else None
        build_glossary(
            args.slug,
            output=out_override,
            include_term_uris=args.include_term_uris,
        )


if __name__ == "__main__":
    main()

"""Build canonical glossary CSVs from verbatim authoring CSVs.

Reads the verbatim CSV(s) under ``sources/glossaries/<slug>/verbatim/`` and
emits the canonical CSVs in ``sources/glossaries/<slug>/`` consumed by
``build_glossary_json.py``.

Filenames are folder-based and unprefixed (``glossary-terms.csv``,
``glossary-sources.csv``); the glossary is identified by its folder name
(``<slug>``), not by an acronym baked into the filename. For backward
compatibility a slug-prefixed input (``<slug>-glossary-terms.csv``) is still
accepted, but the canonical output is always written with the plain,
folder-based name.

Verbatim TERMS columns -> canonical TERMS columns:

    Term       -> label
    Model      -> category
    Definition -> definition
    Notes      -> usage_note
    Source     -> source

Verbatim SOURCES columns -> canonical SOURCES columns:

    Title      -> title
    Reference  -> notation     (join key for terms.source)
    Citation   -> description
    URL        -> url

Any *additional* verbatim columns that don't appear in the mappings above
are passed straight through and appended to the canonical CSV header.
Their names are normalised to ``lowercase_underscore_separated`` form
(e.g. a verbatim column ``Linked Concept`` becomes ``linked_concept``).
If a passthrough name would collide with an existing canonical column,
an ``_extra`` suffix is added.

Other canonical columns (``url``, ``prov_class``, ``examples`` and
``identifier`` in terms; ``publisher`` in sources) are emitted as empty
strings — to be filled in by hand if and when needed. Re-running the
script overwrites those columns, so author hand-edits made in the
canonical CSVs will be lost; do significant editing in the verbatim
files instead.

Usage::

    python src/build_glossary_csvs.py <slug>
    python src/build_glossary_csvs.py <slug> --date 20260520
    python src/build_glossary_csvs.py <slug> --dry-run
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Iterable

ROOT          = Path(__file__).resolve().parents[1]
GLOSS_SRC_DIR = ROOT / "sources" / "glossaries"
VERBATIM_NAME = "verbatim"

TERMS_HEADER = [
    "id", "label", "category", "definition", "usage_note",
    "url", "source", "prov_class", "examples",
    "resource_id", "last_modified", "identifier",
]
SOURCES_HEADER = ["title", "notation", "description", "url", "publisher"]

# Verbatim header (case-insensitive) -> canonical column name.
# Includes the canonical names themselves so a verbatim file that already
# uses canonical naming is treated idempotently.
TERMS_VERBATIM_MAP = {
    "term":          "label",
    "definition":    "definition",
    "notes":         "usage_note",
    "source":        "source",
    "model":         "category",
    "label":         "label",
    "category":      "category",
    "usage_note":    "usage_note",
    "url":           "url",
    "prov_class":    "prov_class",
    "examples":      "examples",
    "identifier":    "identifier",
}
SOURCES_VERBATIM_MAP = {
    "reference":   "notation",
    "citation":    "description",
    "url":         "url",
    "title":       "title",
    "notation":    "notation",
    "description": "description",
    "publisher":   "publisher",
}


# ── helpers ─────────────────────────────────────────────────────────────

def kebab(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _read_verbatim(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV (header-row keyed). Returns (headers, rows)."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            headers = [h.strip() for h in next(reader)]
        except StopIteration:
            return [], []
        rows: list[dict[str, str]] = []
        for raw in reader:
            if not any(c.strip() for c in raw):
                continue
            row = {h: (raw[i] if i < len(raw) else "").strip()
                   for i, h in enumerate(headers)}
            rows.append(row)
        return headers, rows


def _normalize_extra_key(s: str) -> str:
    """Convert an arbitrary verbatim header to a ``lowercase_underscore`` key."""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def _partition_columns(
    headers: list[str],
    mapping: dict[str, str],
    canonical_header: list[str],
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Split verbatim ``headers`` into mapped + extra column tuples.

    Returns ``(mapped, extras)`` where each element is ``(verbatim_header,
    canonical_or_extra_name)``. Extras preserve their order of appearance
    in the verbatim file. Names that would collide with the canonical
    header (or with each other) get a numeric / ``_extra`` suffix."""
    mapped: list[tuple[str, str]] = []
    extras: list[tuple[str, str]] = []
    used_canonical: set[str] = set()
    used_extras: set[str] = set()

    for h in headers:
        canonical = mapping.get(h.strip().lower())
        if canonical:
            if canonical in used_canonical:
                print(f"  WARN: verbatim column {h!r} would re-map to "
                      f"already-populated canonical {canonical!r}; treating as extra")
            else:
                mapped.append((h, canonical))
                used_canonical.add(canonical)
                continue
        key = _normalize_extra_key(h)
        if not key:
            continue
        if key in canonical_header or key in mapping.values():
            key = f"{key}_extra"
        base, n = key, 2
        while key in used_extras:
            key = f"{base}_{n}"
            n += 1
        used_extras.add(key)
        extras.append((h, key))

    return mapped, extras


def _resolve_input(verbatim_dir: Path, slug: str, basename: str) -> Path | None:
    """Return the verbatim file path for ``basename``, preferring the plain,
    folder-based name (``glossary-terms.csv``) and falling back to the legacy
    slug-prefixed form (``<slug>-glossary-terms.csv``). Returns None if neither
    file exists."""
    direct = verbatim_dir / basename
    if direct.is_file():
        return direct
    prefixed = verbatim_dir / f"{slug}-{basename}"
    if prefixed.is_file():
        return prefixed
    return None


def _write_csv(path: Path, header: list[str],
               rows: Iterable[dict[str, str]], *, dry_run: bool) -> int:
    """Write rows to ``path`` using the given header. Returns row count."""
    rows = list(rows)
    if dry_run:
        return len(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header,
                                quoting=csv.QUOTE_MINIMAL,
                                extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in header})
    return len(rows)


# ── builders ────────────────────────────────────────────────────────────

def build_terms(
    verbatim_path: Path, last_modified: str,
) -> tuple[list[dict[str, str]], list[str]]:
    """Return ``(rows, extra_keys)`` for the canonical terms CSV."""
    headers, raw_rows = _read_verbatim(verbatim_path)
    mapped, extras = _partition_columns(headers, TERMS_VERBATIM_MAP, TERMS_HEADER)

    canonical_present = {c for _, c in mapped}
    for required in ("label", "definition"):
        if required not in canonical_present:
            raise SystemExit(
                f"ERROR: {verbatim_path} is missing a column mapping to "
                f"the canonical {required!r} column"
            )
    if extras:
        print(f"  passthrough columns: "
              + ", ".join(f"{h!r} -> {k}" for h, k in extras))

    out: list[dict[str, str]] = []
    seen_ids: dict[str, int] = {}
    skipped = 0

    for row in raw_rows:
        term: dict[str, str] = {h: "" for h in TERMS_HEADER}
        for verbatim_h, canonical in mapped:
            term[canonical] = (row.get(verbatim_h) or "").strip()

        label = term["label"]
        defn  = term["definition"]
        if not label:
            skipped += 1
            continue
        if not defn:
            print(f"  WARN: skipping {label!r} - no definition")
            skipped += 1
            continue

        rid = kebab(label)
        if rid in seen_ids:
            seen_ids[rid] += 1
            new_rid = f"{rid}-{seen_ids[rid]}"
            print(f"  WARN: duplicate label {label!r} -> resource_id {new_rid}")
            rid = new_rid
        else:
            seen_ids[rid] = 1

        term["id"]            = str(len(out))
        term["resource_id"]   = rid
        term["last_modified"] = last_modified

        for verbatim_h, extra_key in extras:
            term[extra_key] = (row.get(verbatim_h) or "").strip()

        out.append(term)

    if skipped:
        print(f"  ({skipped} row(s) skipped)")
    return out, [k for _, k in extras]


def build_sources(
    verbatim_path: Path,
) -> tuple[list[dict[str, str]], list[str]]:
    """Return ``(rows, extra_keys)`` for the canonical sources CSV."""
    headers, raw_rows = _read_verbatim(verbatim_path)
    mapped, extras = _partition_columns(headers, SOURCES_VERBATIM_MAP, SOURCES_HEADER)
    if extras:
        print(f"  passthrough columns: "
              + ", ".join(f"{h!r} -> {k}" for h, k in extras))

    out: list[dict[str, str]] = []
    skipped = 0

    for row in raw_rows:
        src: dict[str, str] = {h: "" for h in SOURCES_HEADER}
        for verbatim_h, canonical in mapped:
            src[canonical] = (row.get(verbatim_h) or "").strip()

        if not (src["notation"] or src["title"]):
            skipped += 1
            continue
        if not src["title"]:
            src["title"] = src["notation"]

        for verbatim_h, extra_key in extras:
            src[extra_key] = (row.get(verbatim_h) or "").strip()

        out.append(src)

    if skipped:
        print(f"  ({skipped} row(s) skipped)")
    return out, [k for _, k in extras]


# ── orchestration ───────────────────────────────────────────────────────

def build_glossary_csvs(slug: str, *, last_modified: str,
                        dry_run: bool = False) -> None:
    src_dir      = GLOSS_SRC_DIR / slug
    verbatim_dir = src_dir / VERBATIM_NAME
    if not src_dir.is_dir():
        raise SystemExit(f"ERROR: glossary folder not found: {src_dir}")
    if not verbatim_dir.is_dir():
        # Glossaries authored directly in canonical form (e.g. kos-terms,
        # collections-digitization) have no verbatim/ step to run. Say so
        # plainly rather than failing as if a file were missing.
        if (src_dir / "glossary-terms.csv").is_file():
            raise SystemExit(
                f"NOTE: {slug} has no verbatim/ folder; its canonical "
                f"glossary-terms.csv is authored directly. Nothing to build here - "
                f"run build_glossary_json.py {slug} to regenerate its JSON."
            )
        raise SystemExit(
            f"ERROR: verbatim folder not found: {verbatim_dir}\n"
            f"       expected 'glossary-terms.csv' (folder-based, unprefixed) under it."
        )

    terms_in   = _resolve_input(verbatim_dir, slug, "glossary-terms.csv")
    sources_in = _resolve_input(verbatim_dir, slug, "glossary-sources.csv")
    if not terms_in:
        raise SystemExit(
            f"ERROR: missing verbatim terms CSV under {verbatim_dir} "
            f"(looked for 'glossary-terms.csv' and legacy '{slug}-glossary-terms.csv')"
        )

    print(f"[{slug}] verbatim terms:   {terms_in.relative_to(ROOT)}")
    if sources_in:
        print(f"[{slug}] verbatim sources: {sources_in.relative_to(ROOT)}")
    else:
        print(f"[{slug}] no verbatim sources CSV found - skipping sources output")

    # Canonical output is always written with the plain, folder-based name,
    # regardless of whether the verbatim input used a legacy slug prefix.
    terms_out_name   = "glossary-terms.csv"
    sources_out_name = "glossary-sources.csv"

    print(f"[{slug}] last_modified: {last_modified}")
    print(f"[{slug}] building terms ...")
    term_rows, term_extras = build_terms(terms_in, last_modified)
    terms_header = TERMS_HEADER + term_extras
    n_terms = _write_csv(src_dir / terms_out_name, terms_header,
                         term_rows, dry_run=dry_run)

    n_sources = 0
    source_extras: list[str] = []
    if sources_in:
        print(f"[{slug}] building sources ...")
        source_rows, source_extras = build_sources(sources_in)
        sources_header = SOURCES_HEADER + source_extras
        n_sources = _write_csv(src_dir / sources_out_name, sources_header,
                               source_rows, dry_run=dry_run)

    verb = "would write" if dry_run else "wrote"
    print(f"[{slug}] {verb} {n_terms} term row(s) -> "
          f"{(src_dir / terms_out_name).relative_to(ROOT)}")
    if sources_in:
        print(f"[{slug}] {verb} {n_sources} source row(s) -> "
              f"{(src_dir / sources_out_name).relative_to(ROOT)}")


# ── CLI ─────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build canonical glossary CSVs from verbatim authoring CSVs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "slug",
        help="Glossary folder name under sources/glossaries/ "
             "(its 'verbatim/' subfolder is read).",
    )
    parser.add_argument(
        "--date",
        metavar="YYYYMMDD",
        default=date.today().strftime("%Y%m%d"),
        help="Value to write into every term's 'last_modified' column "
             "(default: today's date in YYYYMMDD form).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and validate the verbatim CSVs but do not write the output files.",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"\d{8}", args.date):
        print(f"ERROR: --date must be 8 digits (YYYYMMDD); got {args.date!r}",
              file=sys.stderr)
        sys.exit(1)

    build_glossary_csvs(args.slug, last_modified=args.date, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

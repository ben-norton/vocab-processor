"""Build a SKOS Turtle file from a glossary's standard 4-file source set.

Combines the glossary source parser from ``build_glossary_json.py`` (which
reads the standard four files under ``sources/glossaries/<slug>/``) with the
Turtle-rendering conventions used by ``xlsx-to-ttl.py``, emitting a SKOS
concept scheme that passes every check in ``validate-ttl.py``.

Standard 4-file source set (see ``build_glossary_json.py`` for details):

    glossary-config-entry.jsonc   (required)  top-level glossary metadata
    glossary-meta.csv             (optional)  creator/publisher/prefix/rights
    glossary-terms.csv            (required)  the term rows
    glossary-sources.csv          (optional)  bibliographic source rows

Output (default)::

    data/glossaries/<slug>/<slug>.ttl

RDF shape:

  * one ``skos:ConceptScheme`` at the glossary ``uri``;
  * one ``skos:Concept`` per term at ``<uri>/term/<term-id>``; a flat glossary
    has no hierarchy, so every concept is a top concept
    (``skos:topConceptOf`` + scheme ``skos:hasTopConcept``);
  * one ``skos:Collection`` per term category at ``<uri>/collection/<cat-id>``,
    grouping its member concepts via ``skos:member``.

``reg:status`` (required by ``validate-ttl.py``) defaults to ``stable``; set a
``status`` key in the config JSONC or pass ``--status`` to override.

Usage::

    python src/build_glossary_ttl.py <slug>
    python src/build_glossary_ttl.py kos-terms --output some/other/path.ttl
    python src/build_glossary_ttl.py --all
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Reuse the glossary source parser rather than re-implementing it.
import build_glossary_json as bgj

ROOT          = bgj.ROOT
GLOSS_SRC_DIR = bgj.GLOSS_SRC_DIR
GLOSS_OUT_DIR = bgj.GLOSS_OUT_DIR

LANG            = "en"
REG_STATUS_BASE = "https://linked.data.gov.au/def/reg-statuses/"
DEFAULT_STATUS  = "stable"

# Prefix -> namespace IRI. Kept minimal; only what a glossary TTL uses.
PREFIXES: list[tuple[str, str]] = [
    ("dcat",    "http://www.w3.org/ns/dcat#"),
    ("dcterms", "http://purl.org/dc/terms/"),
    ("prov",    "http://www.w3.org/ns/prov#"),
    ("rdfs",    "http://www.w3.org/2000/01/rdf-schema#"),
    ("reg",     "http://purl.org/linked-data/registry#"),
    ("skos",    "http://www.w3.org/2004/02/skos/core#"),
    ("vann",    "http://purl.org/vocab/vann/"),
    ("xsd",     "http://www.w3.org/2001/XMLSchema#"),
]
_DECLARED_PREFIXES = {p for p, _ in PREFIXES}


# ── Turtle literal / formatting helpers (mirrors xlsx-to-ttl.py) ─────────

INDENT = "    "      # 4 spaces for top-level properties
PROP_W = 25          # property column width (value starts at col 29)


def _escape(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def ttl_str(s: str, lang: str | None = LANG) -> str:
    """Turtle string literal; triple-quoted when the value contains newlines."""
    s = str(s).strip()
    tag = f"@{lang}" if lang else ""
    if "\n" in s:
        body = s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        return f'"""{body}"""{tag}'
    return f'"{_escape(s)}"{tag}'


def ttl_long(s: str, lang: str = LANG) -> str:
    """Always triple-quoted — for definitions, descriptions, scope notes."""
    s = str(s).strip()
    body = s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""{body}"""@{lang}'


def ttl_plain(s: str) -> str:
    """Untyped, untagged string literal."""
    return f'"{_escape(str(s).strip())}"'


def iri(s: str) -> str:
    return f"<{str(s).strip()}>"


def date_lit(s: str) -> str | None:
    """xsd:date literal from a YYYY-MM-DD (or YYYYMMDD) string, else None."""
    if not s:
        return None
    s = str(s).strip()
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})", s)
    if m:
        s = f"{m[1]}-{m[2]}-{m[3]}"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return f'"{s}"^^xsd:date'
    return None


def license_obj(s: str) -> str:
    """Render a licence as an IRI when it looks like a URL, else a literal."""
    s = str(s).strip()
    return iri(s) if s.startswith("http") else ttl_plain(s)


def _prop(p: str, v: str, *, indent: str = INDENT, width: int = PROP_W) -> str:
    # Guarantee at least one space when the property name fills/overflows the
    # column (e.g. the long vann:preferredNamespace* predicates).
    pad = max(width, len(p) + 1)
    return f"{indent}{p:<{pad}}{v} ;"


def _multi(p: str, items: list[str], *,
           indent: str = INDENT, width: int = PROP_W) -> str:
    """Property with multiple values: one per line, comma-separated."""
    pad = " " * (len(indent) + width)
    lines = [f"{indent}{p:<{width}}{items[0]}"]
    lines += [f"{pad}{it}" for it in items[1:]]
    return "\n".join(
        ln + (" ," if i < len(lines) - 1 else " ;")
        for i, ln in enumerate(lines)
    )


# ── Metadata helpers ────────────────────────────────────────────────────

def _meta_prefix(meta: dict[str, str]) -> str | None:
    """Namespace prefix from meta, tolerating both the underscore and
    space-separated header spellings."""
    for k in ("namespace_prefix", "namespace prefix", "prefix"):
        v = (meta.get(k) or "").strip()
        if v:
            return v
    return None


def _status_iri(status: str) -> str:
    status = status.strip()
    if status.startswith("http"):
        return iri(status)
    return iri(f"{REG_STATUS_BASE}{status}")


# ── Renderers ────────────────────────────────────────────────────────────

def render_prefix_block() -> str:
    width = max(len(p) for p, _ in PREFIXES) + 1
    lines = ["# Standard prefixes"]
    for p, ns in PREFIXES:
        lines.append(f"@prefix {p + ':':<{width}} <{ns}> .")
    return "\n".join(lines)


def render_scheme(glossary: dict[str, Any], meta: dict[str, str],
                  scheme_uri: str, status: str,
                  term_iris: list[str]) -> str:
    creator   = (meta.get("creator") or "").strip()
    publisher = (meta.get("publisher") or "").strip()
    # dcterms:creator / dcterms:publisher are required by validate-ttl.py.
    creator   = creator or publisher
    publisher = publisher or creator
    if not creator:
        print("  WARN: no creator/publisher in glossary-meta.csv; "
              "falling back to 'GeoSpecimens Platform'")
        creator = publisher = "GeoSpecimens Platform"

    description = glossary.get("description") or glossary["title"]
    created  = glossary.get("created")  or glossary.get("version")
    modified = glossary.get("modified") or glossary.get("version")

    lines: list[str] = [f"{iri(scheme_uri)}"]
    lines.append(_prop("a", "skos:ConceptScheme"))
    lines.append(_prop("dcterms:identifier", ttl_plain(glossary["id"])))
    lines.append(_prop("skos:prefLabel", ttl_str(glossary["title"])))
    lines.append(_prop("dcterms:title", ttl_str(glossary["title"])))
    lines.append(_prop("skos:definition", ttl_long(description)))
    lines.append(_prop("dcterms:description", ttl_long(description)))
    lines.append(_prop("dcterms:creator", ttl_plain(creator)))
    lines.append(_prop("dcterms:publisher", ttl_plain(publisher)))

    if (d := date_lit(created)):
        lines.append(_prop("dcterms:created", d))
    if (d := date_lit(modified)):
        lines.append(_prop("dcterms:modified", d))
    if glossary.get("version"):
        lines.append(_prop("dcat:version", ttl_plain(glossary["version"])))

    prefix = _meta_prefix(meta)
    lines.append(_prop("vann:preferredNamespaceUri", iri(scheme_uri + "/")))
    if prefix:
        lines.append(_prop("vann:preferredNamespacePrefix", ttl_plain(prefix)))

    if glossary.get("scopeNote"):
        lines.append(_prop("skos:scopeNote", ttl_str(glossary["scopeNote"])))
    if glossary.get("historyNote"):
        lines.append(_prop("skos:historyNote", ttl_str(glossary["historyNote"])))
    if glossary.get("changeNote"):
        lines.append(_prop("skos:changeNote", ttl_str(glossary["changeNote"])))

    if glossary.get("license"):
        lines.append(_prop("dcterms:license", license_obj(glossary["license"])))
    if (rights := (meta.get("rights") or "").strip()):
        lines.append(_prop("dcterms:rights", ttl_plain(rights)))

    ext_urls = [l["url"] for l in glossary.get("externalLinks", [])
                if l.get("url")]
    if ext_urls:
        lines.append(_multi("rdfs:seeAlso", [iri(u) for u in ext_urls]))

    if term_iris:
        lines.append(_multi("skos:hasTopConcept", [iri(t) for t in term_iris]))

    lines.append(_prop("reg:status", _status_iri(status)))
    lines.append(".")
    return "\n".join(lines)


def render_concept(term: dict[str, Any], scheme_uri: str,
                   term_uri: str, status: str) -> str:
    types = ["skos:Concept"]
    prov = (term.get("provClass") or "").strip()
    if prov and ":" in prov and prov.split(":", 1)[0] in _DECLARED_PREFIXES:
        types.append(prov)

    lines: list[str] = [f"{iri(term_uri)}"]
    lines.append(_prop("a", " , ".join(types)))
    lines.append(_prop("skos:prefLabel", ttl_str(term["label"])))

    alt = term.get("altLabel") or []
    if isinstance(alt, str):
        alt = [alt]
    if alt:
        lines.append(_multi("skos:altLabel", [ttl_str(a) for a in alt]))

    lines.append(_prop("skos:definition", ttl_long(term["definition"])))

    if term.get("scopeNote"):
        lines.append(_prop("skos:scopeNote", ttl_str(term["scopeNote"])))
    if term.get("example"):
        lines.append(_prop("skos:example", ttl_str(term["example"])))

    lines.append(_prop("skos:notation", ttl_plain(term["id"])))
    lines.append(_prop("dcterms:identifier", ttl_plain(term["id"])))

    if term.get("source"):
        lines.append(_prop("dcterms:source", ttl_plain(term["source"])))
    if term.get("seeAlso"):
        lines.append(_prop("rdfs:seeAlso", iri(term["seeAlso"])))
    if (d := date_lit(term.get("modified") or "")):
        lines.append(_prop("dcterms:modified", d))

    lines.append(_prop("skos:inScheme", iri(scheme_uri)))
    lines.append(_prop("skos:topConceptOf", iri(scheme_uri)))
    lines.append(_prop("reg:status", _status_iri(status)))
    lines.append(".")
    return "\n".join(lines)


def render_collection(cat: dict[str, str], scheme_uri: str,
                      member_iris: list[str]) -> str:
    coll_uri = f"{scheme_uri}/collection/{cat['id']}"
    lines: list[str] = [f"{iri(coll_uri)}"]
    lines.append(_prop("a", "skos:Collection"))
    lines.append(_prop("skos:prefLabel", ttl_str(cat["label"])))
    lines.append(_prop("skos:inScheme", iri(scheme_uri)))
    if member_iris:
        lines.append(_multi("skos:member", [iri(m) for m in member_iris]))
    lines.append(".")
    return "\n".join(lines)


# ── Core build ────────────────────────────────────────────────────────────

def build_glossary_ttl(slug: str, *, output: Path | None = None,
                       status: str = DEFAULT_STATUS) -> Path:
    glossary, meta, _skipped = bgj.assemble_glossary(slug)

    scheme_uri = (glossary.get("uri") or "").rstrip("/")
    if not scheme_uri:
        raise SystemExit(
            f"ERROR: {slug} has no 'uri' in glossary-config-entry.jsonc / "
            f"glossary-meta.csv; cannot mint concept IRIs."
        )
    status = (glossary.get("status") or status).strip() or DEFAULT_STATUS

    terms = glossary["terms"]
    term_uri = {t["id"]: f"{scheme_uri}/term/{t['id']}" for t in terms}
    term_iris = [term_uri[t["id"]] for t in terms]

    # Category id -> member concept IRIs (in term order).
    members: dict[str, list[str]] = {}
    for t in terms:
        cid = (t.get("category") or "").strip()
        if cid:
            members.setdefault(cid, []).append(term_uri[t["id"]])

    header = (
        f"# {glossary['title']} — SKOS ConceptScheme\n"
        f"# Generated from the glossary 4-file source set at "
        f"sources/glossaries/{slug}/\n"
        f"# Generator: src/build_glossary_ttl.py\n"
    )

    blocks: list[str] = [header, render_prefix_block()]
    blocks.append("# " + "=" * 74 + "\n# ConceptScheme\n# " + "=" * 74)
    blocks.append(render_scheme(glossary, meta, scheme_uri, status, term_iris))
    blocks.append("# " + "=" * 74 + "\n# Concepts\n# " + "=" * 74)
    for t in terms:
        blocks.append(render_concept(t, scheme_uri, term_uri[t["id"]], status))

    categories = [c for c in glossary.get("categories", [])
                  if members.get(c["id"])]
    if categories:
        blocks.append("# " + "=" * 74 + "\n# Collections (term categories)\n# "
                      + "=" * 74)
        for c in categories:
            blocks.append(render_collection(c, scheme_uri, members[c["id"]]))

    ttl = "\n\n".join(blocks).rstrip() + "\n"

    out_path = output or (GLOSS_OUT_DIR / slug / f"{slug}.ttl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ttl, encoding="utf-8")

    try:
        display: Path | str = out_path.relative_to(ROOT)
    except ValueError:
        display = out_path
    print(f"[{slug}] wrote {display}")
    print(f"           {len(terms)} concept(s), {len(categories)} collection(s), "
          f"status={status}")
    return out_path


# ── CLI ────────────────────────────────────────────────────────────────

def _discover_slugs() -> list[str]:
    skip = {"templates", "schemes"}
    slugs: list[str] = []
    for p in sorted(GLOSS_SRC_DIR.iterdir()):
        if not p.is_dir() or p.name in skip:
            continue
        if (p / "glossary-terms.csv").is_file() \
                or (p / f"{p.name}-glossary-terms.csv").is_file():
            slugs.append(p.name)
    return slugs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a SKOS Turtle file from a glossary's 4-file source set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "slug", nargs="?",
        help="Glossary folder name under sources/glossaries/ "
             "(omit when --all is given).",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Process every subfolder of sources/glossaries/ that contains "
             "a glossary-terms.csv file.",
    )
    parser.add_argument(
        "--output", metavar="PATH",
        help="Override the output TTL path (only valid with a single slug).",
    )
    parser.add_argument(
        "--status", default=DEFAULT_STATUS,
        help=f"reg:status slug or IRI for the scheme and its concepts "
             f"(default: {DEFAULT_STATUS!r}). A 'status' key in the config "
             f"JSONC takes precedence.",
    )
    args = parser.parse_args()

    if not args.all and not args.slug:
        parser.error("either a slug positional argument or --all is required")
    if args.all and args.output:
        parser.error("--output cannot be combined with --all")

    if args.all:
        slugs = _discover_slugs()
        if not slugs:
            print(f"ERROR: no glossaries found under {GLOSS_SRC_DIR}",
                  file=sys.stderr)
            sys.exit(1)
        for s in slugs:
            print(f"\n=== {s} ===")
            build_glossary_ttl(s, status=args.status)
    else:
        out = Path(args.output) if args.output else None
        build_glossary_ttl(args.slug, output=out, status=args.status)


if __name__ == "__main__":
    main()

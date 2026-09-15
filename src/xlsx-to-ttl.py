"""Comprehensive SKOS TTL generator — merged from xlsx-to-ttl.py and
xlsx-to-ttl-prezlite.py, combining all features from both scripts.

Features included from xlsx-to-ttl.py
  • Standard @prefix Turtle syntax with column-aligned properties
  • Full-IRI ConceptScheme and Concept subjects (<https://...>)
  • Workbook-specific namespace prefixes via the Namespaces / Namespeces sheet
  • Formula-aware conceptIRI resolution (="base/"&ColRef cells)
  • Explicit CS_KEY_ALIASES and CONCEPT_COL_ALIASES lookup tables
  • dcterms:creator / publisher / contributor resolved from Agents.xlsx roles
  • prov:qualifiedAttribution + agent descriptions embedded from Agents.xlsx
  • Data-quality issue detection (IRI scheme, inScheme consistency, broader refs)
  • Post-hoc rdflib validation (optional, requires rdflib)

Features included from xlsx-to-ttl-prezlite.py
  • Mappings sheet: skos:relatedMatch / closeMatch / exactMatch / narrowMatch /
    broadMatch per concept
  • Language-tagged label / note columns (e.g. skos:prefLabel@de)
  • normalize_iri: http://kos.geospecimens.org → https://
  • Explicit skip of Agents.xlsx (handled by build_agents_ttl.py)

Sheets consumed per workbook:
  Concept Scheme / ConceptScheme  — key-value ConceptScheme metadata
  Concepts                        — one row per concept
  Namespaces / Namespeces         — workbook-specific prefix declarations
  Mappings / Mapping              — SKOS match properties per concept

Agents come solely from sources/xlsx/Agents.xlsx (read once per run): its 'map'
sheet assigns agents + roles to each scheme IRI, and those agents are appended to
that vocabulary's TTL. An Agents sheet inside a vocabulary workbook is ignored.

Run from the project root:
  python src/xlsx-to-ttl.py                # process all workbooks
  python src/xlsx-to-ttl.py HazardTypes    # process one workbook by name
  python src/xlsx-to-ttl.py HazardTypes.xlsx

Dependencies: openpyxl (required), rdflib (optional, for post-hoc validation).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
from datetime import date, datetime
from pathlib import Path

import openpyxl

import build_agents_ttl as _agents
from cleanup_ttl_prefixes import analyse as _analyse_prefixes, clean_text as _clean_prefixes

ROOT        = Path(__file__).resolve().parents[1]
XLSX_DIR    = ROOT / "sources" / "xlsx"
OUT_DIR     = ROOT / "data" / "vocabs"
AGENTS_XLSX = XLSX_DIR / "Agents.xlsx"

# ---------------------------------------------------------------------------
# Prefix registry
# ---------------------------------------------------------------------------

STANDARD_PREFIXES: list[tuple[str, str]] = [
    ("dcat",       "http://www.w3.org/ns/dcat#"),
    ("dcterms",    "http://purl.org/dc/terms/"),
    ("isoroles",   "http://def.isotc211.org/iso19115-1/2014/"
                   "CitationAndResponsiblePartyInformation/code/CI_RoleCode/"),
    ("owl",        "http://www.w3.org/2002/07/owl#"),
    ("prov",       "http://www.w3.org/ns/prov#"),
    ("rdf",        "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",       "http://www.w3.org/2000/01/rdf-schema#"),
    ("reg",        "http://purl.org/linked-data/registry#"),
    ("schema",     "https://schema.org/"),
    ("skos",       "http://www.w3.org/2004/02/skos/core#"),
    ("status",     "https://linked.data.gov.au/def/reg-statuses/"),
    ("vann",       "http://purl.org/vocab/vann/"),
    ("vocdermods", "https://linked.data.gov.au/def/vocdermods/"),
    ("xsd",        "http://www.w3.org/2001/XMLSchema#"),
]

STANDARD_NS_SET       = {ns for _, ns in STANDARD_PREFIXES}
STANDARD_PREFIX_NAMES = {p  for p, _ in STANDARD_PREFIXES}

VOCDERMODS_BASE = "https://linked.data.gov.au/def/vocdermods/"

# ---------------------------------------------------------------------------
# Key / column-name normalisation tables
# ---------------------------------------------------------------------------

# Maps both bare and prefix-qualified Concept Scheme row keys to canonical keys.
CS_KEY_ALIASES: dict[str, str] = {
    # prefixed forms
    "dcterms:title":             "title",
    "skos:prefLabel":            "prefLabel",
    "skos:definition":           "definition",
    "dcterms:description":       "description",
    "dcterms:publisher":         "publisher",
    "dcterms:creator":           "creator",
    "dcterms:contributor":       "contributor",
    "dcterms:provenance":        "provenance",
    "dcterms:created":           "created",
    "dcterms:modified":          "modified",
    "dcat:version":              "version",
    "skos:scopeNote":            "scopeNote",
    "vann:usageNote":            "usageNote",
    "skos:historyNote":          "historyNote",
    "skos:note":                 "note",
    "dcat:keyword":              "keywords",
    "schema:keywords":           "keywords",
    "schema:citation":           "citation",
    "prov:wasDerivedFrom":       "derivedFrom",
    "reg:derivationMode":        "derivationMode",
    "regstatus:derivationMode":  "derivationMode",
    "reg:status":                "status",
    "schema:license":            "license",
    "skos:hasTopConcept":        "hasTopConcept",
    # bare-name aliases used by some files
    "keyword":                   "keywords",
    "wasDerivedFrom":            "derivedFrom",
}

# Maps prefixed or bare Concepts-sheet column headers to canonical keys.
# Language-tag variants (e.g. skos:prefLabel@de) are handled separately by
# _normalize_concept_col(); they are not listed here.
CONCEPT_COL_ALIASES: dict[str, str] = {
    "skos:conceptIRI":    "conceptIRI",
    "skos:prefLabel":     "prefLabel",
    "skos:altLabel":      "altLabel",
    "skos:broader":       "broader",
    "skos:definition":    "definition",
    "dcterms:provenance": "provenance",
    "skos:historyNote":   "historyNote",
    "skos:editorialNote": "editorialNote",
    "skos:changeNote":    "changeNote",
    "vann:usageNote":     "usageNote",
    "skos:inScheme":      "inScheme",
    "reg:status":         "registryStatus",
    "skos:topConceptOf":  "isTopConceptOf",
    "skos:notation":      "notation",
}

# Column headers in the Mappings sheet → canonical match-type key.
MAPPINGS_COL_ALIASES: dict[str, str] = {
    "skos:relatedMatch": "relatedMatch",
    "skos:closeMatch":   "closeMatch",
    "skos:exactMatch":   "exactMatch",
    "skos:narrowMatch":  "narrowMatch",
    "skos:broadMatch":   "broadMatch",
    "relatedMatchIRI":   "relatedMatch",
    "closeMatchIRI":     "closeMatch",
    "exactMatchIRI":     "exactMatch",
    "narrowMatchIRI":    "narrowMatch",
    "broadMatchIRI":     "broadMatch",
}

# Maps base-name of language-tag columns to their RDF predicates,
# used when rendering language-variant values from Concepts-sheet columns
# such as "skos:prefLabel@de" or "skos:definition@fr".
_LANG_TAG_PRED: dict[str, str] = {
    "prefLabel":     "skos:prefLabel",
    "altLabel":      "skos:altLabel",
    "definition":    "skos:definition",
    "scopeNote":     "skos:scopeNote",
    "historyNote":   "skos:historyNote",
    "editorialNote": "skos:editorialNote",
    "changeNote":    "skos:changeNote",
    "usageNote":     "vann:usageNote",
    "description":   "dcterms:description",
    "provenance":    "dcterms:provenance",
}

# ---------------------------------------------------------------------------
# Text / IRI helpers
# ---------------------------------------------------------------------------

def _escape(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def ttl_str(s: str, lang: str | None = "en") -> str:
    """Turtle string literal; triple-quoted when the value contains newlines."""
    s = str(s).strip()
    tag = f"@{lang}" if lang else ""
    if "\n" in s:
        body = s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        return f'"""{body}"""{tag}'
    return f'"{_escape(s)}"{tag}'


def ttl_long(s: str, lang: str = "en") -> str:
    """Always triple-quoted — use for definitions, descriptions, scope / usage notes."""
    s = str(s).strip()
    body = s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""{body}"""@{lang}'


def ttl_plain(s: str) -> str:
    """Untyped, untagged string literal."""
    return f'"{_escape(str(s).strip())}"'


def split_vals(raw: str | None, sep: str = r"[,\n]+") -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in re.split(sep, str(raw).strip()) if p.strip()]


def parse_date(val) -> str | None:
    if val is None or str(val).strip() in ("", "None"):
        return None
    if isinstance(val, datetime):
        return val.date().isoformat()
    if isinstance(val, date):
        return val.isoformat()
    s = str(val).strip()
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:\.\d+)?$", s)
    if m:
        return f"{m[1]}-{m[2]}-{m[3]}"
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m[1]
    return None


def iri_slug(iri: str) -> str:
    return iri.rstrip("/").rsplit("/", 1)[-1]


def clean_iri(s: str) -> str:
    """Strip trailing punctuation artifacts (commas, angle brackets) from an IRI."""
    return s.strip().strip("<>").rstrip(",;").strip()


def normalize_iri(iri: str) -> str:
    """Normalise http://kos.geospecimens.org IRIs to https://."""
    iri = iri.strip()
    if iri.startswith("http://kos.geospecimens.org"):
        iri = "https://" + iri[len("http://"):]
    return iri


def _normalise_derivation_mode(raw: str) -> str:
    """Return a full IRI for a reg:derivationMode value.

    Handles full IRIs, bare slugs, and the erroneous 'regstatus:' prefix.
    """
    dm = raw.strip().replace("regstatus:", "").replace("reg:", "").strip()
    if dm.startswith("http"):
        return clean_iri(dm)
    return f"{VOCDERMODS_BASE}{dm}"


# ---------------------------------------------------------------------------
# Turtle formatting
# ---------------------------------------------------------------------------

INDENT    = "    "      # 4 spaces for top-level properties
PROP_W    = 25          # property column width (value starts at col 29)
BN_INDENT = "        "  # 8 spaces inside attribution blank nodes
BN_PROP_W = 17          # property column width inside attribution blank nodes


def _prop(p: str, v: str, indent: str = INDENT, width: int = PROP_W) -> str:
    return f"{indent}{p:<{width}}{v} ;"


def _multi(
    p: str,
    items: list[str],
    indent: str = INDENT,
    width: int = PROP_W,
) -> str:
    """Property with multiple values, one per line, comma-separated, semicolon at end."""
    pad = " " * (len(indent) + width)
    lines = [f"{indent}{p:<{width}}{items[0]}"]
    for item in items[1:]:
        lines.append(f"{pad}{item}")
    result = []
    for i, ln in enumerate(lines):
        result.append(ln + (" ," if i < len(lines) - 1 else " ;"))
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Column normalisation
# ---------------------------------------------------------------------------

def _normalize_concept_col(raw: str) -> str:
    """Normalise a Concepts-sheet column header to its canonical key.

    Priority:
      1. Exact match in CONCEPT_COL_ALIASES (e.g. "skos:prefLabel" → "prefLabel")
      2. Language-tag variant: "ns:localName@lang" → "localName@lang"
      3. Return as-is (bare names like "conceptIRI" pass through unchanged)
    """
    if raw in CONCEPT_COL_ALIASES:
        return CONCEPT_COL_ALIASES[raw]
    m = re.match(r"^[a-zA-Z][\w]*:(.+@[a-z]{2,3}(?:-[A-Za-z0-9]+)?)$", raw)
    if m:
        return m.group(1)
    return raw


def _normalize_mappings_col(raw: str) -> str:
    """Normalise a Mappings-sheet column header to its canonical match-type key."""
    if raw in MAPPINGS_COL_ALIASES:
        return MAPPINGS_COL_ALIASES[raw]
    # Strip namespace prefix then try again (e.g. bare "relatedMatch")
    local = raw.split(":", 1)[-1] if ":" in raw else raw
    return MAPPINGS_COL_ALIASES.get(local, local)


# ---------------------------------------------------------------------------
# Sheet loaders
# ---------------------------------------------------------------------------

def _find_ws(wb, *names: str):
    """Return (worksheet, real_name) for the first matching sheet name (case-insensitive)."""
    lc = {s.lower(): s for s in wb.sheetnames}
    for n in names:
        real = lc.get(n.lower())
        if real:
            return wb[real], real
    return None, None


def load_cs_sheet(ws) -> dict[str, list[str]]:
    """Load Concept Scheme sheet: column A = key, columns B+ = values."""
    out: dict[str, list[str]] = {}
    for row in ws.iter_rows(values_only=True):
        if not row or row[0] is None or str(row[0]).strip() == "":
            continue
        raw_key = str(row[0]).strip()
        key = CS_KEY_ALIASES.get(raw_key, raw_key)
        vals = [str(v).strip() for v in row[1:] if v not in (None, "") and str(v).strip()]
        if vals:
            out.setdefault(key, []).extend(vals)
    return out


def _col_letter_to_idx(col: str) -> int:
    """Convert an Excel column letter (A, B, …, AA, …) to a 0-based index."""
    idx = 0
    for c in col.upper():
        idx = idx * 26 + (ord(c) - ord("A") + 1)
    return idx - 1


def _eval_formula(formula: str, row_cells: list, pref_label: str = "") -> str | None:
    """Resolve a simple Excel concatenation formula like ="base/"&ColRef.

    Falls back to a prefLabel-derived slug when the referenced cell is empty.
    """
    m = re.match(r'^="([^"]*)"&([A-Z]+)\d+$', str(formula))
    if not m:
        return None
    base, col_letters = m.group(1), m.group(2)
    col_idx = _col_letter_to_idx(col_letters)
    slug = None
    if col_idx < len(row_cells):
        cell_val = row_cells[col_idx].value
        if cell_val and not str(cell_val).startswith("http"):
            slug = str(cell_val).strip()
    if not slug and pref_label:
        slug = re.sub(r"[^a-z0-9]+", "-", pref_label.lower()).strip("-")
    return (base + slug) if slug else None


def load_concepts_sheet(ws) -> list[dict]:
    """Load the Concepts sheet.

    Handles formula-based conceptIRI cells (e.g. ="base/"&B2) and
    language-tagged column headers (e.g. skos:prefLabel@de → prefLabel@de).
    Requires a workbook loaded with data_only=False.
    """
    rows_cells = list(ws.iter_rows(values_only=False))
    if not rows_cells:
        return []

    headers: list[str | None] = []
    for c in rows_cells[0]:
        h = c.value
        if h is None or str(h).strip() == "":
            headers.append(None)
        else:
            headers.append(_normalize_concept_col(str(h).strip()))

    iri_idx  = next((i for i, h in enumerate(headers) if h == "conceptIRI"), None)
    pref_idx = next((i for i, h in enumerate(headers) if h == "prefLabel"),  None)

    records = []
    for row_cells in rows_cells[1:]:
        row_values = [c.value for c in row_cells]
        if not any(v not in (None, "") and str(v).strip() for v in row_values):
            continue

        rec: dict = {}
        for h, v in zip(headers, row_values):
            if h and v not in (None, "") and str(v).strip():
                rec[h] = v if isinstance(v, (int, float, datetime, date)) else str(v).strip()

        # Resolve formula-based conceptIRI cells (e.g. ="base/"&B2)
        if iri_idx is not None:
            raw_iri = row_cells[iri_idx].value
            if raw_iri and str(raw_iri).startswith("="):
                pref_label = (
                    str(row_values[pref_idx]).strip()
                    if pref_idx is not None and row_values[pref_idx]
                    else ""
                )
                resolved = _eval_formula(str(raw_iri), row_cells, pref_label)
                if resolved:
                    rec["conceptIRI"] = resolved

        if rec.get("conceptIRI"):
            rec["conceptIRI"] = normalize_iri(str(rec["conceptIRI"]))
            records.append(rec)
    return records


def load_namespaces_sheet(ws) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in ws.iter_rows(values_only=True):
        if not row or len(row) < 2:
            continue
        p  = str(row[0] or "").strip()
        ns = str(row[1] or "").strip()
        if p and ns and (ns.startswith("http://") or ns.startswith("https://")):
            pairs.append((p, ns))
    return pairs


def load_mappings_sheet(ws) -> dict[str, dict[str, list[str]]]:
    """Return {conceptIRI: {matchType: [targetIRI, ...]}} from a Mappings sheet.

    Expects a workbook loaded with data_only=True so that formula-based
    conceptIRI cells return their cached computed values.
    """
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {}

    headers: list[str | None] = []
    for h in rows[0]:
        if not h or str(h).strip() == "":
            headers.append(None)
        else:
            headers.append(_normalize_mappings_col(str(h).strip()))

    match_cols = {"relatedMatch", "closeMatch", "exactMatch", "narrowMatch", "broadMatch"}
    iri_idx = next(
        (i for i, h in enumerate(headers) if h == "conceptIRI"),
        0,
    )

    result: dict[str, dict[str, list[str]]] = {}
    for row in rows[1:]:
        if iri_idx >= len(row) or not row[iri_idx]:
            continue
        concept_iri = normalize_iri(str(row[iri_idx]).strip())
        if not concept_iri.startswith("http"):
            continue
        for ci, h in enumerate(headers):
            if h not in match_cols or ci >= len(row) or not row[ci]:
                continue
            for target in split_vals(str(row[ci])):
                if not target.startswith("http"):
                    continue
                result.setdefault(concept_iri, {}).setdefault(h, [])
                if target not in result[concept_iri][h]:
                    result[concept_iri][h].append(target)
    return result


# ---------------------------------------------------------------------------
# Issue detection
# ---------------------------------------------------------------------------

def detect_issues(
    cs_data: dict,
    concepts: list[dict],
    ns_sheet_name: str | None,
) -> list[str]:
    issues: list[str] = []

    if ns_sheet_name and "namespeces" in ns_sheet_name.lower():
        issues.append('The namespaces sheet is named "Namespeces" (typo for "Namespaces").')

    # Compare against what actually gets emitted: conceptIRI is normalised by
    # the loaders and the scheme subject by render_concept_scheme(), so the raw
    # workbook value would report scheme/concept mismatches that do not exist
    # in the generated TTL.
    scheme_iri = normalize_iri(str((cs_data.get("vocabularyIRI") or [""])[0]).strip())

    if scheme_iri.startswith("http://") and any(
        str(r.get("conceptIRI", "")).startswith("https://") for r in concepts
    ):
        issues.append(
            "vocabularyIRI uses http:// scheme. Concept IRIs in this workbook typically "
            "use https://. Consider normalizing to https:// for the scheme IRI."
        )

    concept_bases: set[str] = set()
    for r in concepts:
        iri = str(r.get("conceptIRI", "")).strip()
        if "/" in iri:
            concept_bases.add(iri.rstrip("/").rsplit("/", 1)[0])
    if concept_bases and concept_bases != {scheme_iri}:
        n = len(concept_bases)
        desc = "\n".join(
            f"       - <{b}> {'(matches scheme)' if b == scheme_iri else '(does NOT match scheme)'}"
            for b in sorted(concept_bases)
        )
        issues.append(
            f"vocabularyIRI is <{scheme_iri}>, but concept IRIs live under {n} distinct "
            f"parent IRI(s):\n{desc}\n"
            "     Transcribed as-written; reconcile in source if this is unintended."
        )

    bad_inschem: set[str] = set()
    for r in concepts:
        ins = normalize_iri(str(r.get("inScheme", "")).strip())
        if ins and ins != scheme_iri:
            bad_inschem.add(ins)
    if bad_inschem:
        desc = "\n".join(f"       - <{s}>" for s in sorted(bad_inschem))
        issues.append(
            f"Some concepts declare skos:inScheme pointing to an IRI other than the "
            f"vocabularyIRI <{scheme_iri}>:\n{desc}\n"
            "     Transcribed as-written; this will cause SKOS scheme membership checks to fail."
        )

    top_raw = cs_data.get("hasTopConcept", [])
    truncated = [v for v in top_raw if str(v).strip().endswith("/")]
    if truncated:
        issues.append(
            f"The scheme-level skos:hasTopConcept cell contains {len(truncated)} truncated "
            "or empty-slug URI(s). skos:hasTopConcept triples were instead derived from "
            "concept-level skos:topConceptOf values, which are complete."
        )

    concept_iris = {str(r.get("conceptIRI", "")).strip() for r in concepts}
    dangling: list[str] = []
    for r in concepts:
        broader = str(r.get("broader", "")).strip()
        if broader and broader not in concept_iris:
            pref = r.get("prefLabel", r.get("conceptIRI", "?"))
            dangling.append(f"       - '{pref}' → <{broader}>")
    if dangling:
        desc = "\n".join(dangling)
        issues.append(
            f"The following skos:broader references point to concepts NOT present in this "
            f"vocabulary:\n{desc}\n     Transcribed as-written."
        )

    return issues


# ---------------------------------------------------------------------------
# Agents (from Agents.xlsx)
# ---------------------------------------------------------------------------

# dcterms: property on the scheme → the isoroles that populate it.
DC_ROLE_MAP: dict[str, tuple[str, ...]] = {
    "creator":     ("isoroles:author", "isoroles:originator"),
    "publisher":   ("isoroles:publisher",),
    "contributor": ("isoroles:contributor",),
}


def _norm_role(r: str) -> str:
    """Repair the 'isorole:' typo and bracket full-IRI roles."""
    if r.startswith("isorole:") and not r.startswith("isoroles:"):
        return "isoroles:" + r[len("isorole:"):]
    if r.startswith(("http://", "https://")):
        return f"<{r}>"
    return r


def load_agent_registry(path: Path) -> dict | None:
    """Load Agents.xlsx: agent rows, agent-agent relations, per-scheme roles.

    Returns None when the workbook is absent. Scheme IRIs from the 'map' sheet
    are normalised so they match the scheme subjects this script emits.
    """
    if not path.is_file():
        return None
    agents: dict[str, list[dict]] = {}
    for row in _agents.load_agents(path):
        if uri := row.get("agentURI"):
            agents.setdefault(uri, []).append(row)
    relations: dict[str, list[tuple[str, str]]] = {}
    for src, tgt, pred in _agents.load_agent_relations(path):
        relations.setdefault(src, []).append((pred, tgt))
    roles: dict[str, dict[str, list[str]]] = {}
    for agent_uri, resource_uri, had_role in _agents.load_relations(path):
        per_agent = roles.setdefault(normalize_iri(resource_uri), {}).setdefault(agent_uri, [])
        for role in map(_norm_role, _agents.split_roles(had_role)):
            if role not in per_agent:
                per_agent.append(role)
    return {"agents": agents, "relations": relations, "roles": roles}


def agents_for_scheme(registry: dict, scheme_roles: dict[str, list[str]]) -> list[str]:
    """Mapped agents plus every registry agent they reference (memberOf, parent
    organisation, relations), transitively, so each is described in the file."""
    agents, relations = registry["agents"], registry["relations"]
    order: list[str] = []
    queue = list(scheme_roles)
    while queue:
        uri = queue.pop(0)
        if uri in order or uri not in agents:
            continue
        order.append(uri)
        for row in agents[uri]:
            queue += [row[k] for k in ("memberOfURI", "parentOrgURI") if row.get(k)]
        queue += [tgt for _pred, tgt in relations.get(uri, [])]
    return order


def resolve_dc_refs(
    cs_data: dict, scheme_roles: dict[str, list[str]]
) -> tuple[str | None, str | None, str | None]:
    """Return (creator_ref, publisher_ref, contributor_ref) for dcterms: properties.

    Each resolves to the IRIs of agents mapped to this scheme in Agents.xlsx
    with a matching role (DC_ROLE_MAP); failing that, the plain @en literal
    from the Concept Scheme sheet.
    """
    def ref(key: str) -> str | None:
        iris = [f"<{a}>" for a, roles in scheme_roles.items()
                if any(r in DC_ROLE_MAP[key] for r in roles)]
        if iris:
            return " , ".join(iris)
        val = (cs_data.get(key) or [None])[0]
        return ttl_str(val) if val and str(val).strip() else None

    return ref("creator"), ref("publisher"), ref("contributor")


# ---------------------------------------------------------------------------
# Block renderers
# ---------------------------------------------------------------------------

def render_prefix_block(
    wb_namespaces: list[tuple[str, str]],
    agent_prefixes: list[tuple[str, str]] | None = None,
) -> str:
    w = max(len(p) + 1 for p, _ in STANDARD_PREFIXES)
    lines = ["# Standard prefixes"]
    for p, ns in STANDARD_PREFIXES:
        label = f"{p}:"
        lines.append(f"@prefix {label:<{w}}  <{ns}> .")

    extras = [
        (p, ns) for p, ns in wb_namespaces
        if ns not in STANDARD_NS_SET and p not in STANDARD_PREFIX_NAMES
    ]
    if extras:
        we = max(len(p) + 1 for p, _ in extras)
        lines.append("")
        lines.append("# Workbook-specific prefixes (from the Namespaces sheet)")
        for p, ns in extras:
            label = f"{p}:"
            lines.append(f"@prefix {label:<{we}}  <{ns}> .")

    declared = STANDARD_PREFIX_NAMES | {p for p, _ in extras}
    agent_extras = [(p, ns) for p, ns in agent_prefixes or [] if p not in declared]
    if agent_extras:
        wa = max(len(p) + 1 for p, _ in agent_extras)
        lines.append("")
        lines.append("# Agent prefixes (from Agents.xlsx)")
        for p, ns in agent_extras:
            label = f"{p}:"
            lines.append(f"@prefix {label:<{wa}}  <{ns}> .")

    return "\n".join(lines)


def render_concept_scheme(
    cs_data: dict,
    top_concepts: list[str],
    creator_ref: str | None,
    publisher_ref: str | None,
    contributor_ref: str | None,
    attributions: list[tuple[str, list[str]]] | None = None,
) -> str:
    # Normalise, as render_ttl() does when deriving the slug and as the concept
    # loaders do for conceptIRI. Emitting the raw value here let a workbook with
    # http://kos.geospecimens.org write a ConceptScheme subject that no longer
    # matched its own concepts — and that the publisher's URI registry, which
    # only accepts the canonical https host, could not resolve.
    scheme_iri = normalize_iri(str(cs_data["vocabularyIRI"][0]).strip())

    def first(key: str) -> str | None:
        vals = cs_data.get(key)
        return str(vals[0]).strip() if vals else None

    lines: list[str] = [f"<{scheme_iri}>"]
    lines.append(_prop("a", "skos:ConceptScheme"))

    if pf := first("prefLabel"):
        lines.append(_prop("skos:prefLabel", ttl_str(pf)))
    if ti := first("title"):
        lines.append(_prop("dcterms:title", ttl_str(ti)))
    if defn := first("definition"):
        lines.append(_prop("skos:definition", ttl_long(defn)))
    if desc := first("description"):
        lines.append(_prop("dcterms:description", ttl_long(desc)))

    if publisher_ref:
        lines.append(_prop("dcterms:publisher", publisher_ref))
    if creator_ref:
        lines.append(_prop("dcterms:creator", creator_ref))
    if contributor_ref:
        lines.append(_prop("dcterms:contributor", contributor_ref))

    if prov := first("provenance"):
        lines.append(_prop("dcterms:provenance", ttl_str(prov)))

    created = parse_date(first("created"))
    if created:
        lines.append(_prop("dcterms:created", f'"{created}"^^xsd:date'))
    modified = parse_date(first("modified"))
    if modified:
        lines.append(_prop("dcterms:modified", f'"{modified}"^^xsd:date'))

    version_raw = first("version")
    if version_raw:
        ver = parse_date(version_raw) or version_raw
        lines.append(_prop("dcat:version", ttl_plain(ver)))

    if sn := first("scopeNote"):
        lines.append(_prop("skos:scopeNote", ttl_str(sn)))
    if un := first("usageNote"):
        lines.append(_prop("vann:usageNote", ttl_str(un)))
    if hn := first("historyNote"):
        lines.append(_prop("skos:historyNote", ttl_str(hn)))
    if note := first("note"):
        lines.append(_prop("skos:note", ttl_str(note)))

    kws = split_vals(first("keywords"))
    if kws:
        lines.append(_multi("dcat:keyword", [ttl_str(k) for k in kws]))

    if cit := first("citation"):
        lines.append(_prop("schema:citation", ttl_str(cit)))

    df_raw = first("derivedFrom")
    if df_raw:
        df_items = [
            item.rstrip(",").strip()
            for item in re.split(r"[|\n]+", df_raw)
            if item.strip().rstrip(",")
        ]
        df_rendered = [
            f"<{clean_iri(i)}>" if re.match(r"^https?://", i) else ttl_str(i)
            for i in df_items
            if i
        ]
        if df_rendered:
            lines.append(_multi("prov:wasDerivedFrom", df_rendered))

    if lic := first("license"):
        lines.append(_prop("schema:license", f"<{clean_iri(lic)}>"))

    if dm := first("derivationMode"):
        lines.append(_prop("reg:derivationMode", f"<{_normalise_derivation_mode(dm)}>"))

    if st := first("status"):
        lines.append(_prop("reg:status", f"<{clean_iri(st)}>"))

    if top_concepts:
        lines.append(_multi("skos:hasTopConcept", [f"<{iri}>" for iri in top_concepts]))

    for agent_ref, roles in attributions or []:
        lines.append(f"{INDENT}prov:qualifiedAttribution [")
        lines.append(f"{BN_INDENT}{'a':<{BN_PROP_W}}prov:Attribution ;")
        lines.append(f"{BN_INDENT}{'prov:agent':<{BN_PROP_W}}{agent_ref} ;")
        if roles:
            lines.append(f"{BN_INDENT}{'dcat:hadRole':<{BN_PROP_W}}{' , '.join(roles)} ;")
        lines.append(f"{INDENT}] ;")

    lines.append(".")
    return "\n".join(lines)


def render_concept(
    rec: dict,
    scheme_iri: str,
    mappings: dict[str, dict[str, list[str]]] | None = None,
) -> str:
    iri = str(rec["conceptIRI"]).strip()
    concept_maps = (mappings or {}).get(iri, {})

    lines = [f"<{iri}>"]
    lines.append(_prop("a", "skos:Concept"))

    if pf := str(rec.get("prefLabel", "")).strip():
        lines.append(_prop("skos:prefLabel", ttl_str(pf)))

    # Language-tagged label / note variants (e.g. prefLabel@de, altLabel@fr)
    for key in sorted(rec.keys()):
        m = re.fullmatch(r"([a-zA-Z]+)@([a-z]{2,3}(?:-[A-Za-z0-9]+)?)", key)
        if not m:
            continue
        base, lang = m.group(1), m.group(2)
        pred = _LANG_TAG_PRED.get(base)
        if pred:
            val = str(rec[key]).strip()
            if val:
                lines.append(_prop(pred, ttl_str(val, lang=lang)))

    alt_raw = str(rec.get("altLabel", "")).strip()
    if alt_raw:
        alts = split_vals(alt_raw)
        if len(alts) == 1:
            lines.append(_prop("skos:altLabel", ttl_str(alts[0])))
        elif alts:
            lines.append(_multi("skos:altLabel", [ttl_str(a) for a in alts]))

    if defn := str(rec.get("definition", "")).strip():
        lines.append(_prop("skos:definition", ttl_long(defn)))

    if broader := str(rec.get("broader", "")).strip():
        lines.append(_prop("skos:broader", f"<{broader}>"))

    if prov := str(rec.get("provenance", "")).strip():
        lines.append(_prop("dcterms:provenance", ttl_str(prov)))

    if hn := str(rec.get("historyNote", "")).strip():
        lines.append(_prop("skos:historyNote", ttl_str(hn)))

    if en := str(rec.get("editorialNote", "")).strip():
        lines.append(_prop("skos:editorialNote", ttl_str(en)))

    if cn := str(rec.get("changeNote", "")).strip():
        lines.append(_prop("skos:changeNote", ttl_str(cn)))

    if un := str(rec.get("usageNote", "")).strip():
        lines.append(_prop("vann:usageNote", ttl_str(un)))

    # skos:inScheme — default to scheme IRI when the column is absent or blank
    inschem = str(rec.get("inScheme", "")).strip() or scheme_iri
    lines.append(_prop("skos:inScheme", f"<{inschem}>"))

    if rs := str(rec.get("registryStatus", "")).strip():
        lines.append(_prop("reg:status", f"<{rs}>"))

    if itco := str(rec.get("isTopConceptOf", "")).strip():
        lines.append(_prop("skos:topConceptOf", f"<{itco}>"))

    if notation := str(rec.get("notation", "")).strip():
        lines.append(_prop("skos:notation", ttl_plain(notation)))

    # SKOS match properties from Mappings sheet
    for match_type in ("relatedMatch", "closeMatch", "exactMatch", "narrowMatch", "broadMatch"):
        targets = concept_maps.get(match_type, [])
        if len(targets) == 1:
            lines.append(_prop(f"skos:{match_type}", f"<{targets[0]}>"))
        elif targets:
            lines.append(_multi(f"skos:{match_type}", [f"<{t}>" for t in targets]))

    lines.append(".")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def render_ttl(xlsx_path: Path, registry: dict | None = None) -> tuple[str, str, str]:
    """Return (ttl_text, scheme_slug, scheme_iri) for a given workbook.

    `registry` is the loaded Agents.xlsx (load_agent_registry); agents mapped
    to this scheme there are appended to the output.

    The workbook is loaded twice:
      data_only=False  — preserves formula strings for conceptIRI resolution
      data_only=True   — returns computed cell values for all other sheets,
                         including Mappings where conceptIRI may be a formula
    """
    wb_raw  = openpyxl.load_workbook(xlsx_path, data_only=False)
    wb_calc = openpyxl.load_workbook(xlsx_path, data_only=True)

    cs_ws,  _       = _find_ws(wb_calc, "Concept Scheme", "ConceptScheme")
    con_ws, _       = _find_ws(wb_raw,  "Concepts")
    ns_ws,  ns_name = _find_ws(wb_calc, "Namespaces", "Namespeces")
    ag_ws,  _       = _find_ws(wb_calc, "Agents")   # detected only, to note it is ignored
    map_ws, _       = _find_ws(wb_calc, "Mappings", "Mapping")

    cs_data       = load_cs_sheet(cs_ws)         if cs_ws  else {}
    concepts      = load_concepts_sheet(con_ws)  if con_ws else []
    wb_namespaces = load_namespaces_sheet(ns_ws) if ns_ws  else []
    mappings      = load_mappings_sheet(map_ws)  if map_ws else {}

    scheme_iri = str((cs_data.get("vocabularyIRI") or [""])[0]).strip()
    if not scheme_iri:
        raise ValueError(f"No vocabularyIRI found in {xlsx_path.name}")
    scheme_iri  = normalize_iri(scheme_iri)
    scheme_slug = iri_slug(scheme_iri)

    # Derive top concepts from concept-level isTopConceptOf (authoritative source).
    # Deduplicate by concept IRI, not by isTopConceptOf value.
    seen_top:     set[str]  = set()
    top_concepts: list[str] = []
    for r in concepts:
        itco  = str(r.get("isTopConceptOf", "")).strip()
        c_iri = str(r.get("conceptIRI",     "")).strip()
        if itco and c_iri and c_iri not in seen_top:
            seen_top.add(c_iri)
            top_concepts.append(c_iri)

    scheme_roles = dict(registry["roles"].get(scheme_iri, {})) if registry else {}
    agent_uris   = agents_for_scheme(registry, scheme_roles) if registry else []
    used_agent_prefixes: set[str] = set()
    agent_blocks = [
        _agents.render_agent_block(
            uri, registry["agents"][uri], registry["relations"].get(uri, []),
            used_agent_prefixes,
        )
        for uri in agent_uris
    ]
    agent_prefixes = [(p, ns) for p, ns in _agents.PREFIXES if p in used_agent_prefixes]
    attributions   = [(f"<{a}>", roles) for a, roles in scheme_roles.items()]

    creator_ref, publisher_ref, contributor_ref = resolve_dc_refs(cs_data, scheme_roles)
    issues     = detect_issues(cs_data, concepts, ns_name)

    sheets_used: list[str] = []
    if cs_ws:  sheets_used.append("Concept Scheme")
    if con_ws: sheets_used.append("Concepts")
    if ns_ws:  sheets_used.append(ns_name or "Namespaces")
    # A Mappings sheet with only column headers counts as absent.
    if any(t for m in mappings.values() for t in m.values()):
        sheets_used.append("Mappings")

    today = _dt.date.today().isoformat()
    out: list[str] = []

    vocab_name = str((cs_data.get("prefLabel") or cs_data.get("title") or [scheme_slug])[0])
    out.append(f"# {vocab_name} — SKOS ConceptScheme")
    out.append(f"# Generated from {xlsx_path.name}")
    out.append(f"# Source sheets used: {', '.join(sheets_used)}")
    if ag_ws:
        out.append("# Agents sheet ignored — agents come from Agents.xlsx")
    if registry is not None:
        if scheme_roles:
            out.append(f"# Agents: {len(scheme_roles)} mapped to this scheme in Agents.xlsx, "
                       f"{len(agent_uris)} described below")
        else:
            out.append("# Agents: none mapped to this scheme in the Agents.xlsx 'map' sheet")
    out.append(f"# Generated: {today}")
    if issues:
        out.append("#")
        out.append("# Data issues / transformation notes:")
        for i, issue in enumerate(issues, 1):
            first_line, *rest = issue.splitlines()
            out.append(f"#  {i}. {first_line}")
            for ln in rest:
                out.append(f"#  {ln}")
    out.append("")

    out.append(render_prefix_block(wb_namespaces, agent_prefixes))
    out.append("")

    out.append("# " + "=" * 76)
    out.append("# ConceptScheme")
    out.append("# " + "=" * 76)
    out.append("")
    out.append(render_concept_scheme(
        cs_data, top_concepts,
        creator_ref, publisher_ref, contributor_ref,
        attributions,
    ))
    out.append("")

    out.append("# " + "=" * 76)
    out.append("# Concepts")
    out.append("# " + "=" * 76)
    out.append("")
    for rec in concepts:
        out.append(render_concept(rec, scheme_iri, mappings))
        out.append("")

    if agent_blocks:
        out.append("# " + "=" * 76)
        out.append("# Agents (from Agents.xlsx)")
        out.append("# " + "=" * 76)
        out.append("")
        for block in agent_blocks:
            out.append(block)
            out.append("")

    return "\n".join(out).rstrip() + "\n", scheme_slug, scheme_iri


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert SKOS vocabulary workbook(s) to Turtle.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python utils/xlsx-to-ttl.py                # process all workbooks\n"
            "  python utils/xlsx-to-ttl.py HazardTypes    # process one by name\n"
            "  python utils/xlsx-to-ttl.py HazardTypes.xlsx"
        ),
    )
    parser.add_argument(
        "vocab",
        nargs="?",
        metavar="VOCAB",
        help="Workbook name to process, with or without the .xlsx extension "
             "(e.g. 'HazardTypes' or 'HazardTypes.xlsx'). "
             "Omit to process every workbook in sources/xlsx/.",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    xlsx_files = sorted(
        p for p in XLSX_DIR.glob("*.xlsx")
        if not p.name.startswith("~$") and p.name != "Agents.xlsx"
    )

    if args.vocab:
        target = args.vocab
        if not target.lower().endswith(".xlsx"):
            target += ".xlsx"
        matched = [p for p in xlsx_files if p.name.lower() == target.lower()]
        if not matched:
            available = ", ".join(p.stem for p in xlsx_files)
            print(f"ERROR: '{args.vocab}' not found in {XLSX_DIR}")
            print(f"Available vocabularies: {available}")
            raise SystemExit(1)
        xlsx_files = matched

    if not xlsx_files:
        print(f"No .xlsx files found in {XLSX_DIR}")
        return

    registry = load_agent_registry(AGENTS_XLSX)
    if registry is None:
        print(f"WARNING: {AGENTS_XLSX.relative_to(ROOT)} not found — no agents will be embedded")

    processed:    list[Path] = []
    seen_schemes: set[str]   = set()
    for xlsx in xlsx_files:
        try:
            ttl, slug, scheme_iri = render_ttl(xlsx, registry)
        except Exception as exc:
            print(f"ERROR processing {xlsx.name}: {exc}")
            continue
        seen_schemes.add(scheme_iri)
        out_path = OUT_DIR / f"{slug}.ttl"
        out_path.write_text(ttl, encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)}  ({len(ttl):,} bytes)")
        processed.append(out_path)

        _, unused = _analyse_prefixes(ttl)
        if unused:
            cleaned = _clean_prefixes(ttl, set(unused))
            out_path.write_text(cleaned, encoding="utf-8")
            print(f"  removed unused prefixes: {', '.join(sorted(unused))}")

    if registry and not args.vocab:
        unmatched = sorted(set(registry["roles"]) - seen_schemes)
        if unmatched:
            print("WARNING: Agents.xlsx 'map' sheet references scheme IRI(s) "
                  "with no vocabulary workbook:\n  " + "\n  ".join(unmatched))

    try:
        import rdflib
        SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
        print("\nValidating generated files…")
        for ttl_path in sorted(processed):
            g = rdflib.Graph().parse(ttl_path, format="turtle")
            schemes  = list(g.subjects(rdflib.RDF.type, SKOS.ConceptScheme))
            concepts = list(g.subjects(rdflib.RDF.type, SKOS.Concept))
            ok = len(schemes) == 1 and concepts
            print(
                f"  [{'OK' if ok else 'WARN'}] {ttl_path.name}: "
                f"{len(schemes)} scheme(s), {len(concepts)} concept(s)"
            )
    except ImportError:
        pass


if __name__ == "__main__":
    main()

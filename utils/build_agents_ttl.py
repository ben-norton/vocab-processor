"""Generate data/vocabs/agents.ttl from sources/xlsx/Agents.xlsx.

Reads:
  sources/xlsx/Agents.xlsx  —  'agents' sheet: agent descriptions
                             —  'map' sheet:    agent → vocabulary URI role mappings

Writes:
  data/vocabs/agents.ttl

Usage:
  # Generate agents.ttl (map sheet must be populated):
  python utils/build_agents_ttl.py

  # Populate the map sheet with default mappings, then generate:
  python utils/build_agents_ttl.py --init-map

The 'map' sheet has three columns, one row per role assignment:
  agentURI     — IRI of the agent
  resourceURI  — IRI of the vocabulary ConceptScheme
  hadRole      — a single isoroles: value (e.g. isoroles:editor)

Multiple rows sharing the same agentURI + resourceURI are merged into a single
prov:qualifiedAssociation block with all roles combined.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = Path(__file__).resolve().parents[1]
AGENTS_XLSX = ROOT / "sources" / "xlsx" / "Agents.xlsx"
OUT_TTL = ROOT / "data" / "vocabs" / "agents.ttl"

PREFIXES: list[tuple[str, str]] = [
    ("cmns-av",  "https://www.omg.org/spec/Commons/AnnotationVocabulary/"),
    ("dcat",     "http://www.w3.org/ns/dcat#"),
    ("isoroles", "http://def.isotc211.org/iso19115-1/2014/"
                 "CitationAndResponsiblePartyInformation/code/CI_RoleCode/"),
    ("prov",     "http://www.w3.org/ns/prov#"),
    ("schema",   "https://schema.org/"),
    ("skos",     "http://www.w3.org/2004/02/skos/core#"),
    ("xsd",      "http://www.w3.org/2001/XMLSchema#"),
]

# Default agent → vocab mappings used by --init-map
# Each entry: (agentURI, hadRole)
VOCAB_URIS: list[str] = [
    "https://kos.resources.org/def/aggregate-form",
    "https://kos.resources.org/def/constituent-part-proportion",
    "https://kos.resources.org/def/geological-specimen-material-type",
    "https://kos.resources.org/def/geological-specimen-name-type",
    "https://kos.resources.org/def/hazard-type",
]

# Default agent → role mappings used by --init-map (one entry per role, matching
# the one-row-per-role format of the 'map' sheet)
DEFAULT_MAPPED_AGENTS: list[tuple[str, str]] = [
    ("https://kos.geospecimens.org/org/ben-norton", "isoroles:publisher"),
    ("https://kos.geospecimens.org/org/ben-norton", "isoroles:author"),
    ("https://kos.geospecimens.org/org/minext",     "isoroles:editor"),
    ("https://kos.geospecimens.org/org/minext",     "isoroles:custodian"),
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _thin_border() -> Border:
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)


def split_roles(val: str | None) -> list[str]:
    if not val:
        return []
    return [r.strip() for r in val.split(",") if r.strip()]


def escape_ttl(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ── xlsx readers ─────────────────────────────────────────────────────────────

def load_agents(xlsx_path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheet_map = {s.lower(): s for s in wb.sheetnames}
    ws_name = sheet_map.get("agents")
    if not ws_name:
        raise ValueError(f"No 'agents' sheet found in {xlsx_path.name}")
    ws = wb[ws_name]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() if h is not None else None for h in rows[0]]
    agents: list[dict] = []
    for row in rows[1:]:
        rec: dict = {}
        for h, v in zip(headers, row):
            if h and v not in (None, "") and str(v).strip():
                rec[h] = str(v).strip()
        if rec.get("agentURI") or rec.get("blankNodeLabel"):
            agents.append(rec)
    return agents


def load_relations(xlsx_path: Path) -> list[tuple[str, str, str]]:
    """Return [(agentURI, resourceURI, hadRole)] from the 'map' sheet.

    Falls back to 'rdf-relations' if 'map' is not present.
    Each row carries a single role value; callers aggregate by (agent, resource).
    """
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheet_map = {s.lower(): s for s in wb.sheetnames}
    ws_name = sheet_map.get("map") or sheet_map.get("rdf-relations")
    if not ws_name:
        return []
    ws = wb[ws_name]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    headers = [str(h).strip().lower() if h is not None else None for h in rows[0]]
    try:
        agent_col = headers.index("agenturi")
        resource_col = headers.index("resourceuri")
    except ValueError:
        return []
    role_col = headers.index("hadrole") if "hadrole" in headers else None
    relations: list[tuple[str, str, str]] = []
    for row in rows[1:]:
        a = row[agent_col]
        r = row[resource_col]
        role = row[role_col] if role_col is not None else None
        if a and r:
            relations.append((
                str(a).strip(),
                str(r).strip(),
                str(role).strip() if role else "",
            ))
    return relations


# ── xlsx writer ───────────────────────────────────────────────────────────────

def populate_map_sheet(
    xlsx_path: Path,
    mapped_agents: list[tuple[str, str]],
    vocab_uris: list[str],
) -> None:
    """Add / replace the 'map' sheet in xlsx_path with default mappings.

    mapped_agents: list of (agentURI, singleRole) tuples — one entry per role.
    Produces one row per (agentURI, role, vocabURI) combination.
    """
    from openpyxl.utils import get_column_letter

    wb = openpyxl.load_workbook(xlsx_path)
    if "map" in wb.sheetnames:
        del wb["map"]
    ws = wb.create_sheet("map")
    ws.sheet_view.showGridLines = False

    thin = _thin_border()
    hdr_fill = PatternFill("solid", fgColor="1F4E79")
    hdr_font = Font(name="Calibri", bold=True, size=10, color="FFFFFF")

    col_widths = [54, 54, 44]
    for ci, (hdr, width) in enumerate(
        zip(["agentURI", "resourceURI", "hadRole"], col_widths), start=1
    ):
        c = ws.cell(row=1, column=ci, value=hdr)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[1].height = 20

    row_idx = 2
    for agent_uri, had_role in mapped_agents:
        for vocab_uri in vocab_uris:
            bg = "EBF3FB" if row_idx % 2 == 0 else "FFFFFF"
            row_fill = PatternFill("solid", fgColor=bg)
            for ci, val in enumerate([agent_uri, vocab_uri, had_role], start=1):
                c = ws.cell(row=row_idx, column=ci, value=val)
                c.font = Font(name="Consolas", size=9, color="1F4E79")
                c.fill = row_fill
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.border = thin
            ws.row_dimensions[row_idx].height = 16
            row_idx += 1

    wb.save(xlsx_path)
    print(
        f"Populated 'map' sheet in {xlsx_path.name} "
        f"({row_idx - 2} rows: {len(mapped_agents)} agent-role pairs × {len(vocab_uris)} vocabs)"
    )


# ── TTL renderers ─────────────────────────────────────────────────────────────

def render_agent_block(uri: str, rows: list[dict]) -> str:
    """Merge multiple rows for the same agentURI into one agent block."""
    first = rows[0]
    atype = first.get("agentType", "schema:Thing")

    lines = [f"<{uri}>"]
    lines.append(f"    a {atype} ;")

    if first.get("agentName"):
        lines.append(f'    schema:name "{escape_ttl(first["agentName"])}" ;')
    if first.get("orcidURI"):
        lines.append(f'    schema:identifier <{first["orcidURI"]}> ;')
    if first.get("agentEmail"):
        lines.append(f'    schema:email "{escape_ttl(first["agentEmail"])}" ;')
    if first.get("agentURL"):
        lines.append(f'    schema:url "{first["agentURL"]}"^^xsd:anyURI ;')
    if first.get("agentHomepage"):
        lines.append(f'    schema:homepage "{first["agentHomepage"]}"^^xsd:anyURI ;')
    if first.get("acronym"):
        lines.append(f'    cmns-av:acronym "{escape_ttl(first["acronym"])}" ;')
    if first.get("parentOrgURI"):
        lines.append(f"    schema:parentOrganization <{first['parentOrgURI']}> ;")

    # Collect all unique memberOf URIs across merged rows
    member_uris: list[str] = []
    seen: set[str] = set()
    for row in rows:
        m = row.get("memberOfURI")
        if m and m not in seen:
            seen.add(m)
            member_uris.append(m)
    if len(member_uris) == 1:
        lines.append(f"    schema:memberOf <{member_uris[0]}> ;")
    elif member_uris:
        joined = " ,\n        ".join(f"<{u}>" for u in member_uris)
        lines.append(f"    schema:memberOf\n        {joined} ;")

    lines.append(".")
    return "\n".join(lines)


def render_vocab_block(
    vocab_uri: str,
    agent_roles: list[tuple[str, list[str]]],
) -> str:
    """Render a ConceptScheme block with prov:qualifiedAssociation per mapped agent."""
    lines = [f"<{vocab_uri}>"]
    lines.append("    a skos:ConceptScheme ;")
    for agent_uri, roles in agent_roles:
        lines.append("    prov:qualifiedAssociation [")
        lines.append("        a prov:Association ;")
        lines.append(f"        prov:agent <{agent_uri}> ;")
        lines.append(f"        prov:hadRole {' , '.join(roles)} ;")
        lines.append("    ] ;")
    lines.append(".")
    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def build_ttl() -> None:
    agent_rows = load_agents(AGENTS_XLSX)
    relations = load_relations(AGENTS_XLSX)

    if not relations:
        raise SystemExit(
            "ERROR: 'map' sheet in Agents.xlsx is empty or missing.\n"
            "Run with --init-map to populate it with default mappings, then retry."
        )

    # Group agent rows by URI (merge multiple memberOf rows)
    agents_by_uri: dict[str, list[dict]] = defaultdict(list)
    agent_order: list[str] = []
    for row in agent_rows:
        uri = row.get("agentURI", "")
        if not uri:
            continue
        if uri not in agents_by_uri:
            agent_order.append(uri)
        agents_by_uri[uri].append(row)

    # Aggregate roles from the map sheet.
    # Multiple rows with the same (agentURI, resourceURI) are merged into one
    # prov:qualifiedAssociation block; insertion order of both vocabs and agents
    # within each vocab is preserved.
    pair_roles: dict[tuple[str, str], list[str]] = defaultdict(list)  # (resource, agent) → roles
    vocab_agent_order: dict[str, list[str]] = defaultdict(list)        # resource → [agent URIs]
    for agent_uri, resource_uri, had_role in relations:
        key = (resource_uri, agent_uri)
        # Accumulate roles (split handles both single values and comma-separated)
        for role in split_roles(had_role):
            if role not in pair_roles[key]:
                pair_roles[key].append(role)
        if agent_uri not in vocab_agent_order[resource_uri]:
            vocab_agent_order[resource_uri].append(agent_uri)

    vocab_agents: dict[str, list[tuple[str, list[str]]]] = {
        resource_uri: [
            (agent_uri, pair_roles[(resource_uri, agent_uri)])
            for agent_uri in agent_uris
            if pair_roles[(resource_uri, agent_uri)]
        ]
        for resource_uri, agent_uris in vocab_agent_order.items()
    }

    # Build TTL
    out: list[str] = []

    longest_prefix = max(len(p) for p, _ in PREFIXES)
    for p, ns in PREFIXES:
        pad = " " * (longest_prefix - len(p) + 1)
        out.append(f"@prefix {p}:{pad}<{ns}> .")
    out.append("")

    out.append("# " + "=" * 76)
    out.append("# Agents")
    out.append("# " + "=" * 76)
    out.append("")
    for uri in agent_order:
        out.append(render_agent_block(uri, agents_by_uri[uri]))
        out.append("")

    if vocab_agents:
        out.append("# " + "=" * 76)
        out.append("# Vocabulary Agent Mappings")
        out.append("# " + "=" * 76)
        out.append("")
        for vocab_uri in sorted(vocab_agents):
            out.append(render_vocab_block(vocab_uri, vocab_agents[vocab_uri]))
            out.append("")

    ttl = "\n".join(out).rstrip() + "\n"
    OUT_TTL.parent.mkdir(parents=True, exist_ok=True)
    OUT_TTL.write_text(ttl, encoding="utf-8")
    print(f"Wrote {OUT_TTL.relative_to(ROOT)}  ({len(ttl):,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate data/vocabs/agents.ttl from Agents.xlsx."
    )
    parser.add_argument(
        "--init-map",
        action="store_true",
        help=(
            "Populate the 'map' sheet in Agents.xlsx with default "
            "agent → vocabulary role mappings, then generate agents.ttl."
        ),
    )
    args = parser.parse_args()

    if args.init_map:
        populate_map_sheet(AGENTS_XLSX, DEFAULT_MAPPED_AGENTS, VOCAB_URIS)


    build_ttl()


if __name__ == "__main__":
    main()

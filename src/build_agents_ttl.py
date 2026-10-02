"""Generate data/vocabs/agents.ttl from sources/xlsx/Agents.xlsx.

Reads:
  sources/xlsx/Agents.xlsx
    - 'agents'    sheet: one row per agent (URI, name, type, memberOf, parent org, …)
    - 'relations' sheet: agent-to-agent relations
                         (agentURI, relatedAgentURI, agentRole)
                         'agentRole' holds a *predicate* IRI such as
                         https://d-nb.info/standards/elementset/agrelon#hasEmployer
                         or http://www.w3.org/ns/org#unitOf.
    - 'map'       sheet: agent -> ConceptScheme role mappings
                         (agentURI, resourceURI, hadRole)

Writes:
  data/vocabs/agents.ttl
    - one block per agent with schema:/cmns-av:/rdfs: metadata plus
      inline agent-to-agent relations pulled from the 'relations' sheet
      (rendered with a CURIE when the predicate namespace is known,
      otherwise as a full <IRI>).
    - one block per ConceptScheme referenced in the map sheet, giving
      each mapped agent a prov:qualifiedAssociation (with prov:agent
      pointing to the *same* agent URI defined above, so the whole
      graph is self-linked).

Usage:
  python src/build_agents_ttl.py                # generate agents.ttl
  python src/build_agents_ttl.py --init-map     # (re)seed the 'map' sheet
                                                # with default mappings,
                                                # then generate.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

ROOT = Path(__file__).resolve().parents[1]
AGENTS_XLSX = ROOT / "sources" / "xlsx" / "Agents.xlsx"
OUT_TTL = ROOT / "data" / "vocabs" / "agents.ttl"

# All prefixes we might emit. `_emit_used_prefixes` filters this list to
# only the ones actually referenced in the output body, so agents.ttl stays
# clean when a namespace isn't needed.
PREFIXES: list[tuple[str, str]] = [
    ("agrelon",  "https://d-nb.info/standards/elementset/agrelon#"),
    ("cmns-av",  "https://www.omg.org/spec/Commons/AnnotationVocabulary/"),
    ("dcat",     "http://www.w3.org/ns/dcat#"),
    ("dcterms",  "http://purl.org/dc/terms/"),
    ("foaf",     "http://xmlns.com/foaf/0.1/"),
    ("isoroles", "http://def.isotc211.org/iso19115-1/2014/"
                 "CitationAndResponsiblePartyInformation/code/CI_RoleCode/"),
    ("org",      "http://www.w3.org/ns/org#"),
    ("owl",      "http://www.w3.org/2002/07/owl#"),
    ("prov",     "http://www.w3.org/ns/prov#"),
    ("rdfs",     "http://www.w3.org/2000/01/rdf-schema#"),
    ("schema",   "https://schema.org/"),
    ("skos",     "http://www.w3.org/2004/02/skos/core#"),
    ("xsd",      "http://www.w3.org/2001/XMLSchema#"),
]

# Default agent → vocab mappings used by --init-map. Each entry:
# (agentURI, singleRole). One row is emitted per (agent, role, vocab) combo.
VOCAB_URIS: list[str] = [
    "https://kos.resources.org/def/aggregate-form",
    "https://kos.resources.org/def/specimen-part-proportion",
    "https://kos.resources.org/def/geological-specimen-material-type",
    "https://kos.resources.org/def/geological-specimen-name-type",
    "https://kos.resources.org/def/hazard-type",
]

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


def normalize_iri(iri: str) -> str:
    """Rewrite http://kos.geospecimens.org → https://, as xlsx-to-ttl.py does,
    so scheme IRIs here match the scheme subjects of the vocabulary files."""
    iri = iri.strip()
    if iri.startswith("http://kos.geospecimens.org"):
        iri = "https://" + iri[len("http://"):]
    return iri


def _scheme_variants(iri: str) -> tuple[str, ...]:
    """Return (iri, iri-with-scheme-swapped) so http↔https data typos still match."""
    if iri.startswith("http://"):
        return (iri, "https://" + iri[len("http://"):])
    if iri.startswith("https://"):
        return (iri, "http://" + iri[len("https://"):])
    return (iri,)


def curie_or_iri(iri: str, prefixes: list[tuple[str, str]]) -> tuple[str, str | None]:
    """Return (rendered, prefix_used_or_None) for a predicate/individual IRI.

    Chooses the longest matching prefix so `https://schema.org/foo` doesn't
    accidentally win over a more specific namespace when both are declared.
    http↔https on the *scheme* is treated as equivalent so hand-authored
    workbook data can match canonical namespace URIs. Falls back to a full
    angle-bracketed IRI when no prefix matches.
    """
    best_prefix: str | None = None
    best_local: str | None = None
    best_ns_len = -1
    for iri_variant in _scheme_variants(iri):
        for prefix, ns in prefixes:
            if iri_variant.startswith(ns) and len(ns) > best_ns_len:
                local = iri_variant[len(ns):]
                if local and all(c not in local for c in " \t<>\"{}|^`"):
                    best_prefix = prefix
                    best_local = local
                    best_ns_len = len(ns)
    if best_prefix is not None and best_local is not None:
        return f"{best_prefix}:{best_local}", best_prefix
    return f"<{iri}>", None


# ── xlsx readers ─────────────────────────────────────────────────────────────

def _sheet(wb: openpyxl.Workbook, *candidates: str):
    """Return the first sheet whose lower-cased name matches any candidate."""
    lookup = {s.lower(): s for s in wb.sheetnames}
    for name in candidates:
        if name.lower() in lookup:
            return wb[lookup[name.lower()]]
    return None


def load_agents(xlsx_path: Path) -> list[dict]:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = _sheet(wb, "agents")
    if ws is None:
        raise ValueError(f"No 'agents' sheet found in {xlsx_path.name}")
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


def load_agent_relations(xlsx_path: Path) -> list[tuple[str, str, str]]:
    """Return [(agentURI, relatedAgentURI, predicateIRI)] from 'relations'."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = _sheet(wb, "relations", "agent-relations")
    if ws is None:
        return []
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return []
    headers = [str(h).strip().lower() if h is not None else None for h in rows[0]]

    def col(*names: str) -> int | None:
        for n in names:
            if n in headers:
                return headers.index(n)
        return None

    ai = col("agenturi")
    ri = col("relatedagenturi", "targeturi", "objecturi")
    pi = col("agentrole", "predicateuri", "predicate", "relationuri", "role")
    if ai is None or ri is None or pi is None:
        return []
    out: list[tuple[str, str, str]] = []
    for row in rows[1:]:
        a = row[ai]
        r = row[ri]
        p = row[pi]
        if a and r and p:
            out.append((str(a).strip(), str(r).strip(), str(p).strip()))
    return out


def load_relations(xlsx_path: Path) -> list[tuple[str, str, str]]:
    """Return [(agentURI, resourceURI, hadRole)] from the 'map' sheet."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = _sheet(wb, "map", "rdf-relations")
    if ws is None:
        return []
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
                normalize_iri(str(r)),
                str(role).strip() if role else "",
            ))
    return relations


# ── xlsx writer ───────────────────────────────────────────────────────────────

def populate_map_sheet(
    xlsx_path: Path,
    mapped_agents: list[tuple[str, str]],
    vocab_uris: list[str],
) -> None:
    """Add / replace the 'map' sheet in xlsx_path with default mappings."""
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

def render_agent_block(
    uri: str,
    rows: list[dict],
    relations: list[tuple[str, str]],
    used_prefixes: set[str],
) -> str:
    """Merge multiple rows for the same agentURI into one agent block.

    `relations` is a list of (predicateIRI, targetIRI) already filtered to
    this agent. Each predicate is rendered as a CURIE when possible; a full
    IRI otherwise. `used_prefixes` accumulates every prefix referenced so the
    header only emits declarations actually needed.
    """
    first = rows[0]
    atype = first.get("agentType", "schema:Thing")

    # Track prefixes used inside this block.
    def use(prefix: str) -> None:
        used_prefixes.add(prefix)

    # Agent type may itself be a CURIE (e.g. "schema:Person"). Record its
    # prefix so it survives filtering.
    if ":" in atype and not atype.startswith("<"):
        use(atype.split(":", 1)[0])

    lines = [f"<{uri}>"]
    lines.append(f"    a {atype} ;")

    if first.get("agentName"):
        use("schema")
        lines.append(f'    schema:name "{escape_ttl(first["agentName"])}" ;')
    if first.get("orcidURI"):
        use("schema")
        lines.append(f'    schema:identifier <{first["orcidURI"]}> ;')
    if first.get("agentEmail"):
        use("schema")
        lines.append(f'    schema:email "{escape_ttl(first["agentEmail"])}" ;')
    if first.get("agentURL"):
        use("schema"); use("xsd")
        lines.append(f'    schema:url "{first["agentURL"]}"^^xsd:anyURI ;')
    if first.get("agentHomepage"):
        use("schema"); use("xsd")
        lines.append(f'    schema:homepage "{first["agentHomepage"]}"^^xsd:anyURI ;')
    if first.get("acronym"):
        use("cmns-av")
        lines.append(f'    cmns-av:acronym "{escape_ttl(first["acronym"])}" ;')
    if first.get("parentOrgURI"):
        use("schema")
        lines.append(f"    schema:parentOrganization <{first['parentOrgURI']}> ;")

    # schema:memberOf — union of all rows for this agent
    member_uris: list[str] = []
    seen: set[str] = set()
    for row in rows:
        m = row.get("memberOfURI")
        if m and m not in seen:
            seen.add(m)
            member_uris.append(m)
    if member_uris:
        use("schema")
        if len(member_uris) == 1:
            lines.append(f"    schema:memberOf <{member_uris[0]}> ;")
        else:
            joined = " ,\n        ".join(f"<{u}>" for u in member_uris)
            lines.append(f"    schema:memberOf\n        {joined} ;")

    # Free-text notes → rdfs:comment (one row's worth is enough; join if many).
    notes = [row["notes"] for row in rows if row.get("notes")]
    if notes:
        use("rdfs")
        text = escape_ttl(" ".join(notes))
        lines.append(f'    rdfs:comment "{text}"@en ;')

    # Agent-to-agent relations from the 'relations' sheet, grouped by predicate
    # so multiple targets on the same predicate share one property line.
    if relations:
        by_pred: dict[str, list[str]] = defaultdict(list)
        pred_order: list[str] = []
        for pred, tgt in relations:
            rendered, pref = curie_or_iri(pred, PREFIXES)
            if pref:
                use(pref)
            if rendered not in pred_order:
                pred_order.append(rendered)
            if tgt not in by_pred[rendered]:
                by_pred[rendered].append(tgt)
        for pred in pred_order:
            targets = by_pred[pred]
            if len(targets) == 1:
                lines.append(f"    {pred} <{targets[0]}> ;")
            else:
                joined = " ,\n        ".join(f"<{t}>" for t in targets)
                lines.append(f"    {pred}\n        {joined} ;")

    lines.append(".")
    return "\n".join(lines)


def render_vocab_block(
    vocab_uri: str,
    agent_roles: list[tuple[str, list[str]]],
    used_prefixes: set[str],
) -> str:
    """Render a ConceptScheme block with prov:qualifiedAssociation per agent."""
    used_prefixes.update({"skos", "prov"})
    for _, roles in agent_roles:
        for role in roles:
            if ":" in role and not role.startswith("<"):
                used_prefixes.add(role.split(":", 1)[0])
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
    map_relations = load_relations(AGENTS_XLSX)
    agent_relations = load_agent_relations(AGENTS_XLSX)

    if not map_relations:
        raise SystemExit(
            "ERROR: 'map' sheet in Agents.xlsx is empty or missing.\n"
            "Run with --init-map to populate it with default mappings, then retry."
        )

    # Group agent rows by URI (merge multiple memberOf rows per agent)
    agents_by_uri: dict[str, list[dict]] = defaultdict(list)
    agent_order: list[str] = []
    for row in agent_rows:
        uri = row.get("agentURI", "")
        if not uri:
            continue
        if uri not in agents_by_uri:
            agent_order.append(uri)
        agents_by_uri[uri].append(row)

    # Group agent-to-agent relations by source URI.
    relations_by_agent: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for src, tgt, pred in agent_relations:
        relations_by_agent[src].append((pred, tgt))

    # Warn on relations pointing at unknown agents (a common authoring bug —
    # e.g. the current workbook mixes kos.resources.org and kos.geospecimens.org).
    unknown_sources = sorted({s for s in relations_by_agent if s not in agents_by_uri})
    unknown_targets = sorted({
        t for rels in relations_by_agent.values() for _p, t in rels
        if t not in agents_by_uri
    })
    if unknown_sources:
        print(
            "WARNING: 'relations' sheet references agentURI(s) not defined in "
            "'agents' sheet:\n  " + "\n  ".join(unknown_sources)
        )
    if unknown_targets:
        print(
            "WARNING: 'relations' sheet references relatedAgentURI(s) not "
            "defined in 'agents' sheet:\n  " + "\n  ".join(unknown_targets)
        )

    # Aggregate roles from the map sheet. Multiple rows sharing
    # (agentURI, resourceURI) merge into a single qualifiedAssociation block.
    pair_roles: dict[tuple[str, str], list[str]] = defaultdict(list)
    vocab_agent_order: dict[str, list[str]] = defaultdict(list)
    for agent_uri, resource_uri, had_role in map_relations:
        key = (resource_uri, agent_uri)
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

    # Render body first; the prefix header is filtered afterwards to include
    # only the namespaces the body actually references.
    used_prefixes: set[str] = set()
    body: list[str] = []

    body.append("# " + "=" * 76)
    body.append("# Agents")
    body.append("# " + "=" * 76)
    body.append("")
    for uri in agent_order:
        body.append(
            render_agent_block(
                uri,
                agents_by_uri[uri],
                relations_by_agent.get(uri, []),
                used_prefixes,
            )
        )
        body.append("")

    if vocab_agents:
        body.append("# " + "=" * 76)
        body.append("# Vocabulary Agent Mappings")
        body.append("# " + "=" * 76)
        body.append("")
        for vocab_uri in sorted(vocab_agents):
            body.append(render_vocab_block(vocab_uri, vocab_agents[vocab_uri], used_prefixes))
            body.append("")

    used = [(p, ns) for p, ns in PREFIXES if p in used_prefixes]
    header: list[str] = []
    if used:
        longest_prefix = max(len(p) for p, _ in used)
        for p, ns in used:
            pad = " " * (longest_prefix - len(p) + 1)
            header.append(f"@prefix {p}:{pad}<{ns}> .")
        header.append("")

    ttl = "\n".join(header + body).rstrip() + "\n"
    OUT_TTL.parent.mkdir(parents=True, exist_ok=True)
    OUT_TTL.write_text(ttl, encoding="utf-8")

    rel_count = sum(len(v) for v in relations_by_agent.values())
    print(
        f"Wrote {OUT_TTL.relative_to(ROOT)}  ({len(ttl):,} bytes) — "
        f"{len(agent_order)} agents, {rel_count} agent-agent relations, "
        f"{len(vocab_agents)} vocab mappings"
    )


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

#!/usr/bin/env python3
"""
Build an XKOS-AP-NO conformant serialization of the Weisberg, McCoy & Krot
(2006) meteorite classification.

Inputs (sources/classification-systems/meteorites/), all built from the source
workbook meteorite-classification.xlsx by
`python src/build_classification_csvs.py meteorites` — edit the workbook, not
the CSVs:
         meteorite_classification_scheme.csv (scheme-level metadata: IRIs,
                                        namespaces, prefixes, titles, publisher,
                                        language, date; key,value,notes rows)
         meteorite_classification.csv  (items; columns per data dictionary)
         meteorite_data_dictionary.csv (column semantics -> predicate mapping)
         meteorite_sources.csv         (bibliography -> provenance resources)

Values in the scheme CSV may reference other keys as {key}, e.g.
level_namespace = {base_iri}/level/, so the base domain is edited in one place.
Profile: xkos-ap-no-shacl-v1.ttl (Norwegian application profile of XKOS)

Column -> RDF mapping (informed by the data dictionary):
  id          -> row key only (hierarchy joins); the item IRI is minted from
                 `name` as a lower-case hyphenated slug, <concept_namespace><slug>,
                 matching the IRI pattern of the other geospecimens vocabularies
                 (e.g. https://kos.geospecimens.org/def/meteorite-classification/<slug>).
                 dct:identifier carries the same slug literal.
  parent_id   -> skos:broader + xkos:specializes (inverses asserted)
  rank        -> skos:member from the matching xkos:ClassificationLevel. One of
                 root or the ranks in RANKS, highest first: division (children
                 of the root), class, clan, group, subgroup. Each rank is a
                 concept <rank_namespace><rank> (/def/meteorite-classification/
                 rank/<rank>) in the rank scheme, ordered by skos:notation 1..5
                 and chained by xkos:next / xkos:previous; level n (xkos:depth n)
                 is xkos:organizedBy rank n.
  code       -> skos:notation (plain literal)
  name        -> skos:prefLabel @en
  description -> skos:definition @en  (AP-NO requires a Literal, not a note instance)
  source      -> dct:source -> mcref:* (dct:BibliographicResource)
  notes       -> skos:editorialNote @en
  depth, materialized_path, path_labels -> not serialized (derivable)
"""
import csv
import re
from datetime import date
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, BNode, RDF, RDFS, XSD
from rdflib.namespace import SKOS, DCTERMS, FOAF
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parents[1]
UP   = ROOT / "sources" / "classification-systems" / "meteorites"

REQUIRED_META = [
    "scheme_iri", "concept_namespace", "concept_prefix", "level_namespace",
    "level_prefix", "rank_namespace", "rank_prefix",
    "reference_namespace", "reference_prefix", "title", "description",
    "source_reference", "creator_iri", "language_iri", "created", "status",
    "publisher_iri",
    "publisher_name", "publisher_homepage", "rank_scheme_iri",
    "rank_scheme_title", "rank_scheme_description",
]


def load_scheme_meta(path: Path) -> dict[str, str]:
    """Read key,value rows from the scheme metadata CSV and resolve {key}
    references between values (e.g. {base_iri}/level/)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        meta = {r["key"].strip(): (r["value"] or "").strip()
                for r in csv.DictReader(f) if (r["key"] or "").strip()}
    ref = re.compile(r"\{(\w+)\}")
    for _ in range(len(meta)):
        resolved = {k: ref.sub(lambda m: meta.get(m.group(1), m.group(0)), v)
                    for k, v in meta.items()}
        if resolved == meta:
            break
        meta = resolved
    missing    = [k for k in REQUIRED_META if not meta.get(k)]
    unresolved = {k: v for k, v in meta.items() if ref.search(v)}
    if missing or unresolved:
        raise SystemExit(f"{path.name}: missing keys {missing}, "
                         f"unresolved references {unresolved}")
    return meta


META = load_scheme_meta(UP / "meteorite_classification_scheme.csv")

MC     = Namespace(META["concept_namespace"])
MCLVL  = Namespace(META["level_namespace"])
MCRANK = Namespace(META["rank_namespace"])
MCREF  = Namespace(META["reference_namespace"])
XKOS   = Namespace("http://rdf-vocabulary.ddialliance.org/xkos#")
UNESKOS= Namespace("http://purl.org/umu/uneskos#")
REG    = Namespace("http://purl.org/linked-data/registry#")
EULANG = URIRef(META["language_iri"])
STATUS = URIRef(META["status"])

g = Graph()
for p, n in [(META["concept_prefix"], MC), (META["level_prefix"], MCLVL),
             (META["rank_prefix"], MCRANK), (META["reference_prefix"], MCREF),
             ("xkos", XKOS), ("uneskos", UNESKOS), ("skos", SKOS),
             ("dct", DCTERMS), ("foaf", FOAF), ("reg", REG), ("xsd", XSD)]:
    g.bind(p, n)

items   = list(csv.DictReader(open(UP / "meteorite_classification.csv", encoding="utf-8-sig")))
sources = list(csv.DictReader(open(UP / "meteorite_sources.csv", encoding="utf-8-sig")))

if META["source_reference"] not in {s["cite_key"] for s in sources}:
    raise SystemExit(f"source_reference {META['source_reference']!r} is not a "
                     "cite_key in meteorite_sources.csv")

scheme      = URIRef(META["scheme_iri"])
rank_scheme = URIRef(META["rank_scheme_iri"])
agent       = URIRef(META["publisher_iri"])
creator     = URIRef(META["creator_iri"])
today       = Literal(META.get("modified") or date.today().isoformat(), datatype=XSD.date)
created     = Literal(META["created"], datatype=XSD.date)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

by_id = {r["id"].strip(): r for r in items}
_slugs = [slugify(r["name"]) for r in items]
_dupes = {s for s in _slugs if _slugs.count(s) > 1}
if _dupes:
    raise SystemExit("duplicate concept slugs, disambiguate names: %s" % sorted(_dupes))

def iri(row_id): return MC[slugify(by_id[str(row_id).strip()]["name"])]

# Descending: division is the highest rank (the root's children), subgroup the lowest.
RANKS = ["division", "class", "clan", "group", "subgroup"]
_bad_ranks = sorted({r["rank"] for r in items} - set(RANKS) - {"root"})
if _bad_ranks:
    raise SystemExit("unknown rank values in meteorite_classification.csv: %s" % _bad_ranks)

# ---------------------------------------------------------------- publisher
g.add((agent, RDF.type, FOAF.Agent))
g.add((agent, FOAF.name, Literal(META["publisher_name"], lang="en")))
g.add((agent, FOAF.homepage, URIRef(META["publisher_homepage"])))

# ---------------------------------------------------------------- bibliography
src_by_short = {}
for s in sources:
    ref = MCREF[s["cite_key"]]
    src_by_short[s["short_form"]] = ref
    g.add((ref, RDF.type, DCTERMS.BibliographicResource))
    g.add((ref, RDFS.label, Literal(s["short_form"], lang="en")))
    g.add((ref, DCTERMS.bibliographicCitation, Literal(s["full_citation"], lang="en")))
    ident = s["identifier"].strip()
    if ident.startswith("doi:"):
        g.add((ref, DCTERMS.identifier, URIRef("https://doi.org/" + ident[4:])))
    elif ident.startswith("ISBN:"):
        g.add((ref, DCTERMS.identifier, URIRef("urn:isbn:" + ident[5:])))
    elif ident.startswith("http"):
        g.add((ref, DCTERMS.identifier, URIRef(ident)))

# ---------------------------------------------------------------- main scheme
g.add((scheme, RDF.type, SKOS.ConceptScheme))
g.add((scheme, DCTERMS.identifier, URIRef(str(scheme))))
g.add((scheme, DCTERMS.title, Literal(META["title"], lang="en")))
g.add((scheme, DCTERMS.description, Literal(META["description"], lang="en")))
g.add((scheme, DCTERMS.publisher, agent))
g.add((scheme, DCTERMS.creator, creator))
g.add((scheme, DCTERMS.language, EULANG))
g.add((scheme, DCTERMS.created, created))
g.add((scheme, DCTERMS.modified, today))
g.add((scheme, REG.status, STATUS))
g.add((scheme, DCTERMS.source, MCREF[META["source_reference"]]))
g.add((scheme, XKOS.numberOfLevels, Literal(str(len(RANKS)), datatype=XSD.positiveInteger)))

# ---------------------------------------------------------------- rank scheme
g.add((rank_scheme, RDF.type, SKOS.ConceptScheme))
g.add((rank_scheme, DCTERMS.identifier, URIRef(str(rank_scheme))))
g.add((rank_scheme, DCTERMS.title, Literal(META["rank_scheme_title"], lang="en")))
g.add((rank_scheme, DCTERMS.description, Literal(META["rank_scheme_description"], lang="en")))
g.add((rank_scheme, DCTERMS.publisher, agent))
g.add((rank_scheme, DCTERMS.creator, creator))
g.add((rank_scheme, DCTERMS.language, EULANG))
g.add((rank_scheme, DCTERMS.created, created))
g.add((rank_scheme, DCTERMS.modified, today))
g.add((rank_scheme, REG.status, STATUS))
g.add((rank_scheme, XKOS.numberOfLevels, Literal("1", datatype=XSD.positiveInteger)))

RANK_DEFS = {
    "division": "Highest rank, directly below the root (Meteorites): chondrites, primitive achondrites and achondrites.",
    "class":    "Group of chondrite or achondrite groups sharing primary whole-rock chemical and O-isotopic characteristics.",
    "clan":     "Chondrite or achondrite groups with chemical, mineralogical and isotopic similarities suggesting a common, closely related precursor or formation region.",
    "group":    "Minimum of five unpaired meteorites of similar petrologic, chemical and isotopic characteristics; the basic classification unit.",
    "subgroup": "Subdivision of a group based on secondary chemical or petrographic distinctions.",
}
for n, r in enumerate(RANKS, start=1):
    c = MCRANK[r]
    g.add((c, RDF.type, SKOS.Concept))
    g.add((c, SKOS.prefLabel, Literal(r, lang="en")))
    g.add((c, SKOS.definition, Literal(RANK_DEFS[r], lang="en")))
    g.add((c, SKOS.notation, Literal(str(n))))   # rank order, 1 = highest
    if n < len(RANKS):                           # next = the rank below
        g.add((c, XKOS.next, MCRANK[RANKS[n]]))
        g.add((MCRANK[RANKS[n]], XKOS.previous, c))
    g.add((c, SKOS.inScheme, rank_scheme))
    g.add((c, REG.status, STATUS))
    g.add((c, SKOS.topConceptOf, rank_scheme))
    g.add((rank_scheme, SKOS.hasTopConcept, c))
    g.add((rank_scheme, UNESKOS.contains, c))

# ---------------------------------------------------------------- levels
level_iri = {r: MCLVL[r] for r in RANKS}
for depth, r in enumerate(RANKS, start=1):
    lvl = level_iri[r]
    g.add((lvl, RDF.type, XKOS.ClassificationLevel))
    g.add((lvl, SKOS.prefLabel, Literal("%s level" % r.capitalize(), lang="en")))
    g.add((lvl, XKOS.depth, Literal(str(depth), datatype=XSD.positiveInteger)))
    g.add((lvl, XKOS.organizedBy, MCRANK[r]))

# ordered, explicitly typed rdf:List for xkos:levels
head = BNode()
Collection(g, head, [level_iri[r] for r in RANKS])
node = head
while node != RDF.nil:
    g.add((node, RDF.type, RDF.List))
    node = g.value(node, RDF.rest)
g.add((RDF.nil, RDF.type, RDF.List))   # axiomatic; required by sh:class rdf:List
g.add((scheme, XKOS.levels, head))

# ---------------------------------------------------------------- items
for row in items:
    c = iri(row["id"])
    g.add((c, RDF.type, SKOS.Concept))
    g.add((c, SKOS.prefLabel, Literal(row["name"], lang="en")))
    g.add((c, SKOS.notation, Literal(row["code"])))
    g.add((c, DCTERMS.identifier, Literal(slugify(row["name"]))))
    g.add((c, SKOS.inScheme, scheme))
    g.add((c, REG.status, STATUS))
    g.add((c, UNESKOS.memberOf, scheme))
    g.add((scheme, UNESKOS.contains, c))
    if row["description"].strip():
        g.add((c, SKOS.definition, Literal(row["description"].strip(), lang="en")))
    if row["notes"].strip():
        g.add((c, SKOS.editorialNote, Literal(row["notes"].strip(), lang="en")))
    # provenance: substring-match short forms in the source field
    for short, ref in src_by_short.items():
        if short in row["source"]:
            g.add((c, DCTERMS.source, ref))
    # hierarchy
    if row["parent_id"].strip():
        p = iri(row["parent_id"])
        g.add((c, SKOS.broader, p))
        g.add((c, XKOS.specializes, p))
        g.add((p, SKOS.narrower, c))
        g.add((p, XKOS.generalizes, c))
    else:
        g.add((c, SKOS.topConceptOf, scheme))
        g.add((scheme, SKOS.hasTopConcept, c))
    # level membership (root carries no rank level)
    if row["rank"] in level_iri:
        g.add((level_iri[row["rank"]], SKOS.member, c))

# Written next to the source CSVs and into data/vocabs/ (the copy the
# publisher picks up), so the two never drift apart.
ttl = g.serialize(format="turtle")
print("triples:", len(g))
for out in (UP / "meteorite-classification.ttl",
            ROOT / "data" / "vocabs" / "meteorite-classification.ttl"):
    out.write_text(ttl, encoding="utf-8")
    print("written:", out.relative_to(ROOT))

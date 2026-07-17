#!/usr/bin/env python3
"""
Build an XKOS-AP-NO conformant serialization of the Weisberg, McCoy & Krot
(2006) meteorite classification.

Inputs : meteorite_classification.csv  (items; columns per data dictionary)
         meteorite_data_dictionary.csv (column semantics -> predicate mapping)
         meteorite_sources.csv         (bibliography -> provenance resources)
Profile: xkos-ap-no-shacl-v1.ttl (Norwegian application profile of XKOS)

Column -> RDF mapping (informed by the data dictionary):
  id          -> row key only (hierarchy joins); the item IRI is minted from
                 `name` as a lower-case hyphenated slug, mc:<slug>, matching
                 the IRI pattern of the other geospecimens vocabularies
                 (https://kos.geospecimens.org/def/meteorite-classification/<slug>).
                 dct:identifier carries the same slug literal.
  parent_id   -> skos:broader + xkos:specializes (inverses asserted)
  rank        -> skos:member from the matching xkos:ClassificationLevel
  code        -> skos:notation (plain literal)
  name        -> skos:prefLabel @en
  description -> skos:definition @en  (AP-NO requires a Literal, not a note instance)
  source      -> dct:source -> mcref:* (dct:BibliographicResource)
  notes       -> skos:editorialNote @en
  depth, materialized_path, path_labels -> not serialized (derivable)
"""
import csv
import re
from rdflib import Graph, Namespace, Literal, URIRef, BNode, RDF, RDFS, XSD
from rdflib.namespace import SKOS, DCTERMS, FOAF
from rdflib.collection import Collection

BASE   = "https://kos.geospecimens.org/def/meteorite-classification/"
MC     = Namespace(BASE)
MCLVL  = Namespace(BASE + "level/")
MCIT   = Namespace(BASE + "item-type/")
MCREF  = Namespace(BASE + "reference/")
XKOS   = Namespace("http://rdf-vocabulary.ddialliance.org/xkos#")
UNESKOS= Namespace("http://purl.org/umu/uneskos#")
EULANG = URIRef("http://publications.europa.eu/resource/authority/language/ENG")

g = Graph()
for p, n in [("mc", MC), ("mclvl", MCLVL), ("mcit", MCIT), ("mcref", MCREF),
             ("xkos", XKOS), ("uneskos", UNESKOS), ("skos", SKOS),
             ("dct", DCTERMS), ("foaf", FOAF), ("xsd", XSD)]:
    g.bind(p, n)

UP = "../sources/classification-systems/meteorites/"
items   = list(csv.DictReader(open(UP + "meteorite_classification.csv", encoding="utf-8-sig")))
sources = list(csv.DictReader(open(UP + "meteorite_sources.csv", encoding="utf-8-sig")))

# The main scheme lives at the base IRI (no trailing path segment), consistent
# with the other geospecimens vocabularies, e.g. .../def/hazard-type.
scheme      = URIRef(BASE.rstrip("/"))
rank_scheme = MC["item-types"]
agent       = MC["agent/geospecimens"]
today       = Literal("2026-06-11", datatype=XSD.date)

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

by_id = {r["id"].strip(): r for r in items}
_slugs = [slugify(r["name"]) for r in items]
_dupes = {s for s in _slugs if _slugs.count(s) > 1}
if _dupes:
    raise SystemExit("duplicate concept slugs, disambiguate names: %s" % sorted(_dupes))

def iri(row_id): return MC[slugify(by_id[str(row_id).strip()]["name"])]

RANKS = ["division", "class", "clan", "group", "subgroup"]

# ---------------------------------------------------------------- publisher
g.add((agent, RDF.type, FOAF.Agent))
g.add((agent, FOAF.name, Literal("geospecimens.org", lang="en")))
g.add((agent, FOAF.homepage, URIRef("https://kos.geospecimens.org/")))

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
g.add((scheme, DCTERMS.title,
       Literal("Meteorite Classification (Weisberg, McCoy & Krot 2006)", lang="en")))
g.add((scheme, DCTERMS.description, Literal(
    "Hierarchical classification of meteorites after Weisberg M. K., McCoy T. J. "
    "and Krot A. N. (2006) Systematics and Evaluation of Meteorite Classification, "
    "Fig. 1: chondrites, primitive achondrites and achondrites organized in five "
    "ranks (division, class, clan, group, subgroup).", lang="en")))
g.add((scheme, DCTERMS.publisher, agent))
g.add((scheme, DCTERMS.creator, agent))
g.add((scheme, DCTERMS.language, EULANG))
g.add((scheme, DCTERMS.modified, today))
g.add((scheme, DCTERMS.source, MCREF.weisberg2006))
g.add((scheme, XKOS.numberOfLevels, Literal("5", datatype=XSD.positiveInteger)))

# ---------------------------------------------------------------- rank scheme
g.add((rank_scheme, RDF.type, SKOS.ConceptScheme))
g.add((rank_scheme, DCTERMS.identifier, URIRef(str(rank_scheme))))
g.add((rank_scheme, DCTERMS.title,
       Literal("Meteorite classification item types", lang="en")))
g.add((rank_scheme, DCTERMS.description, Literal(
    "Flat vocabulary of the five hierarchy ranks used by the Weisberg, McCoy & "
    "Krot (2006) meteorite classification; referenced by the classification "
    "levels via xkos:organizedBy.", lang="en")))
g.add((rank_scheme, DCTERMS.publisher, agent))
g.add((rank_scheme, DCTERMS.language, EULANG))
g.add((rank_scheme, DCTERMS.modified, today))
g.add((rank_scheme, XKOS.numberOfLevels, Literal("1", datatype=XSD.positiveInteger)))

RANK_DEFS = {
    "division": "Highest rank below the root: chondrites, primitive achondrites and achondrites.",
    "class":    "Group of chondrite or achondrite groups sharing primary whole-rock chemical and O-isotopic characteristics.",
    "clan":     "Chondrite or achondrite groups with chemical, mineralogical and isotopic similarities suggesting a common, closely related precursor or formation region.",
    "group":    "Minimum of five unpaired meteorites of similar petrologic, chemical and isotopic characteristics; the basic classification unit.",
    "subgroup": "Subdivision of a group based on secondary chemical or petrographic distinctions.",
}
for r in RANKS:
    c = MCIT[r]
    g.add((c, RDF.type, SKOS.Concept))
    g.add((c, SKOS.prefLabel, Literal(r, lang="en")))
    g.add((c, SKOS.definition, Literal(RANK_DEFS[r], lang="en")))
    g.add((c, SKOS.inScheme, rank_scheme))
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
    g.add((lvl, XKOS.organizedBy, MCIT[r]))

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

out = "../sources/classification-systems/meteorites/meteorite-classification.ttl"
g.serialize(out, format="turtle")
print("triples:", len(g))
print("written:", out)

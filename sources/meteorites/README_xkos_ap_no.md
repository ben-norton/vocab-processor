# Meteorite Classification — XKOS-AP-NO Serialization

Serialization of the Weisberg, McCoy & Krot (2006) meteorite classification as
SKOS + XKOS conforming to **XKOS-AP-NO v1.0**, the Norwegian application
profile of XKOS (Digitaliseringsdirektoratet), validated with pySHACL against
`xkos-ap-no-shacl-v1.ttl`.

**File:** `meteorite_classification_xkos_ap_no.ttl` (Turtle, 1,122 triples)

## Validation results

| Shapes graph | Result |
|---|---|
| `xkos-ap-no-shacl-v1.ttl` (the application profile) | **Conforms: True** |
| `xkos-best-practices-recommended-optional-shapes.ttl` (informational) | Conforms: True |

The file also re-parses cleanly with rdflib.

## Resource inventory

| Resource type | Count | Pattern |
|---|---|---|
| `skos:ConceptScheme` | 2 | `mc:wmk2006` (classification), `mc:itemTypes` (rank vocabulary) |
| `skos:Concept` (items) | 70 | `mc:MC_0001` … `mc:MC_0070` |
| `skos:Concept` (rank types) | 5 | `mcit:division` … `mcit:subgroup` |
| `xkos:ClassificationLevel` | 5 | `mclvl:division` … `mclvl:subgroup` (depths 1–5) |
| `foaf:Agent` | 1 | `mc:agent/geospecimens` (publisher) |
| `dct:BibliographicResource` | 5 | `mcref:weisberg2006` … |

Level membership: 3 + 3 + 13 + 45 + 5 = 69 (root `mc:MC_0001` is top concept
only, not assigned to a numbered level).

## Column → RDF mapping (per the data dictionary)

| CSV column | Predicate(s) | Notes |
|---|---|---|
| `id` | item IRI + `dct:identifier` | `mc:MC_%04d`; identifier literal `"MC_%04d"` (AP-NO: max 1) |
| `parent_id` | `skos:broader` + `xkos:specializes` | inverses asserted on the parent |
| `rank` | `skos:member` from the matching `xkos:ClassificationLevel` | level membership, not tree depth |
| `code` | `skos:notation` | plain literal |
| `name` | `skos:prefLabel`@en | AP-NO mandatory |
| `description` | `skos:definition`@en | **literal**, see decision 1 below |
| `source` | `dct:source` → `mcref:*` | substring-matched short forms; 86 item links + 1 scheme link |
| `notes` | `skos:editorialNote`@en | |
| `depth`, `materialized_path`, `path_labels` | — | derivable, not serialized |

## Profile-driven modeling decisions

These are the points where XKOS-AP-NO conformance changes the modeling
relative to the earlier best-practices serialization (`README_xkos.md`):

1. **Definitions as literals, not note instances.** AP-NO's `Concept_Shape`
   constrains `skos:definition` to `sh:nodeKind sh:Literal`, so definitions
   are language-tagged literals rather than `xkos:ExplanatoryNote` resources.

2. **Mandatory scheme metadata.** Every `skos:ConceptScheme` must carry
   exactly one `xkos:numberOfLevels` (`xsd:positiveInteger`), exactly one
   `dct:identifier`, at least one `dct:title`, and exactly one
   `dct:publisher` resolving to a typed `foaf:Agent`. Consequently the rank
   vocabulary `mc:itemTypes` — needed because `xkos:organizedBy` targets must
   be proper `skos:Concept`s with `skos:inScheme` — carries this full
   metadata set too (`xkos:numberOfLevels "1"`).

3. **`uneskos:contains` enumeration.** AP-NO uses `uneskos:contains` to link
   each scheme to its items (and `uneskos:memberOf` inversely); all 70 items
   plus the 5 rank concepts are enumerated.

4. **`dct:language` from the EU authority list.** The profile requires the
   language URI from `publications.europa.eu/resource/authority/language/`
   (here `…/ENG`), not a BCP-47 literal.

5. **Explicitly typed `rdf:List` for `xkos:levels`.** The profile's
   `List_Shape` validates `rdf:first`/`rdf:rest` with `sh:class` constraints,
   which (without a reasoner) require every list cell — and `rdf:nil` itself —
   to be explicitly typed `rdf:List`. The triple `() a rdf:List .` in the
   output is this axiomatic typing of `rdf:nil`, asserted deliberately.

6. **Generic hierarchy retained.** `skos:broader`/`narrower` plus the XKOS
   refinements `xkos:specializes`/`generalizes` are asserted explicitly in
   both directions, matching the AP-NO optional property set and keeping the
   tree navigable without inference.

7. **`xkos:belongsTo` omitted.** The version-independent anchor concept used
   previously would itself be targeted by `Concept_Shape` and require
   `skos:inScheme` in some scheme, cascading into a third scheme with full
   mandatory metadata. With only one revision in scope, it was omitted;
   `dct:conformsTo` statements to XKOS and XKOS-AP-NO are asserted instead.

## Provenance

`meteorite_sources.csv` is serialized as five `dct:BibliographicResource`
instances with `dct:bibliographicCitation`, `rdfs:label` (short form), and
where available a `dct:identifier` (DOI as `https://doi.org/…`, ISBN as
`urn:isbn:…`, or URL). Item `source` fields are substring-matched against the
short forms, correctly handling the compound entries (e.g. the lunar
literature reference containing internal semicolons).

## Reproducibility

`build_xkos_ap_no.py` (rdflib) rebuilds the file from the three CSVs;
validation: `python3 -m pyshacl -s xkos-ap-no-shacl-v1.ttl <file>`.

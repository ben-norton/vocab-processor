# XLSX → Prez-Lite TTL Conversion Process

Summary of how `sources/xlsx/*.xlsx` workbooks are converted into prez-lite-conformant SKOS Turtle files in `data/vocabs/`.

## Inputs

| Path | Role |
|------|------|
| `sources/xlsx/*.xlsx` | One workbook per vocabulary. Each contains `Concept Scheme`, `Concepts`, `Agents`, and `Namespaces`/`Namespeces` sheets. |
| `sources/VocabularyAnnotations.xlsx` | Authoritative mapping of annotation labels to RDF qualified names and namespace prefixes. |
| `http://localhost:81/prez-lite/authoring/vocabularies` | Prez-lite spec for required/recommended ConceptScheme and Concept properties. |

## Outputs

One TTL per workbook, named after the scheme slug:

- `data/vocabs/constituent-part-proportion.ttl`
- `data/vocabs/geological-specimen-type.ttl`
- `data/vocabs/hazard-type.ttl`
- `data/vocabs/geological-material-name-type.ttl`

## Generator

`scripts/xlsx-to-ttl.py` — reads every `*.xlsx` in `sources/xlsx/` and writes one TTL per file. Run with:

```bash
python scripts/xlsx-to-ttl.py
```

Dependencies: `openpyxl` (parsing), `rdflib` (optional, for post-hoc validation).

## Pipeline

1. **Load workbook** (`openpyxl`, `data_only=True`) and resolve sheet names case-insensitively — tolerates the `Namespeces` misspelling found in several sources.
2. **Parse `Concept Scheme`** as key→values from column A / B+, collecting every non-empty cell per key.
3. **Parse `Concepts`** as header-driven records (row 1 is headers, each subsequent non-empty row is a concept).
4. **Parse `Agents`** as header-driven records; `agentURI` rows become `schema:Person` / `schema:Organization` blocks.
5. **Normalize IRIs**:
   - Upgrade `http://vocab.geospecimens.org/*` → `https://`.
   - Re-base every concept IRI under the scheme IRI (source rows occasionally mixed singular/plural paths or pointed `inScheme` at a sibling).
6. **Normalize dates**: numeric `YYYYMMDD.0` values (e.g. `20260417.0`) convert to ISO `2026-04-17`.
7. **Detect top concepts** from each concept's `isTopConceptOf` column; emit a deduplicated `skos:hasTopConcept` list on the scheme.
8. **Resolve creator/publisher IRIs** from the `Agents` sheet — prefer a URI whose `hadRole` contains `creator`/`publisher`, then fall back to the first `affiliationURI`.
9. **Emit Turtle** with a stable prefix block, then the `skos:ConceptScheme` + `owl:Ontology` block, then agents, then concepts.

## Property Mapping

Taken from `VocabularyAnnotations.xlsx` (`ConceptScheme` and `Concept` sheets), aligned with the prez-lite minimal example.

### ConceptScheme

| XLSX key | RDF property |
|----------|--------------|
| `vocabularyIRI` | subject IRI |
| `title` | `dcterms:title` |
| `prefLabel` | `skos:prefLabel` |
| `definition` | `skos:definition` |
| `description` | `dcterms:description` |
| `scopeNote` | `skos:scopeNote` |
| `usageNote` | `vann:usageNote` |
| `historyNote` | `skos:historyNote` |
| `note` | `skos:note` |
| `provenance` | `dcterms:provenance` |
| `keywords` | `schema:keywords` (split on `,`/newline) |
| `citation` | `schema:citation` |
| `derivedFrom` | `prov:wasDerivedFrom` (IRI values only) |
| `status` | `reg:status` |
| `license` | `schema:license` |
| `creator` | `schema:creator` |
| `publisher` | `schema:publisher` |
| `created` | `schema:dateCreated` (`xsd:date`) |
| `modified` | `schema:dateModified` (`xsd:date`) |
| `version` | `schema:version` |
| top concepts | `skos:hasTopConcept` (derived from concepts) |

### Concept

| XLSX column | RDF property |
|-------------|--------------|
| `conceptIRI` | subject IRI |
| `prefLabel` | `skos:prefLabel` |
| `notation` | `skos:notation` |
| `altLabel` | `skos:altLabel` (split on `,`/newline) |
| `definition` | `skos:definition` |
| `provenance` | `dcterms:provenance` |
| `historyNote` | `skos:historyNote` |
| `editorialNote` | `skos:editorialNote` |
| `changeNote` | `skos:changeNote` |
| `usageNote` | `vann:usageNote` |
| `registryStatus` | `reg:status` |
| `inScheme` | `skos:inScheme` (normalized to scheme IRI) |
| `isTopConceptOf` | `skos:topConceptOf` (normalized to scheme IRI) |
| — | `rdfs:isDefinedBy cs:` (always emitted) |

## Namespace Prefixes Emitted

```turtle
PREFIX : <{scheme_iri}/>
PREFIX cs: <{scheme_iri}>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX isoroles: <https://linked.data.gov.au/def/data-roles/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX reg: <http://purl.org/linked-data/registry#>
PREFIX schema: <https://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX vann: <http://purl.org/vocab/vann/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

## Validation

Parse every generated TTL with rdflib and assert basic SKOS shape:

```python
import rdflib
from pathlib import Path
SKOS = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
for ttl in Path("data/vocabs").glob("*.ttl"):
    g = rdflib.Graph().parse(ttl, format="turtle")
    schemes = list(g.subjects(rdflib.RDF.type, SKOS.ConceptScheme))
    concepts = list(g.subjects(rdflib.RDF.type, SKOS.Concept))
    assert len(schemes) == 1 and concepts, ttl
```

All four generated files pass: 1 scheme each, concepts 7–13, top-concepts derived correctly.

## Known Source Quirks Handled

- Sheet name `Namespeces` (typo) used in three of four workbooks.
- Mixed singular/plural scheme paths in concept IRIs (e.g. `constituent-part-proportion` vs `constituent-part-proportions`).
- One concept row pointed `inScheme` at a sibling scheme (`geological-sample-type`); normalized to the active scheme.
- `created` / `modified` / `version` stored as `YYYYMMDD` floats.
- Duplicate `description` rows in `NameTypes.xlsx` (harmless — only the first is used).
- `hasTopConcept` cells contain trailing partial IRIs — authoritative top-concepts are derived from each concept's `isTopConceptOf` column instead.

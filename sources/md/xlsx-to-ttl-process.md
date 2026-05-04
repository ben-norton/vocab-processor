# xlsx → Turtle transformation process

Summary of the pipeline used to convert vocabulary-authoring spreadsheets into SKOS `ConceptScheme` Turtle files.

**Vocabularies processed:**

| Source workbook | Output file | Scheme IRI | Concepts |
|---|---|---|---|
| `NameTypes.xlsx` | `geological-material-name-type.ttl` | `https://vocab.geospecimens.org/def/geological-material-name-type` | 13 |
| `ConstituentPartProportions.xlsx` | `sources/ttl/constituent-part-proportion.ttl` | `https://vocab.geospecimens.org/def/constituent-part-proportion` | 8 |
| `GeologicalSpecimenMaterialTypes.xlsx` | `sources/ttl/geological-specimen-material-type.ttl` | `http://vocab.geospecimens.org/def/geological-specimen-type` | 13 |
| `HazardTypes.xlsx` | `sources/ttl/hazard-type.ttl` | `http://vocab.geospecimens.org/def/hazard-type` | 7 |

## Input structure

Each workbook follows a shared convention but with variations that the pipeline handles automatically.

### Sheets consumed

- **Concept Scheme** — a two-column, key-value layout whose rows describe the vocabulary as a whole.
- **Concepts** — a tabular sheet with one row per concept.
- **Namespaces** *(or* **Namespeces**, *a recurring typo)* — prefix-to-IRI mappings.
- **Agents** *(optional)* — rows describing creators, editors, publishers, affiliations, and roles.

Additional sheets (`Meta`, `Mappings`, `SSSOM`) exist in the workbooks but are out of scope for this SKOS scheme file. Mappings belong in separate files.

### Column-name variation handled

Three naming styles coexist across the four workbooks, and the pipeline normalizes all of them to a single internal schema before emitting Turtle:

- **Bare keys** — `title`, `description`, `prefLabel`, `prefix`, `isTopConceptOf` *(used in CPP, HAZ)*
- **Prefixed keys** — `dcterms:title`, `skos:prefLabel`, `skos:topConceptOf` *(used in NameTypes, GSMT)*
- **Mixed** — some sheets use bare keys for the Concept Scheme sheet but prefixed keys in the Concepts sheet, or vice versa.

### Optional elements

- The `Agents` sheet is absent in `HazardTypes.xlsx` — handled by omitting the Agents block and the `prov:qualifiedAttribution` properties on the scheme.
- The `skos:broader` column is absent in flat vocabularies (CPP, HAZ) — handled by simply not emitting broader triples.
- The `skos:inScheme` column is absent in HAZ — handled by defaulting to the scheme IRI on each concept.

## Output structure

Each generated `.ttl` file follows the same layout:

1. **Header comment block** — source workbook, sheets used, generation date, and numbered list of data issues found
2. **Prefix declarations** — a fixed set of standard prefixes plus any workbook-specific prefixes from the Namespaces sheet that aren't redundant
3. **ConceptScheme block** — one `skos:ConceptScheme` node with all metadata properties
4. **Concepts section** — one block per `skos:Concept`
5. **Agents section** *(when present)* — `schema:Person` / `schema:Organization` descriptions, plus the affiliation organizations

## Field mapping

### Concept Scheme sheet → `skos:ConceptScheme`

| Normalized source key | Output property | Notes |
|---|---|---|
| `vocabularyIRI` | *(subject of the scheme block)* | — |
| `prefLabel` | `skos:prefLabel` | `@en` language tag |
| `title` | `dcterms:title` | `@en` |
| `definition` | `skos:definition` | Triple-quoted `@en` (long text) |
| `description` | `dcterms:description` | Triple-quoted `@en` |
| `publisher` / `creator` / `contributor` | `dcterms:publisher` / `creator` / `contributor` | Resolves to agent IRI (or blank node) via fuzzy name match against the Agents sheet; falls back to an `@en` string literal if no match |
| `provenance` | `dcterms:provenance` | `@en` |
| `created` / `modified` | `dcterms:created` / `modified` | `YYYYMMDD` integer converted to `xsd:date` (`2026-04-09`) |
| `version` | `dcat:version` | Plain string (DCAT convention) |
| `scopeNote` / `usageNote` / `historyNote` / `note` | `skos:scopeNote` / `vann:usageNote` / `skos:historyNote` / `skos:note` | `@en` |
| `keywords` | `dcat:keyword` | Comma-split into multiple `@en` literals |
| `citation` | `schema:citation` | `@en` |
| `derivedFrom` | `prov:wasDerivedFrom` | Pipe-separated values split into items; entries matching `^https?://` emitted as IRIs, others as `@en` literals |
| `derivationMode` | `reg:derivationMode` | IRI; normalized from the spreadsheet's `regstatus:derivationMode`, which uses an undeclared prefix |
| `status` | `reg:status` | IRI |
| `license` | `schema:license` | IRI |
| `hasTopConcept` | `skos:hasTopConcept` | See top-concept reconciliation below |

**Top-concept reconciliation.** If the scheme-level `hasTopConcept` cell contains truncated URIs (e.g., trailing `/` with no concept slug, as in CPP), `skos:hasTopConcept` is rebuilt from the concept-level `isTopConceptOf` column, which is complete. Otherwise the scheme-level value is used, deduplicated.

### Concepts sheet → `skos:Concept`

| Normalized source column | Output property | Notes |
|---|---|---|
| `conceptIRI` | *(subject)* | — |
| `prefLabel` | `skos:prefLabel` | `@en` |
| `altLabel` | `skos:altLabel` | Comma-split into multiple `@en` literals |
| `broader` | `skos:broader` | IRI; only emitted when present |
| `definition` | `skos:definition` | `@en` (triple-quoted) |
| `provenance` | `dcterms:provenance` | `@en` |
| `historyNote` / `editorialNote` / `changeNote` / `usageNote` | `skos:historyNote` / `editorialNote` / `changeNote` / `vann:usageNote` | `@en` |
| `inScheme` | `skos:inScheme` | Defaults to the scheme IRI when the column is missing or blank |
| `registryStatus` | `reg:status` | IRI |
| `isTopConceptOf` | `skos:topConceptOf` | IRI |
| `notation` | `skos:notation` | Untyped string literal (plain, no language tag) |

Each concept is also typed `a skos:Concept`.

### Agents sheet → PROV attribution + `schema:*` descriptions

Each agent row produces:

- A node typed by `agentType` (e.g., `schema:Person`, `schema:Organization`), identified by `agentURI` when present, otherwise a named blank node `_:agent_<slug_of_name>`.
- `schema:name`, `schema:email`, and `schema:affiliation` properties from the corresponding columns.
- `schema:parentOrganization` as a blank-node `schema:Organization` with `schema:name`.
- A separate `schema:Organization` node for the `affiliationURI` with `schema:name = affiliationName`.

Roles are expressed on the scheme via a `prov:qualifiedAttribution` blank node:

```turtle
prov:qualifiedAttribution [
    a             prov:Attribution ;
    prov:agent    <agent-iri> ;
    dcat:hadRole  isoroles:editor ;
] ;
```

Multiple roles in one cell (e.g., `isoroles:publisher, isoroles:creator`) become multiple `dcat:hadRole` objects on the same attribution.

### Namespaces sheet → `@prefix` declarations

A fixed set of standard prefixes is always emitted regardless of the source sheet (`dcat`, `dcterms`, `isoroles`, `owl`, `prov`, `rdf`, `rdfs`, `reg`, `schema`, `skos`, `status`, `vann`, `vocdermods`, `xsd`). Workbook-specific prefixes from the sheet are added after that, deduplicated by namespace value against the standard set.

## Modeling decisions

These are places where the spreadsheet was ambiguous or where multiple valid encodings existed, resolved consistently across all four files:

- **Agents without an `agentURI` get a named blank node** rather than falling back to `affiliationURI`. This avoids conflating agent identity with affiliation — particularly important for CPP, where the Task Group's affiliation is `https://tdwg.org` (the parent org, not the group).
- **Roles are expressed via `prov:qualifiedAttribution`** with `dcat:hadRole` pointing to `isoroles:*`, rather than treating `isoroles:*` values as predicates. `dcterms:publisher` / `creator` / `contributor` still point directly at agent IRIs for consumers that don't traverse PROV.
- **`regstatus:derivationMode` is emitted as `reg:derivationMode`.** The `regstatus:` prefix isn't declared in any sheet, and semantically `derivationMode` is a property rather than a status value; `reg:derivationMode` matches the Prez / linked.data.gov.au convention paired with `vocdermods:` values.
- **Dates typed as `xsd:date`** (`dcterms:created`, `dcterms:modified`), converting `YYYYMMDD` integers to ISO 8601 `YYYY-MM-DD`.
- **Version kept as a plain string** per DCAT practice, even when it looks like a date.
- **Natural-language literals tagged `@en`**: prefLabel, altLabel, definition, description, provenance, scopeNote, usageNote, historyNote, note, citation, keywords, and the free-text items in `derivedFrom`. IRIs, dates, versions, emails, and `skos:notation` values are untagged.
- **Comma-separated cells split into multiple values** for `dcat:keyword`, `skos:altLabel`, and `skos:hasTopConcept`.
- **Pipe-separated cells split into multiple values** for `prov:wasDerivedFrom` (used in GSMT).

## Issues detected per workbook

The pipeline automatically detects and flags these classes of issues in a numbered comment block at the top of each output file:

1. **`Namespeces` typo** — the Namespaces sheet is named `Namespeces` in NameTypes, CPP, and GSMT; correctly spelled only in HAZ.
2. **Scheme IRI vs. concept IRI mismatch** — when concept IRIs don't share the `vocabularyIRI` as their parent. Present in CPP (2 parent IRIs), GSMT (3 parent IRIs — the worst case), and HAZ (http/https mismatch).
3. **`skos:inScheme` mismatch** — when concepts point to a scheme IRI other than their declared `vocabularyIRI`. GSMT triggers this; every concept's `skos:inScheme` points to a URI that matches neither the scheme nor the other concepts.
4. **Truncated `hasTopConcept` URIs** — cells containing URIs that end with `/` and no concept slug. CPP had 7 of 8 entries corrupted this way. The output rebuilds `skos:hasTopConcept` from the concept-level `isTopConceptOf` column in this case.
5. **Dangling `skos:broader` references** — targets not present as concepts in the vocabulary. NameTypes: `structural-group` → `.../group-name` (no such concept). GSMT: `rock-core` → `.../geological-specimen-material-type/rock`, but the "Rock" concept is defined at `.../geological-material-type/rock` (different base).
6. **`http://` scheme IRI** — when `vocabularyIRI` uses `http://` but the concept IRIs use `https://`. Present in GSMT and HAZ.

All issues are **transcribed as-written** rather than silently corrected; the comments in each file identify what needs to be fixed in the source spreadsheet.

## Validation

Every generated file is parsed with `rdflib` to confirm syntactic validity and the following structural checks:

- `skos:ConceptScheme` count is exactly 1
- `skos:Concept` count matches the source row count
- `skos:hasTopConcept` on the scheme agrees with concept-level `skos:topConceptOf`
- Every `skos:broader` target exists as a `skos:Concept` in the graph (dangling references are flagged, not hidden)

Triple counts per file:

| File | Triples |
|---|---|
| `geological-material-name-type.ttl` | 134 |
| `constituent-part-proportion.ttl` | 119 |
| `geological-specimen-material-type.ttl` | 159 |
| `hazard-type.ttl` | 88 |

## Recommended source-spreadsheet cleanups

In rough priority order — these would eliminate the majority of the flagged issues at source:

1. Rename `Namespeces` → `Namespaces` in the three workbooks where it's misspelled.
2. Reconcile the scheme IRI / concept IRI / `inScheme` URIs to a single canonical form per vocabulary (particularly urgent for GSMT, which has three). Use `https://` consistently.
3. Re-enter the `hasTopConcept` cell in CPP — 7 of 8 entries are truncated.
4. Fix GSMT's `skos:broader` for "Rock Core" (currently points to a concept under the wrong base) and NameTypes' `skos:broader` for "Structural Group" (points to `.../group-name`, likely intended `.../group`).
5. Clean up GSMT's `prov:wasDerivedFrom` cell — one entry is two citations smooshed together, and another is duplicated.
6. Rename the property `regstatus:derivationMode` to `reg:derivationMode` in the Concept Scheme sheets to match the declared registry prefix.
7. Add an Agents sheet to `HazardTypes.xlsx` if the scheme is intended to have the same PROV attribution structure as the other three.

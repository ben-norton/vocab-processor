# Specification: Vocabulary Validation

The checks run against vocabulary files, from source workbook to published site.

| Stage | Process | Runs against | Fails the run? |
|---|---|---|---|
| 1 | [Conformance checks](#1-conformance-checks-validate-ttlpy) — `src/validate-ttl.py` | `data/vocabs/*.ttl`, glossary TTLs | Yes, on any error |
| 2 | [Conversion checks](#2-conversion-checks-xlsx-to-ttlpy) — `src/xlsx-to-ttl.py` | `sources/xlsx/*.xlsx` → generated TTL | No (reported) |
| 3 | [Classification integrity](#3-classification-integrity-build_classification_csvspy) — `src/build_classification_csvs.py` | `sources/classification-systems/<system>/*.xlsx` | Yes; nothing is written |
| 4 | [SSSOM checks](#4-sssom-checks-build_sssom_ttlpy) — `src/build_sssom_ttl.py` | SSSOM sheets → `*_sssom_mappings.ttl` | Partly |
| 5 | [Publication checks](#5-publication-checks-verify-staticjs) — `vocab-publisher/scripts/verify-static.js` | Published resource files | Yes |

Severity: **Error** fails the run (exit 1); **Warning** is reported but passes; **Note** is written to the console or the TTL header only.

---

## 1. Conformance checks (`validate-ttl.py`)

```bash
python src/validate-ttl.py                    # all vocabularies
python src/validate-ttl.py <path.ttl> ...     # named files
```

**Scope:** `data/vocabs/*.ttl` by default, excluding `agents.ttl`, `*-mappings.ttl` and `*_sssom_mappings.ttl` (none declares a ConceptScheme).

| # | Check | Rule | Severity |
|---|---|---|---|
| 1 | Turtle syntax | File parses with rdflib. Failure stops all further checks. | Error |
| 2 | ConceptScheme | At least one `skos:ConceptScheme`. Failure stops all further checks. With several, the one with most member concepts is primary (tie-break: has `xkos:numberOfLevels`); checks 3 and 6–8 run per scheme. | Error |
| 3 | Scheme metadata | Each scheme has every [required scheme property](#required-scheme-properties). | Error |
| 4 | Concept metadata | Every `skos:Concept` has every [required concept property](#required-concept-properties). | Error |
| | | File has no `skos:Concept` at all. | Warning |
| 5 | Scheme membership | Each concept's `skos:inScheme` names a scheme declared in the file. | Error |
| 6 | Top concepts | `skos:hasTopConcept` and `skos:topConceptOf` agree in both directions. | Warning |
| | | Every `skos:hasTopConcept` target is typed `skos:Concept`. | Error |
| 7 | IRI base | Concept IRIs begin with the scheme IRI. | Warning |
| | | Differ only by `http`/`https`. | Warning |
| 8 | Duplicate labels | No two concepts in a scheme share a `skos:prefLabel` in the same language (case-insensitive). | Error |

### Required scheme properties

| Property | Purpose |
|---|---|
| `dcterms:title` | Scheme name |
| `dcterms:description` | Scheme summary |
| `dcterms:created` | Creation date |
| `dcterms:modified` | Last-change date |
| `dcterms:publisher` | Publishing agent |
| `dcterms:creator` | Creating agent |
| `reg:status` | Registry status |

### Required concept properties

| Property | Purpose |
|---|---|
| `skos:prefLabel` | Preferred label |
| `skos:definition` | Definition |
| `skos:inScheme` | Owning scheme |
| `reg:status` | Registry status |

---

## 2. Conversion checks (`xlsx-to-ttl.py`)

Run automatically during conversion. Data-quality issues are written to the header comment of the generated TTL; none stop the build.

| Check | Rule | Outcome |
|---|---|---|
| Sheet name typo | Namespaces sheet named `Namespeces` | Note; sheet still used |
| Scheme IRI scheme | `vocabularyIRI` is `http://` while concepts use `https://` | Note |
| IRI normalisation | `http://kos.geospecimens.org` IRIs | Rewritten to `https://` silently |
| Concept IRI base | Concept IRIs sit under a parent other than `vocabularyIRI` | Note; transcribed as written |
| Scheme membership | `skos:inScheme` names an IRI other than `vocabularyIRI` | Note; fails conformance check 5 |
| Top concepts | Scheme `hasTopConcept` cell has truncated/empty-slug IRIs | Note; rebuilt from concept `topConceptOf` |
| Broader links | `skos:broader` targets a concept not in the workbook | Note; transcribed as written |
| Agents in workbook | Vocabulary workbook has an `Agents` sheet | Note; ignored (agents come from `Agents.xlsx`) |
| Agent map | `Agents.xlsx` `map` sheet names a scheme with no workbook | Console warning (full runs only) |
| Unused prefixes | `@prefix` lines not used in the body | Removed |
| Sanity count | Generated file has exactly one ConceptScheme and ≥ 1 Concept (needs rdflib) | Console `OK` / `WARN` |

---

## 3. Classification integrity (`build_classification_csvs.py`)

```bash
python src/build_classification_csvs.py <system>|--all
```

Applies to every sheet with `id`/`parent_id` columns. Any failure aborts before any CSV is written.

| Check | Rule | Severity |
|---|---|---|
| Row id | Every row has an `id` | Error |
| Unique ids | No `id` repeats within a sheet | Error |
| Parent chain | Every `parent_id` resolves, without cycles | Error |
| Depth | `depth` equals the parent-chain length | Error |
| Path | `materialized_path` equals the parent-chain ids | Error |
| Path labels | `path_labels` | Not checked (authored) |

Generated XKOS TTL is then checked with stage 1.

---

## 4. SSSOM checks (`build_sssom_ttl.py`)

```bash
python src/build_sssom_ttl.py [Workbook ...]
```

| Check | Rule | Outcome |
|---|---|---|
| Sheet present | `SSSOM` sheet has at least one data row | Workbook skipped |
| Vocabulary IRI | Concept Scheme sheet has `vocabularyIRI` | Error; exit 1 |
| Required columns | `subject_id`, `predicate_id`, `object_id` headers present | Error; exit 1 |
| Required values | Row has all three triple values | Row skipped; note |
| CURIE prefixes | Every CURIE uses a built-in or Namespaces-sheet prefix | Row skipped; note |
| Known slots | Columns are SSSOM slot names | Others ignored; note |
| Licence | Concept Scheme sheet has `schema:license` | Note (SSSOM requires one) |
| Parse check | Output parses with rdflib (if installed) | Error; exit 1 |

---

## 5. Publication checks (`verify-static.js`)

Run in `vocab-publisher/` after `npm run index`; also run by `publish_to_vocab_publisher.py`.

```bash
node scripts/verify-static.js
```

| Check | Rule | Severity |
|---|---|---|
| URI registry | Every scheme/concept URI in `src/config/uris.json` has a manifest entry, with none missing or extra | Error |
| Manifest keys | Each entry has `html`, `spa`, `turtle`, `json-ld`, `rdf-xml`, `json`, `label`, `kind`, `vocabId` | Error |
| Files exist | Each manifest URL resolves to a non-empty file (except `spa`) | Error |
| HTML | Has doctype, `rel="canonical"` and Turtle `rel="alternate"` links | Error |
| Turtle | Contains the canonical URI | Error |
| JSON-LD | Parses; `@id` matches; scheme node present | Error |
| RDF/XML | Starts with `<?xml`; has `rdf:about` for the canonical URI | Error |
| JSON | Parses; `uri` matches; no `ttlContent` leak | Error |

On failure, `publish_to_vocab_publisher.py` keeps its backup and exits 1; roll back with `--restore`.

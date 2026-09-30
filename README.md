# Vocabulary Processor for the GeoSpecimens Platform and KOS Publishing System

Formerly: geospecimens-vocab-manager, geospecimens-vocab-processor

`vocab-processor` turns controlled vocabularies, glossaries and classification schemes into validated SKOS Turtle for the GeoSpecimens Platform. Authors work in Excel workbooks or CSV files. Python scripts convert those sources into SKOS (and XKOS for classifications), validate the result and copy it to [vocab-publisher](../vocab-publisher/). vocab-publisher is the web app that publishes the vocabularies at **[kos.geospecimens.org](https://kos.geospecimens.org)**. Each term gets a persistent URI of the form `https://kos.geospecimens.org/def/{vocabulary}/{concept}`.

For command details see [QUICK-REFERENCE.md](QUICK-REFERENCE.md). Contributor notes and the converter's non-obvious behaviours are in [CLAUDE.md](CLAUDE.md) and [docs/](docs/).

## Related projects

| Project | Role |
|---|---|
| [vocab-publisher](../vocab-publisher/) | Sibling repository. A Vue 3 single-page app that parses this repo's `data/` into static JSON at build time and serves it as a browsable SKOS vocabulary site, with content negotiation (Turtle, JSON-LD, RDF/XML, JSON, CSV) at each URI. |
| [kos.geospecimens.org](https://kos.geospecimens.org) | The live KOS Publishing System, where vocab-publisher is deployed and where every IRI minted here resolves. |
| [Prez](https://github.com/RDFLib/prez) | Linked Data API and publishing system for SKOS vocabularies and other knowledge organisation systems. Developed by [Kurrawong AI](https://kurrawong.ai) and published by the [Australian Government Linked Data Working Group](https://www.linked.data.gov.au/). This repo's output follows Prez conventions: catalogue and profile config in `data/config/`, `reg:status` statuses, and qualified agent attributions. |
| [prez-lite](https://github.com/Kurrawong/prez-lite) | Kurrawong AI's lightweight, static-site counterpart to Prez. It was the earlier publishing target for these vocabularies (see `../archive/`); vocab-publisher follows the same build-time, static-output approach. |

## Repository layout

| Directory | Subdirectory | Contents |
|---|---|---|
| `sources/` | `xlsx/` | Vocabulary workbooks (one per vocabulary) and `Agents.xlsx`, the shared registry of agents (publishers, creators and so on). **Source of truth for vocabularies.** |
| | `glossaries/` | Glossaries, each a four-file set in its own `<slug>/` folder. |
| | `classification-systems/` | Classification schemes, one folder per system, each with a source `.xlsx`, the CSVs built from it, and a copy of its Turtle. |
| | `templates/` | `BaseTemplate.xlsx` (starting point for a new vocabulary), `AgentsTemplate` and other templates. |
| | `schemas/` | Third-party reference vocabularies and shapes (SKOS, FOAF, ISO roles, XKOS / XKOS-AP-NO), used as reference material only. |
| | `drafts/` | Work in progress that the pipeline doesn't read. |
| | `import/` | Staging area for incoming source material. |
| `data/` | `vocabs/` | **Generated** SKOS/XKOS Turtle: one file per vocabulary or classification, plus `agents.ttl` and `*-mappings.ttl`. |
| | `glossaries/` | **Generated** glossary Turtle and JSON, one folder per glossary. |
| | `config/` | Hand-written Prez-style catalogue config: `profiles.ttl` and `workspaces.ttl`. |
| | `background/`, `validators/` | Placeholders mirrored to vocab-publisher. |
| `src/` | — | The pipeline scripts. |
| | `archive/` | Superseded converter scripts. |
| `docs/` | — | Field-mapping rules for the xlsx→TTL converter, and the glossary guide. |
| `samples/` | `mappings/` | Example SKOS mapping snippets. |
| `export/` | `system/`, `vocabs/` | Staging area; usually empty. |
| `temp/` | — | *(gitignored)* Timestamped backups of vocab-publisher's `data/`, made during a publish. |

Everything in `data/vocabs/` and `data/glossaries/`, and the CSVs under `sources/classification-systems/`, is build output. Fix the source file and rebuild; hand edits are overwritten.

## Workflows

Setup: activate the venv (`init.bat`, or `.\.venv-geospecimens-process-vocabularies\Scripts\Activate.ps1`) and install `openpyxl` and `rdflib`. All commands run from the project root.

| Flow | Author in | Build | Output |
|---|---|---|---|
| Vocabularies | `sources/xlsx/*.xlsx` | `python src/xlsx-to-ttl.py [Workbook]` | `data/vocabs/{slug}.ttl` |
| Agents | `sources/xlsx/Agents.xlsx` | `python src/build_agents_ttl.py`, then re-run `xlsx-to-ttl.py`, which embeds the agents in each vocabulary | `data/vocabs/agents.ttl` |
| Mappings | a `Mappings` sheet in a vocabulary workbook | `python src/build_mappings_ttl.py` | `data/vocabs/{slug}-mappings.ttl` |
| Glossaries | `sources/glossaries/<slug>/` (four-file set) | `python src/build_glossary_json.py <slug>` and `python src/build_glossary_ttl.py <slug>` (or `--all`) | `data/glossaries/<slug>/` |
| Classification schemes | `sources/classification-systems/<system>/*.xlsx` | `python src/build_classification_csvs.py <system>`, then `python src/build_xkos_ap_no.py` | the system's CSVs, then `data/vocabs/meteorite-classification.ttl` |
| Validate | — | `python src/validate-ttl.py [path ...]` | 8 SKOS conformance checks; exits 1 on any error |
| Publish | — | `python src/publish_to_vocab_publisher.py [--dry-run]` | copies `data/` to `vocab-publisher/data` (see below) |

Publishing works in four steps:
1. Before overwriting anything, the script backs up the publisher's `data/` to `temp/`.
2. It copies this repo's `data/` over the publisher's copy.
3. It rebuilds and checks the publisher (`npm run index` and `verify-static.js`).
4. If the checks pass, it deletes the backup. If they fail, it keeps the backup, exits with an error, and `--restore` rolls the publisher back.

`sync_to_publisher.py` is an alternative that copies only part of `data/` (a single vocabulary or glossary); it reads the target path from `.env`.

## Current content

| Kind | Identifier | Title | Concepts |
|---|---|---|--:|
| Vocabulary | `aggregate-form` | Aggregate Form | 26 |
| Vocabulary | `constituent-part-proportion` | Constituent Part Proportion | 8 |
| Vocabulary | `geological-material-assertion-type` | Geological Material Assertion Types | 17 |
| Vocabulary | `geological-specimen-material-category` | Geological Specimen Material Category | 14 |
| Vocabulary | `geological-specimen-name-type` | Geological Specimen Name Type | 19 |
| Vocabulary | `hazard-type` | Hazard Types | 6 |
| Vocabulary | `kos-meta` | Knowledge Organization System Resources Metadata Vocabulary | 1 |
| Vocabulary | `luster` | Luster | 12 |
| Classification | `meteorite-classification` | Meteorite Classification (Weisberg, McCoy & Krot 2006) | 70 (+5 ranks) |
| Glossary | `collections-digitization` | Collections Digitization Glossary | 180 |
| Glossary | `geological-collections-glossary` | Geological Collections Glossary | 117 |
| Glossary | `kos-terms` | KOS Terminology Glossary | 48 |

Vocabularies and classifications resolve at `https://kos.geospecimens.org/def/{identifier}`. Glossaries resolve at `https://kos.geospecimens.org/glossary/{identifier}`.

## Standards

- **SKOS**: concept schemes, concepts and mappings.
- **XKOS**: classification levels and ranks.
- **XKOS-AP-NO**: application profile the meteorite classification is checked against.
- **DCTERMS** and **DCAT**: scheme-level metadata.
- **PROV-O**: qualified agent attributions (`prov:qualifiedAttribution` with `dcat:hadRole`), using ISO 19115 role codes.
- **Registry statuses**: `reg:status` values from `linked.data.gov.au/def/reg-statuses`.

## Licence

This repository includes an MIT licence ([LICENSE](LICENSE)) and a Creative Commons Attribution-NonCommercial 4.0 licence ([LICENSE-CC-BY-NC.md](LICENSE-CC-BY-NC.md)). See those files for their terms.

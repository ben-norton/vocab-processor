# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Vocabulary processor for the **GeoSpecimens Platform** and KOS Publishing System (https://kos.geospecimens.org). Authors maintain controlled vocabularies as Excel workbooks under `sources/xlsx/`; the scripts in `utils/` transform those workbooks into SKOS Turtle files under `data/vocabs/`, validate them, and publish them to the downstream `vocab-publisher` web app.

The parent directory `G:/repos/vocabularies/` contains several other unrelated vocabulary repos (GSWA-Vocabularies, GeoKOS, bgs-vocabularies, gsq-vocabularies, etc.). Only this project is in active development.

## Environment

- Python 3 with `openpyxl` (required) and `rdflib` (required by `validate-ttl.py`; optional post-hoc validation in `xlsx-to-ttl.py`).
- Local venv at `.venv-geospecimens-process-vocabularies/`. Activate via `init.bat` (Windows): runs `.\.venv-geospecimens-process-vocabularies\Scripts\activate`.
- No `requirements.txt` is checked in — install `openpyxl` and `rdflib` into the venv when setting it up.
- All scripts assume they are run from the project root and use `Path(__file__).resolve().parents[1]` as ROOT, so they don't actually require `cd` — but the venv must be active.

## Core pipeline

The end-to-end flow for adding/updating a vocabulary:

1. Edit the source workbook in `sources/xlsx/` (e.g. `HazardTypes.xlsx`). `Agents.xlsx` is a special cross-vocab agent registry.
2. `python utils/xlsx-to-ttl.py` — regenerates **all** `data/vocabs/{slug}.ttl` files from every `*.xlsx` in `sources/xlsx/` except `Agents.xlsx`. Post-pass strips unused `@prefix` lines via `cleanup_ttl_prefixes.analyse()` and (if `rdflib` is importable) prints a per-file scheme/concept count sanity check.
3. `python utils/build_agents_ttl.py` — regenerates `data/vocabs/agents.ttl` from `Agents.xlsx`. Use `--init-map` to populate the workbook's `map` sheet with the default agent↔vocab role mappings before first generation.
4. `python utils/build_mappings_ttl.py` — emits `{slug}-mappings.ttl` files for each vocab whose workbook has a `Mappings`/`Mapping` sheet (SKOS match triples only).
5. `python utils/validate-ttl.py [path ...]` — runs all eight SKOS conformance checks on `data/vocabs/*.ttl` (or specified paths). Exit code 1 on any failure.
6. `python utils/publish_to_vocab_publisher.py [--dry-run] [--target DIR]` — mirrors `data/` into the vocab-publisher web app. **Default target is the hardcoded Windows path** `G:\webserver\Apache\htdocs-apps\geoapis-htdocs\vocab-publisher\data`; on other machines pass `--target`. Files present only in the target (manifest.ttl, content/, glossaries/, etc.) are never touched.

Standalone helpers: `cleanup_ttl_prefixes.py` (idempotent prefix scrub of `data/vocabs/*.ttl`, supports `--dry-run`); `build_agents_template.py` (regenerates the heavily-styled `AgentsTemplate.xlsx` source-of-truth template); `fetch_roles.py` / `fetch_roles_cit2.py` (one-shot scrapers for ISO 19115-3 CI_RoleCode codelist HTML).

## xlsx → TTL conversion: behaviours to know

`utils/xlsx-to-ttl.py` is the heart of the pipeline. Several non-obvious behaviours are deliberate:

- **Each workbook is loaded twice** — `data_only=False` for the Concepts sheet (to preserve `="base/"&B2` formula strings in `conceptIRI` cells, resolved via `_eval_formula`); `data_only=True` for everything else, including the Mappings sheet whose `conceptIRI` is typically a formula referring back to the Concepts sheet's cached value.
- **Sheet-name lookup is case-insensitive and accepts a typo**: `Namespeces` is recognised as `Namespaces` (and the typo is reported as a data-quality issue in the output's header comment).
- **Three column-naming conventions** (`bare`, `prefixed`, `mixed`) coexist across workbooks. `CS_KEY_ALIASES`, `CONCEPT_COL_ALIASES`, and `MAPPINGS_COL_ALIASES` normalise them. Language-tag variants like `skos:prefLabel@de` are handled separately by `_normalize_concept_col` (regex strips the namespace prefix while preserving the `@lang` suffix).
- **Top-concept reconciliation**: if the scheme-level `hasTopConcept` cell has truncated/empty-slug URIs (a known authoring quirk), `skos:hasTopConcept` is rebuilt from each concept's `isTopConceptOf` column. The reconciliation is reported in the output's header.
- **`normalize_iri()` rewrites `http://kos.geospecimens.org` → `https://`** on every concept/scheme IRI silently. Other http→https mismatches are flagged but not rewritten.
- **Agent resolution is a 3-pass strategy** (`resolve_dc_refs`): role-keyword match → name match against CS-sheet creator/publisher → first-agent fallback → plain-literal fallback. Persons get a separate `schema:Organization` block emitted for each unique `affiliationURI`.
- The output Turtle uses fixed column-aligned formatting (`INDENT=4`, `PROP_W=25`, `BN_INDENT=8`, `BN_PROP_W=17`). When editing renderers, preserve these to avoid noisy diffs in `data/vocabs/`.

## Validation (`utils/validate-ttl.py`)

Eight checks per file: turtle syntax, exactly-one ConceptScheme, required scheme metadata (skos:prefLabel, dcterms:title/description, skos:definition, dcterms:created/modified, dcterms:publisher/creator, reg:status), required concept metadata (skos:prefLabel, skos:definition, skos:inScheme, reg:status), inScheme back-reference, bidirectional hasTopConcept/topConceptOf consistency, IRI base-prefix consistency (http/https mismatch downgraded to a warning), and duplicate prefLabel-within-language. Errors fail the run; warnings don't.

Run a single file: `python utils/validate-ttl.py data/vocabs/hazard-type.ttl`.

## Layout cheat-sheet

- `sources/xlsx/` — authoring workbooks (one per vocab + `Agents.xlsx`). `~$*.xlsx` Excel lock files and `Agents.xlsx` are skipped by `xlsx-to-ttl.py`.
- `sources/external/` — third-party reference vocabs (foaf, skos, isoroles, etc.) used as context, not regenerated.
- `sources/md/xlsx-to-ttl-process.md` — authoritative documentation of the field-mapping rules and known per-workbook quirks; consult before changing the converter.
- `data/vocabs/` — generated SKOS TTLs. **Treat as build output**; do not hand-edit unless you also update the upstream xlsx.
- `data/config/` — `profiles.ttl`, `workspaces.ttl` (Prez catalogue config, hand-written).
- `samples/mappings/` — example TTL snippets for the SKOS Mappings format.
- `utils/archive/` — superseded converter scripts (`xlsx-to-ttl-prezlite.py`, prior `xlsx-to-ttl.py`); the current `utils/xlsx-to-ttl.py` is the merged successor of both.
- `export/` — staging area mirroring `data/` for the vocab-publisher; usually empty in-repo.

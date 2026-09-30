# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Vocabulary processor for the **GeoSpecimens Platform** and KOS Publishing System (https://kos.geospecimens.org). Authors maintain controlled vocabularies as Excel workbooks under `sources/xlsx/`; the scripts in `src/` transform those workbooks into SKOS Turtle files under `data/vocabs/`, validate them, and publish them to the downstream `vocab-publisher` web app.

The parent directory `G:/repos/vocabularies/` contains several other unrelated vocabulary repos (GSWA-Vocabularies, GeoKOS, bgs-vocabularies, gsq-vocabularies, etc.). Only this project and `vocab-publisher` are in active development.

## Working across into vocab-publisher

`G:\repos\vocabularies\vocab-publisher\` (a separate git repo) is an additional working directory for sessions started here. When a change in this project needs a matching change in the publisher, make it there in the same task rather than stopping at this repo. Typical cases: a new IRI pattern needs a URI resolver route; a new TTL property or structure needs parsing or display support; a vocabulary is added or renamed. Read `vocab-publisher/CLAUDE.md` before editing it. Its key constraints:

- **Four resolver implementations must stay in step:** `public/def/resolver.php` + `public/.htaccess` (production), `scripts/vite-plugin-resolver.js` (dev), and `scripts/test-router.php` / `tests/api/test-server.php` (test routers).
- **Serializers are mirrored:** the PHP serializers in `resolver.php` must match the JS ones in `src/utils/rdf-serializers.js`.
- **`src/config/uris.json` is the hand-maintained registry** of scheme and concept URIs. `public/data/` is generated output; never edit it.

Afterwards, sync the data (`sync_to_publisher.py --vocab <slug>`), run `npm run index` and then `node scripts/verify-static.js` in the publisher. Commit each repo separately.

## Environment

- Python 3 with `openpyxl` (required) and `rdflib` (required by `validate-ttl.py`; optional post-hoc validation in `xlsx-to-ttl.py`).
- Local venv at `.venv-geospecimens-process-vocabularies/`. Activate via `init.bat` (cmd) or `.\.venv-geospecimens-process-vocabularies\Scripts\Activate.ps1` (PowerShell). Without activating, call `.\.venv-geospecimens-process-vocabularies\Scripts\python.exe src/<script>.py` directly.
- No `requirements.txt` is checked in — install `openpyxl` and `rdflib` into the venv when setting it up.
- Most scripts use `Path(__file__).resolve().parents[1]` as ROOT, so they don't require `cd` — but the venv must be active. **Exception**: `build_agents_template.py` uses a cwd-relative path (writes `sources/AgentsTemplate.xlsx`, run from project root).
- `.env` (gitignored; copy from `.env.example`) sets `VOCAB_PUBLISHER_PATH` or `VOCAB_PUBLISHER_DATA_DIR` for `sync_to_publisher.py`. Real environment variables override `.env`.

## Core pipeline

The end-to-end flow for adding/updating a vocabulary:

1. Edit the source workbook in `sources/xlsx/` (e.g. `HazardTypes.xlsx`). `Agents.xlsx` is a special cross-vocab agent registry.
2. `python src/xlsx-to-ttl.py [VOCAB]` — regenerates **all** `data/vocabs/{slug}.ttl` files from every `*.xlsx` in `sources/xlsx/` except `Agents.xlsx`; pass a workbook name (`HazardTypes` or `HazardTypes.xlsx`) to build just one. Post-pass strips unused `@prefix` lines via `cleanup_ttl_prefixes.analyse()` and (if `rdflib` is importable) prints a per-file scheme/concept count sanity check.
3. `python src/build_agents_ttl.py` — regenerates `data/vocabs/agents.ttl` from `Agents.xlsx`: the central agent registry (not a vocabulary). vocab-publisher's `build-vocabs.js` loads it as the agent lookup and excludes it from vocab indexing, and `validate-ttl.py` skips it by default. Use `--init-map` to populate the workbook's `map` sheet with the default agent↔vocab role mappings before first generation.
4. `python src/build_mappings_ttl.py` — emits `{slug}-mappings.ttl` files for each vocab whose workbook has a `Mappings`/`Mapping` sheet (SKOS match triples only).
5. `python src/validate-ttl.py [path ...]` — runs all eight SKOS conformance checks on `data/vocabs/*.ttl`, excluding `agents.ttl` and `*-mappings.ttl` since neither declares a ConceptScheme. Pass paths explicitly to check other files. Exit code 1 on any failure.
6. `python src/publish_to_vocab_publisher.py [--dry-run] [--target DIR]` — mirrors `data/` into the vocab-publisher web app. **Default target is the hardcoded Windows path** `G:\repos\vocabularies\vocab-publisher\data`; on other machines pass `--target`. Files present only in the target (manifest.ttl, content/, glossaries/, etc.) are never touched. Before overwriting anything it snapshots the whole target to `temp/publisher-data-backup-YYYYMMDD-HHMMSS/` (gitignored). It then runs `npm run index` and `node scripts/verify-static.js` in the publisher: on success the backup is deleted; on failure it is kept, the exit code is 1, and `--restore [NAME]` rolls the target back (newest backup by default). `--no-verify` skips the checks and keeps the backup; `--clean-backups` deletes all backups.
   - `python src/sync_to_publisher.py` is the `.env`-driven alternative with scoping: `--only vocabs`, `--vocab hazard-type`, `--glossary gcdm`, `--dry-run`, `--force` (recopy identical files), `--delete` (prune target-only files within scope). Exits with an error if no publisher path is configured.

Standalone helpers: `cleanup_ttl_prefixes.py` (idempotent prefix scrub of `data/vocabs/*.ttl`, supports `--dry-run`); `build_agents_template.py` (regenerates the heavily-styled `AgentsTemplate.xlsx` source-of-truth template); `fetch_roles.py` / `fetch_roles_cit2.py` (one-shot scrapers for ISO 19115-3 CI_RoleCode codelist HTML).

## Classification scheme pipeline (xlsx → CSV → XKOS TTL)

Classification systems live in `sources/classification-systems/<system>/`, each authored in the **single `.xlsx` workbook in that folder**; the CSVs beside it are build output.

1. `python src/build_classification_csvs.py <system>|--all` writes every sheet (except `README`) to `<sheet name>.csv`. It also generates `<stem>_closure.csv` from the `<stem>_classification` sheet. Before writing anything, it checks `id`/`parent_id` sheets against the parent chain: parents must resolve and ids be unique, and `depth` / `materialized_path` must match. `path_labels` is authored, since it uses abbreviations, and is not checked.
2. `python src/build_xkos_ap_no.py` builds the XKOS-AP-NO meteorite classification from the meteorite CSVs (rdflib-based; profile shapes in `sources/schemas/xkos/`). It writes identical output both next to the CSVs and to `data/vocabs/meteorite-classification.ttl`.
   - Scheme-level metadata (base IRI, namespaces, prefixes, titles, publisher, language, status, dates, rank scheme) lives in the `meteorite_classification_scheme` sheet as `key,value,notes` rows; a value can reference another key as `{key}`, e.g. `{base_iri}/level/`.
   - Ranks are concepts at `{base_iri}/rank/{rank}` in their own scheme, ordered by `skos:notation` and `xkos:next`/`xkos:previous`.
3. Validate and publish as for vocabularies.

## Glossary pipeline (4-file source set → JSON + TTL)

Glossaries are authored not in Excel but as a standard four-file set under `sources/glossaries/<slug>/`: `glossary-config-entry.jsonc` (required metadata), `glossary-terms.csv` (required rows), `glossary-meta.csv` (optional creator/publisher/prefix/rights + term URI base), `glossary-sources.csv` (optional citations). Filenames are folder-based and unprefixed; the folder name is the slug (legacy acronym-prefixed names are still accepted as a fallback).

1. `python src/build_glossary_csvs.py <slug>` — *optional*; only for glossaries authored in a `verbatim/` subfolder. Converts verbatim CSVs → canonical `glossary-*.csv`. Glossaries authored directly in canonical form skip this step.
2. `python src/build_glossary_json.py <slug>|--all` — 4-file set → `data/glossaries/<slug>/glossary.json` (consumed by the vocab-publisher web app).
3. `python src/build_glossary_ttl.py <slug>|--all [--status STATUS]` — 4-file set → `data/glossaries/<slug>/<slug>.ttl` (SKOS RDF; shares the same parser as the JSON builder). Emits one `skos:ConceptScheme`, one `skos:Concept` per term at `<uri>/term/<id>` (flat, so every term is a top concept), and one `skos:Collection` per category. `reg:status` defaults to `stable`.
4. `python src/validate-ttl.py data/glossaries/<slug>/<slug>.ttl` — the same eight checks apply.

Publish with `publish_to_vocab_publisher.py` as for vocabs (it mirrors all of `data/`, including `data/glossaries/`).

> **See [`QUICK-REFERENCE.md`](QUICK-REFERENCE.md)** for a condensed command cheat-sheet covering both the vocabulary and glossary flows.

## xlsx → TTL conversion: behaviours to know

`src/xlsx-to-ttl.py` is the heart of the pipeline. Several non-obvious behaviours are deliberate:

- **Each workbook is loaded twice** — `data_only=False` for the Concepts sheet (to preserve `="base/"&B2` formula strings in `conceptIRI` cells, resolved via `_eval_formula`); `data_only=True` for everything else, including the Mappings sheet whose `conceptIRI` is typically a formula referring back to the Concepts sheet's cached value.
- **Sheet-name lookup is case-insensitive and accepts a typo**: `Namespeces` is recognised as `Namespaces` (and the typo is reported as a data-quality issue in the output's header comment).
- **Three column-naming conventions** (`bare`, `prefixed`, `mixed`) coexist across workbooks. `CS_KEY_ALIASES`, `CONCEPT_COL_ALIASES`, and `MAPPINGS_COL_ALIASES` normalise them. Language-tag variants like `skos:prefLabel@de` are handled separately by `_normalize_concept_col` (regex strips the namespace prefix while preserving the `@lang` suffix).
- **Top-concept reconciliation**: if the scheme-level `hasTopConcept` cell has truncated/empty-slug URIs (a known authoring quirk), `skos:hasTopConcept` is rebuilt from each concept's `isTopConceptOf` column. The reconciliation is reported in the output's header.
- **Scheme labelling uses `dcterms:title` / `dcterms:description`**; `skos:prefLabel` / `skos:definition` have been dropped from the scheme-level template (`BaseTemplate.xlsx`). The converter still emits them if a workbook has those rows, but the validator no longer requires them.
- **`normalize_iri()` rewrites `http://kos.geospecimens.org` → `https://`** on every concept/scheme IRI silently (`build_agents_ttl.py` applies the same rewrite to `map`-sheet `resourceURI`s). Other http→https mismatches are flagged but not rewritten.
- **Agents come only from `Agents.xlsx`, embedded into each vocabulary TTL.** An `Agents` sheet in a vocabulary workbook is ignored (the output header notes it). `xlsx-to-ttl.py` loads `Agents.xlsx` once (reusing the `build_agents_ttl.py` loaders and `render_agent_block`). For each scheme it looks up the `map` sheet rows whose `resourceURI` equals the scheme IRI, then emits:
  - one `prov:qualifiedAttribution` / `dcat:hadRole` per agent (the pattern `vocab-publisher`'s `profiles.ttl` renders);
  - `dcterms:publisher` / `creator` / `contributor` as agent IRIs by role (`DC_ROLE_MAP`), falling back to the Concept Scheme sheet literal;
  - agent description blocks for the mapped agents plus any agents they reference.

  The publisher's `build-vocabs.js` drops literal creators/publishers, so they need to be IRIs to display. **After editing `Agents.xlsx`, re-run both `build_agents_ttl.py` and `xlsx-to-ttl.py`.** The first rebuilds the central `agents.ttl` registry, which vocab-publisher uses as its agent lookup. The second rebuilds the embedded copies, which keep each vocabulary self-contained when exported.
- The output Turtle uses fixed column-aligned formatting (`INDENT=4`, `PROP_W=25`, `BN_INDENT=8`, `BN_PROP_W=17`). When editing renderers, preserve these to avoid noisy diffs in `data/vocabs/`.

## Validation (`src/validate-ttl.py`)

Eight checks per file: turtle syntax, exactly-one ConceptScheme, required scheme metadata (dcterms:title/description, dcterms:created/modified, dcterms:publisher/creator, reg:status), required concept metadata (skos:prefLabel, skos:definition, skos:inScheme, reg:status), inScheme back-reference, bidirectional hasTopConcept/topConceptOf consistency, IRI base-prefix consistency (http/https mismatch downgraded to a warning), and duplicate prefLabel-within-language. Errors fail the run; warnings don't.

Run a single file: `python src/validate-ttl.py data/vocabs/hazard-type.ttl`.

## Layout cheat-sheet

- `sources/xlsx/` — authoring workbooks (one per vocab + `Agents.xlsx`). `~$*.xlsx` Excel lock files and `Agents.xlsx` are skipped by `xlsx-to-ttl.py`.
- `sources/templates/` — `BaseTemplate.xlsx` is the starting point for new vocab workbooks; its Concept Scheme sheet defines the expected row keys.
- `sources/schemas/` — third-party reference vocabs (foaf, skos, isoroles, xkos, etc.) used as context, not regenerated.
- `sources/drafts/` — work-in-progress workbooks/glossaries not yet picked up by the pipeline.
- `docs/xlsx-to-ttl-process.md` — authoritative documentation of the field-mapping rules and known per-workbook quirks; consult before changing the converter. `docs/generate_glossary.md` covers the glossary flow.
- `data/vocabs/` — generated SKOS TTLs. **Treat as build output**; do not hand-edit unless you also update the upstream xlsx.
- `data/config/` — `profiles.ttl`, `workspaces.ttl` (Prez catalogue config, hand-written).
- `samples/mappings/` — example TTL snippets for the SKOS Mappings format.
- `src/archive/` — superseded converter scripts (`xlsx-to-ttl-prezlite.py`, prior `xlsx-to-ttl.py`); the current `src/xlsx-to-ttl.py` is the merged successor of both.
- `export/` — staging area mirroring `data/` for the vocab-publisher; usually empty in-repo.

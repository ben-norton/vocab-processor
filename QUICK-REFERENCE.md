# Quick Reference — Building TTL Vocabularies, Glossaries & Classification Schemes

Cheat-sheet for the `vocab-processor` pipeline. Three independent flows produce
SKOS Turtle:

- **Vocabularies** — authored in Excel (`sources/xlsx/*.xlsx`) → `data/vocabs/*.ttl`
- **Glossaries** — authored as a 4-file set (`sources/glossaries/<slug>/`) → `data/glossaries/<slug>/`
- **Classification schemes** — authored in Excel (`sources/classification-systems/<system>/*.xlsx`) → CSVs → XKOS `data/vocabs/*.ttl`

> Scripts live in **`src/`**. All scripts resolve paths from the project root
> via `Path(__file__).resolve().parents[1]`, so they run from any working
> directory — but the venv must be active.

---

## 0. One-time setup

```bat
cd vocab-processor
init.bat                 :: activates .venv-geospecimens-process-vocabularies
```

PowerShell equivalent:

```powershell
.\.venv-geospecimens-process-vocabularies\Scripts\Activate.ps1
```

Required packages (install into the venv; no `requirements.txt`):

```
pip install openpyxl rdflib
```

---

## 1. Vocabularies (Excel → TTL)

### TL;DR

```bash
python src/xlsx-to-ttl.py                 # all workbooks → data/vocabs/*.ttl
python src/build_agents_ttl.py            # Agents.xlsx  → data/vocabs/agents.ttl
python src/build_mappings_ttl.py          # *-mappings.ttl for workbooks w/ a Mappings sheet
python src/validate-ttl.py                # 8-point SKOS check on data/vocabs/*.ttl
python src/publish_to_vocab_publisher.py  # mirror data/ → vocab-publisher/data
```

### Steps

| # | Command | Input → Output |
|---|---------|----------------|
| 1 | `python src/xlsx-to-ttl.py [VOCAB]` | `sources/xlsx/*.xlsx` → `data/vocabs/{slug}.ttl` |
| 2 | `python src/build_agents_ttl.py [--init-map]` | `sources/xlsx/Agents.xlsx` → `data/vocabs/agents.ttl` |
| 3 | `python src/build_mappings_ttl.py` | workbooks with a `Mappings` sheet → `data/vocabs/{slug}-mappings.ttl` |
| 4 | `python src/validate-ttl.py [path ...]` | validates `data/vocabs/*.ttl` (exit 1 on any error) |
| 5 | `python src/publish_to_vocab_publisher.py [--dry-run] [--target DIR]` | `data/` → `vocab-publisher/data` |

Notes:

- **`xlsx-to-ttl.py`** processes **every** `*.xlsx` in `sources/xlsx/` except
  `Agents.xlsx` and Excel lock files (`~$*.xlsx`). Pass a workbook name
  (`HazardTypes` or `HazardTypes.xlsx`) to build just one. It also strips unused
  `@prefix` lines and, if `rdflib` is importable, prints a scheme/concept sanity count.
- **`build_agents_ttl.py --init-map`** first populates the `map` sheet in
  `Agents.xlsx` with the default agent↔vocab role mappings — run once before the
  first generation.
- **`publish_to_vocab_publisher.py`** default target is
  `G:\repos\vocabularies\vocab-publisher\data`; pass `--target` on other machines.
  Files present only in the target (`manifest.ttl`, `content/`, `glossaries/`, …)
  are never touched. Use `--dry-run` to preview. Before overwriting, it backs the
  target up to `temp/publisher-data-backup-<timestamp>/`, then runs `npm run index`
  and `verify-static.js` in the publisher. If they pass, the backup is deleted; if
  they fail, it is kept (exit 1). Other options:
  - `--restore [NAME]` rolls back to a backup (the newest by default).
  - `--no-verify` skips the checks and keeps the backup.
  - `--clean-backups` deletes all backups.

Helper: `python src/cleanup_ttl_prefixes.py [--dry-run]` — idempotent prefix
scrub of `data/vocabs/*.ttl`.

---

## 2. Glossaries (4-file set → JSON + TTL)

### The standard 4-file source set — `sources/glossaries/<slug>/`

| File | Required | Purpose |
|------|:--------:|---------|
| `glossary-config-entry.jsonc` | ✅ | top-level metadata (`id`, `title`, `uri`, notes, version, license, externalLinks) |
| `glossary-terms.csv`          | ✅ | the term rows |
| `glossary-meta.csv`           | ⬜ | creator / publisher / namespace prefix / rights + term URI base |
| `glossary-sources.csv`        | ⬜ | bibliographic source rows |

> Filenames are **folder-based and unprefixed** — the folder name (`<slug>`)
> identifies the glossary; files inside are plain `glossary-*.csv`. (Legacy
> acronym-prefixed names like `gcdm-glossary-terms.csv` are still accepted as a
> fallback.)

### TL;DR

```bash
# (optional) verbatim authoring CSVs → canonical CSVs
python src/build_glossary_csvs.py <slug>

python src/build_glossary_json.py <slug>          # → data/glossaries/<slug>/glossary.json
python src/build_glossary_ttl.py  <slug>          # → data/glossaries/<slug>/<slug>.ttl
python src/validate-ttl.py data/glossaries/<slug>/<slug>.ttl
```

Process every glossary at once with `--all`:

```bash
python src/build_glossary_json.py --all
python src/build_glossary_ttl.py  --all
```

### Steps

| # | Command | Input → Output |
|---|---------|----------------|
| 1 *(opt.)* | `python src/build_glossary_csvs.py <slug> [--date YYYYMMDD] [--dry-run]` | `<slug>/verbatim/glossary-*.csv` → canonical `<slug>/glossary-*.csv` |
| 2 | `python src/build_glossary_json.py <slug>\|--all [--output PATH] [--include-term-uris]` | 4-file set → `data/glossaries/<slug>/glossary.json` |
| 3 | `python src/build_glossary_ttl.py <slug>\|--all [--output PATH] [--status STATUS]` | 4-file set → `data/glossaries/<slug>/<slug>.ttl` |
| 4 | `python src/validate-ttl.py data/glossaries/<slug>/<slug>.ttl` | validates the generated TTL |

Notes:

- Step 1 is only for glossaries authored in a `verbatim/` subfolder; glossaries
  authored directly in canonical CSVs skip it (the script says so and exits).
- **`build_glossary_json.py`** feeds the vocab-publisher web app (JSON).
  **`build_glossary_ttl.py`** emits the RDF serialization (both read the same
  4-file set via a shared parser).
- **TTL shape:** one `skos:ConceptScheme` at the glossary `uri`; one
  `skos:Concept` per term at `<uri>/term/<id>` (flat → every term is a top
  concept); one `skos:Collection` per category at `<uri>/collection/<cat-id>`.
- **`reg:status`** defaults to `stable`; override with `--status <slug|IRI>` or a
  `status` key in the config JSONC.
- Publish glossaries the same way as vocabs — `publish_to_vocab_publisher.py`
  mirrors all of `data/`, including `data/glossaries/`.

---

## 3. Classification schemes (Excel → CSV → XKOS TTL)

Hierarchical classifications with ranked levels (SKOS + XKOS, profiled by
XKOS-AP-NO), e.g. the Weisberg, McCoy & Krot (2006) meteorite classification.
Each system has its own folder, and its **workbook is the source of truth**:

```
sources/classification-systems/<system>/
  <system-name>.xlsx      ← edit this (one workbook per folder)
  *.csv                   ← built from the workbook; don't hand-edit
  <scheme>.ttl            ← copy of the built TTL, kept next to its sources
```

### TL;DR (meteorites)

```bash
python src/build_classification_csvs.py meteorites   # meteorite-classification.xlsx → *.csv
python src/build_xkos_ap_no.py                        # *.csv → data/vocabs/meteorite-classification.ttl
python src/validate-ttl.py data/vocabs/meteorite-classification.ttl
python src/publish_to_vocab_publisher.py              # data/ → vocab-publisher (backup + verify)
```

### Steps

| # | Command | Input → Output |
|---|---------|----------------|
| 1 | Edit `sources/classification-systems/<system>/*.xlsx` | — |
| 2 | `python src/build_classification_csvs.py <system>\|--all` | every sheet except `README` → `<sheet name>.csv`, plus the derived `<stem>_closure.csv` |
| 3 | `python src/build_xkos_ap_no.py` | meteorite CSVs → `data/vocabs/meteorite-classification.ttl` (+ a copy next to the CSVs) |
| 4 | `python src/validate-ttl.py data/vocabs/<scheme>.ttl` | the same 8 checks as vocabularies |
| 5 | `python src/publish_to_vocab_publisher.py` | as for vocabularies |

### Meteorite workbook sheets (`meteorite-classification.xlsx`)

| Sheet → CSV | Holds | Read by `build_xkos_ap_no.py` |
|---|---|:--:|
| `meteorite_classification_scheme` | scheme metadata as `key,value,notes` rows: base IRI, namespaces and prefixes, titles, publisher, language, status, dates, rank scheme. A value can reference another key as `{key}` (e.g. `{base_iri}/level/`) | ✅ |
| `meteorite_classification` | one row per concept: `id`, `parent_id`, `rank`, `code`, `name`, `description`, `source`, `notes`, … | ✅ |
| `meteorite_sources` | bibliography (`cite_key`, `short_form`, `full_citation`, `identifier`) | ✅ |
| `meteorite_data_dictionary` | column definitions | — |
| `additional_classifications` | candidate subgroup rows not yet merged in | — |
| *(derived)* `meteorite_closure.csv` | ancestor/descendant pairs, generated from `meteorite_classification` | — |

Notes:

- **Build checks:** `build_classification_csvs.py` checks every `id`/`parent_id` sheet against the parent chain before writing anything. Every `parent_id` must resolve, ids must be unique, and `depth` / `materialized_path` must match the chain. `path_labels` is authored.
- **Concept IRIs** are `{base_iri}/<slug of name>`, so renaming a row changes its IRI.
- **`rank`** must be `root` or one of the ranks, highest first: `division` (children of the root), `class`, `clan`, `group`, `subgroup`. Any other value stops the build.
- **Ranks** are concepts in their own scheme at `{base_iri}/rank/{rank}`. They carry `skos:notation` 1–5 and are chained by `xkos:next` / `xkos:previous`. Level *n* (`xkos:depth` *n*) is `xkos:organizedBy` rank *n*.
- **vocab-publisher** serves ranks at `/def/{scheme}/rank/{rank}`.
- **Adding a system:** create a new folder with its workbook, then run step 2. `build_xkos_ap_no.py` is currently meteorite-specific, so a second system also needs its own builder or a generalised one.

---

## 4. Validation — the 8 checks (`validate-ttl.py`)

Runs on `data/vocabs/*.ttl` by default, except `agents.ttl` and `*-mappings.ttl` (no ConceptScheme), or on any path(s) you pass. **Errors fail
the run (exit 1); warnings don't.**

1. **Turtle syntax** — parses under `rdflib`
2. **ConceptScheme** — at least one `skos:ConceptScheme`. With several (e.g. a classification plus its rank scheme), the one with the most concepts is primary, and checks 3 and 6–8 run per scheme over its own concepts.
3. **Scheme props** — `dcterms:title`, `dcterms:description`, `dcterms:created`, `dcterms:modified`, `dcterms:publisher`, `dcterms:creator`, `reg:status`
4. **Concept props** — every `skos:Concept` has `skos:prefLabel`, `skos:definition`, `skos:inScheme`, `reg:status`
5. **inScheme** — each concept's `skos:inScheme` points at a scheme declared in the file
6. **Top concepts** — `hasTopConcept` / `topConceptOf` are bidirectionally consistent
7. **IRI prefix** — concept IRIs share the scheme's base (http/https mismatch → warning)
8. **Duplicate labels** — no two concepts share a `prefLabel` in the same language

```bash
python src/validate-ttl.py                          # data/vocabs/*.ttl (minus agents / mappings)
python src/validate-ttl.py data/vocabs/hazard-type.ttl
python src/validate-ttl.py data/glossaries/kos-terms/kos-terms.ttl
```

---

## 5. Downstream — vocab-publisher web app

Run from `vocab-publisher/`:

```bash
npm run index      # re-parse TTL → public/data/*.json (after editing .ttl)
npm run dev        # index + Vite dev server (http://localhost:5173)
npm run build      # index + production build → dist/
```

`predev`/`prebuild` hooks run `index` automatically; you only need `npm run
index` manually when the dev server is already running and you've changed a `.ttl`.

---

## ⚠️ Generated output — don't hand-edit

| Path | Regenerated by | Fix upstream in |
|------|----------------|-----------------|
| `data/vocabs/*.ttl` | `xlsx-to-ttl.py` | `sources/xlsx/*.xlsx` |
| `data/glossaries/<slug>/glossary.json` | `build_glossary_json.py` | the 4-file set |
| `data/glossaries/<slug>/<slug>.ttl` | `build_glossary_ttl.py` | the 4-file set |
| `sources/classification-systems/<system>/*.csv` | `build_classification_csvs.py` | the system's `.xlsx` |
| `data/vocabs/meteorite-classification.ttl` | `build_xkos_ap_no.py` | `meteorite-classification.xlsx` (then rebuild the CSVs) |
| `vocab-publisher/public/data/*.json` | `npm run index` | the upstream `.ttl` |

Hand-edits to any of these are overwritten on the next build.

# Quick Reference — Building TTL Vocabularies & Glossaries

Cheat-sheet for the `vocab-processor` pipeline. Two independent flows produce
SKOS Turtle:

- **Vocabularies** — authored in Excel (`sources/xlsx/*.xlsx`) → `data/vocabs/*.ttl`
- **Glossaries** — authored as a 4-file set (`sources/glossaries/<slug>/`) → `data/glossaries/<slug>/`

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
  are never touched. Use `--dry-run` to preview.

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

## 3. Validation — the 8 checks (`validate-ttl.py`)

Runs on `data/vocabs/*.ttl` by default, or any path(s) you pass. **Errors fail
the run (exit 1); warnings don't.**

1. **Turtle syntax** — parses under `rdflib`
2. **ConceptScheme** — exactly one `skos:ConceptScheme`
3. **Scheme props** — `skos:prefLabel`, `dcterms:title`, `skos:definition`, `dcterms:description`, `dcterms:created`, `dcterms:modified`, `dcterms:publisher`, `dcterms:creator`, `reg:status`
4. **Concept props** — every `skos:Concept` has `skos:prefLabel`, `skos:definition`, `skos:inScheme`, `reg:status`
5. **inScheme** — each concept's `skos:inScheme` points at the scheme
6. **Top concepts** — `hasTopConcept` / `topConceptOf` are bidirectionally consistent
7. **IRI prefix** — concept IRIs share the scheme's base (http/https mismatch → warning)
8. **Duplicate labels** — no two concepts share a `prefLabel` in the same language

```bash
python src/validate-ttl.py                          # all data/vocabs/*.ttl
python src/validate-ttl.py data/vocabs/hazard-type.ttl
python src/validate-ttl.py data/glossaries/kos-terms/kos-terms.ttl
```

---

## 4. Downstream — vocab-publisher web app

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
| `vocab-publisher/public/data/*.json` | `npm run index` | the upstream `.ttl` |

Hand-edits to any of these are overwritten on the next build.

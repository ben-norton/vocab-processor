# How-to: Process Source Files into RDF

Run every command from the `vocab-processor/` root.

## Before you start

1. Activate the venv:
   ```powershell
   .\.venv-geospecimens-process-vocabularies\Scripts\Activate.ps1
   ```
   (cmd: `init.bat`)

---

## Process a Vocabulary

1. Edit `sources/xlsx/<Workbook>.xlsx`.
2. Build the TTL:
   ```bash
   python src/xlsx-to-ttl.py <Workbook>
   ```
3. Build the mappings (only if the workbook has a `Mappings` / `SSSOM` sheet):
   ```bash
   python src/build_mappings_ttl.py
   python src/build_sssom_ttl.py <Workbook>
   ```
4. Validate:
   ```bash
   python src/validate-ttl.py data/vocabs/<slug>.ttl
   ```
5. Done → `data/vocabs/<slug>.ttl` (plus `<slug>-mappings.ttl`, `<slug>_sssom_mappings.ttl`).

## Process All Vocabularies

1. Build:
   ```bash
   python src/xlsx-to-ttl.py
   python src/build_mappings_ttl.py
   python src/build_sssom_ttl.py
   ```
2. Validate:
   ```bash
   python src/validate-ttl.py
   ```
3. Done → `data/vocabs/*.ttl`.

## Process Agents

1. Edit `sources/xlsx/Agents.xlsx`.
2. Build the agent registry:
   ```bash
   python src/build_agents_ttl.py
   ```
3. Rebuild the vocabularies, which embed agent copies:
   ```bash
   python src/xlsx-to-ttl.py
   ```
4. Done → `data/vocabs/agents.ttl` and every `data/vocabs/*.ttl`.

## Process a Glossary

1. Edit the files in `sources/glossaries/<slug>/`.
2. Convert verbatim CSVs (only if the glossary has a `verbatim/` folder):
   ```bash
   python src/build_glossary_csvs.py <slug>
   ```
3. Build:
   ```bash
   python src/build_glossary_ttl.py <slug>
   python src/build_glossary_json.py <slug>
   ```
4. Validate:
   ```bash
   python src/validate-ttl.py data/glossaries/<slug>/<slug>.ttl
   ```
5. Done → `data/glossaries/<slug>/<slug>.ttl` and `glossary.json`.

All glossaries: replace `<slug>` with `--all` in step 3.

## Process the Meteorite Classification

1. Edit `sources/classification-systems/meteorites/meteorite-classification.xlsx`.
2. Build the CSVs:
   ```bash
   python src/build_classification_csvs.py meteorites
   ```
3. Build the TTL:
   ```bash
   python src/build_xkos_ap_no.py
   ```
4. Validate:
   ```bash
   python src/validate-ttl.py data/vocabs/meteorite-classification.ttl
   ```
5. Done → `data/vocabs/meteorite-classification.ttl`.

---

## Next: Publish

```bash
python src/publish_to_vocab_publisher.py --dry-run   # preview
python src/publish_to_vocab_publisher.py
```

See [`QUICK-REFERENCE.md`](../../QUICK-REFERENCE.md) for options and details.

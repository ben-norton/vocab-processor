# GCDM Glossary — generation notes

Generated 2026-07-30 from **GCDM_v20260727_1.docx**.

## What was extracted

| File | Rows | Source in manuscript |
|---|---|---|
| `glossary-terms.csv` | 105 terms | All paragraphs styled `TermDefinition` in §2.1, §3.1, §4.1, §5.1, §6.1, §7.1 |
| `glossary-sources.csv` | 45 sources | Every work cited inside a Terms definition, keyed by its in-text citation and carrying the verbatim §10 reference |
| `glossary-meta.csv` | 1 row | Manuscript title/abstract, acknowledgements, and the supplied template defaults |
| `glossary-config-entry.jsonc` | — | Populated from the supplied template |

### Terms by category

| Category | Terms |
|---|---|
| Names and Classification Systems (§4.1) | 29 |
| Geologic Settings and Sampling (§7.1) | 20 |
| Geologic Age (§6.1) | 19 |
| Compound Specimens (§3.1) | 18 |
| Stratigraphy (§5.1) | 11 |
| Data Modeling and Ontology (§2.1) | 8 |

## Column conventions applied

- **`id`** — 0-based sequential integer, following the template's example row.
- **`category`** — the manuscript Terms subsection the term came from, given a human-readable name. These become the glossary's `categories` at build time.
- **`definition`** — the manuscript definition with the trailing source citation and any cross-reference (`§4.5.3`, `Figure 10`) removed; punctuation closed and curly quotes normalised to ASCII. No wording was invented or paraphrased.
- **`usage_note`** — model context that was inline in the manuscript (relation names, figure references, section pointers, conventions), plus short editorial notes where the term's use in the GCDM is not obvious from the definition alone.
- **`source` (×2)** — the header has two `source` columns, used as primary and secondary source so the manuscript's dual citations survive (e.g. *Specimen Part Role* → `Brodaric & Richard 2021` + `Richard et al. 2003`). **Each value is the in-text citation exactly as the manuscript writes it**, and is the `notation` of a row in `glossary-sources.csv`. Terms with no external citation carry `This Document`.

In `glossary-sources.csv`: `notation` = the manuscript's in-text citation, `description` = the full §10 reference pulled verbatim from the manuscript, `title` = a short name for the work, `url` = its DOI or resolvable URL. All 45 notations are referenced by at least one term, and every term source resolves to a row.

#### Citation forms normalised

The manuscript cites five works two different ways. One form was picked per work so each source has a single key:

| Manuscript forms | Key used |
|---|---|
| `ISO 5127 2017`, `ISO 5127:2017` | `ISO 5127:2017` |
| `ISO/IEC 11179-1 2023`, `ISO/IEC 11179-1:2023` | `ISO/IEC 11179-1:2023` |
| `Brodaric & Richard 2021`, `Brodaric & Richard, 2021` | `Brodaric & Richard 2021` |
| `TERN 2020`, `TERN Ontology 2020` | `TERN Ontology 2020` |
| `Cox and Little, 2022` | `Cox and Little 2022` (comma dropped) |

Also collapsed: `http://www.w3.org/ns/prov#Agent` and `…#Activity` are cited as bare class URIs of one work, and share the key `http://www.w3.org/ns/prov#`. Worth fixing in the manuscript so the in-text forms agree — `Name` is cited as `ISO 11179-3:2023` while `Data Model` uses the `ISO/IEC` prefix for Part 1 of the same standard, and the §10 entries carry the same inconsistency.
- **`prov_class`** — the PROV-O class the term's *referent* instantiates: `prov:Entity` (77), `prov:Plan` (14), `prov:Activity` (11), `prov:Organization` (2), `prov:Agent` (1). Rule applied:
  - `prov:Agent` — bears responsibility for an activity or entity (*Agent*).
  - `prov:Organization` — social/legal institution; subclass of `prov:Agent` (*Authority*, *Naming Authority*).
  - `prov:Activity` — occurs over a period of time and acts upon or with entities (*Classification*, *Identification*, *Geologic Event*, *Geologic Process*, *Radioactive Decay*, *Radiometric Dating*, *Relative Dating*, *Sampling Event*, and the two terms defined as practices, *Stratigraphy* and *Geochronology*).
  - `prov:Plan` — prescribes how something is to be done: a method, procedure, protocol, scheme, or model that guides construction or representation; subclass of `prov:Entity` (the six data-model terms, *Ontology*, *Compound/Simple Specimen Model*, *Classification Scheme/System/Version*, *Confirmation Protocol*, *Linnaean Taxonomy*, *Geologic Unit Type*).
  - `prov:Entity` — default for everything else: physical objects, values, names, units, ages, intervals, features, and places.
- **`examples`** — populated only where the manuscript gives explicit examples (9 terms). Left empty elsewhere rather than invented.
- **`resource_id`** — kebab-case slug of the label; unique across all 105 terms.
- **`last_modified`** — `20260730` (YYYYMMDD, per the template example).

### Borderline `prov_class` calls worth a look

- *Geologic Timescale*, *Regional Timescale* — typed `prov:Entity` (reference artifacts) rather than `prov:Plan`.
- *Geochronology*, *Stratigraphy* — typed `prov:Activity` because the manuscript defines both as practices ("the science of determining…", "the description of… in order to establish…") rather than as bodies of knowledge.
- *Determination*, *Geochronologic Interpretation* — typed `prov:Entity` because both definitions name the *result* (an identity, an interpretation), not the act that produced it.
- *Lithology* — definition (a) is an activity of description, (b) is the physical character of a rock; typed `prov:Entity` on sense (b).
- *Classification System*, *Classification Version* — typed `prov:Plan` for consistency with *Classification Scheme*, which the source defines explicitly as "a method of organization".
- Definition provenance (previously `verbatim` / `adapted` / `original`) is no longer carried in the CSV now that `prov_class` holds the PROV-O type. It can be restored as a separate column on request.

## Editorial findings to review

1. **`FAO 2025`** is cited in the definition of *Physiographic Feature* (§7.1) but has no entry in the §10 References list. It now has a source row so the term's citation matches the manuscript, but the row's `title` and `description` say the reference is unresolved and its `url` is empty. **This must be filled in before publication.**
2. **`BFO 2020`** is cited in the definition of *Material Entity* (§3.1) but has no entry in §10. The source row keeps the manuscript's `BFO 2020` citation and points to ISO/IEC 21838-2:2021, the standard that specifies BFO 2020. A matching bibliography entry should be added to the manuscript.
3. **PROV-O** (`http://www.w3.org/ns/prov#Agent`, `#Activity`) and the **Dublin Core** identifier URI are cited as bare URIs in §3.1 and §2.1 with no bibliography entries. Both have source rows here, keyed by the URI the manuscript actually cites, with the gap stated in the row's `description`.
4. The supplied `glossaryconfigentry.jsonc` template pointed `"terms"` at `glossary-sources.csv`. Corrected to `glossary-terms.csv` in the generated config.
5. *Depth* (§4.1) is a very generic label for a shared glossary namespace; consider *Classification Depth* if collisions with other glossaries matter.
6. Two terms are defined twice in spirit — *Geochronologic Unit* (§6.1, authored) overlaps with *Chronostratigraphic Unit* (§5.1, ISSC). Both are retained as they appear in the manuscript.
7. *Mine* appears last in §7.1, out of the otherwise alphabetical ordering of that subsection. Term order in the CSV follows the manuscript exactly.

## Regenerating

`build_glossary.py` + `sources_registry.py` reproduce all four files from the `.docx`. The citation → source mapping lives in `CITMAP`, the source records in `sources_registry.py`.

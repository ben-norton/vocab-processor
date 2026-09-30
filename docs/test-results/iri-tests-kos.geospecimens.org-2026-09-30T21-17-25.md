# IRI Resolution Test Results

| | |
|---|---|
| Target | https://kos.geospecimens.org |
| Inventory | local build (`public/data/`) |
| Commit | `fd24b93` |
| Started | 2026-09-30T21:17:25.024Z |
| Duration | 26.3 s |
| Result | **FAIL** — 6292/6604 checks passed across 508 IRIs; 1 published resource(s) without a persistent IRI |

Each IRI is requested through the resolver with every `Accept` type the publisher negotiates, fetched as every static file extension, and its SPA route is loaded. A 200 response must carry the expected `Content-Type` and, for RDF/data formats and static files, mention the IRI in the body. HTML negotiation must 303 to the SPA route (glossaries serve the SPA inline, since their IRI path is the route). The client-side `?_format=` export runs only in the browser and is not tested here.

## Summary by KOS type

| KOS type | IRIs | IRIs fully passing | Checks | Passed | Failed |
|---|---:|---:|---:|---:|---:|
| vocabulary | 7 | 6 | 91 | 79 | 12 |
| vocabulary-concept | 96 | 79 | 1248 | 1044 | 204 |
| classification | 1 | 1 | 13 | 13 | 0 |
| classification-concept | 70 | 67 | 910 | 874 | 36 |
| classification-rank | 5 | 0 | 65 | 5 | 60 |
| glossary | 3 | 3 | 39 | 39 | 0 |
| glossary-term | 326 | 326 | 4238 | 4238 | 0 |
| **Total** | **508** | **482** | **6604** | **6292** | **312** |

## Content types by KOS type

Passed / tested for each representation.

| KOS type | Accept HTML | Accept Turtle | Accept JSON-LD | Accept RDF/XML | Accept JSON | Accept CSV | .html | .ttl | .jsonld | .rdf | .json | .csv | SPA route |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| vocabulary | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✗ 6/7 | ✓ 7 |
| vocabulary-concept | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✗ 79/96 | ✓ 96 |
| classification | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 | ✓ 1 |
| classification-concept | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✗ 67/70 | ✓ 70 |
| classification-rank | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✗ 0/5 | ✓ 5 |
| glossary | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 | ✓ 3 |
| glossary-term | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 | ✓ 326 |

## Registry coverage

These resources render in the SPA but have no persistent IRI (absent from `src/config/uris.json` / `resource-urls.json`), so they were not tested and their IRI will 404:

| KOS type | ID | IRI |
|---|---|---|
| vocabulary | `kos-meta` | https://kos.geospecimens.org/def/kos-meta |

## Failures

### vocabulary (12)

| IRI | Check | Request | Reason |
|---|---|---|---|
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:html | `/def/geological-material-assertion-type` | expected 303 → /vocab/geological-material-assertion-type, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:turtle | `/def/geological-material-assertion-type` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:json-ld | `/def/geological-material-assertion-type` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:rdf-xml | `/def/geological-material-assertion-type` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:json | `/def/geological-material-assertion-type` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | negotiate:csv | `/def/geological-material-assertion-type` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:html | `/def/geological-material-assertion-type.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:turtle | `/def/geological-material-assertion-type.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:json-ld | `/def/geological-material-assertion-type.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:rdf-xml | `/def/geological-material-assertion-type.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:json | `/def/geological-material-assertion-type.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type | static:csv | `/def/geological-material-assertion-type.csv` | expected 200 text/csv, got 404 |

### vocabulary-concept (204)

| IRI | Check | Request | Reason |
|---|---|---|---|
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:html | `/def/geological-material-assertion-type/aggregate-form` | expected 303 → /vocab/geological-material-assertion-type/concept/aggregate-form, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:turtle | `/def/geological-material-assertion-type/aggregate-form` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:json-ld | `/def/geological-material-assertion-type/aggregate-form` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:rdf-xml | `/def/geological-material-assertion-type/aggregate-form` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:json | `/def/geological-material-assertion-type/aggregate-form` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | negotiate:csv | `/def/geological-material-assertion-type/aggregate-form` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:html | `/def/geological-material-assertion-type/aggregate-form.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:turtle | `/def/geological-material-assertion-type/aggregate-form.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:json-ld | `/def/geological-material-assertion-type/aggregate-form.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:rdf-xml | `/def/geological-material-assertion-type/aggregate-form.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:json | `/def/geological-material-assertion-type/aggregate-form.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form | static:csv | `/def/geological-material-assertion-type/aggregate-form.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:html | `/def/geological-material-assertion-type/alteration-description` | expected 303 → /vocab/geological-material-assertion-type/concept/alteration-description, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:turtle | `/def/geological-material-assertion-type/alteration-description` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:json-ld | `/def/geological-material-assertion-type/alteration-description` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:rdf-xml | `/def/geological-material-assertion-type/alteration-description` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:json | `/def/geological-material-assertion-type/alteration-description` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | negotiate:csv | `/def/geological-material-assertion-type/alteration-description` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:html | `/def/geological-material-assertion-type/alteration-description.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:turtle | `/def/geological-material-assertion-type/alteration-description.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:json-ld | `/def/geological-material-assertion-type/alteration-description.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:rdf-xml | `/def/geological-material-assertion-type/alteration-description.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:json | `/def/geological-material-assertion-type/alteration-description.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description | static:csv | `/def/geological-material-assertion-type/alteration-description.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:html | `/def/geological-material-assertion-type/associated-minerals` | expected 303 → /vocab/geological-material-assertion-type/concept/associated-minerals, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:turtle | `/def/geological-material-assertion-type/associated-minerals` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:json-ld | `/def/geological-material-assertion-type/associated-minerals` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:rdf-xml | `/def/geological-material-assertion-type/associated-minerals` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:json | `/def/geological-material-assertion-type/associated-minerals` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | negotiate:csv | `/def/geological-material-assertion-type/associated-minerals` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:html | `/def/geological-material-assertion-type/associated-minerals.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:turtle | `/def/geological-material-assertion-type/associated-minerals.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:json-ld | `/def/geological-material-assertion-type/associated-minerals.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:rdf-xml | `/def/geological-material-assertion-type/associated-minerals.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:json | `/def/geological-material-assertion-type/associated-minerals.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals | static:csv | `/def/geological-material-assertion-type/associated-minerals.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:html | `/def/geological-material-assertion-type/cleavage` | expected 303 → /vocab/geological-material-assertion-type/concept/cleavage, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:turtle | `/def/geological-material-assertion-type/cleavage` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:json-ld | `/def/geological-material-assertion-type/cleavage` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:rdf-xml | `/def/geological-material-assertion-type/cleavage` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:json | `/def/geological-material-assertion-type/cleavage` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | negotiate:csv | `/def/geological-material-assertion-type/cleavage` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:html | `/def/geological-material-assertion-type/cleavage.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:turtle | `/def/geological-material-assertion-type/cleavage.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:json-ld | `/def/geological-material-assertion-type/cleavage.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:rdf-xml | `/def/geological-material-assertion-type/cleavage.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:json | `/def/geological-material-assertion-type/cleavage.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage | static:csv | `/def/geological-material-assertion-type/cleavage.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:html | `/def/geological-material-assertion-type/color` | expected 303 → /vocab/geological-material-assertion-type/concept/color, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:turtle | `/def/geological-material-assertion-type/color` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:json-ld | `/def/geological-material-assertion-type/color` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:rdf-xml | `/def/geological-material-assertion-type/color` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:json | `/def/geological-material-assertion-type/color` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | negotiate:csv | `/def/geological-material-assertion-type/color` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:html | `/def/geological-material-assertion-type/color.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:turtle | `/def/geological-material-assertion-type/color.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:json-ld | `/def/geological-material-assertion-type/color.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:rdf-xml | `/def/geological-material-assertion-type/color.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:json | `/def/geological-material-assertion-type/color.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/color | static:csv | `/def/geological-material-assertion-type/color.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:html | `/def/geological-material-assertion-type/crystal-form` | expected 303 → /vocab/geological-material-assertion-type/concept/crystal-form, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:turtle | `/def/geological-material-assertion-type/crystal-form` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:json-ld | `/def/geological-material-assertion-type/crystal-form` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:rdf-xml | `/def/geological-material-assertion-type/crystal-form` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:json | `/def/geological-material-assertion-type/crystal-form` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | negotiate:csv | `/def/geological-material-assertion-type/crystal-form` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:html | `/def/geological-material-assertion-type/crystal-form.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:turtle | `/def/geological-material-assertion-type/crystal-form.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:json-ld | `/def/geological-material-assertion-type/crystal-form.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:rdf-xml | `/def/geological-material-assertion-type/crystal-form.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:json | `/def/geological-material-assertion-type/crystal-form.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form | static:csv | `/def/geological-material-assertion-type/crystal-form.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:html | `/def/geological-material-assertion-type/crystal-habit` | expected 303 → /vocab/geological-material-assertion-type/concept/crystal-habit, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:turtle | `/def/geological-material-assertion-type/crystal-habit` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:json-ld | `/def/geological-material-assertion-type/crystal-habit` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:rdf-xml | `/def/geological-material-assertion-type/crystal-habit` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:json | `/def/geological-material-assertion-type/crystal-habit` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | negotiate:csv | `/def/geological-material-assertion-type/crystal-habit` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:html | `/def/geological-material-assertion-type/crystal-habit.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:turtle | `/def/geological-material-assertion-type/crystal-habit.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:json-ld | `/def/geological-material-assertion-type/crystal-habit.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:rdf-xml | `/def/geological-material-assertion-type/crystal-habit.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:json | `/def/geological-material-assertion-type/crystal-habit.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit | static:csv | `/def/geological-material-assertion-type/crystal-habit.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:html | `/def/geological-material-assertion-type/exsolution-texture` | expected 303 → /vocab/geological-material-assertion-type/concept/exsolution-texture, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:turtle | `/def/geological-material-assertion-type/exsolution-texture` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:json-ld | `/def/geological-material-assertion-type/exsolution-texture` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:rdf-xml | `/def/geological-material-assertion-type/exsolution-texture` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:json | `/def/geological-material-assertion-type/exsolution-texture` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | negotiate:csv | `/def/geological-material-assertion-type/exsolution-texture` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:html | `/def/geological-material-assertion-type/exsolution-texture.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:turtle | `/def/geological-material-assertion-type/exsolution-texture.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:json-ld | `/def/geological-material-assertion-type/exsolution-texture.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:rdf-xml | `/def/geological-material-assertion-type/exsolution-texture.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:json | `/def/geological-material-assertion-type/exsolution-texture.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture | static:csv | `/def/geological-material-assertion-type/exsolution-texture.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:html | `/def/geological-material-assertion-type/inclusions` | expected 303 → /vocab/geological-material-assertion-type/concept/inclusions, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:turtle | `/def/geological-material-assertion-type/inclusions` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:json-ld | `/def/geological-material-assertion-type/inclusions` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:rdf-xml | `/def/geological-material-assertion-type/inclusions` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:json | `/def/geological-material-assertion-type/inclusions` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | negotiate:csv | `/def/geological-material-assertion-type/inclusions` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:html | `/def/geological-material-assertion-type/inclusions.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:turtle | `/def/geological-material-assertion-type/inclusions.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:json-ld | `/def/geological-material-assertion-type/inclusions.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:rdf-xml | `/def/geological-material-assertion-type/inclusions.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:json | `/def/geological-material-assertion-type/inclusions.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions | static:csv | `/def/geological-material-assertion-type/inclusions.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:html | `/def/geological-material-assertion-type/luminescence-description` | expected 303 → /vocab/geological-material-assertion-type/concept/luminescence-description, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:turtle | `/def/geological-material-assertion-type/luminescence-description` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:json-ld | `/def/geological-material-assertion-type/luminescence-description` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:rdf-xml | `/def/geological-material-assertion-type/luminescence-description` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:json | `/def/geological-material-assertion-type/luminescence-description` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | negotiate:csv | `/def/geological-material-assertion-type/luminescence-description` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:html | `/def/geological-material-assertion-type/luminescence-description.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:turtle | `/def/geological-material-assertion-type/luminescence-description.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:json-ld | `/def/geological-material-assertion-type/luminescence-description.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:rdf-xml | `/def/geological-material-assertion-type/luminescence-description.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:json | `/def/geological-material-assertion-type/luminescence-description.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description | static:csv | `/def/geological-material-assertion-type/luminescence-description.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:html | `/def/geological-material-assertion-type/luster` | expected 303 → /vocab/geological-material-assertion-type/concept/luster, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:turtle | `/def/geological-material-assertion-type/luster` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:json-ld | `/def/geological-material-assertion-type/luster` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:rdf-xml | `/def/geological-material-assertion-type/luster` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:json | `/def/geological-material-assertion-type/luster` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | negotiate:csv | `/def/geological-material-assertion-type/luster` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:html | `/def/geological-material-assertion-type/luster.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:turtle | `/def/geological-material-assertion-type/luster.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:json-ld | `/def/geological-material-assertion-type/luster.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:rdf-xml | `/def/geological-material-assertion-type/luster.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:json | `/def/geological-material-assertion-type/luster.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/luster | static:csv | `/def/geological-material-assertion-type/luster.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:html | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 303 → /vocab/geological-material-assertion-type/concept/maximum-axial-dimension, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:turtle | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:json-ld | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:rdf-xml | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:json | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | negotiate:csv | `/def/geological-material-assertion-type/maximum-axial-dimension` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:html | `/def/geological-material-assertion-type/maximum-axial-dimension.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:turtle | `/def/geological-material-assertion-type/maximum-axial-dimension.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:json-ld | `/def/geological-material-assertion-type/maximum-axial-dimension.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:rdf-xml | `/def/geological-material-assertion-type/maximum-axial-dimension.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:json | `/def/geological-material-assertion-type/maximum-axial-dimension.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension | static:csv | `/def/geological-material-assertion-type/maximum-axial-dimension.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:html | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 303 → /vocab/geological-material-assertion-type/concept/measured-depth-in-millimeters, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:turtle | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:json-ld | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:rdf-xml | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:json | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | negotiate:csv | `/def/geological-material-assertion-type/measured-depth-in-millimeters` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:html | `/def/geological-material-assertion-type/measured-depth-in-millimeters.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:turtle | `/def/geological-material-assertion-type/measured-depth-in-millimeters.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:json-ld | `/def/geological-material-assertion-type/measured-depth-in-millimeters.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:rdf-xml | `/def/geological-material-assertion-type/measured-depth-in-millimeters.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:json | `/def/geological-material-assertion-type/measured-depth-in-millimeters.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters | static:csv | `/def/geological-material-assertion-type/measured-depth-in-millimeters.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:html | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 303 → /vocab/geological-material-assertion-type/concept/measured-height-in-millimeters, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:turtle | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:json-ld | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:rdf-xml | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:json | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | negotiate:csv | `/def/geological-material-assertion-type/measured-height-in-millimeters` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:html | `/def/geological-material-assertion-type/measured-height-in-millimeters.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:turtle | `/def/geological-material-assertion-type/measured-height-in-millimeters.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:json-ld | `/def/geological-material-assertion-type/measured-height-in-millimeters.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:rdf-xml | `/def/geological-material-assertion-type/measured-height-in-millimeters.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:json | `/def/geological-material-assertion-type/measured-height-in-millimeters.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters | static:csv | `/def/geological-material-assertion-type/measured-height-in-millimeters.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:html | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 303 → /vocab/geological-material-assertion-type/concept/measured-width-in-millimeters, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:turtle | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:json-ld | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:rdf-xml | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:json | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | negotiate:csv | `/def/geological-material-assertion-type/measured-width-in-millimeters` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:html | `/def/geological-material-assertion-type/measured-width-in-millimeters.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:turtle | `/def/geological-material-assertion-type/measured-width-in-millimeters.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:json-ld | `/def/geological-material-assertion-type/measured-width-in-millimeters.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:rdf-xml | `/def/geological-material-assertion-type/measured-width-in-millimeters.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:json | `/def/geological-material-assertion-type/measured-width-in-millimeters.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters | static:csv | `/def/geological-material-assertion-type/measured-width-in-millimeters.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:html | `/def/geological-material-assertion-type/twinning-law` | expected 303 → /vocab/geological-material-assertion-type/concept/twinning-law, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:turtle | `/def/geological-material-assertion-type/twinning-law` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:json-ld | `/def/geological-material-assertion-type/twinning-law` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:rdf-xml | `/def/geological-material-assertion-type/twinning-law` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:json | `/def/geological-material-assertion-type/twinning-law` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | negotiate:csv | `/def/geological-material-assertion-type/twinning-law` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:html | `/def/geological-material-assertion-type/twinning-law.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:turtle | `/def/geological-material-assertion-type/twinning-law.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:json-ld | `/def/geological-material-assertion-type/twinning-law.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:rdf-xml | `/def/geological-material-assertion-type/twinning-law.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:json | `/def/geological-material-assertion-type/twinning-law.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law | static:csv | `/def/geological-material-assertion-type/twinning-law.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:html | `/def/geological-material-assertion-type/verbatim-size` | expected 303 → /vocab/geological-material-assertion-type/concept/verbatim-size, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:turtle | `/def/geological-material-assertion-type/verbatim-size` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:json-ld | `/def/geological-material-assertion-type/verbatim-size` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:rdf-xml | `/def/geological-material-assertion-type/verbatim-size` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:json | `/def/geological-material-assertion-type/verbatim-size` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | negotiate:csv | `/def/geological-material-assertion-type/verbatim-size` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:html | `/def/geological-material-assertion-type/verbatim-size.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:turtle | `/def/geological-material-assertion-type/verbatim-size.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:json-ld | `/def/geological-material-assertion-type/verbatim-size.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:rdf-xml | `/def/geological-material-assertion-type/verbatim-size.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:json | `/def/geological-material-assertion-type/verbatim-size.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size | static:csv | `/def/geological-material-assertion-type/verbatim-size.csv` | expected 200 text/csv, got 404 |

### classification-concept (36)

| IRI | Check | Request | Reason |
|---|---|---|---|
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:html | `/def/meteorite-classification/mesosiderite` | expected 303 → /vocab/meteorite-classification/concept/mesosiderite, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:turtle | `/def/meteorite-classification/mesosiderite` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:json-ld | `/def/meteorite-classification/mesosiderite` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:rdf-xml | `/def/meteorite-classification/mesosiderite` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:json | `/def/meteorite-classification/mesosiderite` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | negotiate:csv | `/def/meteorite-classification/mesosiderite` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:html | `/def/meteorite-classification/mesosiderite.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:turtle | `/def/meteorite-classification/mesosiderite.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:json-ld | `/def/meteorite-classification/mesosiderite.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:rdf-xml | `/def/meteorite-classification/mesosiderite.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:json | `/def/meteorite-classification/mesosiderite.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/mesosiderite | static:csv | `/def/meteorite-classification/mesosiderite.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:html | `/def/meteorite-classification/orthopyroxenite` | expected 303 → /vocab/meteorite-classification/concept/orthopyroxenite, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:turtle | `/def/meteorite-classification/orthopyroxenite` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:json-ld | `/def/meteorite-classification/orthopyroxenite` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:rdf-xml | `/def/meteorite-classification/orthopyroxenite` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:json | `/def/meteorite-classification/orthopyroxenite` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | negotiate:csv | `/def/meteorite-classification/orthopyroxenite` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:html | `/def/meteorite-classification/orthopyroxenite.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:turtle | `/def/meteorite-classification/orthopyroxenite.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:json-ld | `/def/meteorite-classification/orthopyroxenite.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:rdf-xml | `/def/meteorite-classification/orthopyroxenite.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:json | `/def/meteorite-classification/orthopyroxenite.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite | static:csv | `/def/meteorite-classification/orthopyroxenite.csv` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:html | `/def/meteorite-classification/pallasites` | expected 303 → /vocab/meteorite-classification/concept/pallasites, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:turtle | `/def/meteorite-classification/pallasites` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:json-ld | `/def/meteorite-classification/pallasites` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:rdf-xml | `/def/meteorite-classification/pallasites` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:json | `/def/meteorite-classification/pallasites` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | negotiate:csv | `/def/meteorite-classification/pallasites` | expected 200 text/csv, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:html | `/def/meteorite-classification/pallasites.html` | expected 200 text/html, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:turtle | `/def/meteorite-classification/pallasites.ttl` | expected 200 text/turtle, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:json-ld | `/def/meteorite-classification/pallasites.jsonld` | expected 200 application/ld+json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:rdf-xml | `/def/meteorite-classification/pallasites.rdf` | expected 200 application/rdf+xml, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:json | `/def/meteorite-classification/pallasites.json` | expected 200 application/json, got 404 |
| https://kos.geospecimens.org/def/meteorite-classification/pallasites | static:csv | `/def/meteorite-classification/pallasites.csv` | expected 200 text/csv, got 404 |

### classification-rank (60)

| IRI | Check | Request | Reason |
|---|---|---|---|
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:html | `/def/meteorite-classification/rank/division` | expected 303 → /vocab/meteorite-classification, got 200 |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:turtle | `/def/meteorite-classification/rank/division` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:json-ld | `/def/meteorite-classification/rank/division` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:rdf-xml | `/def/meteorite-classification/rank/division` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:json | `/def/meteorite-classification/rank/division` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | negotiate:csv | `/def/meteorite-classification/rank/division` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:html | `/def/meteorite-classification/rank/division.html` | body does not mention the IRI |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:turtle | `/def/meteorite-classification/rank/division.ttl` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:json-ld | `/def/meteorite-classification/rank/division.jsonld` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:rdf-xml | `/def/meteorite-classification/rank/division.rdf` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:json | `/def/meteorite-classification/rank/division.json` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/division | static:csv | `/def/meteorite-classification/rank/division.csv` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:html | `/def/meteorite-classification/rank/class` | expected 303 → /vocab/meteorite-classification, got 200 |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:turtle | `/def/meteorite-classification/rank/class` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:json-ld | `/def/meteorite-classification/rank/class` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:rdf-xml | `/def/meteorite-classification/rank/class` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:json | `/def/meteorite-classification/rank/class` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | negotiate:csv | `/def/meteorite-classification/rank/class` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:html | `/def/meteorite-classification/rank/class.html` | body does not mention the IRI |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:turtle | `/def/meteorite-classification/rank/class.ttl` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:json-ld | `/def/meteorite-classification/rank/class.jsonld` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:rdf-xml | `/def/meteorite-classification/rank/class.rdf` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:json | `/def/meteorite-classification/rank/class.json` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/class | static:csv | `/def/meteorite-classification/rank/class.csv` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:html | `/def/meteorite-classification/rank/clan` | expected 303 → /vocab/meteorite-classification, got 200 |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:turtle | `/def/meteorite-classification/rank/clan` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:json-ld | `/def/meteorite-classification/rank/clan` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:rdf-xml | `/def/meteorite-classification/rank/clan` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:json | `/def/meteorite-classification/rank/clan` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | negotiate:csv | `/def/meteorite-classification/rank/clan` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:html | `/def/meteorite-classification/rank/clan.html` | body does not mention the IRI |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:turtle | `/def/meteorite-classification/rank/clan.ttl` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:json-ld | `/def/meteorite-classification/rank/clan.jsonld` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:rdf-xml | `/def/meteorite-classification/rank/clan.rdf` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:json | `/def/meteorite-classification/rank/clan.json` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/clan | static:csv | `/def/meteorite-classification/rank/clan.csv` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:html | `/def/meteorite-classification/rank/group` | expected 303 → /vocab/meteorite-classification, got 200 |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:turtle | `/def/meteorite-classification/rank/group` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:json-ld | `/def/meteorite-classification/rank/group` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:rdf-xml | `/def/meteorite-classification/rank/group` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:json | `/def/meteorite-classification/rank/group` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | negotiate:csv | `/def/meteorite-classification/rank/group` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:html | `/def/meteorite-classification/rank/group.html` | body does not mention the IRI |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:turtle | `/def/meteorite-classification/rank/group.ttl` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:json-ld | `/def/meteorite-classification/rank/group.jsonld` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:rdf-xml | `/def/meteorite-classification/rank/group.rdf` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:json | `/def/meteorite-classification/rank/group.json` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/group | static:csv | `/def/meteorite-classification/rank/group.csv` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:html | `/def/meteorite-classification/rank/subgroup` | expected 303 → /vocab/meteorite-classification, got 200 |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:turtle | `/def/meteorite-classification/rank/subgroup` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:json-ld | `/def/meteorite-classification/rank/subgroup` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:rdf-xml | `/def/meteorite-classification/rank/subgroup` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:json | `/def/meteorite-classification/rank/subgroup` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | negotiate:csv | `/def/meteorite-classification/rank/subgroup` | expected Content-Type text/csv, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:html | `/def/meteorite-classification/rank/subgroup.html` | body does not mention the IRI |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:turtle | `/def/meteorite-classification/rank/subgroup.ttl` | expected Content-Type text/turtle, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:json-ld | `/def/meteorite-classification/rank/subgroup.jsonld` | expected Content-Type application/ld+json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:rdf-xml | `/def/meteorite-classification/rank/subgroup.rdf` | expected Content-Type application/rdf+xml, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:json | `/def/meteorite-classification/rank/subgroup.json` | expected Content-Type application/json, got text/html |
| https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup | static:csv | `/def/meteorite-classification/rank/subgroup.csv` | expected Content-Type text/csv, got text/html |

## IRIs tested

Full per-request results are in the accompanying `.json` file.

<details><summary>vocabulary — 7 IRIs</summary>

- ✓ https://kos.geospecimens.org/def/aggregate-form — Aggregate Form
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion — Constituent Part Proportion
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type — Geological Material Assertion Types
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category — Geological Specimen Material Category
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type — Geological Specimen Name Type
- ✓ https://kos.geospecimens.org/def/hazard-type — Hazard Types
- ✓ https://kos.geospecimens.org/def/luster — Luster

</details>

<details><summary>vocabulary-concept — 96 IRIs</summary>

- ✓ https://kos.geospecimens.org/def/aggregate-form/acicular — Acicular
- ✓ https://kos.geospecimens.org/def/aggregate-form/acicular-parallel — Acicular Parallel
- ✓ https://kos.geospecimens.org/def/aggregate-form/acicular-radial — Acicular Radial
- ✓ https://kos.geospecimens.org/def/aggregate-form/acicular-random — Acicular Random
- ✓ https://kos.geospecimens.org/def/aggregate-form/banded — Banded
- ✓ https://kos.geospecimens.org/def/aggregate-form/botryoidal — Botryoidal
- ✓ https://kos.geospecimens.org/def/aggregate-form/columnar — Columnar
- ✓ https://kos.geospecimens.org/def/aggregate-form/concentric — Concentric
- ✓ https://kos.geospecimens.org/def/aggregate-form/coxcomb — Coxcomb
- ✓ https://kos.geospecimens.org/def/aggregate-form/dendritic — Dendritic
- ✓ https://kos.geospecimens.org/def/aggregate-form/druse — Druse
- ✓ https://kos.geospecimens.org/def/aggregate-form/fibrous — Fibrous
- ✓ https://kos.geospecimens.org/def/aggregate-form/fibrous-parallel — Fibrous, Parallel
- ✓ https://kos.geospecimens.org/def/aggregate-form/fibrous-random — Fibrous, Random
- ✓ https://kos.geospecimens.org/def/aggregate-form/foliated-lamellar — Foliated, Lamellar
- ✓ https://kos.geospecimens.org/def/aggregate-form/geode — Geode
- ✓ https://kos.geospecimens.org/def/aggregate-form/granular — Granular
- ✓ https://kos.geospecimens.org/def/aggregate-form/mammillary — Mammillary
- ✓ https://kos.geospecimens.org/def/aggregate-form/massive — Massive
- ✓ https://kos.geospecimens.org/def/aggregate-form/micaceous — Micaceous
- ✓ https://kos.geospecimens.org/def/aggregate-form/oolitic — Oolitic
- ✓ https://kos.geospecimens.org/def/aggregate-form/pisolitic — Pisolitic
- ✓ https://kos.geospecimens.org/def/aggregate-form/radiating — Radiating
- ✓ https://kos.geospecimens.org/def/aggregate-form/reniform — Reniform
- ✓ https://kos.geospecimens.org/def/aggregate-form/stalactitic — Stalactitic
- ✓ https://kos.geospecimens.org/def/aggregate-form/wheat-sheaf — Wheat Sheaf
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/absent — Absent
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/all — All
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/major — Major
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/minor — Minor
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/present — Present
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/rare — Rare
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/trace — Trace
- ✓ https://kos.geospecimens.org/def/constituent-part-proportion/variable — Variable
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/aggregate-form — Aggregate Form
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/alteration-description — Alteration Description
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/associated-minerals — Associated Minerals
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/cleavage — Cleavage
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/color — Color
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-form — Crystal Form
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/crystal-habit — Crystal Habit
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/exsolution-texture — Exsolution Texture
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/inclusions — Inclusions
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/luminescence-description — Luminescence Description
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/luster — Luster
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/maximum-axial-dimension — Maximum Axial Dimension
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/measured-depth-in-millimeters — Measured Depth in Millimeters
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/measured-height-in-millimeters — Measured Height in Millimeters
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/measured-width-in-millimeters — Measured Width in Millimeters
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/twinning-law — Twinning Law
- ✗ https://kos.geospecimens.org/def/geological-material-assertion-type/verbatim-size — Verbatim Size
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/astromaterial — Astromaterial
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/fossil — Fossil
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/gemstone — Gemstone
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/geological-material — Geological Material
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/meteorite — Meteorite
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/mineral — Mineral
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/ore — Ore
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/rock — Rock
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/rock-core — Rock Core
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/sample-return — Sample Return
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/synthetic-mineral — Synthetic Mineral
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/trace-fossil — Trace Fossil
- ✓ https://kos.geospecimens.org/def/geological-specimen-material-category/unconsolidated-material — Unconsolidated Material
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/alternate-name — Alternate Name
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/cataloged-name — Cataloged Name
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/classification — Classification
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/formal-name — Formal Name
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/geological-material-name — Geological Material Name
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/group — Group
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/historical — Historical
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/ima-approved-name — IMA Approved Name
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/obsolete — Obsolete
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/series — Series
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/structural-group — Structural Group
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/synonym — Synonym
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/unapproved — Unapproved
- ✓ https://kos.geospecimens.org/def/geological-specimen-name-type/variety — Variety
- ✓ https://kos.geospecimens.org/def/hazard-type/carcinogen — Carcinogen
- ✓ https://kos.geospecimens.org/def/hazard-type/corrosive — Corrosive
- ✓ https://kos.geospecimens.org/def/hazard-type/explosive — Explosive
- ✓ https://kos.geospecimens.org/def/hazard-type/flammable — Flammable
- ✓ https://kos.geospecimens.org/def/hazard-type/radioactive — Radioactive
- ✓ https://kos.geospecimens.org/def/hazard-type/toxic — Toxic
- ✓ https://kos.geospecimens.org/def/luster/adamantine — Adamantine
- ✓ https://kos.geospecimens.org/def/luster/dull — Dull
- ✓ https://kos.geospecimens.org/def/luster/greasy — Greasy
- ✓ https://kos.geospecimens.org/def/luster/metallic — Metallic
- ✓ https://kos.geospecimens.org/def/luster/pearly — Pearly
- ✓ https://kos.geospecimens.org/def/luster/resinous — Resinous
- ✓ https://kos.geospecimens.org/def/luster/silky — Silky
- ✓ https://kos.geospecimens.org/def/luster/smoky — Smoky
- ✓ https://kos.geospecimens.org/def/luster/submetallic — Submetallic
- ✓ https://kos.geospecimens.org/def/luster/translucent — Translucent
- ✓ https://kos.geospecimens.org/def/luster/vitreous — Vitreous
- ✓ https://kos.geospecimens.org/def/luster/waxy — Waxy

</details>

<details><summary>classification — 1 IRIs</summary>

- ✓ https://kos.geospecimens.org/def/meteorite-classification — Meteorite Classification (Weisberg, McCoy & Krot 2006)

</details>

<details><summary>classification-concept — 70 IRIs</summary>

- ✓ https://kos.geospecimens.org/def/meteorite-classification/acapulcoite — Acapulcoite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/acapulcoite-lodranite-clan — Acapulcoite-Lodranite clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/achondrites — Achondrites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/angrite — Angrite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/aubrite — Aubrite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/brachinite — Brachinite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/carbonaceous-chondrites — Carbonaceous chondrites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cb-bencubbin-type — CB (Bencubbin-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cb-subgroup-a — CB subgroup a
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cb-subgroup-b — CB subgroup b
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ch-high-metal — CH (high-metal)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/chassignite — Chassignite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/chondrites — Chondrites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ci-clan — CI clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ci-ivuna-type — CI (Ivuna-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ck-karoonda-type — CK (Karoonda-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cm-co-clan — CM-CO clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cm-mighei-type — CM (Mighei-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/co-ornans-type — CO (Ornans-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cr-clan — CR clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cr-renazzo-type — CR (Renazzo-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cv-ck-clan — CV-CK clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cv-subgroup-a-oxidized-allende-like — CV subgroup A (oxidized, Allende-like)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cv-subgroup-b-oxidized-bali-like — CV subgroup B (oxidized, Bali-like)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cv-subgroup-reduced — CV subgroup (reduced)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/cv-vigarano-type — CV (Vigarano-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/diogenite — Diogenite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/eagle-station-pallasite — Eagle Station pallasite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/eh-el-clan — EH-EL clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/eh-high-iron — EH (high iron)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/el-low-iron — EL (low iron)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/enstatite-chondrites — Enstatite chondrites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/eucrite — Eucrite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/h-high-iron — H (high iron)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/h-l-ll-clan — H-L-LL clan
- ✓ https://kos.geospecimens.org/def/meteorite-classification/hed-clan-vesta — HED clan (Vesta)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/howardite — Howardite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iab-iron-silicate-bearing — IAB iron (silicate-bearing)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ic-iron-group — IC iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iiab-iron-group — IIAB iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iic-iron-group — IIC iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iid-iron-group — IID iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iie-iron-group — IIE iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iiiab-iron-group — IIIAB iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iiicd-iron-silicate-bearing — IIICD iron (silicate-bearing)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iiie-iron-group — IIIE iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iiif-iron-group — IIIF iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/irons — Irons
- ✓ https://kos.geospecimens.org/def/meteorite-classification/iva-iron-group — IVA iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ivb-iron-group — IVB iron group
- ✓ https://kos.geospecimens.org/def/meteorite-classification/k-kakangari-type — K (Kakangari-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/l-low-iron — L (low iron)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ll-low-iron-low-metal — LL (low iron, low metal)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/lodranite — Lodranite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/lunar-moon — Lunar (Moon)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/main-group-pallasite — Main-group pallasite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/martian-snc — Martian (SNC)
- ✗ https://kos.geospecimens.org/def/meteorite-classification/mesosiderite — Mesosiderite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/meteorites — Meteorites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/nakhlite — Nakhlite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ordinary-chondrites — Ordinary chondrites
- ✗ https://kos.geospecimens.org/def/meteorite-classification/orthopyroxenite — Orthopyroxenite
- ✗ https://kos.geospecimens.org/def/meteorite-classification/pallasites — Pallasites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/primitive-achondrites — Primitive achondrites
- ✓ https://kos.geospecimens.org/def/meteorite-classification/pyroxene-pallasite — Pyroxene pallasite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/r-rumuruti-type — R (Rumuruti-type)
- ✓ https://kos.geospecimens.org/def/meteorite-classification/shergottite — Shergottite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/ureilite — Ureilite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/winonaite — Winonaite
- ✓ https://kos.geospecimens.org/def/meteorite-classification/winonaite-iab-iiicd-clan — Winonaite-IAB-IIICD clan

</details>

<details><summary>classification-rank — 5 IRIs</summary>

- ✗ https://kos.geospecimens.org/def/meteorite-classification/rank/division — division
- ✗ https://kos.geospecimens.org/def/meteorite-classification/rank/class — class
- ✗ https://kos.geospecimens.org/def/meteorite-classification/rank/clan — clan
- ✗ https://kos.geospecimens.org/def/meteorite-classification/rank/group — group
- ✗ https://kos.geospecimens.org/def/meteorite-classification/rank/subgroup — subgroup

</details>

<details><summary>glossary — 3 IRIs</summary>

- ✓ https://kos.geospecimens.org/glossary/collections-digitization — Collections Digitization Glossary
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary — Geological Collections Glossary
- ✓ https://kos.geospecimens.org/glossary/kos-terms — KOS Terminology Glossary

</details>

<details><summary>glossary-term — 326 IRIs</summary>

- ✓ https://kos.geospecimens.org/glossary/collections-digitization/accession-assessment — Accession Assessment
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/accessioning — Accessioning
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/acquisition — Acquisition
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/action — Action
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/action-specification — Action Specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/activity — Activity
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/agent — Agent
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/anthropology — Anthropology
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/archaeological-material — Archaeological material
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/archaeology — Archaeology
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/ark — Archival Resource Key
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/asset — Asset
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/astromaterial — Astromaterial
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/astromaterial-collection — Astromaterial Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/barcode — Barcode
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/bioinformatics-pipeline — Bioinformatics Pipeline
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/biological-collection — Biological Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/biological-material — Biological Material
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/biological-object — Biological Object
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/biology — Biology
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/catalog-record — Catalog Record
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/collection — Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/collection-management — Collection Management
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/collection-management-system — Collection Management System
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/collection-object — Collection Object
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/collection-workflow — Collection Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/concept-harmonization — Concept Harmonization
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/conservator — Conservator
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/contributor — Contributor
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/crystallography — Crystallography
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/cultural-heritage — Cultural Heritage
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/cultural-studies — Cultural Studies
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/curated-holding — Curated Holding
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/curator — Curator
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-curation-and-archival — Data Archiving
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-capture — Data Capture
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-cleaning — Data Cleaning
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-collector — Data Collector
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-curation — Data Curation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-curation-workflow — Data Curation Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-curator — Data Curator
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-entry — Data Entry
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-governance — Data Governance
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-integration — Data Integration
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-lifecycle — Data Lifecycle
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-management-plan — Data Management Plan
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-manager — Data Manager
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-migration — Data Migration
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-mobility — Data Mobility
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/pipeline — Data Pipeline
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-policy — Data Policy
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-preparation — Data Preparation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-product — Data Product
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-product-specification — Data Product Specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-profiling — Data Profiling
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-provider — Data Provider
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-publication-workflow — Data Publication Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-publishing — Data Publishing
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-quality — Data Quality
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-steward — Data Steward
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-transformation — Data Transformation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/data-validation — Data Validation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/dataset — Dataset
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/deaccession — Deaccession
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/derivation — Derivation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/determination — Determination
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/digital-collections — Digital Collections
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/doi — Digital Object Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/digitization — Digitization
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/backlog — Digitization Backlog
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/distribution — Distribution
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/distribution-phase — Distribution Phase
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/entity — Entity
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/environmental-science — Environmental Science
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/event — Event
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/event-type — Event Type
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/extract-transform-load — Extract Transform Load
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/fair-principles — FAIR Principles
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/feature-of-interest — Feature of Interest
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/field — Field
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/field-work — Field Work
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/format-transformation — Format Transformation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/fossil — Fossil
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/functional-specification — Functional Specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/generated — Generated
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/geological-collection — Geological Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/geological-material — Geological Material
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/geologic-specimen — Geological Specimen
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/geology — Geology
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/glossary — Glossary
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/identifier — Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/identifier-assignment — Identifier assignment
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/initiator — Initiator
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/igsn — International Generic Sample Number
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/iri — Internationalized Resource Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/iterative-workflow — Iterative Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/kind-of — Kind (of)
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/library — Library
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/lsid — Life Science Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/loan — Loan
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/local-identifier — Local Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/man-made-object — Man-made Object
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/material-entity — Material Entity
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/material-sample — Material Sample
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/metadata — Metadata
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/mobilization — Mobilization
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/module — Module
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/museum — Museum
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/museum-collection — Museum Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/natural-sciences — Natural Sciences
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/online-collection — Online Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/orcid — Open Researcher and Contributor ID
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/organization — Organization
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/paleontology — Paleontology
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/paleontology-collection — Paleontology Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/parallel-workflow — Parallel Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/pid — Persistent Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/physical-collection — Physical Collection
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/physical-object — Physical Object
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/plan — Plan
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/plan-specification — Plan specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/planned-process — Planned process
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/preparation — Preparation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/preparation-object — Preparation Object
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/preparator — Preparator
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/preservation — Preservation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/primary-source — Primary Source
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/procedure — Procedure
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/procedure-specification — Procedure Specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/process — Process
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/process-protocol — Process Protocol
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/project — Project
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/project-phase — Project Phase
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/property — Property
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/provenance — Provenance
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/provenance-statement — Provenance Statement
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/quantity-kind — Quantity Kind
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/registrar — Registrar
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/repository — Repository
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/requirements — Requirements
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/research-data-publication-workflow — Research Data Publication Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/ror-id — Research Organization Registry Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/role — Role
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/sample — Sample
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/sample-collection-data-entry — Sample Collection Data Entry
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/semantic-interoperability — Semantic Interoperability
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/serial-workflow — Serial Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/social-sciences — Social Sciences
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/source-data-verification — Source Data Verification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/space-science — Space Science
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/specialized-material-entity — Specialized Material Entity
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/specification — Specification
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/specimen — Specimen
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/step — Step
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/subprocess — Subprocess
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/task — Task
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/handle — The Handle system
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/tool — Tool
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/transaction — Transaction
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/transaction-identifier — Transaction Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/trigger — Trigger
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/uri — Uniform Resource Identifier
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/urn — Universal Resource Name
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/uuid — Universally Unique Identifier (Version 4)
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/validation — Validation
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/value — Value
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/voucher-specimen — Voucher specimen
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow — Workflow
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-action — Workflow Action
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-branch — Workflow Branch
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-event — Workflow Event
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-management-system — Workflow Management System
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-phase — Workflow Phase
- ✓ https://kos.geospecimens.org/glossary/collections-digitization/workflow-tool — Workflow Tool
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/activity — Activity
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/agent — Agent
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/alternate-name — Alternate Name
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/authoritative-name — Authoritative Name
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/authority — Authority
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/biostratigraphic-unit — Biostratigraphic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/chronometric-age — Chronometric Age
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/chronostratigraphic-unit — Chronostratigraphic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification — Classification
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-code — Classification Code
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-family — Classification Family
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-item — Classification Item
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-item-relation — Classification Item Relation
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-level — Classification Level
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-name — Classification Name
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-rank — Classification Rank
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-rank-relation — Classification Rank Relation
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-scheme — Classification Scheme
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-series — Classification Series
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-system — Classification System
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-term — Classification Term
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/classification-version — Classification Version
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/collection-object — Collection Object
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/compound-specimen — Compound Specimen
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/compound-specimen-model — Compound Specimen Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/concept — Concept
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/conceptual-model — Conceptual Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/confirmation-protocol — Confirmation Protocol
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/data-model — Data Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/depth — Depth
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/determination — Determination
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/division — Division (Minerals)
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/feature — Feature
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/feature-of-interest — Feature of Interest
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronologic-boundary — Geochronologic Boundary
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronologic-era — Geochronologic Era
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronologic-interpretation — Geochronologic Interpretation
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronologic-rank — Geochronologic Rank
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronologic-unit — Geochronologic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geochronology — Geochronology
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-environment — Geologic Environment
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-event — Geologic Event
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-event-environment — Geologic Event Environment
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-feature — Geologic Feature
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-material — Geologic Material
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-process — Geologic Process
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-specimen — Geologic Specimen
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-timescale — Geologic Timescale
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-unit — Geologic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/geologic-unit-type — Geologic Unit Type
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/group — Group (Minerals)
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/hierarchy — Hierarchy
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/identification — Identification
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/identifier — Identifier
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/law-of-superposition — Law of Superposition
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/linnaean-taxonomy — Linnaean Taxonomy
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/lithodemic-unit — Lithodemic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/lithology — Lithology
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/lithostratigraphic-unit — Lithostratigraphic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/logical-data-model — Logical Data Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/lower-temporal-boundary — Lower Temporal Boundary
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/magnetostratigraphic-unit — Magnetostratigraphic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/material-category — Material Category
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/material-entity — Material Entity
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/material-sample — Material Sample
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/mine — Mine
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/model — Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/monohierarchy — Monohierarchy
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/name — Name
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/name-type — Name Type
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/naming-authority — Naming Authority
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/nomenclature-status — Nomenclature Status
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/object — Object
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/ontology — Ontology
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/petrographic-province — Petrographic Province
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/physical-data-model — Physical Data Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/physiographic-feature — Physiographic Feature
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/physiographic-province — Physiographic Province
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/province — Province
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/quarry — Quarry
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/radioactive-decay — Radioactive Decay
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/radiometric-age — Radiometric Age
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/radiometric-dating — Radiometric Dating
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/regional-timescale — Regional Timescale
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/relation-predicate — Relation Predicate
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/relative-age — Relative Age
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/relative-dating — Relative Dating
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/sample — Sample
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/sampling-event — Sampling Event
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/sampling-feature — Sampling Feature
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/sampling-feature-type — Sampling Feature Type
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/sampling-location — Sampling Location
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/simple-specimen — Simple Specimen
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/simple-specimen-model — Simple Specimen Model
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/species — Species (Minerals)
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/specimen-name — Specimen Name
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/specimen-part — Specimen Part
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/specimen-part-proportion — Specimen Part Proportion
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/specimen-part-relation — Specimen Part Relation
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/specimen-part-role — Specimen Part Role
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/stratigraphy — Stratigraphy
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/structural-group — Structural Group
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/tectonic-province — Tectonic Province
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/tectonic-setting — Tectonic Setting
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/tectonostratigraphic-unit — Tectonostratigraphic Unit
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/terrane — Terrane
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/time-interval — Time Interval
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/type — Type (Minerals)
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/upper-temporal-boundary — Upper Temporal Boundary
- ✓ https://kos.geospecimens.org/glossary/geological-collections-glossary/value-set — Value Set
- ✓ https://kos.geospecimens.org/glossary/kos-terms/authority-file — Authority File
- ✓ https://kos.geospecimens.org/glossary/kos-terms/authority-list — Authority List
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-obolibrary-org-obo-omrse-00000262 — Categorization Scheme
- ✓ https://kos.geospecimens.org/glossary/kos-terms/category — Category
- ✓ https://kos.geospecimens.org/glossary/kos-terms/classification-scheme — Classification Scheme
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-obolibrary-org-obo-ncit-c41080 — Classification Scheme Item
- ✓ https://kos.geospecimens.org/glossary/kos-terms/classification-system — Classification System
- ✓ https://kos.geospecimens.org/glossary/kos-terms/codelist — Codelist
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-controlledvocabulary — Controlled Vocabulary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/https-w3id-org-iddo-dictionary — Data Dictionary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-obolibrary-org-obo-ncit-c41087 — Data Element Concept
- ✓ https://kos.geospecimens.org/glossary/kos-terms/data-interchange-standard — Data Interchange Standard
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-ncicb-nci-nih-gov-xml-owl-evs-thesaurus-owl-c103180 — Data Standard
- ✓ https://kos.geospecimens.org/glossary/kos-terms/dataset — Dataset
- ✓ https://kos.geospecimens.org/glossary/kos-terms/datatype — Datatype
- ✓ https://kos.geospecimens.org/glossary/kos-terms/https-schema-org-definedtermset — Defined Term Set
- ✓ https://kos.geospecimens.org/glossary/kos-terms/deliverable — Deliverable
- ✓ https://kos.geospecimens.org/glossary/kos-terms/described-value-domain — Described Value Domain
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-disciplinedictionary — Discipline Dictionary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/enumerated-value-domain — Enumerated Value Domain
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-obolibrary-org-obo-ncit-c18232 — Glossary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/https-aristotle-cloud-help-concepts-aristotle-glossary-glossaryitem — Glossary Item
- ✓ https://kos.geospecimens.org/glossary/kos-terms/hierarchical-relationship — Hierarchical Relationship
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-coar-resource-type-gsza-y7v7 — Knowledge Organization System
- ✓ https://kos.geospecimens.org/glossary/kos-terms/list — List
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-metadata — Metadata
- ✓ https://kos.geospecimens.org/glossary/kos-terms/metadata-standard — Metadata Standard
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-minimalinformationstandard — Minimum Information Standard
- ✓ https://kos.geospecimens.org/glossary/kos-terms/narrower-term — Narrower Term
- ✓ https://kos.geospecimens.org/glossary/kos-terms/ontology — Ontology
- ✓ https://kos.geospecimens.org/glossary/kos-terms/permissible-value — Permissible Value
- ✓ https://kos.geospecimens.org/glossary/kos-terms/pick-list — Pick List
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-ontology-bibo-standard — Standard
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-taxonomy — Taxonomy
- ✓ https://kos.geospecimens.org/glossary/kos-terms/terminological-dictionary — Terminological Dictionary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/thesaurus — Thesaurus
- ✓ https://kos.geospecimens.org/glossary/kos-terms/tree-structure — Tree Structure
- ✓ https://kos.geospecimens.org/glossary/kos-terms/type-vocabulary — Type Vocabulary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/uncontrolled-vocabulary — Uncontrolled Vocabulary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/value-domain — Value Domain
- ✓ https://kos.geospecimens.org/glossary/kos-terms/http-purl-org-spar-fabio-vocabulary — Vocabulary
- ✓ https://kos.geospecimens.org/glossary/kos-terms/vocabulary-mapping — Vocabulary Mapping

</details>

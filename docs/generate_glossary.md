# Generate Glossary RDF
Project: vocab-processor
Created: 2026-07-12

To generate the glossary RDF, run the following commands: 
$ python src/build_glossary_json.py collections-digitization 
> Generates data/glossaries/<slug>/glossary.json

$ python src/build_glossary_ttl.py collections-digitization
> Generates data/glossaries/<slug>/<slug>.ttl


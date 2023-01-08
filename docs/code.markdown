---
layout: page
title: Code
permalink: /code/
---
## Body Parts Data File

The index is contained in a JSON file available at the link below. The JSON validates against a schema specified in JSON Schema format, also linked below. The structure of the file is illustrated in the figure below.

- [body_parts.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json)—currently at release 1.0.0-rc.1
- [body_parts_schema.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts_schema.json)
- [CHANGELOG.md](https://github.com/talkasab/anatomiclocations.org/blob/main/data/CHANGELOG.md)

![Body parts data file JSON structure](/assets/JSONStructure.png "Body parts data file JSON structure")

* **RadLex ID** identifier
* **Description and synonyms** (from RadLex ontology)
* **“contained by” hierarchy**: physicially contained in <br> _(e.g., kidney in the retroperitoneum)_
* **“part of” hierarchy**: a component of a larger structure/system <br> _(e.g., adnexa part of femal genital system)_
* **Left/right/unsided** triads
* **Sex-phenotype specificity** when applicable
* Links to **SNOMED**, UMLS, FMA

## Utility Libraries

The index can be easily included in your projects by using one of the open-source TypeScript or Python libraries:

- **TypeScript**: [Github](https://github.com/talkasab/BodyPartIndex.ts) [NPM](https://www.npmjs.com/package/@talkasab/body_part_index)
- **Python**: [Github](https://github.com/talkasab/BodyPartIndex.py)
---
layout: page
title: Code
permalink: /code/
---
## Body Parts Data File

The Anatomic Locations Index (ALI) is a single JSON file that validates against a schema in JSON Schema format. Release 1.0.0 has 2,899 entries.

- [body_parts.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json), release 1.0.0
- [body_parts_schema.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts_schema.json)
- [CHANGELOG.md](https://github.com/talkasab/anatomiclocations.org/blob/main/data/CHANGELOG.md), which lists the changes in each release

The following figure shows every field of one entry, the uterine adnexa:

![JSON node structure showing all fields for a representative Anatomic Locations Index entry (uterine adnexa)](/assets/JSONStructure.png "JSON structure of an entry")

An entry can have these fields:

- **RadLex ID** (`radlexId`): a RadLex identifier, or a post-coordinated term built from RadLex identifiers, such as `RID294_RID5824` for the left uterine adnexa
- **Description and synonyms** (`description`, `synonyms`): the preferred name and its exact English synonyms
- **containedBy hierarchy** (`containedById`): the smallest region that physically encloses the structure, such as the retroperitoneal space for the kidney
- **partOf hierarchy** (`partOfId`): the larger structure, set, or system the entry belongs to, such as the female genital system for the uterine adnexa, with at most one per entry
- **Laterality triads** (`leftId`, `rightId`, `unsidedId`): links among the unsided, left, and right entries of a paired structure, such as `RID205` kidney, `RID29663` left kidney, and `RID29662` right kidney
- **Sex phenotype** (`sexSpecific`): `Male` or `Female` for a structure specific to one sex phenotype, such as `Female` for the uterine adnexa
- **Codes** (`codes`) in FMA, SNOMED CT, MeSH, UMLS, and TA2, with the `system` values `FMA`, `SNOMED`, `MESH`, `UMLS`, and `TA2`

`RID39569` whole body names itself as its container, so a program that follows `containedById` upward stops there. A left or right entry with no sided SNOMED CT concept carries a laterality expression. The right testicular artery carries `27175001:272741003=24028007`, which combines the testicular artery concept `27175001`, the laterality attribute `272741003`, and right, `24028007`.

## Utility Libraries

Open-source libraries load the ALI in TypeScript and Python. Each bundles an earlier version of the data. BodyPartIndex.py loads release 1.0.0 from a downloaded file with `BodyPartIndex(json_filename='body_parts.json')`.

- **TypeScript**: [GitHub](https://github.com/talkasab/BodyPartIndex.ts) [NPM](https://www.npmjs.com/package/@talkasab/body_part_index)
- **Python**: [GitHub](https://github.com/talkasab/BodyPartIndex.py)

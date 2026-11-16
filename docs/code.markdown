---
layout: page
title: Code
permalink: /code/
---
## Body Parts Data File

The Anatomic Locations Index (ALI) is a single JSON file that validates against a schema in JSON Schema format. Release 1.0.1 has 2,893 entries.

- [body_parts.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json), release 1.0.1
- [body_parts_schema.json](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts_schema.json)
- [CHANGELOG.md](https://github.com/talkasab/anatomiclocations.org/blob/main/data/CHANGELOG.md), which lists the changes in each release

The following figure shows every field of one entry, the uterine adnexa:

![JSON node structure showing all fields for a representative Anatomic Locations Index entry (uterine adnexa)](/assets/JSONStructure.png "JSON structure of an entry")

An entry can have these fields:

- **RadLex ID** (`radlexId`): a RadLex identifier, or a post-coordinated term built from RadLex identifiers, such as `RID294_RID5824` for the left uterine adnexa
- **Description and synonyms** (`description`, `synonyms`): the preferred name and its exact English synonyms
- **Definition** (`definition`): the RadLex definition, on entries with a single RadLex identifier, ending with its source in brackets where RadLex gives one, such as `[MeSH]` or `[FMA]`
- **containedBy hierarchy** (`containedById`): the smallest region that physically encloses the structure, such as the retroperitoneal space for the kidney
- **partOf hierarchy** (`partOfId`): the larger structure, set, or system the entry belongs to, such as the female genital system for the uterine adnexa, with at most one per entry
- **Laterality triads** (`leftId`, `rightId`, `unsidedId`): links among the unsided, left, and right entries of a paired structure, such as `RID205` kidney, `RID29663` left kidney, and `RID29662` right kidney
- **Sex phenotype** (`sexSpecific`): `Male` or `Female` for a structure specific to one sex phenotype, such as `Female` for the uterine adnexa
- **Codes** (`codes`) in FMA, SNOMED CT, MeSH, UMLS, and TA2, with the `system` values `FMA`, `SNOMED`, `MESH`, `UMLS`, and `TA2`

`RID39569` whole body names itself as its container, so a program that follows `containedById` upward stops there. A left or right entry whose structure has a SNOMED CT concept, but no sided one, carries a laterality expression. The right testicular artery carries `27175001:272741003=24028007`, which combines the testicular artery concept `27175001`, the laterality attribute `272741003`, and right, `24028007`.

## Placement Conventions

These rules decide where an entry sits in the two hierarchies:

- **Containment is location; partOf is structure.** The mandible, maxilla, and the other facial bones are contained in the face but are part of the skull.
- **Structures that span regions** sit in the region that holds most of them, such as the esophagus in the thorax. When no single region fits, they sit in the whole body, as the gastrointestinal tract and the iliopsoas do. Bone and tendon parts at a joint, such as the femoral head, sit in that joint's region.
- **Joints** do not contain the bones that form them. Ligaments are contained in, and part of, their joint.
- **Dural venous sinuses** sit in the cranial cavity, except the sagittal sinuses, which sit in the falx cerebri.
- **Brain vessels** sit in the smallest brain division that holds their whole course:
  - the lobe, for a vessel within one lobe;
  - the left or right cerebral hemisphere, for a vessel over several lobes;
  - the supratentorial brain, for midline and basal vessels;
  - the brain, for vessels that wrap around the midbrain;
  - the infratentorial brain, or the part they supply, in the posterior fossa.

  The frontal, temporal, parietal, and occipital brain region entries contain nothing.
- **Lymph nodes:** `RID28847` lymph node group is the root of the lymph node hierarchy. The IASLC mediastinal stations are part of `RID28852` set of mediastinal lymph nodes.
- **Collective entries:** `RID33180` mesentery is any mesentery, not only the small-bowel mesentery. `RID2202` wrist joint is the joint of the whole wrist region.
- **Synonyms** are exact English names. Two entries may share one, such as `uncinate process`, so a match on a shared synonym needs context.
- **Codes** name the same structure as the entry, not a part, a neighbor, or a broader structure. SNOMED CT codes are "Structure of" concepts.

## Utility Libraries

Open-source libraries load the ALI in TypeScript and Python. Each bundles an earlier version of the data. BodyPartIndex.py loads release 1.0.1 from a downloaded file with `BodyPartIndex(json_filename='body_parts.json')`.

- **TypeScript**: [GitHub](https://github.com/talkasab/BodyPartIndex.ts) [NPM](https://www.npmjs.com/package/@talkasab/body_part_index)
- **Python**: [GitHub](https://github.com/talkasab/BodyPartIndex.py)

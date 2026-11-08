---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

[![Mind map of the containedBy hierarchy, with the whole body in the center and the body regions and their subregions branching from it, each labeled with the number of entries it contains](/assets/BodyPartHierarchy.png "Containment hierarchy")](/assets/BodyPartHierarchyFull.png)

### Introduction

A radiologist who reads "cyst in the tail of the pancreas" knows the regions that enclose it: the pancreas, the retroperitoneal space, the abdomen, and the whole body. Software can follow that chain only if a terminology records it. SNOMED CT, the Foundational Model of Anatomy (FMA), and RadLex each define a containment relation, but in none of them can a program follow a structure to the whole body.

![Containment hierarchy in the Anatomic Locations Index, from the pancreas to the whole body. Nested boxes show containedBy relations, and dashed arrows show partOf relations.](/assets/PancreasContainment.png "From the pancreas to the whole body")

The Anatomic Locations Index (ALI) records those chains for the structures radiologists name when they localize findings in reports. Each entry has exactly one enclosing region, so every entry reaches the whole body by one path. The ALI records part-whole relationships, such as the common bile duct as part of the biliary tree, in a separate field.

### Our Approach

We drew candidate terms from about 100,000 consecutive radiology reports. Three board-certified radiologists and one radiology trainee curated the terms, using RadLex names and identifiers. RadLex has a term for forearm but none for left forearm, so the ALI identifies left forearm as `RID2107_RID5824`, a post-coordinated term built from the RadLex identifiers for forearm and left.

### Features

- 2,899 entries, each with a RadLex identifier or a post-coordinated term
- One containment tree rooted at the whole body, which you can browse on the [Hierarchy page](/hierarchy/)
- Part-whole links, at most one per entry, kept separate from containment
- Unsided, left, and right entries for paired structures, linked to each other
- Flags for structures specific to the male or female sex phenotype
- Codes in SNOMED CT, FMA, MeSH, UMLS, and Terminologia Anatomica (TA2)
- A single [JSON file](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json), release 1.0.0, described on the [Code page](/code/)
- Companion libraries for [TypeScript](https://github.com/talkasab/BodyPartIndex.ts) and [Python](https://github.com/talkasab/BodyPartIndex.py)
- A [GitHub project](https://github.com/talkasab/anatomiclocations.org) under an [open-source license](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/LICENSE.txt) ([ISC License](https://en.wikipedia.org/wiki/ISC_license))

To propose an addition or correction, open an issue or pull request on [GitHub](https://github.com/talkasab/anatomiclocations.org), or email [info@anatomiclocations.org](mailto:info@anatomiclocations.org).

### Roadmap

- Content
  - Bring the containment relationships and post-coordinated terms into RadLex with the RSNA RadLex Committee, which will give them standard RadLex identifiers
  - Add missing structures, such as the accessory spleen
  - Add finer subregions where radiologists localize findings more precisely
  - Extend coverage to fetal, neonatal, and developmental anatomy and to anatomic variants
  - Define exam types by the body parts each one includes, using the LOINC and RadLex Playbook exam definitions
- Code
  - Bundle release 1.0.0 in [BodyPartIndex.ts](https://github.com/talkasab/BodyPartIndex.ts) and [BodyPartIndex.py](https://github.com/talkasab/BodyPartIndex.py)
  - Finish [BodyPartIndex.py](https://github.com/talkasab/BodyPartIndex.py) and publish to [PyPI](https://pypi.org)
  - Create a BodyPartIndex.cs
- Website
  - Add search

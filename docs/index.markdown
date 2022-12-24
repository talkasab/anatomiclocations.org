---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

[![Tree of body part nodes organized according to a "contained-by" hierarchy](/assets/BodyPartHierarchy.png "Body Part Hierarchy")](/assets/BodyPartHierarchyFull.png)
### Introduction
Standard identifiers for discrete anatomic locations would enable numerous levels of interoperability if applied broadly. However, attempts to use existing ontologies containing anatomic terms—such as [Radlex](https://radlex.org/) or [SNOMED-CT](https://www.snomed.org)—have disappointed: existing ontologies lack numerous desired terms; they contain too many unnecessary/degenerate terms; and they are not organized anatomically. We sought to identify a subset of anatomic nodes from existing ontologies that could be shaped into a usable collection of anatomic identifiers.

> **Goal**: Build and maintain a curated subset of anatomic terms can be developed from existing ontologies
> to enable informatics interoperability.

### Our Approach
Starting with a set of Radlex terms that had been previously recognized in radiology reports, a subset of used and useful anatomic terms was identified. For each term, its location in an anatomic hierarchy was identified, references to other ontologies were recognized, and laterality and sex phenotype information was associated.

### Current Features
- Curated set of 2890 nodes, primarily identified by RadLex ontology IDs.
  - Complete-ish: contains almost all clinically used anatomic terms
  - Non-degenerate: no uncertainty as to which node represents a structure
- Organized into a directed, rooted tree hierarchy, starting from the whole body and ramifying through body regions. 
- For all sided terms, unsided and contralateral versions of the term were identified.
- Identifies structures specific to male or female sex phenotypes
- Available as a single [JSON file](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/data/body_parts.json) (see [Code page](/code/) for more details)
- Companion libraries available for [TypeScript](https://github.com/talkasab/BodyPartIndex.ts) and [Python](https://github.com/talkasab/BodyPartIndex.py)
- Available as a [Github project](https://github.com/talkasab/anatomiclocations.org) under an [open-source license](https://raw.githubusercontent.com/talkasab/anatomiclocations.org/main/LICENSE.txt) ([ISC License](https://en.wikipedia.org/wiki/ISC_license)). Please join us and contribute!

### Roadmap
- Recruit collaborators!
- Content
  - Review hierarchy; add, prune, modify
  - Edit and improve synonyms
  - Complete SNOMED identification
  - Work on a companion for exam types based on LOIC/Radlex Playbook exam definitions that specify all *included* body parts for the exam
- Code
  - Finish [BodyPartIndex.py](https://github.com/talkasab/BodyPartIndex.py)
  - Create a BodyPartIndex.cs

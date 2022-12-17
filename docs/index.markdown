---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

[![Tree of body part nodes organized according to a "contained-by" hierarchy](/assets/BodyPartHierarchy.png "Body Part Hierarchy")](/assets/BodyPartHierarchyFull.png)
### Introduction
Standard identifiers for discrete anatomic locations would enable numerous levels of interoperability if applied broadly. However, attempts to use existing ontologies containing anatomic terms— such as Radlex or SNOMED-CT—have disappointed: existing ontologies lack numerous desired terms; they contain too many unnecessary/degenerate terms; and they are not organized anatomically. We sought to identify a subset of anatomic nodes from existing ontologies that could be shaped into a usable collection of anatomic identifiers.

### Goal
Build and maintain a curated subset of anatomic terms can be developed from existing ontologies to enable informatics interoperability.

### Our Approach
Starting with a set of Radlex terms that had been previously recognized in radiology reports, a subset of used and useful anatomic terms was identified. For each term, its location in an anatomic hierarchy was identified, references to other ontologies were recognized, and laterality and sex phenotype information was associated.

### Current Status
A set of 2889 nodes, primarily from the RadLex ontology. These were able to be organized into an anatomic directed graph hierarchy, starting from the whole body and ramifying through body regions. For all sided terms, unsided and contralateral versions of the term were identified. Of these terms, 900 terms had to be synthesized from more basic Radlex nodes. Corresponding SNOMED-CT terms were identified for most (2282/2889; 79%) nodes in the network.

### Conclusion
We have created a curated set of anatomic tags from the Radlex ontology, intended for use in applications requiring anatomic localization. For example, using this network to tag the LOINC list of standard imaging procedures would enable applications to find LOINC codes containing specific body parts. This would enable more effective identification of relevant priors, even focused on currently viewed anatomy. As the true value of this standard set can only be realized as more applications leverage it, it has been made available under open-source license at [anatomiclocations.org](https://anatomiclocations.org).

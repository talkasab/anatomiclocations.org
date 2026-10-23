# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-23
### Added
- Added 852 TA2 codes
- Raised the number of FMA codes from 1,643 to 2,667
- Raised the number of SNOMED CT codes from 1,732 to 2,634
- Added `RID174` body of pancreas and `RID7361` spinal cord
- Added left and right entries for 12 unsided entries, such as `RID1362` pleura and `RID228` renal pelvis

### Changed
- Moved 1,081 entries to the smallest region that encloses each one, such as `RID29154` vertebra from whole body to `RID7741` spine
- Added 231 `partOfId` values, changed 93, and removed 75
- Corrected or standardized 276 labels, such as `risoris muscle` to `risorius muscle` and `intracranial head` to `cranial cavity`
- Removed synonyms that are not exact English names, such as shorthand (`mediast`) and Latin and German forms (`ren`, `Niere`)
- Removed synonyms written in another terminology's notation, such as `optic nerve [II]` and `Structure of right seminal vesicle`
- Removed synonyms whose meaning differs from the entry, such as `abdominopelvis` for `RID56` abdomen
- Replaced MeSH tree numbers with descriptor IDs, such as `D000005` for abdomen
- Gave each sided entry SNOMED CT's sided concept where one exists, and otherwise a laterality expression, such as `27175001:272741003=24028007` for `RID38035` right testicular artery
- Renamed the 52 tooth identifiers so the side comes last, as in every other post-coordinated term: `RID5825_RID9279_RID5827_RID9127` became `RID9127_RID9279_RID5827_RID5825`
- Renamed the left and right crura of the diaphragm, `RID1529_RID5824` and `RID1529_RID5825`, to their RadLex identifiers, `RID34476` and `RID34477`

### Removed
- Removed entries that have a RadLex successor:
  - `RID2137` volar compartment of forearm, replaced by `RID39931` anterior compartment of forearm, and the same for their left and right entries
  - `RID2135` dorsal compartment of forearm, replaced by `RID39928` posterior compartment of forearm, and the same for their left and right entries
  - `RID40365` muscle body of obturator internus, replaced by `RID2633` obturator internus muscle, and the same for their left and right entries
  - `RID40392` muscle body of coccygeus, replaced by `RID7819` coccygeus muscle, and the same for their left and right entries
  - `RID9554` paranasal sinus, replaced by `RID28579` paranasal sinuses
  - `RID28576` mandibular rami, replaced by `RID9108` ramus of mandible
- Removed two duplicates with their left and right entries: `RID28571` inferior nasal concha, kept as `RID10051` inferior turbinate, and `RID2287` palmar ligament, kept as `RID40874` palmar radiocarpal ligament
- Removed entries with no successor:
  - `RID31686` endometrium of cervix
  - `RID30683` myometrium of cervix
  - `RID6379_RID9080` extracranial head
  - `RID7489` muscle of neck
  - `RID17726` tract of spinal cord
  - `RID9554_RID5824` left paranasal sinus and `RID9554_RID5825` right paranasal sinus
  - `RID9896` chondroglossus muscle, with its left and right entries
  - `RID9897` ceratoglossus muscle, with its left and right entries

### Fixed
- Pointed the `$schema` declaration at the URL of a specific version of the schema
- Corrected codes that belonged to another structure, such as the FMA code for `RID1385` heart, from `14550`, the right colic flexure, to `7088`
- Corrected 15 laterality links on 11 entries, such as the `unsidedId` of `RID976` right pulmonary artery, which named `RID936` renal artery
- Linked the unsided, left, and right entries of the thalamus, subclavian artery, and seminal vesicle
- Changed the `partOfId` of `RID1397` tricuspid valve from itself to `RID1385` heart
- Replaced the SNOMED CT code of `RID39569` whole body, the retired qualifier value `261188006`, with `38266002`
- Removed `Male` from `RID2509` sacrum, and marked the amnion, chorion, placenta, and umbilical cord `Female`

## 1.0.0-rc.1 (2022–December–18)
### Added
- Put a version number in the data file
- Many new SNOMED connections
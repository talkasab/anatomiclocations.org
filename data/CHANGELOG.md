# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-11-08
Every change in this release, with its reason, is listed in [release-notes/1.0.1-changes.csv](release-notes/1.0.1-changes.csv).

### Added
- Added a `definition` field, with the RadLex definition on 269 entries
- Raised the number of SNOMED CT codes from 2,634 to 2,697, FMA codes from 2,667 to 2,695, and TA2 codes from 852 to 884, such as the codes of the intervertebral discs, the Couinaud segments, and the carpal bones
- Added common names as synonyms, such as `pulmonary trunk` and `MPA` for `RID975` main pulmonary artery and `fibular collateral ligament` for `RID2797` lateral collateral ligament

### Changed
- Moved 347 entries to the region that encloses them, such as `RID7094` falx cerebri to the cranial cavity, the mandibular teeth to the mandible, and the nasal, zygomatic, and lacrimal bones and the maxilla to the face. The rules are on the Code page under "Placement Conventions"
- Placed intracranial vessels by one rule: dural venous sinuses in the cranial cavity, except the sagittal sinuses in the falx cerebri, and brain vessels in the smallest brain division that holds their course
- Moved `RID94` gastrointestinal tract and `RID30906` iliopsoas, with its left and right entries, to `RID39569` whole body, since each spans several regions
- Added 170 `partOfId` values, changed 67, and removed 10, such as `RID168` appendix from the cecum to `RID152` large intestine and the IASLC stations to `RID28852` set of mediastinal lymph nodes
- Corrected or standardized 101 labels, such as `eight thoracic vertebra` to `eighth thoracic vertebra` and `temporal artery` to `temporal branches of middle cerebral artery`. Most replaced labels are kept as synonyms
- Removed synonyms that name a different, broader, or narrower structure, such as `coronary artery segment 11` (the proximal circumflex) for `RID486` left main coronary artery and `pyloric part of stomach` for `RID122` pylorus. Synonyms that are correct but shared with another structure, such as `uncinate process`, are kept

### Removed
- Removed the left and right entries of three unpaired structures; use the unsided entry instead:
  - `RID44638` left and `RID44639` right anterior spinal artery; use `RID789`
  - `RID7651_RID5824` left and `RID7651_RID5825` right transverse arytenoid muscle; use `RID7651`
  - `RID36189` left and `RID36188` right great cerebral vein; use `RID1132`

### Fixed
- Pointed the `$schema` declaration at the schema in the 1.0.1 release, which adds `definition`
- Corrected the MeSH code for `RID7745` atlas, from `D020466`, the publication type, to `D001270`
- Replaced codes that named a broader or neighboring structure, such as SNOMED CT `11899006` esophageal lymph node with `127940001` on `RID1484` paraesophageal lymph node (station 8), FMA `305654`, a ligament cluster, with `9660` on `RID2797` lateral collateral ligament, and TA2 `2972` ileal orifice with `2971` ileal papilla on `RID153` ileocecal valve
- Replaced the SNOMED CT code of `RID56` abdomen, `818983003`, which includes the pelvis, with `818984009` abdomen proper, since the pelvis is a separate entry
- Removed the FMA codes for the TA98 artery divisions from `RID651` A2 and `RID680` M3 segments and their left and right entries, since those divisions run farther than the radiology segments
- Removed TA2 `4572`, the lateral occipital artery, from `RID818` P3 segment of the posterior cerebral artery
- Removed TA2 `3740` and the synonym `small bowel mesentery` from `RID33180` mesentery, which is the generic mesentery
- Replaced the retired UMLS CUI of `RID1490` inferior pulmonary ligament lymph node, `C4248061`, with `C1268057`
- Replaced 13 UMLS CUIs that named SNOMED CT "Entire" concepts with the CUIs of the entries' "Structure" concepts, on 12 teeth and `RID7780` erector spinae muscle group
- Replaced the UMLS CUI of `RID28591` set of ribs, a single rib, with `C0223074` all ribs, and of `RID407` rectouterine pouch, a generic cul-de-sac, with `C0013075`
- Replaced the laterality expressions of the left and right wrist joint with SNOMED CT's sided concepts, `840404009` and `840403003`
- Corrected misspelled and garbled synonyms, such as `cortical part of middle cerebral artery` on `RID680` M3 segment, now `opercular segment of middle cerebral artery`
- Marked `RID407` rectouterine pouch `Female`

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
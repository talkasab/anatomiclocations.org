# /// script
# requires-python = ">=3.11"
# dependencies = ["rdflib"]
# ///
"""Build ROBOT template tables that bring the Anatomic Locations Index into RadLex.

Compares data/body_parts.json with a RadLex.owl file and writes, to --out:

  ali-add.tsv                      ROBOT template: everything to add
  ali-remove.tsv                   ROBOT template: values the ALI replaces or has dropped
  new-class-ids.tsv                ALI combined ID -> provisional new RID
  review-notes.tsv                 things a reviewer should look at; not ROBOT input

Row 1 of each template is the column name and row 2 the ROBOT template string.
Run both templates with --input RadLex.owl: without it ROBOT cannot tell which
RadLex properties are object properties, and mistypes some rows.
Columns with an empty row 2 are for reviewers; ROBOT ignores them.

Targets the property names of RadLex PR #39: oboInOwl:hasExactSynonym for
synonyms and obo:IAO_0000115 for definitions. sexSpecific is not exported.

    uv run scripts/build_radlex_templates.py --radlex-owl PATH/RadLex.owl --out radlex-import
"""

import argparse
import collections
import csv
import json
import re
from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef

RID = "http://www.radlex.org/RID/"
OIO = "http://www.geneontology.org/formats/oboInOwl#"
DEFINITION = "http://purl.obolibrary.org/obo/IAO_0000115"
SYNONYM = OIO + "hasExactSynonym"
ACRONYM = RID + "Acronym"
XREF = RID + "ExternalRefID"
OBSOLETE_ROOT = "RID15849"

# RadLex properties that say "is part of" in some form. If RadLex already links
# an entry to the ALI's whole with any of these, no Part_Of is added.
PART_PROPERTIES = {
    "Part_Of", "Regional_Part_Of", "Constitutional_Part_Of", "Member_Of",
    "Branch_Of", "Segment_Of", "Tributary_Of", "Branch_Part_of",
}  # fmt: skip
INVERSE = {"Contained_In": "Contains"}

# ALI code system -> prefix used in RID:ExternalRefID. FMA and UMLS are RadLex's
# existing prefixes; the other three are new to RadLex.
XREF_PREFIX = {"FMA": "FMA", "UMLS": "UMLS", "SNOMED": "SNOMEDCT", "TA2": "TA2", "MESH": "MESH"}
# Systems where the ALI's codes replace RadLex's when they disagree.
REPLACE_SYSTEMS = {"FMA", "UMLS"}

# Parents for new classes that have no unsided entry and whose first ID
# component is not a kind the entry belongs to.
PARENT_OVERRIDES = {
    "RID28591": "RID2471",  # "set of ribs" + level -> rib
    "RID6383_RID9080": "RID32952",  # cranial cavity -> body cavity subdivision
    "RID6389_RID6434": "RID13853",  # supratentorial brain -> segment of brain
    "RID6381_RID6434": "RID13853",  # infratentorial brain -> segment of brain
}

ACRONYM_RE = re.compile(r"[A-Z0-9][A-Z0-9/\-]{1,6}")


def head_noun(label):
    """The noun a label is about: "proximal phalanx of great toe" -> "phalanx"."""
    return label.split(" of ")[0].split()[-1].lower() if label else ""


def norm(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def load_radlex(path):
    graph = Graph()
    graph.parse(path, format="xml")
    classes = {}
    for cls in graph.subjects(RDF.type, OWL.Class):
        if not isinstance(cls, URIRef) or not str(cls).startswith(RID):
            continue
        entry = {"ann": collections.defaultdict(list), "parents": [], "rel": set()}
        for pred, obj in graph.predicate_objects(cls):
            if pred == RDFS.subClassOf:
                if isinstance(obj, URIRef):
                    entry["parents"].append(str(obj).removeprefix(RID))
                else:
                    prop = graph.value(obj, OWL.onProperty)
                    target = graph.value(obj, OWL.someValuesFrom)
                    if prop is not None and isinstance(target, URIRef):
                        entry["rel"].add((str(prop).removeprefix(RID), str(target).removeprefix(RID)))
            elif isinstance(obj, Literal):
                entry["ann"][str(pred)].append((str(obj), obj.language))
        classes[str(cls).removeprefix(RID)] = entry
    # Annotations on a cross-reference, such as the UMLS term beside a UMLS code.
    # ROBOT can only remove such a cross-reference if the row repeats them.
    for axiom in graph.subjects(RDF.type, OWL.Axiom):
        source = graph.value(axiom, OWL.annotatedSource)
        target = graph.value(axiom, OWL.annotatedTarget)
        if str(graph.value(axiom, OWL.annotatedProperty)) != XREF or str(source).removeprefix(RID) not in classes:
            continue
        for pred, obj in graph.predicate_objects(axiom):
            if str(pred).startswith(RID):
                notes = classes[str(source).removeprefix(RID)].setdefault("xref_notes", {})
                notes.setdefault(str(target), []).append((str(pred).removeprefix(RID), str(obj)))
    return classes


class Builder:
    def __init__(self, ali, radlex, first_rid, version, source):
        self.ali = {e["radlexId"]: e for e in ali["bodyParts"]}
        self.radlex = radlex
        self.version = version
        self.source = source
        self.notes = []
        self.obsolete = {r for r in radlex if OBSOLETE_ROOT in self.ancestors(r)}
        self.alias = self.find_aliases()
        self.new_ids = {}
        number = first_rid
        for ali_id in self.ali:
            if ali_id not in radlex and ali_id not in self.alias:
                while f"RID{number}" in radlex:
                    number += 1
                self.new_ids[ali_id] = f"RID{number}"
                number += 1

    def ancestors(self, rid, seen=None):
        seen = set() if seen is None else seen
        for parent in self.radlex.get(rid, {}).get("parents", []):
            if parent not in seen:
                seen.add(parent)
                self.ancestors(parent, seen)
        return seen

    def values(self, rid, prop, langs=("en", None)):
        return [(v, lang) for v, lang in self.radlex[rid]["ann"].get(prop, []) if lang in langs]

    def en_label(self, rid):
        labels = [v for v, lang in self.radlex.get(rid, {}).get("ann", {}).get(str(RDFS.label), []) if lang == "en"]
        return labels[0] if labels else ""

    def find_aliases(self):
        """ALI combined IDs whose name is already a live RadLex class under another RID."""
        by_name = collections.defaultdict(set)
        for rid, entry in self.radlex.items():
            if rid in self.obsolete:
                continue
            for prop in (str(RDFS.label), SYNONYM):
                for value, lang in entry["ann"].get(prop, []):
                    if lang in ("en", None):
                        by_name[norm(value)].add(rid)
        alias = {}
        for ali_id, entry in self.ali.items():
            if ali_id in self.radlex:
                continue
            names = [entry["description"], *entry.get("synonyms", [])]
            hits = {rid for name in names for rid in by_name.get(norm(name), ()) if rid not in self.ali}
            if len(hits) == 1:
                alias[ali_id] = hits.pop()
                self.note(ali_id, alias[ali_id], "existing-class",
                          f"ALI combined ID is already RadLex class {alias[ali_id]} "
                          f"({self.en_label(alias[ali_id])}); treated as that class")  # fmt: skip
            elif hits:
                self.note(ali_id, "", "ambiguous-name", f"name matches several RadLex classes: {sorted(hits)}")
        return alias

    def note(self, ali_id, rid, kind, text):
        self.notes.append({"ALI ID": ali_id, "RadLex ID": rid, "Kind": kind, "Note": text})

    def rid(self, ali_id):
        if ali_id in self.radlex:
            return ali_id
        return self.alias.get(ali_id) or self.new_ids[ali_id]

    def label_of(self, ali_id):
        return self.ali[ali_id]["description"]

    def names(self, entry):
        synonyms, acronyms = [], []
        for name in entry.get("synonyms", []):
            (acronyms if ACRONYM_RE.fullmatch(name) else synonyms).append(name)
        return synonyms, acronyms

    def codes(self, entry):
        out = collections.defaultdict(list)
        skipped = 0
        for code in entry.get("codes", []):
            if not re.fullmatch(r"[A-Za-z0-9]+", code["code"]):
                skipped += 1  # a SNOMED CT laterality expression, not a code
                continue
            out[code["system"]].append(code["code"])
        return out, skipped

    def new_parent(self, ali_id, entry):
        if "unsidedId" in entry:
            return [self.rid(entry["unsidedId"])], "unsided entry"
        parts = ali_id.split("_")
        override = PARENT_OVERRIDES.get(ali_id) or PARENT_OVERRIDES.get(parts[0])
        if override:
            self.note(ali_id, self.new_ids[ali_id], "parent-chosen-by-hand",
                      f"parent set to {override} ({self.en_label(override)})")  # fmt: skip
            return [override], "chosen by hand"
        # The parent is the part of the combined ID that names the same kind of
        # thing as the entry: "first metatarsal" is a metatarsal, not a great toe.
        # Matched on the head noun, never on position. Several parts can match:
        # a deciduous incisor is both an incisor tooth and a deciduous tooth.
        head = head_noun(entry["description"])
        same_kind = [p for p in parts if "RID3" in self.ancestors(p) and head_noun(self.en_label(p)) == head]
        if not same_kind:
            names = ", ".join(f"{p} ({self.en_label(p)})" for p in parts)
            raise ValueError(f"no parent for {ali_id} {entry['description']!r} among {names}; "
                             "add it to PARENT_OVERRIDES")  # fmt: skip
        return same_kind, "same kind of structure"

    def build(self):
        add_rows, remove_rows = [], []
        skipped_expressions = 0
        for ali_id, entry in self.ali.items():
            rid = self.rid(ali_id)
            is_new = ali_id in self.new_ids
            synonyms, acronyms = self.names(entry)
            codes, skipped = self.codes(entry)
            skipped_expressions += skipped
            add = collections.defaultdict(list)
            remove = collections.defaultdict(list)
            review = {
                "ALI ID": ali_id,
                "Status": "new" if is_new else "existing",
                "ALI label": entry["description"],
                "Current RadLex label": "" if is_new else self.en_label(rid),
            }

            container = entry["containedById"]
            whole = entry.get("partOfId")
            if container == ali_id:
                container = None  # the root contains itself in the ALI

            if is_new:
                parents, why = self.new_parent(ali_id, entry)
                review["Parent label"] = f"{'|'.join(self.label_of_rid(p) for p in parents)} [{why}]"
                add["Label"] = [entry["description"]]
                add["RadLexID"] = [rid]
                add["Parent"] = parents
                add["Synonyms"] = synonyms
                add["Acronyms"] = acronyms
                if entry.get("definition"):
                    add["Definition"] = [entry["definition"]]
                for system, values in codes.items():
                    add["Codes"] += [f"{XREF_PREFIX[system]}:{v}" for v in values]
                add["Version"] = [f"{self.version} new"]
                add["Source"] = [self.source]
                if container:
                    add["Contained in"] = [self.rid(container)]
                if whole:
                    add["Part of"] = [self.rid(whole)]
            else:
                current = self.radlex[rid]
                # Label
                labels = [v for v, _ in self.values(rid, str(RDFS.label), ("en",))]
                new_label = entry["description"]
                if new_label not in labels:
                    add["Label"] = [new_label]
                    remove["Label"] = labels
                # Synonyms and acronyms
                have_syn = self.values(rid, SYNONYM)
                have_acr = self.values(rid, ACRONYM)
                known = {norm(v) for v, _ in have_syn + have_acr} | {norm(new_label)}
                add["Synonyms"] = [s for s in synonyms if norm(s) not in known]
                add["Acronyms"] = [a for a in acronyms if norm(a) not in known]
                # A synonym equal to the label fails RadLex CI.
                for value, lang in have_syn + have_acr:
                    if norm(value) == norm(new_label):
                        prop = "Synonyms" if (value, lang) in have_syn else "Acronyms"
                        remove[prop + (" (no language tag)" if lang is None else "")].append(value)
                ali_names = {norm(n) for n in [new_label, *entry.get("synonyms", [])]}
                # English synonyms the ALI removed as wrong or inexact are removed here too.
                for value, lang in have_syn:
                    if norm(value) not in ali_names:
                        remove["Synonyms" + (" (no language tag)" if lang is None else "")].append(value)
                # Definition
                if entry.get("definition"):
                    have_def = current["ann"].get(DEFINITION, [])
                    if entry["definition"] not in [v for v, _ in have_def]:
                        add["Definition"] = [entry["definition"]]
                        for value, lang in have_def:
                            remove["Definition" + (" (en)" if lang == "en" else "")].append(value)
                # Codes
                have_x = collections.defaultdict(set)
                for value, _ in current["ann"].get(XREF, []):
                    prefix, _, code = value.partition(":")
                    have_x[prefix].add(code)
                for system, values in codes.items():
                    prefix = XREF_PREFIX[system]
                    add["Codes"] += [f"{prefix}:{v}" for v in values if v not in have_x[prefix]]
                    if system in REPLACE_SYSTEMS:
                        for old in sorted(have_x[prefix] - set(values)):
                            xref = f"{prefix}:{old}"
                            annotations = current.get("xref_notes", {}).get(xref)
                            if not annotations:
                                remove["Codes"].append(xref)
                            elif [name for name, _ in annotations] == ["UMLS_Term"]:
                                remove_rows.append({"ID": f"RID:{rid}", **review,
                                                    "Annotated code": xref, "UMLS term": annotations[0][1]})  # fmt: skip
                            else:
                                raise ValueError(f"{rid} {xref}: unhandled annotations {annotations}")
                # Containment: the ALI holds one smallest container, so it replaces RadLex's.
                if container:
                    target = self.rid(container)
                    have_c = {t for p, t in current["rel"] if p == "Contained_In"}
                    if target not in have_c:
                        add["Contained in"] = [target]
                        remove["Contained in"] = sorted(have_c)
                        for old in sorted(have_c):
                            if ("Contains", rid) in self.radlex.get(old, {}).get("rel", ()):
                                remove_rows.append({
                                    "ID": f"RID:{old}", "ALI ID": "", "Status": "existing",
                                    "ALI label": "", "Current RadLex label": self.en_label(old),
                                    "Contains": f"RID:{rid}", "Contains label": self.en_label(rid),
                                })  # fmt: skip
                # Part-whole: added alongside RadLex's own part relations, never replacing them.
                if whole:
                    target = self.rid(whole)
                    have_p = {(p, t) for p, t in current["rel"] if p in PART_PROPERTIES}
                    if not any(t == target for _, t in have_p):
                        add["Part of"] = [target]
                        if have_p:
                            others = ", ".join(f"{p} {t} ({self.en_label(t)})" for p, t in sorted(have_p))
                            self.note(ali_id, rid, "part-of-differs",
                                      f"adding Part_Of {target} ({self.label_of_rid(target)}); RadLex keeps: {others}")  # fmt: skip
                # Left/right: RadLex models a sided class as a subclass of the unsided one.
                unsided = entry.get("unsidedId")
                if unsided and self.rid(unsided) not in self.ancestors(rid):
                    self.note(ali_id, rid, "not-under-unsided",
                              f"not a subclass of its unsided entry {self.rid(unsided)} ({self.label_of(unsided)}); "
                              f"RadLex parent: {', '.join(current['parents'])}")  # fmt: skip

            for rows, data in ((add_rows, add), (remove_rows, remove)):
                data = {k: v for k, v in data.items() if v}
                if not data:
                    continue
                row = {"ID": f"RID:{rid}", **review}
                for key, values in data.items():
                    if key in ("Parent", "Contained in", "Part of"):
                        row[key] = "|".join(f"RID:{v}" for v in values)
                        row.setdefault(key + " label", "|".join(self.label_of_rid(v) for v in values))
                    else:
                        row[key] = "|".join(values)
                rows.append(row)
        if skipped_expressions:
            self.note(
                "", "", "summary", f"{skipped_expressions} SNOMED CT laterality expressions not exported as codes"
            )
        return add_rows, remove_rows

    def label_of_rid(self, rid):
        if rid in self.radlex:
            return self.en_label(rid)
        for ali_id, new in self.new_ids.items():
            if new == rid:
                return self.ali[ali_id]["description"]
        return ""


REVIEW = ["ALI ID", "Status", "ALI label", "Current RadLex label"]
ADD_COLUMNS = [
    ("ID", "ID"), *[(c, "") for c in REVIEW],
    ("Label", "AL rdfs:label@en"),
    ("RadLexID", "AL RID:RadLexID@en"),
    ("Parent", "SC % SPLIT=|"), ("Parent label", ""),
    ("Contained in", "SC RID:Contained_In some %"), ("Contained in label", ""),
    ("Part of", "SC RID:Part_Of some %"), ("Part of label", ""),
    ("Synonyms", "AL oboInOwl:hasExactSynonym@en SPLIT=|"),
    ("Acronyms", "AL RID:Acronym@en SPLIT=|"),
    ("Definition", "A obo:IAO_0000115"),
    ("Codes", "A RID:ExternalRefID SPLIT=|"),
    ("Version", "A RID:Radlex_version_of_class_change"),
    ("Source", "A RID:Source"),
]  # fmt: skip
REMOVE_COLUMNS = [
    ("ID", "ID"), *[(c, "") for c in REVIEW],
    ("Label", "AL rdfs:label@en SPLIT=|"),
    ("Contained in", "SC RID:Contained_In some % SPLIT=|"), ("Contained in label", ""),
    ("Contains", "SC RID:Contains some %"), ("Contains label", ""),
    ("Synonyms", "AL oboInOwl:hasExactSynonym@en SPLIT=|"),
    ("Synonyms (no language tag)", "A oboInOwl:hasExactSynonym SPLIT=|"),
    ("Acronyms", "AL RID:Acronym@en SPLIT=|"),
    ("Acronyms (no language tag)", "A RID:Acronym SPLIT=|"),
    ("Definition", "A obo:IAO_0000115"),
    ("Definition (en)", "AL obo:IAO_0000115@en"),
    ("Codes", "A RID:ExternalRefID SPLIT=|"),
    ("Annotated code", "A RID:ExternalRefID"), ("UMLS term", ">A RID:UMLS_Term"),
]  # fmt: skip


def write_template(path, columns, rows):
    for row in rows:
        for value in row.values():
            if "\t" in value:
                raise ValueError(f"tab in {row['ID']}: {value!r}")
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([name for name, _ in columns])
        writer.writerow([template for _, template in columns])
        for row in rows:
            writer.writerow([row.get(name, "") for name, _ in columns])


def main():
    parser = argparse.ArgumentParser(description="Build ROBOT template tables from the ALI")
    parser.add_argument("--ali", default="data/body_parts.json")
    parser.add_argument("--radlex-owl", required=True)
    parser.add_argument("--out", default="radlex-import")
    parser.add_argument("--first-rid", type=int, default=52000, help="number of the first new RID (provisional)")
    parser.add_argument("--radlex-version", default="4.4", help="release that introduces the new classes")
    args = parser.parse_args()

    ali = json.loads(Path(args.ali).read_text())
    builder = Builder(ali, load_radlex(args.radlex_owl), args.first_rid, args.radlex_version,
                      f"Anatomic Locations Index {ali['$version']}")  # fmt: skip
    add_rows, remove_rows = builder.build()
    for entry in ali["bodyParts"]:
        if any("|" in name for name in [entry["description"], *entry.get("synonyms", [])]):
            raise ValueError(f"'|' in a name of {entry['radlexId']}; it is the list separator")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    write_template(out / "ali-add.tsv", ADD_COLUMNS, add_rows)
    write_template(out / "ali-remove.tsv", REMOVE_COLUMNS, remove_rows)
    with open(out / "new-class-ids.tsv", "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["ALI ID", "Provisional RID", "Label"])
        for ali_id, rid in builder.new_ids.items():
            writer.writerow([ali_id, rid, builder.ali[ali_id]["description"]])
    with open(out / "review-notes.tsv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, ["Kind", "ALI ID", "RadLex ID", "Note"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(builder.notes, key=lambda n: n["Kind"]))

    def count(rows, column):
        return sum(len(r[column].split("|")) for r in rows if r.get(column))

    print(f"ALI {ali['$version']}: {len(builder.ali)} entries")
    print(
        f"  existing RadLex classes: {len(builder.ali) - len(builder.new_ids)} ({len(builder.alias)} under another RID)"
    )
    print(
        f"  new classes: {len(builder.new_ids)}, RID{args.first_rid} to {max(builder.new_ids.values(), key=lambda r: int(r[3:]))}"
    )
    for title, rows, columns in (("add", add_rows, ADD_COLUMNS), ("remove", remove_rows, REMOVE_COLUMNS)):
        print(f"{title}: {len(rows)} rows")
        for name, template in columns[1:]:
            if template and count(rows, name):
                print(f"  {name}: {count(rows, name)}")
    print("notes:", dict(collections.Counter(n["Kind"] for n in builder.notes)))


if __name__ == "__main__":
    main()

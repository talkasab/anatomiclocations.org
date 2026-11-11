#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.23", "duckdb>=1.5"]
# ///
"""Mechanical checks for the Anatomic Locations Index (data/body_parts.json).

    uv run scripts/check_ali.py                      # self-contained checks (what CI runs)
    uv run scripts/check_ali.py --terminologies DIR  # also check codes against local DuckDB builds
                                                     # of SNOMED CT, FMA and TA2 (snomed_us_*.duckdb,
                                                     # fma_*.duckdb, ta2_*.duckdb in DIR)

Errors make the run fail. Warnings are things a person should look at; --strict makes them fail too.
Accepted warnings go in scripts/check_ali_allow.json as {"check", "radlexId", "reason"} entries.

These checks catch structural and textual mistakes. They cannot tell whether a structure is in the right
place anatomically or whether a synonym means the same thing; that still needs review by a person.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_ID = "RID39569"  # whole body: the only entry that contains itself
LEFT, RIGHT = "_RID5824", "_RID5825"
SNOMED_LEFT, SNOMED_RIGHT, SNOMED_LATERALITY = "7771000", "24028007", "272741003"
REPO = Path(__file__).resolve().parent.parent

CODE_FORMATS = {
    "SNOMED": re.compile(r"^\d{6,18}(:272741003=(7771000|24028007))?$"),
    "FMA": re.compile(r"^\d+$"),
    "TA2": re.compile(r"^\d+$"),
    "MESH": re.compile(r"^D\d{6,9}$"),
    "UMLS": re.compile(r"^C\d{7}$"),
}
BONE_WORDS = re.compile(
    r"\b(bone|condyle|epicondyle|malleolus|tubercle|tuberosity|trochanter|acetabulum|patella|talus|"
    r"capitellum|trochlea|olecranon|styloid|head of|neck of|spine|process|vertebra|phalanx|metatarsal|"
    r"metacarpal|scaphoid|lunate|triquetrum|pisiform|trapezium|trapezoid|capitate|hamate|calcaneus|"
    r"cuboid|cuneiform|navicular)\b"
)
SET_WORDS = re.compile(r"^(set of)\b|\b(system|group|tree)$")


@dataclass
class Finding:
    level: str  # "error" | "warning"
    check: str
    rid: str
    message: str


class Checker:
    def __init__(self, data_path: Path, schema_path: Path):
        self.doc = json.loads(data_path.read_text())
        self.schema = json.loads(schema_path.read_text())
        self.entries = self.doc.get("bodyParts", [])
        self.E = {}
        self.findings: list[Finding] = []

    # ------------------------------------------------------------------ helpers
    def add(self, level, check, rid, message):
        self.findings.append(Finding(level, check, rid, message))

    def name(self, rid):
        return self.E[rid]["description"] if rid in self.E else f"<{rid}>"

    def side(self, rid):
        """'L' or 'R' if this entry is listed as the left/right entry of its unsided entry."""
        e = self.E.get(rid, {})
        u = self.E.get(e.get("unsidedId"), {})
        if u.get("leftId") == rid:
            return "L"
        if u.get("rightId") == rid:
            return "R"
        return None

    def effective_side(self, rid):
        """Side of a left/right entry, including pairs that have no unsided entry and only point at each other
        (the right entry carries leftId, the left entry carries rightId)."""
        s = self.side(rid)
        if s:
            return s
        e = self.E.get(rid, {})
        if e.get("unsidedId"):
            return None
        partner_l, partner_r = e.get("leftId"), e.get("rightId")
        if partner_l and not partner_r and self.E.get(partner_l, {}).get("rightId") == rid:
            return "R"
        if partner_r and not partner_l and self.E.get(partner_r, {}).get("leftId") == rid:
            return "L"
        return None

    def chain(self, rid, key="containedById"):
        """Entries reached by following key from rid (rid first). Stops at a self-reference or a cycle."""
        out = []
        while rid in self.E and rid not in out:
            out.append(rid)
            nxt = self.E[rid].get(key)
            if not nxt or nxt == rid:
                break
            rid = nxt
        return out

    def snomed(self, rid):
        return [c["code"] for c in self.E.get(rid, {}).get("codes", []) if c["system"] == "SNOMED"]

    # ------------------------------------------------------------------ self-contained checks
    def check_schema(self):
        try:
            import jsonschema
        except ImportError:
            self.add("error", "schema", "", "jsonschema is not installed; run with `uv run`")
            return
        for err in sorted(jsonschema.Draft6Validator(self.schema).iter_errors(self.doc), key=str):
            where = "/".join(str(p) for p in err.absolute_path)
            self.add("error", "schema", where, err.message)

    def check_ids(self):
        counts = collections.Counter(e.get("radlexId") for e in self.entries)
        for rid, n in counts.items():
            if n > 1:
                self.add("error", "ids-unique", rid, f"radlexId appears {n} times")
        self.E = {e["radlexId"]: e for e in self.entries if "radlexId" in e}
        for rid, e in self.E.items():
            if not re.fullmatch(r"RID\d+(_RID\d+)*", rid):
                self.add("error", "ids-format", rid, "malformed radlexId")
            for k in ("containedById", "partOfId", "leftId", "rightId", "unsidedId"):
                t = e.get(k)
                if t and t not in self.E:
                    self.add("error", "refs-resolve", rid, f"{k} {t} is not an entry")

    def check_containment(self):
        if ROOT_ID not in self.E or self.E[ROOT_ID].get("containedById") != ROOT_ID:
            self.add("error", "containment-root", ROOT_ID, "whole body must exist and contain itself")
        for rid, e in self.E.items():
            if rid != ROOT_ID and e.get("containedById") == rid:
                self.add("error", "containment-root", rid, "entry contains itself")
                continue
            c = self.chain(rid)
            if c[-1] != ROOT_ID:
                nxt = self.E.get(c[-1], {}).get("containedById")
                why = "cycle" if nxt in c else "chain ends"
                self.add("error", "containment-root", rid, f"containment does not reach whole body ({why} at {c[-1]})")
            p = e.get("partOfId")
            if p == rid:
                self.add("error", "partof-cycle", rid, "entry is partOf itself")
            elif p:
                pc = self.chain(p, "partOfId")
                last = self.E.get(pc[-1], {}).get("partOfId") if pc else None
                if rid in pc or (last and last in pc and last != pc[-1]):
                    self.add("error", "partof-cycle", rid, "partOf chain loops")
                if rid in self.chain(p)[1:]:
                    self.add("error", "partof-inverted", rid, f"its whole {p} {self.name(p)} is contained inside it")

    def check_laterality(self):
        for rid, e in self.E.items():
            for k in ("leftId", "rightId"):
                t = e.get(k)
                if not t or t not in self.E:
                    continue
                te = self.E[t]
                if e.get("unsidedId"):  # sided entry pointing at its opposite number
                    u = e["unsidedId"]
                    if t == rid or t != self.E.get(u, {}).get(k) or te.get("unsidedId") != u:
                        self.add("error", "laterality-links", rid, f"{k} {t} is not the opposite-side entry of unsidedId {u}")
                    continue
                if te.get("unsidedId") == rid:
                    continue
                if te.get("unsidedId"):
                    self.add("error", "laterality-links", rid, f"{k} {t} names a different unsided entry {te['unsidedId']}")
                elif not self.E.get(t, {}).get("leftId") and not self.E.get(t, {}).get("rightId"):
                    self.add("error", "laterality-links", rid, f"{k} {t} has no unsidedId")
            u = e.get("unsidedId")
            if u and u in self.E and self.side(rid) is None:
                self.add("error", "laterality-links", rid, f"unsidedId {u} does not list it as left or right")
            s = self.side(rid)
            if not s:
                if (e.get("leftId") or e.get("rightId")) and not e.get("unsidedId"):
                    partner = e.get("leftId") or e.get("rightId")
                    if self.E.get(partner, {}).get("unsidedId") is None and (rid.endswith((LEFT, RIGHT)) or re.search(r"\b(left|right)\b", e["description"])):
                        self.add("warning", "pair-without-unsided", rid, f"sided pair with {partner} has no unsided entry")
                continue
            uu = self.E[u]
            word, other = ("left", "right") if s == "L" else ("right", "left")
            words = e["description"].lower().split()
            if other in words and word not in words:
                self.add("error", "laterality-names", rid, f"{word} entry is named '{e['description']}'")
            if word not in words:
                self.add("warning", "laterality-names", rid, f"{word} entry has no '{word}' in its name")
            elif " ".join(w for w in e["description"].split() if w.lower() != word) != uu["description"]:
                self.add("warning", "laterality-names", rid, f"name differs from unsided '{uu['description']}' beyond the side word")
            if e.get("sexSpecific") != uu.get("sexSpecific"):
                self.add("error", "laterality-sex", rid, f"sexSpecific {e.get('sexSpecific')} but unsided has {uu.get('sexSpecific')}")
            for syn in e.get("synonyms", []):
                sw = syn.lower().split()
                if other in sw and word not in sw:
                    self.add("error", "laterality-synonyms", rid, f"synonym names the {other} side: '{syn}'")
            for k in ("containedById", "partOfId"):
                t = e.get(k)
                if t and self.side(t) and self.side(t) != s:
                    self.add("error", "laterality-containers", rid, f"{k} is the opposite-side entry {t} {self.name(t)}")
            exp_id = u + (LEFT if s == "L" else RIGHT)
            if "_" in rid and rid != exp_id:
                self.add("warning", "laterality-ids", rid, f"expected id {exp_id}")

    def check_sex(self):
        for rid, e in self.E.items():
            for k in ("containedById", "partOfId"):
                t = e.get(k)
                if not t or t == rid or t not in self.E:
                    continue
                ts = self.E[t].get("sexSpecific")
                es = e.get("sexSpecific")
                if ts and es and ts != es:
                    self.add("error", "sex-inheritance", rid, f"{es} entry in {ts} entry {t} {self.name(t)}")
                elif ts and not es:
                    self.add("warning", "sex-inheritance", rid, f"no sexSpecific, but its {k} {t} {self.name(t)} is {ts}")

    def check_names(self):
        owners = collections.defaultdict(set)
        for rid, e in self.E.items():
            label = e["description"]
            for text, field in [(label, "description")] + [(s, "synonym") for s in e.get("synonyms", [])]:
                if text != text.strip() or "  " in text:
                    self.add("warning", "text-spacing", rid, f"{field} has extra spaces: '{text}'")
                if re.search(r"\s l\s", text):
                    self.add("warning", "text-joined", rid, f"{field} looks like several names joined with ' l ': '{text}'")
                owners[re.sub(r"\s+", " ", text.strip().lower())].add(rid)
            syns = [s.strip().lower() for s in e.get("synonyms", [])]
            for s, n in collections.Counter(syns).items():
                if n > 1:
                    self.add("warning", "synonym-duplicate", rid, f"synonym '{s}' repeated")
            if label.strip().lower() in syns:
                self.add("warning", "synonym-duplicate", rid, "a synonym repeats the description")
        for text, rids in owners.items():
            if len(rids) > 1:
                for rid in sorted(rids):
                    others = ", ".join(sorted(rids - {rid}))
                    self.add("error", "names-shared", rid, f"'{text}' is also a name of {others}")

    def check_spelling(self, accepted_words=frozenset()):
        """Flag a rare word that is one edit away from a common word in the same file (e.g. 'muslce', 'eight').
        Real words that trip this (e.g. 'hepatis' next to 'hepatic') go in the allow file's "words" list."""
        counts = collections.Counter()
        where = collections.defaultdict(set)
        for rid, e in self.E.items():
            for text in [e["description"]] + e.get("synonyms", []):
                for w in re.findall(r"[a-z]{4,}", text.lower()):
                    counts[w] += 1
                    where[w].add(rid)
        common = [w for w, n in counts.items() if n >= 5]
        by_len = collections.defaultdict(list)
        for w in common:
            by_len[len(w)].append(w)
        for w, n in counts.items():
            if n > 2 or w in accepted_words:
                continue
            near = [c for L in (len(w) - 1, len(w), len(w) + 1) for c in by_len.get(L, []) if c != w and _one_edit(w, c)]
            near = [c for c in near if not _benign_variant(w, c)]
            if near:
                for rid in sorted(where[w]):
                    self.add("warning", "spelling", rid, f"'{w}' is one edit from the common word '{near[0]}'")

    def check_codes(self):
        for rid, e in self.E.items():
            seen = set()
            for c in e.get("codes", []):
                key = (c["system"], c["code"])
                if key in seen:
                    self.add("error", "codes-duplicate", rid, f"{c['system']} {c['code']} listed twice")
                seen.add(key)
                fmt = CODE_FORMATS.get(c["system"])
                if not fmt:
                    self.add("error", "codes-system", rid, f"unknown code system {c['system']}")
                elif not fmt.match(c["code"]):
                    self.add("error", "codes-format", rid, f"malformed {c['system']} code '{c['code']}'")
            s = self.effective_side(rid)
            for code in self.snomed(rid):
                if ":" not in code or not CODE_FORMATS["SNOMED"].fullmatch(code):
                    continue
                focus, val = code.split(":")[0], code.split("=")[1]
                if not s:
                    self.add("error", "snomed-expression", rid, f"laterality expression {code} on an entry that is not a left/right entry")
                    continue
                if (s == "L") != (val == SNOMED_LEFT):
                    self.add("error", "snomed-expression", rid, f"expression {code} has the wrong side")
                if not e.get("unsidedId"):
                    self.add("warning", "snomed-expression", rid, "left/right pair has no unsided entry, so the expression focus cannot be checked")
                    continue
                ucodes = [x for x in self.snomed(e["unsidedId"]) if ":" not in x]
                if ucodes and focus not in ucodes:
                    self.add("error", "snomed-expression", rid, f"expression focus {focus} is not the unsided entry's SNOMED code {ucodes[0]}")
                if not ucodes:
                    self.add("warning", "snomed-expression", rid, "unsided entry has no SNOMED code to match the expression focus")
        shared = collections.defaultdict(set)
        for rid, e in self.E.items():
            for c in e.get("codes", []):
                if ":" not in c["code"]:
                    shared[(c["system"], c["code"])].add(rid)
        for (system, code), rids in shared.items():
            if len(rids) > 1:
                for rid in sorted(rids):
                    self.add("warning", "codes-shared", rid, f"{system} {code} is also on {', '.join(sorted(rids - {rid}))}")

    def check_placement(self):
        for rid, e in self.E.items():
            c = e.get("containedById")
            if not c or c == rid or c not in self.E:
                continue
            cname = self.name(c).lower()
            if re.search(r"\bjoint\b", cname) and BONE_WORDS.search(e["description"].lower()) and "ligament" not in e["description"].lower():
                self.add("warning", "bone-in-joint", rid, f"bone or bone part contained in a joint ({c} {self.name(c)})")
            if SET_WORDS.search(cname):
                self.add("warning", "container-is-set", rid, f"contained in a set or system ({c} {self.name(c)}), which is not a region")
            p = e.get("partOfId")
            if p and p in self.E and p != rid and not SET_WORDS.search(self.name(p).lower()):
                wc = self.E[p].get("containedById")
                mine = self.chain(rid)
                if p not in mine and wc not in mine:
                    self.add("warning", "part-outside-whole", rid,
                             f"part of {p} {self.name(p)} (in {self.name(wc)}) but contained in {self.name(c)}, outside its whole's container")

    def check_definitions(self):
        for rid, e in self.E.items():
            d = e.get("definition")
            if d is None:
                continue
            if "Examples:" in d and "There is only" in d or "There are only" in d:
                self.add("warning", "definition-text", rid, "definition has FMA 'Examples: There is only …' filler")
            if d[:1].islower():
                self.add("warning", "definition-text", rid, "definition starts with a lowercase letter")
            if not re.search(r"[.\])]$", d.strip()):
                self.add("warning", "definition-text", rid, "definition does not end with a period or source tag")

    # ------------------------------------------------------------------ terminology checks (local only)
    def check_terminologies(self, folder: Path):
        import duckdb

        def newest(pattern):
            files = sorted(folder.glob(pattern))
            return files[-1] if files else None

        sn_path, fma_path, ta2_path = newest("snomed_*.duckdb"), newest("fma_*.duckdb"), newest("ta2_*.duckdb")
        if sn_path:
            sn = duckdb.connect(str(sn_path), read_only=True)
            rows = sn.execute("select id, active, fsn, semantic_tag, laterality from concepts").fetchall()
            C = {str(r[0]): r for r in rows}
            for rid, e in self.E.items():
                for code in self.snomed(rid):
                    focus = code.split(":")[0]
                    r = C.get(focus)
                    if not r:
                        self.add("error", "snomed-exists", rid, f"SNOMED {focus} not found in {sn_path.name}")
                        continue
                    _, active, fsn, tag, lat = r
                    if not active:
                        self.add("error", "snomed-active", rid, f"SNOMED {focus} is inactive")
                    if tag != "body structure":
                        self.add("error", "snomed-hierarchy", rid, f"SNOMED {focus} is a {tag}, not a body structure")
                    if fsn.startswith("Entire ") and rid != ROOT_ID:
                        self.add("warning", "snomed-entire", rid, f"SNOMED {focus} is an 'Entire' concept: {fsn}")
                    s = self.effective_side(rid)
                    if ":" in code:
                        if lat not in (182353008,):
                            self.add("warning", "snomed-expression", rid, f"expression focus {focus} is not marked lateralizable")
                    elif s:
                        want = int(SNOMED_LEFT if s == "L" else SNOMED_RIGHT)
                        if lat != want:
                            self.add("error", "snomed-side", rid, f"SNOMED {focus} ({fsn}) does not have the entry's side")
                        ucodes = [x for x in self.snomed(e.get("unsidedId")) if ":" not in x]
                        if ucodes:
                            up = sn.execute("select 1 from isa_closure where descendant=? and ancestor=?", [int(focus), int(ucodes[0])]).fetchone()
                            if not up:
                                self.add("warning", "snomed-side", rid, f"SNOMED {focus} is not a descendant of the unsided entry's {ucodes[0]}")
                    elif lat in (int(SNOMED_LEFT), int(SNOMED_RIGHT)) and (e.get("leftId") or e.get("rightId")):
                        # an inherently sided structure (right lung lobe) is fine; the unsided parent of a pair is not
                        self.add("error", "snomed-side", rid, f"unsided parent of a left/right pair has a sided SNOMED concept {focus} ({fsn})")
        if fma_path:
            fma = duckdb.connect(str(fma_path), read_only=True)
            F = {str(r[0]): r for r in fma.execute("select fma_id, display_name, explicitly_deprecated from concepts where fma_id is not null").fetchall()}
            for rid, e in self.E.items():
                for c in e.get("codes", []):
                    if c["system"] == "FMA":
                        r = F.get(c["code"])
                        if not r:
                            self.add("error", "fma-exists", rid, f"FMA {c['code']} not found in {fma_path.name}")
                        elif r[2]:
                            self.add("error", "fma-deprecated", rid, f"FMA {c['code']} ({r[1]}) is deprecated")
        if ta2_path:
            ta2 = duckdb.connect(str(ta2_path), read_only=True)
            T = {str(r[0]) for r in ta2.execute("select ta2_id from terms").fetchall()}
            for rid, e in self.E.items():
                for c in e.get("codes", []):
                    if c["system"] == "TA2" and c["code"] not in T:
                        self.add("error", "ta2-exists", rid, f"TA2 {c['code']} not found in {ta2_path.name}")
        if not (sn_path or fma_path or ta2_path):
            self.add("error", "terminologies", str(folder), "no snomed_*.duckdb, fma_*.duckdb or ta2_*.duckdb files found")

    def run(self, terminologies: Path | None, accepted_words=frozenset()):
        self.check_schema()
        if any(f.level == "error" for f in self.findings):
            return  # Later checks require schema-valid entries.
        self.check_ids()
        self.check_containment()
        self.check_laterality()
        self.check_sex()
        self.check_names()
        self.check_spelling(accepted_words)
        self.check_codes()
        self.check_placement()
        self.check_definitions()
        if terminologies:
            self.check_terminologies(terminologies)


def _one_edit(a, b):
    """True if a and b differ by one insertion, deletion, substitution, or adjacent swap."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        diff = [i for i in range(len(a)) if a[i] != b[i]]
        return len(diff) == 1 or (len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def _benign_variant(w, c):
    """Plurals, Latin/English endings and US/UK spellings that are not typos."""
    pairs = {(w, c), (c, w)}
    for x, y in pairs:
        if y == x + "s" or y == x + "e" or (x.endswith("us") and y == x[:-2] + "i"):
            return True
        if x.replace("ae", "e") == y.replace("ae", "e") or x.replace("disk", "disc") == y.replace("disk", "disc"):
            return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--data", type=Path, default=REPO / "data" / "body_parts.json")
    ap.add_argument("--schema", type=Path, default=REPO / "data" / "body_parts_schema.json")
    ap.add_argument("--allow", type=Path, default=REPO / "scripts" / "check_ali_allow.json")
    ap.add_argument("--terminologies", type=Path, help="folder with snomed_*.duckdb, fma_*.duckdb, ta2_*.duckdb")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--only", help="comma-separated check names to report")
    ap.add_argument("--summary", action="store_true", help="print counts per check only")
    args = ap.parse_args(argv)

    allow = json.loads(args.allow.read_text()) if args.allow.exists() else {}
    allowed = {(a["check"], a["radlexId"]) for a in allow.get("accepted", [])}
    ck = Checker(args.data, args.schema)
    ck.run(args.terminologies, frozenset(allow.get("words", [])))

    findings = [f for f in ck.findings if f.level != "warning" or (f.check, f.rid) not in allowed]
    n_accepted = len(ck.findings) - len(findings)
    if args.only:
        keep = set(args.only.split(","))
        findings = [f for f in findings if f.check in keep]

    by_check = collections.defaultdict(list)
    for f in findings:
        by_check[(f.level, f.check)].append(f)
    for (level, check), fs in sorted(by_check.items(), key=lambda kv: (kv[0][0] != "error", kv[0][1])):
        print(f"{level.upper()} {check}: {len(fs)}")
        if not args.summary:
            for f in fs:
                label = ck.name(f.rid) if f.rid in ck.E else ""
                print(f"  {f.rid} {label}: {f.message}")
    n_err = sum(f.level == "error" for f in findings)
    n_warn = len(findings) - n_err
    print(f"\n{len(ck.E)} entries checked: {n_err} errors, {n_warn} warnings"
          + (f" ({n_accepted} accepted in {args.allow.name})" if n_accepted else ""))
    return 1 if n_err or (args.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main())

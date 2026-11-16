This repository holds the Anatomic Locations Index (ALI) and its website, https://www.anatomiclocations.org. The ALI is a curated set of anatomic terms for imaging informatics, organized into a containment hierarchy in which each term's chain of enclosing regions ends at the whole body.

- `data/body_parts.json` is the ALI. Its schema is `data/body_parts_schema.json`, and `data/CHANGELOG.md` lists the changes in each release.
- `docs/` is the website, which GitHub Pages builds from the `main` branch.

## Checking the data

`scripts/check_ali.py` checks `data/body_parts.json` for mechanical errors: schema, broken references, containment loops, left/right links and names, sex consistency, shared names, likely typos, and code formats. It runs on every pull request that touches `data/`. To run it locally:

```
uv run scripts/check_ali.py
```

Errors fail the check; warnings are for a person to review. Reviewed warnings and real words the spelling check flags go in `scripts/check_ali_allow.json`. With `--terminologies DIR`, it also checks every SNOMED CT, FMA, and TA2 code against local DuckDB builds of those terminologies (not included in this repository).

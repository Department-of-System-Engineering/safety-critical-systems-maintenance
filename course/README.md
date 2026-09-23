# Course notebooks

The twelve English notebooks follow the sequence in the root README. Each unit combines theory, a small hand calculation, visible Python, result interpretation, the common TK-101 case, exercises and a summary.

Run notebooks from `course/` or from the repository root using a Python kernel with the project dependencies installed. Each notebook runs independently from a fresh kernel. Source notebooks deliberately do not contain stale execution outputs; `scripts/validate_notebooks.py` executes and saves reproducible copies under `build/executed/`.

Unit 4 first explains the legacy exchange representation and then imports a real SysML v2 reference-tool export. Unit 12 uses the native export as its system-model source. Changing `.sysml` requires regenerating the export; the provenance test rejects an out-of-date source/export pair.

Week 7 is the intermediate checkpoint and week 14 is the final assessment. The teaching scope is two teaching periods per week; advanced extensions can be assigned as independent project work.

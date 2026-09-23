# Validation evidence

`sysml_provenance.json` and `sysml_validation.log` record the successful native-tool run for the checked-in source/export pair. The manifest identifies the tool version, source commit, run ID and source/export SHA-256 hashes. `models/sysml/tk101.export.json` is the full, unmodified native JSON export.

Reference validation run: https://github.com/ruptomi22/safety-critical-systems-maintenance/actions/runs/35839002637

The regression test `test_native_export_provenance` checks the manifest hashes. Other adapter tests verify the transformation against hand calculations and the independent legacy YAML model, including minimal cut sets. Unit 4 demonstrates both routes; unit 12 starts from the native export. All inputs remain synthetic.

`baseline_results.json` contains the deterministic adapter/FTA output for this fixture. Reproduce it with the CLI described in the root README. Current test and notebook-execution logs are published as GitHub Actions artifacts rather than embedded as stale success claims in the source. A workflow configuration alone is not proof that its latest run passed; inspect the relevant run.

No native validation, adapter regression or notebook test is an industrial pilot, safety certification or contractual acceptance decision.

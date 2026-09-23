# Native SysML v2 to fault-tree adapter

## Scope

The input is a **native metamodel JSON export** produced by the SysML v2 Pilot Implementation, not a handwritten "SysML-like" JSON file. The workflow is:

```text
models/sysml/tk101.sysml
  -> official SysML v2 Pilot parser and validator
  -> models/sysml/tk101.export.json
  -> safetycourse.sysml_adapter
  -> risk-model exchange dictionary / YAML
  -> safetycourse.model_io.generate_fault_tree
  -> FTA probability, minimal cut sets and source traceability
```

The source is authored in SysML v2 textual notation and successfully checked by the reference implementation. Python handles a **bounded metamodel mapping**, not the full SysML syntax or semantics. There is no AADL or Simulink adapter.

## Supported annotation contract

A selected package contains `PROJECT_ID` and `DATA_STATUS` string attributes, two named part definitions, typed part usages, and Boolean hazard attributes.

| Source construct | Meaning in this demonstrator |
|---|---|
| `part def SafetyComponent` | Definition of an annotated component with one failure mode |
| `componentType`, `functionName` | Component category and required function |
| `failureId`, `failureLabel`, `failureMode` | Stable risk-event identifier, label and mode |
| `probability : Real` | Synthetic basic-event probability in [0, 1] |
| `failed : Boolean` | Failure occurrence variable, not a probability |
| `part def RiskEvent` | External or system-level event with `label`, `probability` and `occurs` |
| `attribute OVERFLOW : Boolean = ...` | Explicit engineering failure-propagation expression |
| `and`, `or`, parentheses | Coherent Boolean hazard logic mapped into FTA gates |
| Hazard-to-hazard references | Acyclic expansion of a previously defined expression |

The adapter follows real exported `PartUsage`, `PartDefinition`, `AttributeUsage`, `FeatureValue`, literal, `OperatorExpression`, `FeatureReferenceExpression` and `FeatureChainExpression` elements by their IDs. Parenthesized expressions may be represented as expression references by the exporter; these are resolved, not parsed as text.

Only an explicitly valued, single annotated failure mode per component is supported. Unsupported part types, operators, missing values, required unresolved references, duplicate IDs and cycles raise an error. Other SysML constructs, multiplicity-dependent reliability, dynamic event gates and automatic hazard discovery are outside the contract. Native validation must precede adaptation; passing this adapter alone is not a general SysML validation result.

## Engineering assumptions

Hazard logic is supplied in the native model by the engineer. Physical component connections do not uniquely determine failure propagation, and this implementation does not infer the missing logic. Probability parameters share an illustrative exposure basis; no plant-calibrated time horizon is asserted. The FTA evaluator assumes independent immediate inputs and rejects a repeated basic event rather than silently applying independence to shared events. Common-cause mechanisms need an explicitly appropriate model.

The legacy `data/pundit_case/system_model.yaml` remains an independent teaching/reference input. Its nested `hazards.logic` is compared with the SysML-derived logic by their probabilities and minimal cut sets, not by auto-generated gate names.

## CLI and outputs

```bash
python -m safetycourse.sysml_adapter models/sysml/tk101.export.json --output-dir build/sysml
# Equivalent installed entry point:
safetycourse-sysml models/sysml/tk101.export.json --package TK101Study --output-dir build/sysml
```

The command produces a risk exchange YAML file, FTA JSON files, `results.json` and `traceability.csv`. Each trace row identifies a source metamodel element, target ID and target path. The risk-model metadata records the imported export's SHA-256 hash. Generated FTA nodes retain their source element IDs.

## Native validation and export regeneration

The separate GitHub Actions workflow `sysml-reference` installs the pinned `jupyter-sysml-kernel=0.62.0` and Java 21 in an isolated Conda environment. It compiles `scripts/ExportSysML.java`, loads the standard library, processes the source and checks `hasErrors()` before exporting. Its artifact includes the source, JSON export, validation log and hash manifest. A successful fresh run is required when the source changes.

To run the same process locally after installing that reference-tool environment:

```bash
mkdir -p build/native
JAR=$(python scripts/locate_sysml_runtime.py --field jar)
LIB=$(python scripts/locate_sysml_runtime.py --field library)
javac -cp "$JAR" -d build/native scripts/ExportSysML.java
java -Xmx3g -cp "$JAR:build/native" ExportSysML "$LIB" models/sysml/tk101.sysml TK101Study build/native/tk101.export.json
```

The locator selects the JAR by its `SysMLInteractive` class, not by a directory-name match that could select an unrelated Java runtime archive.

After a successful run, replace the checked-in export and refresh `evidence/sysml_provenance.json` and `evidence/sysml_validation.log` together. Do not edit the export manually and call it a reference-tool result. Exported element UUIDs can change between reference-tool runs; semantic regression results must remain equivalent. Provenance tests check the source/export bytes against their recorded run, not global UUID stability.

## Evidence and limitations

The recorded run validates the actual native model and exports its metamodel. Adapter tests reproduce both top events, four/eight minimal cut sets and source mappings; mutation tests check rejected inputs and numerical sensitivity. Mutation tests are deliberately separate from native-language validation.

This establishes an executable, restricted **SysML-model-to-risk-model transformation** for a synthetic example. It does not establish an industrially validated PUNDIT installation, all possible SysML model imports, a complete Dynamic HAZOP methodology, or formal funding-body acceptance. No new contribution is attributed to the University of Stuttgart without separate evidence.

## Primary technical sources

- SysML v2 Pilot Implementation: https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation
- Reference release and installation: https://github.com/Systems-Modeling/SysML-v2-Release/tree/2026-08/install/jupyter
- The inspected reference API is `org.omg.sysml.interactive.SysMLInteractive`: `loadLibrary`, `process` and `export`.

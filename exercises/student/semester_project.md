# Semester project - student brief

Choose a small safety-critical or high-availability engineering system that can be modeled meaningfully with 6-15 relevant failure events.

## Required elements

1. System boundary and functions.
2. PHA, FMEA and a compact HAZOP.
3. An FTA with at least six basic events.
4. Minimal cut sets and at least one importance/sensitivity analysis.
5. A structured risk exchange model and deterministic model-to-FTA transformation.
6. A Bayesian diagnostic question.
7. A Markov model with at least three states.
8. Monte Carlo analysis or uncertainty propagation.
9. Common-cause and dependency considerations.
10. A sensor/evidence demonstration.
11. A risk-informed maintenance decision.
12. Assumptions, limitations and a validation plan.

Synthetic numerical data are permitted but must be explicitly identified. Use industrial data only with appropriate permission.

## Native SysML extension

Start from `models/sysml/tk101.sysml`, change a supported part annotation or hazard expression, regenerate the export using the reference tool, and import it with `safetycourse.sysml_adapter`. Submit the source, the real tool export, source/export hashes, generated FTA and comparison with a hand calculation. A hand-edited JSON fixture tests the adapter but does not count as a newly validated SysML source/export pair.

The advanced extension does not require implementing an industrial SysML tool or using AADL/Simulink.

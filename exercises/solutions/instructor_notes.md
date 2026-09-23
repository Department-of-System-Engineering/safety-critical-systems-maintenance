# Instructor notes for the semester project

Prioritize consistent event semantics, source-to-result traceability, explicit assumptions, correct probability calculations, dependency recognition, separation of prior and evidence, reproducible code, and a defensible maintenance decision rather than model size.

Critical errors include treating RPN as a universal acceptance limit; assuming dependent redundant channels are independent without justification; converting a forecast directly into an FMEA rating or Markov transition; and presenting synthetic data as measurements.

## Scope and interpretation

The introductory FMEA notebook and the separate `failure_modes.yaml` exercise use different synthetic detection ratings for some items. They are distinct classroom scenarios, not a single calibrated data set. State which scenario is being used before comparing results.

The aggregated TK-101 CTMC merges histories at the challenge state; it is a state-evolution example, not a calibrated demonstration of the effect of sensor repair on accident risk. Occupancy at time t is not the probability of visiting that state before t. The residual-to-probability sigmoid is an uncalibrated proxy, not a validated posterior model. Discuss these limitations when assessing the integrated case.

The native SysML adapter supports a restricted annotation contract. Students should demonstrate an actual reference-tool export and numerical equivalence, not claim safety certification or automatic hazard discovery.

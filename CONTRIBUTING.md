# Contributing

## Teaching-content rules

1. Keep Hungarian explanatory text concise and technically explicit.
2. Use accepted English technical terms in parentheses where useful.
3. Keep equations LaTeX-compatible.
4. Label synthetic data explicitly.
5. Do not present fixed FMEA RPN thresholds as universal acceptance criteria.
6. Do not assume independence without stating it.
7. Do not map forecast probabilities directly to FMEA occurrence or Markov rates without a documented calibration model.
8. Treat the YAML model as a simplified SysML-derived exchange representation unless a native importer is actually implemented.
9. Keep PUNDIT educational-exploitation wording separate from technical-deliverable claims.
10. Put reusable algorithms in `src/safetycourse/`, not duplicated across notebooks.

## Validation

Before merging:

```bash
pytest -q
quarto render
```

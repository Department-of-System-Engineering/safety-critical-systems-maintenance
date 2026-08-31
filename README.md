# Safety-Critical Systems and Maintenance

Hungarian Quarto/Jupyter teaching material for the University of Pannonia course **Biztonságkritikus rendszerek és karbantartás**.

## Scope

The repository integrates:

- reliability and quantitative risk foundations;
- PHA, FMEA and HAZOP;
- Fault Tree Analysis and minimal cut sets;
- simplified SysML-derived model-to-FTA transformation;
- Bayesian networks and FTA-to-BN reasoning;
- Markov models and Dynamic HAZOP concepts;
- Monte Carlo and rare-event simulation;
- redundancy, dependencies and cascading effects;
- corrective, preventive, condition-based, predictive and risk-based maintenance;
- fault diagnosis and sensor evidence;
- dynamic risk updating and maintenance decision support;
- one semester-long TK-101 case study.

## PUNDIT note

The material supports educational exploitation of PUNDIT project results (`2020-1.2.3-EUREKA-2022-00021`). It does **not** constitute evidence that any original technical project deliverable has been completed.

## Quick start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -e .[dev]
quarto render
```

HTML and PDF outputs are generated under `_book/`.

## Tests

```bash
pytest
```

## Repository layout

- `chapters/` – Quarto teaching chapters
- `notebooks/` – executable teaching notebooks
- `src/safetycourse/` – reusable Python functions
- `data/pundit_case/` – synthetic educational case data
- `exercises/` – student and instructor task sheets
- `project/pundit_traceability.yml` – educational exploitation traceability
- `.github/workflows/` – automated test/render workflow

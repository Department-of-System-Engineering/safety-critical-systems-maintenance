# Safety-Critical Systems and Maintenance

An executable, English-language course and risk-analysis demonstrator developed for the University of Pannonia. Twelve Jupyter notebooks connect reliability, hazard analysis and maintenance decisions through the synthetic **TK-101 flammable-liquid receiving and storage system**.

## What is implemented

- PHA, FMEA, HAZOP, fault trees, minimal cut sets and importance analysis.
- Bayesian diagnosis, Markov state dynamics, Monte Carlo examples, redundancy and risk-informed maintenance.
- **Native SysML v2 model -> reference-tool JSON export -> Python adapter -> risk model -> FTA**, with source-element traceability and regression tests.

The native model is parsed and validated by the **SysML v2 Pilot Implementation 0.62.0**. The Python adapter resolves that tool's actual metamodel export; it does not rename handwritten YAML as SysML. It supports a deliberately limited risk-annotation contract, not the entire SysML language, AADL or Simulink. See [adapter documentation](docs/sysml_adapter.md).

## Start in a browser

Open **Code -> Codespaces -> Create codespace on main**. The development container installs the project and notebook dependencies. Open `course/01_SAFETY_CRITICAL_FOUNDATIONS.ipynb`, select the Python kernel and execute cells or use **Run All**. Codespaces availability and usage depend on the account's GitHub settings and quota.

## Local installation

Python 3.10 or newer is required. CI uses Python 3.12.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
jupyter lab
```

Ordinary notebook use does not need Java or a SysML installation: a genuine reference-tool export is included. To change the SysML model, regenerate that export using the documented reference-tool workflow.

## Run the native SysML demonstration

From the repository root:

```bash
python -m safetycourse.sysml_adapter models/sysml/tk101.export.json --output-dir build/sysml
```

This writes `system_model.yaml`, two `*.fta.json` files, `traceability.csv` and `results.json`. With the supplied synthetic input:

| Top event | Probability | Minimal cut sets |
|---|---:|---:|
| `OVERFLOW` | 0.0000708032 | 4 |
| `ESCALATED_FIRE` | 0.00000048854208 | 8 |

These are probabilities under the declared independent-event assumptions and the common illustrative exposure basis, **not calibrated per-hour failure rates or industrial safety limits**. They are checked against both hand calculations and the legacy YAML model. Model annotations supply the failure logic; it is not inferred from equipment topology.

## Course sequence

Each unit follows **theory -> hand example -> visible Python -> interpretation -> TK-101 application -> exercises -> summary**.

| Week | Notebook / activity |
|---:|---|
| 1 | [Safety-critical foundations](course/01_SAFETY_CRITICAL_FOUNDATIONS.ipynb) |
| 2 | [PHA, FMEA and HAZOP](course/02_PHA_FMEA_HAZOP.ipynb) |
| 3 | [Fault-tree analysis](course/03_FTA.ipynb) |
| 4 | [Model-based risk analysis and native SysML import](course/04_MODEL_BASED_RISK.ipynb) |
| 5 | [Bayesian networks](course/05_BAYESIAN_NETWORKS.ipynb) |
| 6 | [Markov models and Dynamic HAZOP](course/06_MARKOV_DYNAMIC_HAZOP.ipynb) |
| 7 | Intermediate assessment / integration checkpoint |
| 8 | [Monte Carlo and rare events](course/07_MONTE_CARLO_RARE_EVENTS.ipynb) |
| 9 | [Redundancy and dependencies](course/08_REDUNDANCY_DEPENDENCIES.ipynb) |
| 10 | [Maintenance strategies](course/09_MAINTENANCE_STRATEGIES.ipynb) |
| 11 | [Fault diagnosis](course/10_FAULT_DIAGNOSIS.ipynb) |
| 12 | [Dynamic risk and RBM](course/11_DYNAMIC_RISK_RBM.ipynb) |
| 13 | [Integrated PUNDIT case](course/12_PUNDIT_INTEGRATED_CASE.ipynb) |
| 14 | Final assessment / project presentations |

## Verification

```bash
python -m pytest -q
python scripts/validate_notebooks.py
```

The first command checks the adapter, model-to-FTA equivalence, provenance hashes, failure cases and existing numerical utilities. The second executes all twelve notebooks from separate clean kernels, saving outputs under ignored `build/`. GitHub Actions performs the same checks; a separate workflow validates the native SysML model with the reference tool and archives its export and log.

## Repository map

- `course/`: English teaching notebooks.
- `models/sysml/`: native source and actual reference-tool export.
- `src/safetycourse/`: reusable numerical utilities and the SysML adapter.
- `data/pundit_case/`: synthetic data and the legacy exchange-model exercise.
- `tests/`: numerical, adapter and provenance tests.
- `scripts/`: notebook validation and native-model export helper.
- `evidence/`: recorded native-validation provenance and results.
- `docs/`: adapter contract and reproduction guide.
- `exercises/`: student brief and instructor notes.
- `project/`: PUNDIT traceability and source register.

## PUNDIT and evidence boundaries

Project identifier: **2020-1.2.3-EUREKA-2022-00021**.

This repository supports PUNDIT educational exploitation and documents a restricted technical demonstration. The TK-101 data are synthetic, and the example is not the industrial pilot. A passing test demonstrates the tested calculation or transformation, not physical validation, safety certification, or automatic contractual acceptance. The teaching disclaimer remains in place; the native adapter's demonstrated scope is recorded separately in [project traceability](project/pundit_traceability.yml) and [validation evidence](evidence/README.md).

Original internal source filenames are retained in the source register for attribution. The repository's current teaching text, code comments, labels, exercise instructions and documentation are in English. Earlier Hungarian versions remain available in Git history.

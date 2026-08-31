# Source register

This register documents the internal teaching/project materials that informed the redesign. Source files are **not redistributed in this repository**.

## PUNDIT project sources

- `137479601.pdf` – Hungarian national application.
- `2021-17454_NP_BILAT_HU_DE_1 PUNDIT.pdf` – international EUREKA proposal.
- PUNDIT progress reports.
- `PUNDIT_zaro_feladatok.docx` – closing-task status and educational exploitation record.
- `ASME_journal_SLR_RiskCPS_Revision.pdf` – risk/CPS research material.

## Existing course sources reused conceptually

- `03_FMEA_PHA.pptx` – PHA/FMEA foundations.
- `Graf_alapu_elemzesi_technikak.pptx` – fault tree and MATLAB node representation.
- `04_Markov_modell.pdf` – Markov foundations.
- `02_Monte_Carlo.pdf` – Monte Carlo foundations.
- `hibadiagnosztika_eloadas.pptx` – fault diagnosis foundations.
- `Bizt_krit_Karbantartási_stratégiák_életciklusa_SZJ_20250920.pptx` – maintenance strategies.
- `10_Kockazatalapu_karbantartas_vDA2.pptx/.pdf` – risk-based maintenance and the original tank/barrier scenario.
- `BiztKrit_ARIMA_másmodellek_SZJ_20250920.pptx` – optional prognostic integration ideas.
- `02_Redundans_rendszerek-2.pdf` – redundancy foundations.
- `02_Kvantitativ_megbizhatosag.pdf` – quantitative reliability foundations.

## Migration rules applied

- Fixed RPN thresholds are not treated as universal acceptance limits.
- TBM is Time-Based Maintenance; UBM is Usage-Based Maintenance.
- Forecast probability is not automatically converted to FMEA occurrence score or Markov transition probability.
- Normal forecast errors are not assumed without model justification.
- MATLAB FTA examples are reimplemented in Python.
- SysML is represented initially by a simplified SysML-derived YAML exchange model; no native SysML parser is claimed.
- PUNDIT linkage is educational exploitation only unless separately demonstrated by project technical evidence.

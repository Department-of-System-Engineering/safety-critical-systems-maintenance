from pathlib import Path

QUARTO = '''project:
  type: book
  output-dir: _book
  execute-dir: project

book:
  title: "Biztonságkritikus rendszerek és karbantartás"
  subtitle: "Notebook-alapú interaktív egyetemi jegyzet"
  author: "Pannon Egyetem – Rendszer- és Számítástudományi Tanszék"
  date: today
  chapters:
    - index.qmd
    - course/01_BIZTONSAGKRITIKUS_ALAPOK.ipynb
    - course/02_PHA_FMEA_HAZOP.ipynb
    - course/03_FTA.ipynb
    - course/04_MODELLALAPU_KOCKAZAT.ipynb
    - course/05_BAYES_HALOK.ipynb
    - course/06_MARKOV_DYNAMIC_HAZOP.ipynb
    - course/07_MONTE_CARLO_RITKA_ESEMENYEK.ipynb
    - course/08_REDUNDANCIA_FUGGOSEGEK.ipynb
    - course/09_KARBANTARTASI_STRATEGIAK.ipynb
    - course/10_HIBADIAGNOSZTIKA.ipynb
    - course/11_DINAMIKUS_KOCKAZAT_RBM.ipynb
    - course/12_PUNDIT_INTEGRALT_ESET.ipynb
  appendices:
    - appendices/python_gyorstalpalo.qmd
    - appendices/jelolesek.qmd
  repo-url: https://github.com/ruptomi22/safety-critical-systems-maintenance
  repo-actions: [edit, issue]

bibliography: references.bib
lang: hu

format:
  html:
    theme: cosmo
    toc: true
    number-sections: true
    code-fold: false
    code-tools: true
    fig-align: center
    link-external-newwindow: true
  pdf:
    documentclass: scrreprt
    pdf-engine: xelatex
    papersize: a4
    toc: true
    number-sections: true

execute:
  echo: true
  warning: false
  error: false
  freeze: auto

jupyter: python3
'''

README = '''# Safety-Critical Systems and Maintenance

Notebook-first, böngészőből futtatható magyar egyetemi tananyag a Pannon Egyetem **Biztonságkritikus rendszerek és karbantartás** kurzusához.

## Elsődleges tananyag

A `course/` mappában 12, teljes tanegységként felépített Jupyter notebook található. A notebookok felépítése következetesen:

**elmélet → kézi/egyszerű példa → látható Python → eredményértelmezés → TK-101 alkalmazás → Próbáld ki! → összefoglalás**.

| Hét | Notebook |
|---:|---|
| 1 | `01_BIZTONSAGKRITIKUS_ALAPOK.ipynb` |
| 2 | `02_PHA_FMEA_HAZOP.ipynb` |
| 3 | `03_FTA.ipynb` |
| 4 | `04_MODELLALAPU_KOCKAZAT.ipynb` |
| 5 | `05_BAYES_HALOK.ipynb` |
| 6 | `06_MARKOV_DYNAMIC_HAZOP.ipynb` |
| 7 | 1. ZH / integrációs checkpoint |
| 8 | `07_MONTE_CARLO_RITKA_ESEMENYEK.ipynb` |
| 9 | `08_REDUNDANCIA_FUGGOSEGEK.ipynb` |
| 10 | `09_KARBANTARTASI_STRATEGIAK.ipynb` |
| 11 | `10_HIBADIAGNOSZTIKA.ipynb` |
| 12 | `11_DINAMIKUS_KOCKAZAT_RBM.ipynb` |
| 13 | `12_PUNDIT_INTEGRALT_ESET.ipynb` |
| 14 | 2. ZH / projektbemutatók |

## Böngészőből futtatás

1. Nyisd meg a repositoryt GitHubon.
2. **Code → Codespaces → Create codespace on main**.
3. Nyisd meg a `course/` mappából a kívánt notebookot.
4. Futtasd a cellákat felülről lefelé.

A Codespace Python/Jupyter/Quarto környezetet kap. Helyi telepítés nem szükséges.

## Közös TK-101 eset

A félév során ugyanaz az éghető folyadék fogadó- és tárolórendszer fejlődik tovább:

**system → hazards → PHA/FMEA/HAZOP → FTA → model-to-FTA → Bayes → Markov/Dynamic HAZOP → Monte Carlo → dependencies → maintenance → diagnosis → dynamic risk → RBM decision**.

## PUNDIT

A tananyag a PUNDIT projekt (`2020-1.2.3-EUREKA-2022-00021`) eredményeinek **oktatási hasznosítását** támogatja. Nem helyettesíti és önmagában nem igazolja a projekt eredeti műszaki vállalásainak teljesítését.

## Technikai rétegek

- `course/` – elsődleges, futtatható tananyag;
- `src/safetycourse/` – tesztelt háttérfüggvények validációhoz/integrációhoz;
- `data/pundit_case/` – szintetikus oktatási case-adatok;
- `chapters/` – korábbi Quarto szöveges referenciaanyag;
- `_quarto.yml` – a notebookokból HTML/PDF könyv export;
- `tools/course_*.py` – determinisztikus notebook-generátor;
- `project/pundit_traceability.yml` – educational-exploitation traceability.

## Ellenőrzés

```bash
pytest -q
quarto render
```

A GitHub workflow a generált notebookokat tiszta kernelből végigfuttatja commit előtt.
'''

INDEX = '''# Biztonságkritikus rendszerek és karbantartás

Ez a kurzus **notebook-first** tananyag: a teljes tanulási folyamat a `course/` Jupyter notebookjaiban található, magyarázó Markdown cellákkal, képletekkel, lépésről lépésre felépített Python-kóddal, ábrákkal, TK-101 példákkal és hallgatói feladatokkal.

A Quarto ennek publikációs/export rétege, nem külön elsődleges tananyag.

## Tanulási ív

**rendszer → veszély → failure mode → PHA/FMEA/HAZOP → FTA → model-based risk → Bayes → Markov → Monte Carlo → függőségek → maintenance → diagnosis → dynamic risk → RBM decision**

A közös esettanulmány a **TK-101 éghető folyadék fogadó- és tárolórendszer**.

::: {.callout-note title="PUNDIT educational exploitation"}
A tananyag a PUNDIT projekt (`2020-1.2.3-EUREKA-2022-00021`) eredményeinek oktatási hasznosítását támogatja; nem helyettesíti és nem igazolja önmagában a projekt eredeti műszaki vállalásainak teljesítését.
:::
'''

TRACE = '''project_id: 2020-1.2.3-EUREKA-2022-00021
project_name: PUNDIT
purpose: educational_exploitation
technical_deliverable_claim: false
primary_artifact_type: executable_teaching_notebook
disclaimer: >-
  Az itt bemutatott oktatási demonstráció a PUNDIT projekt eredményeinek
  oktatási hasznosítását támogatja; nem helyettesíti és nem igazolja önmagában
  a projekt eredeti műszaki vállalásainak teljesítését.
chapters:
  - {chapter: 01, topic: "Reliability and risk foundations", pundit_link: "risk-based maintenance foundations", artifact: "course/01_BIZTONSAGKRITIKUS_ALAPOK.ipynb"}
  - {chapter: 02, topic: "PHA, FMEA, HAZOP", pundit_link: "hazard identification and process safety analysis", artifact: "course/02_PHA_FMEA_HAZOP.ipynb"}
  - {chapter: 03, topic: "Fault Tree Analysis", pundit_link: "probabilistic risk models", artifact: "course/03_FTA.ipynb"}
  - chapter: 04
    topic: Model-Based Risk Analysis
    pundit_link: automated derivation of risk models from system models
    artifact: course/04_MODELLALAPU_KOCKAZAT.ipynb
    representation_note: simplified SysML-derived representation; not a native SysML parser
  - {chapter: 05, topic: "Bayesian networks", pundit_link: "combined probabilistic models and diagnostic inference", artifact: "course/05_BAYES_HALOK.ipynb"}
  - {chapter: 06, topic: "Markov models and Dynamic HAZOP", pundit_link: "dynamic risk modelling", artifact: "course/06_MARKOV_DYNAMIC_HAZOP.ipynb"}
  - {chapter: 07, topic: "Monte Carlo and rare events", pundit_link: "uncertainty-aware risk estimation", artifact: "course/07_MONTE_CARLO_RITKA_ESEMENYEK.ipynb"}
  - {chapter: 08, topic: "Redundancy and dependencies", pundit_link: "system-level risk dependencies", artifact: "course/08_REDUNDANCIA_FUGGOSEGEK.ipynb"}
  - {chapter: 09, topic: "Maintenance strategies", pundit_link: "risk-based maintenance decision context", artifact: "course/09_KARBANTARTASI_STRATEGIAK.ipynb"}
  - {chapter: 10, topic: "Fault diagnosis and sensor evidence", pundit_link: "condition monitoring and digital-twin evidence", artifact: "course/10_HIBADIAGNOSZTIKA.ipynb"}
  - {chapter: 11, topic: "Dynamic risk and RBM", pundit_link: "dynamic risk-based maintenance support", artifact: "course/11_DINAMIKUS_KOCKAZAT_RBM.ipynb"}
  - {chapter: 12, topic: "Integrated TK-101 case", pundit_link: "integrated educational demonstration", artifact: "course/12_PUNDIT_INTEGRALT_ESET.ipynb"}
'''

DEPRECATED = '''# Deprecated short demos

A korábbi rövid demonstrációs notebookokat a teljes, notebook-first tananyag váltotta fel.

Az elsődleges notebookok a [`../course/`](../course/) mappában találhatók.
'''


def main():
    Path('_quarto.yml').write_text(QUARTO, encoding='utf-8')
    Path('README.md').write_text(README, encoding='utf-8')
    Path('index.qmd').write_text(INDEX, encoding='utf-8')
    Path('project/pundit_traceability.yml').write_text(TRACE, encoding='utf-8')
    Path('notebooks').mkdir(exist_ok=True)
    for p in Path('notebooks').glob('*.ipynb'):
        p.unlink()
    Path('notebooks/README.md').write_text(DEPRECATED, encoding='utf-8')
    print('Notebook-first repository structure finalized.')


if __name__ == '__main__':
    main()

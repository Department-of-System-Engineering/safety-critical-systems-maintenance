# Safety-Critical Systems and Maintenance

Notebook-first, böngészőből futtatható magyar egyetemi tananyag a Pannon Egyetem **Biztonságkritikus rendszerek és karbantartás** kurzusához.

## Tananyag

A `course/` mappában 12 Jupyter notebook található. Minden tanegység ugyanazt a logikát követi:

**elmélet → egyszerű/kézi példa → látható Python → eredményértelmezés → TK-101 alkalmazás → Próbáld ki! → összefoglalás**.

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

## Futtatás böngészőből

1. **Code → Codespaces → Create codespace on main**.
2. Nyisd meg a `course/01_BIZTONSAGKRITIKUS_ALAPOK.ipynb` fájlt.
3. Válaszd a Python kernelt.
4. Haladj cellánként, vagy használd a **Run All** parancsot.

Helyi telepítés nem szükséges.

## Közös eset

A 12 notebook ugyanazt a TK-101 éghető folyadék fogadó- és tárolórendszert építi tovább:

**system → hazards → PHA/FMEA/HAZOP → FTA → model-to-FTA → Bayes → Markov/Dynamic HAZOP → Monte Carlo → dependencies → maintenance → diagnosis → dynamic risk → RBM decision**.

## Repository

- `course/` – elsődleges tananyag;
- `data/pundit_case/` – szintetikus oktatási adatok;
- `src/safetycourse/` – újrahasznosítható háttérfüggvények;
- `tests/` – unit tesztek;
- `exercises/` – féléves hallgatói projekt és oktatói megjegyzések;
- `project/` – PUNDIT educational-exploitation traceability és forrásregiszter;
- `.devcontainer/` – böngészős Codespaces környezet;
- `.github/workflows/validate.yml` – automatikus teszt és notebook-futtatás.

## PUNDIT

A tananyag a PUNDIT projekt (`2020-1.2.3-EUREKA-2022-00021`) eredményeinek **oktatási hasznosítását** támogatja. Nem helyettesíti és önmagában nem igazolja a projekt eredeti műszaki vállalásainak teljesítését.

## Validáció

A GitHub Actions minden módosításnál lefuttatja a Python-teszteket és mind a 12 notebookot tiszta kernelből.

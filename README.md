# Safety-Critical Systems and Maintenance

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

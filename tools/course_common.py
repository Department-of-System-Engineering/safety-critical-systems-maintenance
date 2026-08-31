from __future__ import annotations

import json
from pathlib import Path

DISCLAIMER = (
    "**PUNDIT kapcsolat.** Ez a tanegység a PUNDIT projekt "
    "(`2020-1.2.3-EUREKA-2022-00021`) eredményeinek **oktatási hasznosítását** "
    "támogatja; önmagában nem helyettesíti és nem igazolja a projekt eredeti "
    "műszaki vállalásainak teljesítését."
)

SETUP = '''from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path.cwd()
if not (ROOT / "data").exists():
    ROOT = ROOT.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
print("Projekt gyökér:", ROOT)
'''


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip() + "\n"}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip() + "\n",
    }


def notebook(title: str, week: str, objectives: list[str], cells: list[dict]) -> dict:
    intro = "# " + title + "\n\n" + f"**{week}. tanegység · javasolt idő: 2 × 50 perc**\n\n"
    intro += "## Tanulási célok\n\n" + "\n".join(f"- {x}" for x in objectives)
    intro += "\n\n" + DISCLAIMER
    return {
        "cells": [md(intro), code(SETUP)] + cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_notebook(filename: str, nb: dict) -> None:
    out = Path("course")
    out.mkdir(parents=True, exist_ok=True)
    (out / filename).write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


def exercise(items: list[str]) -> dict:
    return md("## Próbáld ki!\n\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(items)))


def summary(text: str) -> dict:
    return md("## Összefoglalás\n\n" + text)

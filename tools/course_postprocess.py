from __future__ import annotations

import json
from pathlib import Path


def patch_model_based_notebook() -> None:
    path = Path('course/04_MODELLALAPU_KOCKAZAT.ipynb')
    nb = json.loads(path.read_text(encoding='utf-8'))
    marker = '## 6. Teljes TK-101 modell betöltése'
    idx = next(i for i, c in enumerate(nb['cells']) if c['cell_type'] == 'markdown' and marker in c['source'])
    source = '''# A teljes TK-101 modell basic_events elemeket is használ, ezért kiterjesztjük a katalógust.
def catalog(m):
    cat = {}
    for component in m.get("components", []):
        for fm in component.get("failure_modes", []):
            cat[fm["id"]] = {**fm, "component": component["id"]}
    for event in m.get("basic_events", []):
        cat[event["id"]] = {**event, "component": "system/basic_event"}
    return cat
'''
    cell = {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': source,
    }
    nb['cells'].insert(idx, cell)
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding='utf-8')


def validate_json() -> None:
    paths = sorted(Path('course').glob('*.ipynb'))
    if len(paths) != 12:
        raise RuntimeError(f'Expected 12 notebooks, found {len(paths)}')
    for path in paths:
        nb = json.loads(path.read_text(encoding='utf-8'))
        if nb.get('nbformat') != 4:
            raise RuntimeError(f'Invalid nbformat: {path}')
        markdown = [c for c in nb['cells'] if c['cell_type'] == 'markdown']
        code = [c for c in nb['cells'] if c['cell_type'] == 'code']
        if len(markdown) < 6 or len(code) < 3:
            raise RuntimeError(f'Notebook too thin: {path}')
        if not any('Próbáld ki!' in c['source'] for c in markdown):
            raise RuntimeError(f'Missing exercise section: {path}')
        if not any('Összefoglalás' in c['source'] for c in markdown):
            raise RuntimeError(f'Missing summary: {path}')
        if not any('PUNDIT' in c['source'] for c in markdown):
            raise RuntimeError(f'Missing PUNDIT educational note: {path}')


if __name__ == '__main__':
    patch_model_based_notebook()
    validate_json()
    print('Generated notebook structure: OK')

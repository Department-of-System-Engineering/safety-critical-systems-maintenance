"""Run all course notebooks with separate clean kernels and save build artifacts."""
import json
from pathlib import Path
import time

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
paths = sorted((ROOT / "course").glob("*.ipynb"))
assert len(paths) == 12, f"Expected 12 course notebooks, found {len(paths)}"
output = ROOT / "build/executed"
output.mkdir(parents=True, exist_ok=True)
results = []
for path in paths:
    start = time.monotonic()
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    print(f"Executing {path.name}", flush=True)
    ExecutePreprocessor(timeout=180, kernel_name="python3").preprocess(
        notebook, {"metadata": {"path": str(path.parent)}})
    nbformat.write(notebook, output / path.name)
    results.append({"notebook": path.name, "status": "passed",
                    "elapsed_seconds": round(time.monotonic() - start, 3)})
(output.parent / "notebook_validation.json").write_text(json.dumps(results, indent=2) + "\n")
print(f"All {len(results)} notebooks passed with clean kernels.")

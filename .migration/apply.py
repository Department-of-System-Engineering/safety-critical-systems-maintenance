"""Apply the reviewed migration, refusing any source or artifact mismatch."""
from pathlib import Path
import hashlib
import json
import lzma
import shutil
import subprocess

ROOT = Path.cwd().resolve()
EXPECTED = 'a4310c944eff9e3b3f53a2c73dce60d4bc740fb48ecd5c7fbb9b3793216d2a6e'
chunks = sorted((ROOT / '.migration').glob('part*.xz'))
assert len(chunks) == 6
payload = b''.join(path.read_bytes() for path in chunks)
assert len(payload) == 42164
assert hashlib.sha256(payload).hexdigest() == EXPECTED
bundle = json.loads(lzma.decompress(payload))
subprocess.run(['git', 'merge-base', '--is-ancestor', bundle['base_commit'], 'HEAD'], check=True)

def checked_path(name):
    rel = Path(name)
    if rel.is_absolute() or '..' in rel.parts or '.git' in rel.parts:
        raise ValueError('Unsafe migration path: ' + name)
    path = (ROOT / rel).resolve()
    path.relative_to(ROOT)
    return path

def blob(path):
    if not path.exists():
        return None
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

# Complete the conflict preflight before changing any tracked content.
for name, entry in bundle['files'].items():
    actual = blob(checked_path(name))
    if actual != entry['expected_blob']:
        raise ValueError(f'Concurrent file change: {name}: {actual}')
for name, expected in bundle['deletes'].items():
    if blob(checked_path(name)) != expected:
        raise ValueError('Concurrent deletion-target change: ' + name)

native = ROOT / 'build' / 'source-evidence'
manifest = json.loads((native / 'provenance.json').read_text())
assert manifest['source_commit'] == bundle['base_commit']
assert manifest['run_id'] == '35839002637'
assert manifest['native_validation'] == 'passed'
assert hashlib.sha256((native / 'tk101.sysml').read_bytes()).hexdigest() == manifest['source_sha256']
assert hashlib.sha256((ROOT / 'models/sysml/tk101.sysml').read_bytes()).hexdigest() == manifest['source_sha256']
assert hashlib.sha256((native / 'tk101.export.json').read_bytes()).hexdigest() == manifest['export_sha256']
json.loads((native / 'tk101.export.json').read_text())

for name, entry in bundle['files'].items():
    path = checked_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(entry['content'], encoding='utf-8')
for name in bundle['deletes']:
    checked_path(name).unlink()
for source, destination in {
    'tk101.export.json': 'models/sysml/tk101.export.json',
    'provenance.json': 'evidence/sysml_provenance.json',
    'validation.log': 'evidence/sysml_validation.log',
}.items():
    path = checked_path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(native / source, path)

# Workflow updates are finalized separately through the authenticated connector.
# The job token only pushes the reviewed source and native evidence files.
subprocess.run(['git', 'restore', '--source=HEAD', '--worktree', '.github/workflows'], check=True)
print(f"Applied {len(bundle['files'])} reviewed file updates and {len(bundle['deletes'])} explicit deletions; workflow changes deferred.")

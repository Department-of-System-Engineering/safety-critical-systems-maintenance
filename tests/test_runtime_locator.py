"""Do not select a Java runtime JAR just because its parent includes 'sysml'."""
import importlib.util
from pathlib import Path
from zipfile import ZipFile

import pytest

source = Path(__file__).resolve().parents[1] / 'scripts/locate_sysml_runtime.py'
spec = importlib.util.spec_from_file_location('runtime_locator', source)
locator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(locator)


def write_jar(path, member):
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, 'w') as archive:
        archive.writestr(member, b'fixture')


def test_select_by_class_not_parent_name(tmp_path):
    prefix = tmp_path / 'sysml-pilot'
    write_jar(prefix / 'lib/jrt-fs.jar', 'java/runtime.class')
    target = prefix / 'share/jupyter/kernels/sysml/kernel.jar'
    write_jar(target, locator.INTERACTIVE_CLASS)
    assert locator.find_sysml_jar(prefix) == target.resolve()


def test_missing_reference_jar_rejected(tmp_path):
    write_jar(tmp_path / 'java.jar', 'unrelated.class')
    with pytest.raises(ValueError, match='found 0'):
        locator.find_sysml_jar(tmp_path)


def test_ambiguous_reference_jars_rejected(tmp_path):
    for name in ['one.jar', 'two.jar']:
        write_jar(tmp_path / name, locator.INTERACTIVE_CLASS)
    with pytest.raises(ValueError, match='found 2'):
        locator.find_sysml_jar(tmp_path)


def test_library_requires_source_files(tmp_path):
    empty = tmp_path / 'empty/sysml.library'
    empty.mkdir(parents=True)
    real = tmp_path / 'actual/sysml.library'
    real.mkdir(parents=True)
    (real / 'fixture.sysml').write_text('package Example {}')
    assert locator.find_sysml_library(tmp_path) == real.resolve()


def test_cli_reports_selected_jar(tmp_path, capsys):
    target = tmp_path / 'kernel.jar'
    write_jar(target, locator.INTERACTIVE_CLASS)
    locator.main(['--prefix', str(tmp_path), '--field', 'jar'])
    assert capsys.readouterr().out.strip() == str(target.resolve())

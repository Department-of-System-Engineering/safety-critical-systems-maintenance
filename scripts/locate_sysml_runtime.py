"""Locate the reference-tool JAR by class content, never by directory name."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from zipfile import BadZipFile, ZipFile

INTERACTIVE_CLASS = 'org/omg/sysml/interactive/SysMLInteractive.class'


def find_sysml_jar(prefix: Path) -> Path:
    candidates = set()
    for path in prefix.rglob('*.jar'):
        try:
            with ZipFile(path) as archive:
                if INTERACTIVE_CLASS in archive.namelist():
                    candidates.add(path.resolve())
        except (BadZipFile, OSError):
            continue
    if len(candidates) != 1:
        raise ValueError(f'Expected exactly one reference-tool JAR containing {INTERACTIVE_CLASS}; found {len(candidates)}')
    return candidates.pop()


def find_sysml_library(prefix: Path) -> Path:
    candidates = {
        path.resolve() for path in prefix.rglob('sysml.library')
        if path.is_dir() and any(path.rglob('*.sysml'))
    }
    if len(candidates) != 1:
        raise ValueError(f'Expected exactly one sysml.library directory with SysML sources; found {len(candidates)}')
    return candidates.pop()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', default=os.environ.get('CONDA_PREFIX'))
    parser.add_argument('--field', required=True, choices=['jar', 'library'])
    args = parser.parse_args(argv)
    if not args.prefix or not Path(args.prefix).is_dir():
        parser.error('Activate the reference-tool Conda environment or supply an existing --prefix')
    try:
        locate = find_sysml_jar if args.field == 'jar' else find_sysml_library
        print(locate(Path(args.prefix)))
    except ValueError as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()

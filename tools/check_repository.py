"""Offline syntax, preservation, asset and documentation checks; no hardware."""

import ast
import csv
import hashlib
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit
from build_code_index import ROOT, python_files, render


def main():
    failures = []
    sources = python_files()
    for path in sources:
        try:
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        except (SyntaxError, UnicodeError) as exc:
            failures.append(f'{path.relative_to(ROOT)}: {exc}')
    for name, path_column, hash_column in [
        ('migration.csv', 'current_path', 'sha256_canonical'),
        ('assets.csv', 'path', 'sha256_canonical'),
    ]:
        with (ROOT / 'docs' / 'inventory' / name).open(encoding='utf-8', newline='') as stream:
            for row in csv.DictReader(stream):
                path = ROOT / row[path_column]
                if not path.is_file():
                    failures.append(f'missing preserved file: {row[path_column]}')
                    continue
                data = path.read_bytes()
                if row['hash_mode'] == 'lf':
                    data = data.replace(b'\r\n', b'\n')
                if hashlib.sha256(data).hexdigest() != row[hash_column]:
                    failures.append(f'changed preserved content: {row[path_column]}')
    documents = list((ROOT / 'docs').rglob('*.md')) + list(ROOT.glob('*.md'))
    for path in documents:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            target = target.strip('<>')
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            target = unquote(target.split('#', 1)[0])
            if target and not (path.parent / target).exists():
                failures.append(f'broken local link in {path.relative_to(ROOT)}: {target}')
    if (ROOT / 'docs' / 'CODE_INDEX.md').read_text(encoding='utf-8') != render():
        failures.append('CODE_INDEX.md is stale; run python tools/build_code_index.py')
    tracked = subprocess.run(['git', 'ls-files', '--stage'], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.splitlines()
    for entry in tracked:
        mode, _, path = entry.partition(' ')
        if mode == '160000':
            failures.append(f'unexpected gitlink: {path}')
        name = entry.split('\t')[-1]
        if any(part in {'.git', '.idea', '__pycache__', '.codex-work', '.venv'} for part in Path(name).parts):
            failures.append(f'local metadata staged: {name}')
    if failures:
        print('\n'.join(failures))
        return 1
    print(f'PASS: {len(sources)} Python files parsed; preservation/asset hashes, documentation links and source index verified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

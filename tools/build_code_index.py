"""Generate a source index using AST only; never import project modules."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.idea', '__pycache__', '.venv', 'venv', '.codex-work', '.superpowers'}


def python_files():
    files = (p for p in ROOT.rglob('*.py') if not EXCLUDED.intersection(p.relative_to(ROOT).parts))
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def render():
    rows = ['# Python 代码索引', '',
            '由 `python tools/build_code_index.py` 从语法树生成。仅解析文本，不导入或执行模块。', '',
            '历史脚本和参考仓库中的 test 文件不是自动化测试；正式测试位于 `tests/`。', '',
            '| 文件 | 行数 | 定义（名称:行号） |', '|---|---:|---|']
    for path in python_files():
        source = path.read_text(encoding='utf-8-sig')
        tree = ast.parse(source, filename=str(path))
        names = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(f'`{node.name}:{node.lineno}`')
                if isinstance(node, ast.ClassDef):
                    names.extend(f'`{node.name}.{child.name}:{child.lineno}`' for child in node.body
                                 if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
        relative = path.relative_to(ROOT).as_posix()
        rows.append(f'| [{relative}](../{relative}) | {len(source.splitlines())} | {", ".join(names) or "—"} |')
    return '\n'.join(rows) + '\n'


if __name__ == '__main__':
    (ROOT / 'docs' / 'CODE_INDEX.md').write_text(render(), encoding='utf-8')
    print('Updated docs/CODE_INDEX.md')

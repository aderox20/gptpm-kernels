#!/usr/bin/env python3
"""Build simple directory indexes and folder ZIP downloads for GitHub Pages."""
from html import escape
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKIP = {'.git', '.github', 'scripts'}


def href(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def write_index(directory: Path) -> None:
    entries = []
    for path in sorted(directory.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
        if path.name in SKIP or path.name == 'index.html' or path.name.endswith('.zip'):
            continue
        if path.is_dir():
            archive = directory / f'{path.name}.zip'
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
                for child in path.rglob('*'):
                    if child.is_file() and child.name != 'index.html' and child.suffix != '.zip':
                        zf.write(child, child.relative_to(path.parent))
            entries.append(
                f'<p><a href="{escape(path.name)}/">{escape(path.name)}/</a> '
                f'<a href="{escape(archive.name)}" download>Download Folder</a></p>'
            )
        else:
            entries.append(
                f'<p><a href="{escape(path.name)}">{escape(path.name)}</a> '
                f'<a href="{escape(path.name)}" download>Download File</a></p>'
            )

    parent = '' if directory == ROOT else '../'
    title = './' if directory == ROOT else f'{directory.relative_to(ROOT).as_posix()}/'
    body = [
        '<!doctype html>', '<html lang="en"><head>', '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>GPTPM kernels - {escape(title)}</title>',
        '<style>body{max-width:700px;margin:40px 16px;color:#222;background:#fff;font:15px/1.6 monospace}h1{font-size:20px;font-weight:normal}a{color:#06c}</style>',
        '</head><body>', f'<h1>Index of {escape(title)}</h1>',
        f'<p><a href="{parent}">../</a></p>' if directory != ROOT else '',
        *entries,
        '</body></html>',
    ]
    (directory / 'index.html').write_text('\n'.join(body), encoding='utf-8')


for directory in sorted([ROOT, *[p for p in ROOT.rglob('*') if p.is_dir() and not any(part in SKIP for part in p.relative_to(ROOT).parts)]], key=lambda p: len(p.parts), reverse=True):
    write_index(directory)

"""Render the list sections of README.md from data/entries.yaml.

    python scripts/build_readme.py          # rewrite README.md in place
    python scripts/build_readme.py --check  # exit 1 if README.md is stale or an entry is invalid

Only the regions between <!-- BEGIN x --> and <!-- END x --> markers are generated;
everything else in README.md is edited by hand.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ACCESS = {'open': '`OPEN`', 'closed': '`CLOSED`', 'paper': '`PAPER`'}
LINKS = ['paper', 'code', 'blog', 'project', 'docs']
ROMAN = 'I II III IV V VI VII VIII IX X XI XII XIII XIV XV'.split()


def load():
    sections = yaml.safe_load((ROOT / 'data/sections.yaml').read_text())
    entries = yaml.safe_load((ROOT / 'data/entries.yaml').read_text()) or []
    return sections, entries


def validate(sections, entries):
    ids = set()
    for s in sections:
        ids.add(s['id'])
        ids.update(g['id'] for g in s.get('groups', []))
    errors, seen = [], {}
    for i, e in enumerate(entries):
        where = f"entry {i} ({e.get('title', '?')[:50]})"
        for k in ('title', 'year', 'section', 'access', 'links', 'note'):
            if not e.get(k):
                errors.append(f'{where}: missing {k}')
        if e.get('section') not in ids:
            errors.append(f"{where}: unknown section {e.get('section')}")
        grouped = {g['id'] for s in sections for g in s.get('groups', [])}
        if e.get('section') in {s['id'] for s in sections if s.get('groups')} and e.get('section') not in grouped:
            errors.append(f"{where}: section {e.get('section')} has groups; pick one")
        if e.get('access') not in ACCESS:
            errors.append(f"{where}: access must be one of {list(ACCESS)}")
        for k, v in (e.get('links') or {}).items():
            if k not in LINKS:
                errors.append(f'{where}: unknown link type {k}')
            elif not str(v).startswith('http'):
                errors.append(f'{where}: bad url {v}')
            elif v in seen:
                errors.append(f'{where}: duplicate link {v} (also in {seen[v]})')
            else:
                seen[v] = where
    return errors


def cell(s):
    return str(s).replace('|', '\\|').replace('\n', ' ').strip()


def title_md(e):
    t = cell(e['title'])
    name = e.get('name')
    if name and t.startswith(name):
        return f'**{name}**{t[len(name):]}'
    m = re.match(r'^([^:]{1,48}):(.*)$', t)
    if m:
        return f'**{m.group(1)}**:{m.group(2)}'
    return t


def row(e):
    venue = cell(e.get('venue', ''))
    if e.get('org'):
        venue = f"{venue}<br><sub>{cell(e['org'])}</sub>" if venue else cell(e['org'])
    links = ' · '.join(f'[{k}]({e["links"][k]})' for k in LINKS if e['links'].get(k))
    return f"| {e['year']} | {title_md(e)} | {venue} | {links} | {ACCESS[e['access']]} | {cell(e['note'])} |"


HEAD = '| Year | Title | Venue / Org | Links | Access | Why it matters for infra |\n|---:|---|---|---|:-:|---|'


def table(items):
    items = sorted(items, key=lambda e: (e['year'], e.get('month', 0), e['title'].lower()))
    return HEAD + '\n' + '\n'.join(row(e) for e in items)


def render_list(sections, entries):
    by = {}
    for e in entries:
        by.setdefault(e['section'], []).append(e)
    out = []
    for n, s in zip(ROMAN, sections):
        out.append(f'<a id="{s["id"]}"></a>\n\n### {n}. {s["title"]}\n')
        out.append(f'> {s["blurb"]}\n')
        groups = s.get('groups') or [{'id': s['id'], 'title': s['title']}]
        for k, g in enumerate(groups, 1):
            items = by.get(g['id'], [])
            if not items:
                continue
            label = f'{n}.{k}&ensp;{g["title"]}' if s.get('groups') else 'Entries'
            out.append(f'<details open>\n<summary><b>{label}</b> <sub>({len(items)})</sub></summary>\n\n{table(items)}\n\n</details>\n')
    return '\n'.join(out).rstrip() + '\n'


def render_toc(sections):
    lines = []
    for n, s in zip(ROMAN, sections):
        lines.append(f'  - [{n}. {s["title"]}](#{s["id"]})')
    return '\n'.join(lines) + '\n'


def splice(text, name, body):
    pat = re.compile(rf'(<!-- BEGIN {name} -->\n)(.*?)([ \t]*<!-- END {name} -->)', re.S)
    if not pat.search(text):
        raise SystemExit(f'README.md has no {name} markers')
    return pat.sub(lambda m: m.group(1) + body + m.group(3), text)


def main():
    sections, entries = load()
    errors = validate(sections, entries)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    path = ROOT / 'README.md'
    old = path.read_text()
    new = splice(old, 'TOC', render_toc(sections))
    new = splice(new, 'LIST', render_list(sections, entries))
    if '--check' in sys.argv:
        if new != old:
            print('README.md is out of date: run python scripts/build_readme.py')
            raise SystemExit(1)
        print(f'ok: {len(entries)} entries')
        return
    path.write_text(new)
    print(f'README.md: {len(entries)} entries')


if __name__ == '__main__':
    main()

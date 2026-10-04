"""Strip one language's markup from a bilingual Edualist page.

Elements carrying class "tr-only" / "en-only" are removed for the other
language; the marker class is dropped from the kept ones.
"""
import re

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'source', 'track', 'wbr'}
RAW = {'script', 'style'}
TAG_RE = re.compile(r'<!--.*?-->|<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>', re.S)
CLASS_RE = re.compile(r'(\sclass=)(["\'])(.*?)\2', re.S)


def _classes(attrs):
    m = CLASS_RE.search(attrs)
    return m.group(3).split() if m else []


def _end_of(s, name, pos):
    """Index just past the end tag matching an element opened before pos."""
    depth = 1
    for m in TAG_RE.finditer(s, pos):
        if m.group(0).startswith('<!--') or m.group(2).lower() != name:
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    raise ValueError(f'unclosed <{name}> at {pos}')


def split(s, lang):
    drop, keep = ('en-only', 'tr-only') if lang == 'tr' else ('tr-only', 'en-only')
    out, i = [], 0
    pos = 0
    while True:
        m = TAG_RE.search(s, pos)
        if not m:
            break
        if m.group(0).startswith('<!--') or m.group(1):
            pos = m.end()
            continue
        name = m.group(2).lower()
        cls = _classes(m.group(3))
        if name in RAW and drop not in cls:
            pos = s.index(f'</{name}', m.end())
            continue
        if drop in cls:
            end = m.end() if (name in VOID or m.group(3).rstrip().endswith('/')) else _end_of(s, name, m.end())
            out.append(s[i:m.start()])
            # swallow the whitespace-only line the element sat on
            if out[-1].endswith('\n') or re.search(r'\n[ \t]*$', out[-1]):
                out[-1] = re.sub(r'[ \t]*$', '', out[-1])
                if s[end:end + 1] == '\n':
                    end += 1
            i = pos = end
            continue
        if keep in cls:
            rest = [c for c in cls if c != keep]
            cm = CLASS_RE.search(m.group(3))
            new_attrs = (m.group(3)[:cm.start()] +
                         (f'{cm.group(1)}{cm.group(2)}{" ".join(rest)}{cm.group(2)}' if rest else '') +
                         m.group(3)[cm.end():])
            out.append(s[i:m.start()])
            out.append(f'<{m.group(2)}{new_attrs}>')
            i = m.end()
        pos = m.end()
    out.append(s[i:])
    return ''.join(out)


def text_len(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S | re.I)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s.split('<body', 1)[-1])))

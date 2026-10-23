"""Izvlači tekst knjige iz PDF-a (InDesign izvoz) u jalics/data/vremena.json.

Uporaba (iz korijena repozitorija; treba `pdftotext` iz poppler-a):
    python3 scripts/pdf_to_vremena.py "nagovori/<knjiga>.pdf" \
        [--old jalics/data/vremena.json] [--out jalics/data/vremena.json] \
        [--report /tmp/report.txt]

Postojeći JSON (--old) služi za polja koja nisu u knjizi: key/index/title,
sažeci odjeljaka nagovora, naslovi `numbered` smjernica, osvrt desetog vremena.
Izvještaj ispisuje sve razlike u strukturi (naslovi, imena, broj razgovora,
tipfeleri govornika, neuravnoteženi navodnici) — pregledati prije commita.
"""
import argparse, json, re, subprocess, sys, tempfile, collections

ap = argparse.ArgumentParser()
ap.add_argument('pdf')
ap.add_argument('--old', default='jalics/data/vremena.json')
ap.add_argument('--out', default='jalics/data/vremena.json')
ap.add_argument('--report')
args = ap.parse_args()

lay = tempfile.NamedTemporaryFile(suffix='.txt', delete=False).name
subprocess.run(['pdftotext', '-layout', args.pdf, lay], check=True)
old_path, out_path, rep_path = args.old, args.out, args.report
old = json.load(open(old_path))
report = []
R = lambda *a: report.append(' '.join(str(x) for x in a))

ORD = ['PRVO', 'DRUGO', 'TREĆE', 'ČETVRTO', 'PETO', 'ŠESTO', 'SEDMO', 'OSMO', 'DEVETO', 'DESETO']
UP = 'A-ZČĆŽŠĐÜÖÄ'

# ---------- 1. lines -> paragraphs (with block markers) ----------
pages = open(lay).read().split('\f')
lines = []  # (indent, text)
started = False
for pg in pages:
    for l in pg.split('\n'):
        s = l.strip()
        if not s or re.fullmatch(r'\d+', s):
            continue
        if not started:
            # body starts at the second "PRVO VRIJEME" (first is the TOC)
            if s == 'PRVO VRIJEME' and len(l) - len(l.lstrip()) > 5:
                started = True
            else:
                continue
        if s.startswith('FRANZ JALICS, DI'):
            break
        lines.append((len(l) - len(l.lstrip()), s.replace('­', '')))
    else:
        continue
    break

# words seen with a real hyphen inside a line -> keep hyphen when such a word is split at line end
inline_hyph = set(m.group(0).lower() for _, s in lines for m in re.finditer(rf'[\w{UP}]+-[\w]+', s))

def is_heading(ind, s):
    if re.fullmatch(rf'({"|".join(ORD)}) VRIJEME', s): return 'vrijeme'
    if s == 'I. NAGOVOR:': return 'nagovor'
    if s.startswith('II. UPUTE ZA'): return 'upute'
    if re.fullmatch(r'III\. (OPROŠTAJNI )?RAZGOVORI', s): return 'razgovori'
    if s.startswith('IV. OSVRT I PRIJELAZ'): return 'osvrt'
    if re.fullmatch(rf'\d+\. ?\d+\. [{UP}][{UP} ()-]+', s): return 'razgovor'
    return None

# Build flat token stream: ('H', kind, text) or ('P', text)
stream = []
cur = None
def flush():
    global cur
    if cur is not None:
        stream.append(['P', cur])
    cur = None

def append(s):
    global cur
    if cur is None:
        cur = s; return
    if cur.endswith('-') and re.match(r'[a-zčćžšđ]', s):
        m = re.search(r'([\w]+)-$', cur)
        nxt = re.match(r'\w+', s).group(0)
        if m and (m.group(1) + '-' + nxt).lower() in inline_hyph:
            cur = cur + s; R('KEEP-HYPHEN', m.group(1) + '-' + nxt)
        else:
            cur = cur[:-1] + s
    else:
        cur = cur + ' ' + s

pending_title = None  # collect uppercase nagovor title lines
for i, (ind, s) in enumerate(lines):
    h = is_heading(ind, s)
    if h:
        flush(); stream.append(['H', h, s]); continue
    # nagovor title lines (uppercase, right after 'I. NAGOVOR:')
    if stream and stream[-1][0] == 'H' and stream[-1][1] in ('nagovor', 'ntitle') and s.upper() == s and not cur:
        if stream[-1][1] == 'ntitle': stream[-1][2] += ' ' + s
        else: stream.append(['H', 'ntitle', s])
        continue
    # section heading "N. Title" (indented, short, followed by a fresh paragraph)
    if re.fullmatch(r'\d\. [A-ZČĆŽŠĐ„“"].{2,70}', s) and not s.endswith(('.', ',', ';')) and ind >= 2:
        flush(); stream.append(['H', 'sec', s]); continue
    if ind >= 2:
        flush()
    append(s)
flush()

# ---------- 2. stream -> structure ----------
def sentence_summary(t):
    first = re.split(r'(?<=[.!?…])\s', t)[0]
    if len(first) > 75:
        cut = first[:72].rsplit(' ', 1)[0].rstrip(',;:')
        first = cut + '…'
    return first

def similar(a, b):
    import difflib
    return a != b and difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.75

QOPEN = set(' \n([{—–-/')
def croatian_quotes(t):
    t2 = re.sub(r'(: )["“”] (?=\w)', r'\1“', t)  # stray space after opening quote
    if t2 != t: R('QUOTE-SPACE fixed:', re.search(r'.{0,30}: “\w+', t2).group(0))
    t = t2
    out = []
    for k, ch in enumerate(t):
        if ch in '"“”':
            prev = t[k - 1] if k else ' '
            nxt = t[k + 1] if k + 1 < len(t) else ' '
            out.append('„' if prev in QOPEN and nxt not in ' \n' else '“')
        else:
            out.append(ch)
    s = ''.join(out)
    if s.count('„') != s.count('“'):
        R('QUOTES UNBALANCED:', s[:120])
    return s

def walk(o):
    if isinstance(o, str): return croatian_quotes(o)
    if isinstance(o, list): return [walk(x) for x in o]
    if isinstance(o, dict): return {k: (walk(v) if k not in ('key', 'name', 'speaker') else v) for k, v in o.items()}
    return o

def title_case_name(n):
    return ' '.join(w[:1] + w[1:].lower() for w in n.split(' '))

def fix_paren(n):
    return re.sub(r'\(([^)]+)\)', lambda m: '(' + title_case_name(m.group(1)) + ')', n)

vremena = []
V = None; part = None
for tok in stream:
    if tok[0] == 'H':
        kind, s = tok[1], tok[2]
        if kind == 'vrijeme':
            V = {'nagovor': [], 'upute': [], 'razgovori': [], 'osvrt': {'paras': [], 'questions': [], 'parasAfter': []}}
            vremena.append(V); part = 'pre'
        elif kind == 'nagovor': part = 'nagovor'
        elif kind == 'ntitle': V['nagovorTitleUpper'] = s
        elif kind == 'upute': part = 'upute'; V['uputeTitle'] = s
        elif kind == 'razgovori': part = 'razgovori'
        elif kind == 'osvrt': part = 'osvrt'
        elif kind == 'razgovor':
            name = re.sub(r'^\d+\. ?\d+\. ', '', s)
            V['razgovori'].append({'name': name, 'turns': [], 'pre': []})
        elif kind == 'sec':
            heading = re.sub(r'^\d\. ', '', s)
            if part == 'nagovor':
                V['nagovor'].append({'heading': heading, 'paras': []})
            elif part == 'upute':
                V['upute'].append({'heading': heading, 'paras': []})
            else:
                R('UNEXPECTED SEC', part, s)
        continue
    t = tok[1]
    if part == 'nagovor':
        if not V['nagovor']: V['nagovor'].append({'heading': None, 'paras': []})
        V['nagovor'][-1]['paras'].append(t)
    elif part == 'upute':
        if not V['upute']: V['upute'].append({'heading': None, 'paras': []})
        V['upute'][-1]['paras'].append(t)
    elif part == 'razgovori':
        r = V['razgovori'][-1]
        m = re.match(r'([A-ZČĆŽŠĐ][\wčćžšđüöäß]+)(?:: | (\([^)]*\)):? )(.*)', t)
        if m:
            text = (m.group(2) + ' ' if m.group(2) else '') + m.group(3)
            r['turns'].append({'speaker': m.group(1), 'text': text})
        elif r['turns']:
            r['turns'][-1]['text'] += '\n\n' + t
        else:
            r['pre'].append(t)
    elif part == 'osvrt':
        o = V['osvrt']
        if t.startswith('•'):
            o['questions'].append(t.lstrip('• ').strip())
        elif o['questions']:
            o['parasAfter'].append(t)
        else:
            o['paras'].append(t)
    else:
        R('ORPHAN TEXT', part, t[:80])

# ---------- 3. TOC: proper-case nagovor titles ----------
toc_titles = re.findall(r'I\. nagovor: (.+)', open(lay).read().split('PREDGOVOR')[0])

# ---------- 4. merge with old: keep key/index/title/summaries/numbered titles ----------
out = []
assert len(vremena) == 10, len(vremena)
for i, (V, O) in enumerate(zip(vremena, old)):
    N = {'key': O['key'], 'index': O['index'], 'title': O['title'],
         'nagovorTitle': toc_titles[i].strip()}
    if N['nagovorTitle'] != O['nagovorTitle']:
        R(f'[{i+1}] nagovorTitle:', repr(O['nagovorTitle']), '->', repr(N['nagovorTitle']))
    # nagovor
    if len(V['nagovor']) != len(O['nagovor']):
        R(f'[{i+1}] NAGOVOR section count {len(O["nagovor"])} -> {len(V["nagovor"])}')
    nag = []
    for j, s in enumerate(V['nagovor']):
        os_ = O['nagovor'][j] if j < len(O['nagovor']) else {}
        if os_.get('heading') != s['heading']:
            R(f'[{i+1}] nagovor heading {j+1}:', repr(os_.get('heading')), '->', repr(s['heading']))
        ns = {'heading': s['heading'], 'paras': s['paras']}
        if os_.get('summary'): ns['summary'] = os_['summary']
        if os_.get('numbered'):
            # split "N) ..." items out of paras
            paras, items = [], []
            for p in s['paras']:
                m = re.match(r'(\d)\) (.*)', p)
                if m: items.append({'text': m.group(2), 'rest': []})
                elif items: items[-1]['rest'].append(p)
                else: paras.append(p)
            olds = os_['numbered']
            if len(items) != len(olds): R(f'[{i+1}] NUMBERED count {len(olds)} -> {len(items)}')
            num = []
            for k, it in enumerate(items):
                ot = olds[k] if k < len(olds) else {'title': '?', 'sub': []}
                sub = []
                if it['rest']:
                    if len(it['rest']) != len(ot['sub']): R(f'[{i+1}] NUMBERED sub count mismatch item {k+1}')
                    sub = [{'title': (ot['sub'][q]['title'] if q < len(ot['sub']) else '?'), 'text': t} for q, t in enumerate(it['rest'])]
                num.append({'title': ot['title'], 'text': it['text'], 'sub': sub})
            ns['paras'] = paras; ns['numbered'] = num
        nag.append(ns)
    N['nagovor'] = nag
    # upute
    N['upute'] = V['upute']
    if [u['heading'] for u in V['upute']] != [u['heading'] for u in O['upute'] if True] and i != 1:
        R(f'[{i+1}] upute headings', [u['heading'] for u in O['upute']], '->', [u['heading'] for u in V['upute']])
    # razgovori
    oldnames = [r['name'] for r in O['razgovori']]
    raz = []
    for r in V['razgovori']:
        if r['pre']: R(f'[{i+1}] {r["name"]}: text before first speaker:', r['pre'])
        disp = fix_paren(title_case_name(r['name']))
        base = disp.split(' ')[0]
        for t in r['turns']:
            sp = t['speaker']
            if sp not in ('Voditelj', base) and (similar(sp, 'Voditelj') or similar(sp, base)):
                fixed = 'Voditelj' if similar(sp, 'Voditelj') else base
                R(f'[{i+1}] {r["name"]}: TIPFELER govornika {sp!r} -> {fixed!r}')
                t['speaker'] = fixed
        speakers = set(t['speaker'] for t in r['turns']) - {'Voditelj'}
        if speakers and not any(sp in disp for sp in speakers):
            R(f'[{i+1}] {r["name"]}: speakers {speakers}')
        if len(speakers) > 1: R(f'[{i+1}] {r["name"]}: multiple speakers {speakers}')
        first = next((t['text'] for t in r['turns'] if t['speaker'] != 'Voditelj'), '')
        raz.append({'name': r['name'], 'display': disp, 'summary': sentence_summary(first), 'turns': r['turns']})
    newnames = [r['name'] for r in raz]
    if newnames != oldnames:
        R(f'[{i+1}] razgovori {len(oldnames)} -> {len(newnames)}')
        for a, b in __import__('itertools').zip_longest(oldnames, newnames):
            if a != b: R('     ', a, '->', b)
    N['razgovori'] = raz
    # osvrt
    o = V['osvrt']
    if not (o['paras'] or o['questions']):
        R(f'[{i+1}] OSVRT not in book -> keeping old')
        N['osvrt'] = O['osvrt']
    else:
        N['osvrt'] = {'paras': o['paras'], 'questions': o['questions']}
        if o['parasAfter']: N['osvrt']['parasAfter'] = o['parasAfter']
        R(f'[{i+1}] osvrt paras {len(O["osvrt"]["paras"])}->{len(o["paras"])}, questions {len(O["osvrt"]["questions"])}->{len(o["questions"])}, after {len(o["parasAfter"])}')
    out.append(N)

out = walk(out)
out[0]['nagovorTitle'] = 'Što su to duhovne vježbe?'  # TOC capitalises "Duhovne"; body/lektura use lowercase
json.dump(out, open(out_path, 'w'), ensure_ascii=False, separators=(',', ':'))
if rep_path:
    open(rep_path, 'w').write('\n'.join(report) + '\n')
print('\n'.join(report))

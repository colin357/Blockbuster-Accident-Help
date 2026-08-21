import os, re, shutil, html

SRC   = '/tmp/claude-0/-home-user-Blockbuster-Accident-Help/212140dd-0680-5976-9ed6-9f66823a2921/scratchpad'
OUT   = '/home/user/Blockbuster-Accident-Help'
OLDDOM_VARIANTS = ['https://www.accidentreporthelp.com', 'https://accidentreporthelp.com']
NEWDOM = 'https://www.blockbusterinjury.com'

# ---------- asset map ----------
assetmap = {}
for line in open(f'{SRC}/assetmap.txt'):
    u, n = line.rstrip('\n').split('\t')
    assetmap[u] = n

# old brand imagery -> new brand imagery
def outname(n):
    return LOGO_SWAP.get(n, n.replace('Accident_Report_Help', 'Blockbuster_Injury'))

LOGO_SWAP = {
    '69a0a104ddd5198ec257107a_ARH.webp':      'logo.svg',
    '69283f35a3808c85d24ec106_logo_2.webp':   'logo.svg',
    '692eee83fddc72604ffa8ca2_favicon.png':   'favicon.png',
    '692eee87f99bac762735ef6b_webclip.png':   'webclip.png',
}

# ---------- colour retheme: mint/red -> navy/gold ----------
COLORS = [
    ('#52db82', '#16264d'), ('#1aa47b', '#0e1730'), ('#edfcf2', '#eef1f8'),
    ('#dffae8', '#dde3f0'), ('#bbfbd1', '#c2cde5'), ('#668176', '#5c6a8a'),
    ('#056d4e', '#16264d'), ('#ecfdf3', '#eff2f9'), ('#daedee', '#dee5f2'),
    ('#fdc951', '#f7b91b'), ('#fffbe5', '#fff9e8'), ('#fff7cc', '#fef1d0'),
    ('#cc2f31', '#f7b91b'), ('#111418', '#0e1730'), ('#121212', '#101a33'),
    ('#111827', '#101a33'), ('#1f2937', '#1e3260'),
]
def retheme(t):
    for old, new in COLORS:
        t = re.sub(re.escape(old), new, t, flags=re.I)
    return t

# ---------- brand copy ----------
BRAND = [
    ('info@accidentreporthelp.com', 'info@blockbusterinjury.com'),
    ('AccidentReportHelp.com',      'BlockbusterInjury.com'),
    ('accidentreporthelp.com',      'blockbusterinjury.com'),
    ('AccidentReportHelp',          'BlockbusterInjury'),
    ('Accident Report Help',        'Blockbuster Injury'),
    ('Accident Report help',        'Blockbuster Injury'),
    ('accident report help</a>',    'Blockbuster Injury</a>'),
    ('Accident&nbsp;Report&nbsp;Help', 'Blockbuster&nbsp;Injury'),
    ('AccidentReport Help',         'Blockbuster Injury'),
    # one post has the leading "a" outside the link: `such as a<a ...>ccident report help</a>`
    ('such as a<a href="/">ccident report help</a>', 'such as <a href="/">Blockbuster Injury</a>'),
]
def rebrand(t):
    for old, new in BRAND:
        t = t.replace(old, new)
    return t

# ---------- assets ----------
os.makedirs(f'{OUT}/assets', exist_ok=True)
for u, n in assetmap.items():
    if n in LOGO_SWAP:            # replaced by new brand artwork
        continue
    src = f'{SRC}/assets/{n}'
    if not os.path.exists(src):
        continue
    if n.endswith('.css'):
        css = open(src, encoding='utf-8', errors='replace').read()
        for uu, nn in assetmap.items():
            css = css.replace(uu, '/assets/' + outname(nn))
            css = css.replace(uu.replace('%20', ' '), '/assets/' + outname(nn))
        open(f'{OUT}/assets/{outname(n)}', 'w', encoding='utf-8').write(retheme(css))
    else:
        shutil.copy2(src, f'{OUT}/assets/{outname(n)}')
shutil.copy2(f'{SRC}/assets/jquery-3.5.1.min.js', f'{OUT}/assets/jquery-3.5.1.min.js')
for b in os.listdir(f'{SRC}/brand'):
    shutil.copy2(f'{SRC}/brand/{b}', f'{OUT}/assets/{b}')

# ---------- pages ----------
def transform(t):
    # 1. local assets
    for u, n in assetmap.items():
        tgt = '/assets/' + outname(n)
        t = t.replace(u, tgt).replace(u.replace('%20', '&#x20;'), tgt)
    t = re.sub(r'https://d3e54v103j8qbb\.cloudfront\.net/js/jquery-3\.5\.1\.min\.[a-z0-9]+\.js(\?[^"\']*)?',
               '/assets/jquery-3.5.1.min.js', t)
    # 1b. the Webflow CDN is no longer used - drop its preconnect hint
    t = re.sub(r'<link\b(?=[^>]*(?:preconnect|dns-prefetch))(?=[^>]*website-files\.com)[^>]*>', '', t)
    # 1c. brand overrides load after every generated stylesheet
    t = t.replace('</head>', '<link href="/assets/brand.css" rel="stylesheet" type="text/css"/></head>', 1)
    # 2. drop SRI (stylesheets are modified locally)
    t = re.sub(r'\s+integrity="[^"]*"', '', t)
    t = re.sub(r'(<(?:link|script)\b[^>]*?)\s+crossorigin="anonymous"', r'\1', t)
    # 3. canonical + og:url keep an absolute URL on the new domain
    def canon(m):
        return m.group(0).replace('accidentreporthelp.com', 'blockbusterinjury.com')
    t = re.sub(r'<link[^>]+rel="canonical"[^>]*/?>', canon, t)
    t = re.sub(r'<meta[^>]+og:url[^>]*/?>', canon, t)
    # 4. remaining internal links -> root relative
    t = re.sub(r'href="https://(?:www\.)?accidentreporthelp\.com(/[^"]*)?"',
               lambda m: 'href="%s"' % (m.group(1) or '/'), t)
    # 5. anything else on the old domain -> new domain
    for d in OLDDOM_VARIANTS:
        t = t.replace(d, NEWDOM)
    t = t.replace('www.accidentreporthelp.com', 'www.blockbusterinjury.com')
    # 6. brand + theme
    return retheme(rebrand(t))

pages = 0
for root, _, files in os.walk(f'{SRC}/pages'):
    for f in files:
        if not f.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(root, f), f'{SRC}/pages')
        dest = f'{OUT}/index.html' if rel == 'index.html' else f'{OUT}/{rel[:-5]}/index.html'
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        src_txt = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
        open(dest, 'w', encoding='utf-8').write(transform(src_txt))
        pages += 1
print('pages:', pages, 'assets:', len(os.listdir(f'{OUT}/assets')))

# ---------- site meta ----------
paths = []
for line in open(f'{SRC}/urls.txt'):
    p = line.strip().replace('https://www.accidentreporthelp.com', '') or '/'
    paths.append(p if p.endswith('/') else p + '/')
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in sorted(paths):
    sm.append(f'  <url>\n    <loc>{NEWDOM}{p}</loc>\n  </url>')
sm.append('</urlset>')
open(f'{OUT}/sitemap.xml', 'w').write('\n'.join(sm) + '\n')

open(f'{OUT}/robots.txt', 'w').write(
    f'User-agent: *\nAllow: /\n\nSitemap: {NEWDOM}/sitemap.xml\n')

# 404 page reuses the site chrome from the thank-you page
src404 = open(f'{OUT}/thank-you/index.html', encoding='utf-8').read()
src404 = re.sub(r'<title>[^<]*</title>', '<title>Page Not Found | Blockbuster Injury</title>', src404)
open(f'{OUT}/404.html', 'w', encoding='utf-8').write(src404)
print('meta: sitemap.xml, robots.txt, 404.html')

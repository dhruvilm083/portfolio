# Build the static site from the Format scrape.
# usage: python3 -I build.py <_scrape dir> <site dir> <domain>
import json, os, re, shutil, sys

SRC, OUT, DOMAIN = sys.argv[1], sys.argv[2], sys.argv[3]
FA = os.path.join(SRC, 'assets', 'dhruvil.format.com')
FF = os.path.join(SRC, 'assets', 'format-fonts.format.com')
BK = os.path.join(SRC, 'assets', 'bucket1.format-assets.com', 'theme_versions', '11002439', 'assets', 'js')

raw = open(os.path.join(SRC, 'pages', 'index', 'raw.html'), encoding='utf8').read()
variants = {v['order']: v for v in json.load(open(os.path.join(OUT, 'image-variants.json')))}
scraped = {x['order']: x for x in json.load(open(os.path.join(SRC, 'images.json')))}

# ---------- static assets ----------
A = os.path.join(OUT, 'assets')
for d in ('css', 'js', 'fonts', 'img'):
    os.makedirs(os.path.join(A, d), exist_ok=True)

def short(path):
    """Drop Format's fingerprint hash from a filename."""
    base = os.path.basename(path)
    return re.sub(r'-[0-9a-f]{64}', '', base)

# CSS files kept from the original page, in order. Icon-font sheets for
# features this site doesn't use (social icons, ss-standard) are dropped.
css_map = {}   # original href -> local filename
static_files = {}  # original url path -> local asset path (relative to assets/)
for m in re.finditer(r'<link[^>]+href=[\'"](/[^\'"]+\.css[^\'"]*)[\'"]', raw):
    href = m.group(1)
    if 'hosted_fonts' in href or 'webtype_fonts' in href or 'theme_social' in href or 'ss-standard' in href:
        continue
    if href.startswith('/stylesheet.css'):
        src, name = os.path.join(FA, 'stylesheet.css__v_2026-10-09T13_03_39Z'), 'theme.css'
    else:
        src, name = os.path.join(FA, href.lstrip('/')), short(href)
    css = open(src, encoding='utf8').read()
    def fix_url(u):
        u2 = u.group(1).strip('\'"')
        p = os.path.join(FA, u2.lstrip('/'))
        if u2.startswith('/static/') and os.path.exists(p):
            shutil.copy(p, os.path.join(A, 'img', short(u2)))
            return 'url(../img/%s)' % short(u2)
        return 'url(data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==)'  # 404 on Format too
    css = re.sub(r'url\(([^)]*)\)', fix_url, css)
    open(os.path.join(A, 'css', name), 'w', encoding='utf8').write(css)
    css_map[href] = name

# Fonts: DM Sans (free, OFL) in place of Format's licensed Proxima Nova / Input Mono.
DM = sys.argv[4]  # @fontsource/dm-sans package dir
for w in (400, 700):
    for st in ('normal', 'italic'):
        for ext in ('woff2', 'woff'):
            shutil.copy(os.path.join(DM, 'files', 'dm-sans-latin-%d-%s.%s' % (w, st, ext)),
                        os.path.join(A, 'fonts', 'DMSans-%d-%s.%s' % (w, st, ext)))
def face(family, weight, style, file_weight=None):
    f = 'DMSans-%d-%s' % (file_weight or weight, style)
    return ("@font-face{font-family:'%s';src:url(../fonts/%s.woff2) format('woff2'),url(../fonts/%s.woff) format('woff');"
            "font-weight:%d;font-style:%s;font-display:swap}\n" % (family, f, f, weight, style))
open(os.path.join(A, 'css', 'fonts.css'), 'w').write(
    face('DM Sans', 400, 'normal') + face('DM Sans', 400, 'italic') +
    face('DM Sans', 700, 'normal') + face('DM Sans', 700, 'italic') +
    # The theme sets bold headings as a separate family at normal weight.
    face('DM Sans Bold', 400, 'normal', 700) + face('DM Sans Bold', 400, 'italic', 700) +
    face('DM Sans Bold', 700, 'normal') + face('DM Sans Bold', 700, 'italic'))
for name in os.listdir(os.path.join(A, 'css')):
    p = os.path.join(A, 'css', name)
    css = open(p, encoding='utf8').read()
    css = re.sub(r'"Proxima Nova Bold"', '"DM Sans Bold"', css)
    css = re.sub(r'"Proxima Nova (Regular|Book)"', '"DM Sans"', css)
    css = re.sub(r'"Input Mono Narrow Regular"', '"DM Sans"', css)
    open(p, 'w', encoding='utf8').write(css)

# JS: the theme's own gallery code and its libraries.
js_map = {}
for m in re.finditer(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', raw):
    src = m.group(1)
    if src.startswith('/static/theme_api/vendor/'):
        p, name = os.path.join(FA, src.lstrip('/')), short(src)
    elif src.startswith('https://bucket1.format-assets.com/'):
        p, name = os.path.join(BK, os.path.basename(src)), os.path.basename(src)
    else:
        continue
    shutil.copy(p, os.path.join(A, 'js', name))
    js_map[src] = name

# Dark mode switch and header spacing (hand-written, kept in the repo).
for f in ('css/darkmode.css', 'js/darkmode.js', 'css/header.css'):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', f)
    if os.path.abspath(src) != os.path.abspath(os.path.join(A, f)):
        shutil.copy(src, os.path.join(A, f))

# Favicons: "dm" in DM Sans, light and dark (hand-made, kept in the repo).
for f in ('favicon.svg', 'favicon-light.svg', 'favicon-dark.svg', 'favicon-32.png', 'favicon-192.png'):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'img', f)
    if os.path.abspath(src) != os.path.abspath(os.path.join(A, 'img', f)):
        shutil.copy(src, os.path.join(A, 'img', f))

# ---------- page data ----------
m = re.search(r'var _4ORMAT_DATA = (\{.*?\});\s*\n', raw, flags=re.S)
data = json.loads(m.group(1))
page = data['page']
keep_asset = ('id', 'type', 'copy_alignment', 'copy', 'alt_text', 'dominant_color', 'width', 'height')
assets = []
for i, a in enumerate(page['assets']):
    v = variants[i]
    b = {k: a.get(k) for k in keep_asset}
    b['image_url_1600x1200'] = 'images/%s/lightbox.jpg' % v['name']
    assets.append(b)
slim = {
    'page': {k: page[k] for k in ('id', 'type', 'layout', 'name', 'url', 'is_homepage')},
    'theme': data['theme'],
}
slim['page']['assets'] = assets

# ---------- HTML ----------
def section(start, end):
    a = raw.index(start); b = raw.index(end, a) + len(end)
    return raw[a:b]

browser_selector = section("<script type='text/javascript'>\ntry{function css_browser_selector", '</script>')
body_open = section('<body', '>')
body_main = section('<header class="header', '</footer>')
body_main = body_main.replace('    © All rights reserved\n</footer>',
                            '    © All rights reserved\n    <div class="made-with" style="margin-top: 8px;">made with 💙 by daedalus</div>\n</footer>')
popup = section('<section id="popup"', '</section>')

def build(prefix, canonical):
    def img(mm):
        tag = mm.group(0)
        i = int(re.search(r'data-id="(\d+)"', tag).group(1))
        v = variants[i]
        base = '%simages/%s/' % (prefix, v['name'])
        srcset = ', '.join('%s%d.jpg %dw %dh' % (base, w, w, hh) for w, hh in sorted(v['variants'], reverse=True))
        small = [w for w, _ in v['variants'] if w <= 700][-1]
        tag = re.sub(r'data-src="[^"]*"', 'data-src="%s%d.jpg"' % (base, small), tag)
        tag = re.sub(r'data-srcset="[^"]*"', 'data-srcset="%s"' % srcset, tag)
        alt = (scraped[i]['alt_text'] or '').replace('"', '&quot;')
        return tag.replace('alt=""', 'alt="%s"' % alt)
    main = re.sub(r'<img data-sizes="auto"[^>]*>', img, body_main)
    main = main.replace('<a href="/">', '<a href="%s">' % (prefix or './'))
    main = re.sub(r'\n\s*\n(\s*\n)+', '\n\n', main)

    pd = dict(slim, page=dict(slim['page'], assets=[dict(a, image_url_1600x1200=prefix + a['image_url_1600x1200']) for a in assets]))
    css = ['fonts.css'] + list(css_map.values()) + ['darkmode.css', 'header.css']
    links = '\n'.join('<link href="%sassets/css/%s" media="screen" rel="stylesheet" type="text/css">' % (prefix, c) for c in css)
    icons = ('<link href="%(p)sassets/img/favicon-32.png" rel="icon" sizes="32x32">\n'
             '<link href="%(p)sassets/img/favicon.svg" rel="icon" type="image/svg+xml" id="favicon">\n'
             '<link href="%(p)sassets/img/favicon-192.png" rel="apple-touch-icon">' % {'p': prefix})
    cover = 'https://%s/images/cover/1600.jpg' % DOMAIN
    scripts = '\n'.join('<script src="%sassets/js/%s"%s></script>' % (prefix, n, ' async' if n in ('picturefill-3.0.1.min.js', 'lazysizes.min.js', 'ls.parent-fit.min.js') else '')
                        for n in list(js_map.values()) + ['darkmode.js'] if n != 'jquery-1.11.2.min.js')
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>Photographs - Dhruvil Mehta's Portfolio</title>
<link rel="canonical" href="%(canonical)s">
<script>try{if(localStorage.getItem('theme')==='dark')document.documentElement.setAttribute('data-theme','dark')}catch(e){}</script>
%(browser_selector)s
%(icons)s
<meta name="description" content="My photos!">
<meta name="robots" content="noai, noimageai">
<meta property="og:site_name" content="Dhruvil Mehta's Portfolio">
<meta property="og:title" content="Photographs - Dhruvil Mehta's Portfolio">
<meta property="og:type" content="website">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(cover)s">
<meta property="og:image:width" content="1600">
<meta property="og:image:height" content="1600">
<meta property="og:description" content="My photos!">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Photographs - Dhruvil Mehta's Portfolio">
<meta name="twitter:description" content="My photos!">
%(links)s
<style>b, strong { font-weight: bold; } i, em { font-style: italic; }</style>
</head>
%(body_open)s

%(main)s

<script src="%(prefix)sassets/js/jquery-1.11.2.min.js"></script>
<script>
var _4ORMAT_DATA = %(data)s;
</script>

%(popup)s

<script>
window.lazySizesConfig = window.lazySizesConfig || {};
window.lazySizesConfig.expand = 700;
window.lazySizesConfig.expFactor = 4;
</script>
%(scripts)s
</body>
</html>
""" % dict(canonical=canonical, browser_selector=browser_selector, icons=icons, cover=cover, links=links,
           body_open=body_open, main=main, prefix=prefix, data=json.dumps(pd, separators=(',', ':')),
           popup=popup, scripts=scripts)

html = build('', 'https://%s/' % DOMAIN)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(html)
# /portfolio serves the same gallery on Format.
os.makedirs(os.path.join(OUT, 'portfolio'), exist_ok=True)
open(os.path.join(OUT, 'portfolio', 'index.html'), 'w', encoding='utf8').write(build('../', 'https://%s/' % DOMAIN))
open(os.path.join(OUT, 'CNAME'), 'w').write(DOMAIN + '\n')
open(os.path.join(OUT, '.nojekyll'), 'w').write('')
print('ok', len(html))

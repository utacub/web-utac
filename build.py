"""Generador del web estàtic de la UTAC.

Ús:
  python build.py              -> versió de producció a ./dist (URL netes: /productes-suport/teclats/)
  python build.py --preview    -> versió de prova a ./preview (enllaços relatius i camins ASCII)

Idiomes: el català és a l'arrel (content/) i les traduccions a content-es/ (-> /es/...) i content-en/ (-> /en/...).
Cada pàgina traduïda té el mateix camí que la catalana (o ho indica amb el camp «original»).
Si una pàgina encara no té traducció, es publica amb el text català.
"""
import os, re, sys, shutil, unicodedata, html
import yaml, markdown
from urllib.parse import unquote
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.abspath(__file__))
PREVIEW = '--preview' in sys.argv
OUT = os.path.join(ROOT, 'preview' if PREVIEW else 'dist')
# Prefix de l'adreça quan el web no és a l'arrel del domini (p. ex. '/web-utac' a utacub.github.io/web-utac/)
BASE = os.environ.get('SITE_BASE', '').rstrip('/')
# Domini propi (p. ex. 'www.utac.cat'); només s'activa quan els DNS ja apunten a GitHub
DOMINI = os.environ.get('CUSTOM_DOMAIN', '').strip()

SITE = yaml.safe_load(open(os.path.join(ROOT, 'data/site.yaml')))
MENU = yaml.safe_load(open(os.path.join(ROOT, 'data/menu.yaml')))['menu']
ICONS = yaml.safe_load(open(os.path.join(ROOT, 'data/icones.yaml')))
TEXTOS = yaml.safe_load(open(os.path.join(ROOT, 'data/textos.yaml')))

# Idiomes del web: el primer és el principal (sense prefix a l'adreça)
IDIOMES = [
    {'codi': 'ca', 'nom': 'Català', 'carpeta': 'content'},
    {'codi': 'es', 'nom': 'Castellano', 'carpeta': 'content-es'},
    {'codi': 'en', 'nom': 'English', 'carpeta': 'content-en'},
]
CODIS = [i['codi'] for i in IDIOMES]
PRINCIPAL = CODIS[0]


def prefix(lang):
    return '' if lang == PRINCIPAL else '/' + lang


def split_lang(url):
    """'/es/descarregues' -> ('es', '/descarregues'); '/descarregues' -> ('ca', '/descarregues')."""
    parts = url.split('/')
    if len(parts) > 1 and parts[1] in CODIS and parts[1] != PRINCIPAL:
        return parts[1], '/' + '/'.join(parts[2:])
    return PRINCIPAL, url


def textos(lang):
    return {k: (v.get(lang) if v.get(lang) is not None else v.get(PRINCIPAL, '')) for k, v in TEXTOS.items()}


def ascii_path(p):
    p = unicodedata.normalize('NFKD', p).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9/_-]+', '-', p)


def out_rel(url):
    """Ruta del fitxer HTML de sortida per a una URL interna ('/x/y')."""
    p = url.strip('/')
    if PREVIEW:
        p = ascii_path(p)
        lang, rest = split_lang('/' + p)
        if rest.strip('/') in ('', 'inici'):
            return prefix(lang).lstrip('/') + ('/' if lang != PRINCIPAL else '') + 'index.html'
    return p + '/index.html' if p else 'index.html'


def load_pages(carpeta):
    pages = {}
    base = os.path.join(ROOT, carpeta)
    for dp, _, fs in os.walk(base):
        for f in fs:
            if f.endswith('.md'):
                full = os.path.join(dp, f)
                raw = open(full, encoding='utf-8').read()
                fm = yaml.safe_load(raw.split('---\n')[1]) or {}
                url = '/' + os.path.relpath(full, base)[:-3]
                # una traducció creada des del panell pot tenir un altre nom de fitxer: «original» diu de quina pàgina és
                orig = (fm.get('original') or '').strip()
                if orig:
                    url = '/' + split_lang(unquote(orig).rstrip('/'))[1].strip('/')
                fm['url'] = url
                pages[url] = fm
    return pages


PAGES = load_pages('content')
TRADUCCIONS = {i['codi']: load_pages(i['carpeta']) for i in IDIOMES if i['codi'] != PRINCIPAL}


def walk_menu(items, parents=()):
    for it in items:
        yield it, parents
        yield from walk_menu(it.get('fills', []), parents + (it,))


MENU_INDEX = {it['url']: (it, parents) for it, parents in walk_menu(MENU)}


def make_linker(current_url, lang=PRINCIPAL):
    cur_file = out_rel(current_url)
    cur_dir = os.path.dirname(cur_file)

    def link(url, to_lang=None):
        """Enllaç intern: les adreces del contingut són les catalanes i s'hi afegeix el prefix de l'idioma."""
        if not url:
            return url
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
            return url
        if url.startswith('/assets/'):
            # fitxer pujat des del panell d'edició
            return os.path.relpath(url[1:], cur_dir or '.') if PREVIEW else BASE + url
        if url.startswith('/'):
            path, _, frag = url.partition("#")
            path = unquote(path)
            ll, rest = split_lang(path)
            if ll == PRINCIPAL:
                ll = to_lang or lang
            path = prefix(ll) + rest
            if PREVIEW:
                target = out_rel(path)
                r = os.path.relpath(target, cur_dir or '.')
            else:
                r = BASE + (path.rstrip('/') + '/' if rest not in ('/', '/inici') else prefix(ll) + '/')
            return r + ('#' + frag if frag else '')
        return url

    def asset(name):
        if PREVIEW:
            return os.path.relpath('assets/' + name, cur_dir or '.')
        return BASE + '/assets/' + name

    def img(name):
        """Imatge de assets/img; accepta 'foto.webp' o '/assets/img/foto.webp' (format del panell)."""
        n = (name or '').strip()
        for pre in ('/assets/img/', 'assets/img/', '/'):
            if n.startswith(pre):
                n = n[len(pre):]
                break
        return asset('img/' + n)

    return link, asset, img


MD = markdown.Markdown(extensions=['extra', 'sane_lists'])


def render_md(text, link):
    MD.reset()
    t = text or ''
    # salts de línia que escriu l'editor del panell ('\\' o <br> al final de línia)
    t = re.sub(r'\\\n', '  \n', t)
    h = MD.convert(t)
    h = re.sub(r'href="([^"]+)"', lambda m: 'href="%s"' % html.escape(link(html.unescape(m.group(1))), quote=True), h)
    return h


def file_kind(name):
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if '/' in ext or len(ext) > 8:
        ext = ''
    return ext.upper() if ext else ''


env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')), autoescape=select_autoescape(['html']))
env.globals.update(SITE=SITE, MENU=MENU, ICONS=ICONS, PREVIEW=PREVIEW, file_kind=file_kind, IDIOMES=IDIOMES)


def make_titol(lang):
    """Nom d'un element del menú en l'idioma: titol_es/titol_en, si no el títol de la pàgina traduïda, si no el català."""
    def titol(item):
        if lang == PRINCIPAL:
            return item.get('titol')
        t = item.get('titol_' + lang)
        if t:
            return t
        tr = TRADUCCIONS[lang].get(item.get('url'))
        return (tr or {}).get('titol') or item.get('titol')
    return titol


def absolut(url):
    return ('https://' + DOMINI if DOMINI else '') + url


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    tpl = env.get_template('pagina.html')
    total = 0
    for lang in CODIS:
        urls = list(PAGES) + [u for u in TRADUCCIONS.get(lang, {}) if u not in PAGES]
        sense = []
        for url in urls:
            if lang == PRINCIPAL:
                page, traduida = PAGES[url], True
            else:
                tr = TRADUCCIONS[lang].get(url)
                page, traduida = (tr, True) if tr else (PAGES[url], False)
                if not tr:
                    sense.append(url)
            lurl = prefix(lang) + url
            link, asset, img = make_linker(lurl, lang)
            titol = make_titol(lang)
            node, parents = MENU_INDEX.get(url, ({'titol': page['titol'], 'url': url}, ()))
            section = parents[0] if parents else node
            # adreça d'aquesta mateixa pàgina en cada idioma (selector i hreflang)
            alternatives = [dict(i, href=link(url, i['codi']), abs=absolut(prefix(i['codi']) + ('/' if url == '/inici' else url.rstrip('/') + '/')))
                            for i in IDIOMES]
            ctx = dict(page=page, link=link, asset=asset, img=img, md=lambda t, link=link: render_md(t, link),
                       node=node, parents=parents, section=section, current=url, lang=lang, T=textos(lang),
                       titol=titol, alternatives=alternatives, traduida=traduida,
                       lang_contingut=lang if traduida else PRINCIPAL)
            html_out = tpl.render(**ctx)
            dest = os.path.join(OUT, out_rel(lurl))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, 'w', encoding='utf-8').write(html_out)
            if url == '/inici' and not PREVIEW:
                open(os.path.join(OUT, prefix(lang).lstrip('/'), 'index.html'), 'w', encoding='utf-8').write(html_out)
            total += 1
        if sense:
            print('Pàgines sense traducció (%s), publicades en català:' % lang, ', '.join(sorted(sense)))
    if not PREVIEW:
      link, asset, img = make_linker('/404')
      open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
        env.get_template('404.html').render(link=link, asset=asset, img=img, current='/404', lang=PRINCIPAL,
                                            T=textos(PRINCIPAL), titol=make_titol(PRINCIPAL), alternatives=[],
                                            TT={l: textos(l) for l in CODIS}, prefix=prefix))
    if not PREVIEW:
        if DOMINI:
            open(os.path.join(OUT, 'CNAME'), 'w').write(DOMINI + '\n')
        open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('Pàgines generades:', total, '->', OUT)


if __name__ == '__main__':
    build()

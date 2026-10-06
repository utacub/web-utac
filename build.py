"""Generador del web estàtic de la UTAC.

Ús:
  python build.py              -> versió de producció a ./dist (URL netes: /productes-suport/teclats/)
  python build.py --preview    -> versió de prova a ./preview (enllaços relatius i camins ASCII)
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


def ascii_path(p):
    p = unicodedata.normalize('NFKD', p).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9/_-]+', '-', p)


def out_rel(url):
    """Ruta del fitxer HTML de sortida per a una URL interna ('/x/y')."""
    p = url.strip('/')
    if PREVIEW:
        p = ascii_path(p)
    return 'index.html' if p in ('', 'inici') and PREVIEW else (p + '/index.html' if p else 'index.html')


def load_pages():
    pages = {}
    for dp, _, fs in os.walk(os.path.join(ROOT, 'content')):
        for f in fs:
            if f.endswith('.md'):
                full = os.path.join(dp, f)
                raw = open(full, encoding='utf-8').read()
                fm = yaml.safe_load(raw.split('---\n')[1])
                url = '/' + os.path.relpath(full, os.path.join(ROOT, 'content'))[:-3]
                fm['url'] = url
                pages[url] = fm
    return pages


PAGES = load_pages()


def walk_menu(items, parents=()):
    for it in items:
        yield it, parents
        yield from walk_menu(it.get('fills', []), parents + (it,))


MENU_INDEX = {it['url']: (it, parents) for it, parents in walk_menu(MENU)}


def make_linker(current_url):
    cur_file = out_rel(current_url)
    cur_dir = os.path.dirname(cur_file)

    def link(url):
        if not url:
            return url
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
            return url
        if url.startswith('/'):
            path, _, frag = url.partition("#")
            path = unquote(path)
            if PREVIEW:
                target = out_rel(path)
                r = os.path.relpath(target, cur_dir or '.')
            else:
                r = BASE + (path.rstrip('/') + '/' if path not in ('/', '/inici') else '/')
            return r + ('#' + frag if frag else '')
        return url

    def asset(name):
        if PREVIEW:
            return os.path.relpath('assets/' + name, cur_dir or '.')
        return BASE + '/assets/' + name

    return link, asset


MD = markdown.Markdown(extensions=['extra', 'sane_lists'])


def render_md(text, link):
    MD.reset()
    h = MD.convert(text or '')
    h = re.sub(r'href="([^"]+)"', lambda m: 'href="%s"' % html.escape(link(html.unescape(m.group(1))), quote=True), h)
    return h


def file_kind(name):
    ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if '/' in ext or len(ext) > 8:
        ext = ''
    return ext.upper() if ext else 'Fitxer'


env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')), autoescape=select_autoescape(['html']))
env.globals.update(SITE=SITE, MENU=MENU, ICONS=ICONS, PREVIEW=PREVIEW, file_kind=file_kind)


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    tpl = env.get_template('pagina.html')
    for url, page in PAGES.items():
        link, asset = make_linker(url)
        node, parents = MENU_INDEX.get(url, ({'titol': page['titol'], 'url': url}, ()))
        section = parents[0] if parents else node
        ctx = dict(page=page, link=link, asset=asset, md=lambda t, link=link: render_md(t, link),
                   node=node, parents=parents, section=section, current=url)
        html_out = tpl.render(**ctx)
        dest = os.path.join(OUT, out_rel(url))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'w', encoding='utf-8').write(html_out)
        if url == '/inici' and not PREVIEW:
            open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html_out)
    if not PREVIEW:
      link, asset = make_linker('/404')
      open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
        env.get_template('404.html').render(link=link, asset=asset, current='/404'))
    if not PREVIEW:
        if DOMINI:
            open(os.path.join(OUT, 'CNAME'), 'w').write(DOMINI + '\n')
        open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('Pàgines generades:', len(PAGES), '->', OUT)


if __name__ == '__main__':
    build()

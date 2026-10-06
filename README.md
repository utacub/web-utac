# Web de la UTAC

Codi i contingut del web de la Unitat de Tècniques Augmentatives de Comunicació (UTAC).

- `content/` — una pàgina per fitxer (text i blocs: fitxes, vídeos, descàrregues...).
- `data/` — menú (`menu.yaml`), dades generals i peu de pàgina (`site.yaml`), icones.
- `assets/` — imatges, full d'estil i JavaScript.
- `templates/` — plantilles HTML.
- `build.py` — genera el web a `dist/`.

Cada canvi desat a la branca `main` es publica automàticament (GitHub Actions → GitHub Pages) en un o dos minuts.

Prova local: `pip install -r requirements.txt` i després `python build.py` (o `python build.py --preview`).

## Panell d'edició

El contingut es pot editar sense tocar codi des de **https://app.pagescms.org**, entrant amb el compte de GitHub i triant el repositori `web-utac`. La configuració del panell és al fitxer `.pages.yml`. Cada canvi desat es publica automàticament en un o dos minuts.

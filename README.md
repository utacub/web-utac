# Web de la UTAC

Codi i contingut del web de la Unitat de Tècniques Augmentatives de Comunicació (UTAC).

- `content/` — una pàgina per fitxer (text i blocs: fitxes, vídeos, descàrregues...).
- `data/` — menú (`menu.yaml`), dades generals i peu de pàgina (`site.yaml`), icones.
- `assets/` — imatges, full d'estil i JavaScript.
- `templates/` — plantilles HTML.
- `build.py` — genera el web a `dist/`.

Cada canvi desat a la branca `main` es publica automàticament (GitHub Actions → GitHub Pages) en un o dos minuts.

Prova local: `pip install -r requirements.txt` i després `python build.py` (o `python build.py --preview`).

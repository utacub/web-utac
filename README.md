# Web de la UTAC

Codi i contingut del web de la Unitat de Tècniques Augmentatives de Comunicació (UTAC).

- `content/` — una pàgina per fitxer (text i blocs: fitxes, vídeos, descàrregues...), en català.
- `content-es/`, `content-en/` — les mateixes pàgines en castellà i anglès, amb el mateix camí i nom de fitxer.
- `data/` — menú (`menu.yaml`, amb els noms en els tres idiomes), dades generals (`site.yaml`), textos fixos de la interfície en tres idiomes (`textos.yaml`), icones.
- `assets/` — imatges, full d'estil i JavaScript.
- `templates/` — plantilles HTML.
- `build.py` — genera el web a `dist/`.

Cada canvi desat a la branca `main` es publica automàticament (GitHub Actions → GitHub Pages) en un o dos minuts.

Prova local: `pip install -r requirements.txt` i després `python build.py` (o `python build.py --preview`).

## Panell d'edició

El contingut es pot editar sense tocar codi des de **https://app.pagescms.org**, entrant amb el compte de GitHub i triant el repositori `web-utac`. La configuració del panell és al fitxer `.pages.yml`. Cada canvi desat es publica automàticament en un o dos minuts.

## Idiomes

El web es publica en català (www.utac.cat/...), castellà (www.utac.cat/es/...) i anglès (www.utac.cat/en/...). La capçalera té un selector CA · ES · EN que porta a la mateixa pàgina en l'altre idioma.

- Els enllaços interns del contingut s'escriuen sempre amb l'adreça catalana (p. ex. `/descarregues`); el generador hi afegeix `/es` o `/en` segons l'idioma de la pàgina.
- Quan es crea una pàgina catalana nova, fins que no se'n fa la traducció, les versions /es/ i /en/ mostren el text català amb un avís.
- Per traduir-la des del panell: «Pàgines en castellà» o «Pàgines en anglès», a la mateixa carpeta, i omplir el camp «Pàgina catalana que tradueix» amb l'adreça catalana. Al menú, cal omplir també «Nom en castellà» i «Nom en anglès».

## Criteri obligatori d’edició multilingüe

Tots els canvis del web s’han d’aplicar en català, castellà i anglès en la mateixa actualització. En modificar una pàgina, actualitza les versions de `content/`, `content-es/` i `content-en/`, tradueix els textos i les descripcions alternatives, i mantén equivalents els enllaços, els recursos visuals i el format. Verifica les tres versions publicades. Aquest criteri també s’aplica als textos d’interfície, els menús i les plantilles compartides; evita publicar una versió amb contingut desactualitzat.

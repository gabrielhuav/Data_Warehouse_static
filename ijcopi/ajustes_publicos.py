#!/usr/bin/env python3
"""Vuelve metropolitana la copia publica, que reutiliza assets/ y las paginas de ICOKG.

    python ajustes_publicos.py <carpeta de la copia>

Solo se aplica a la copia que prepara publicar.ps1. En la rama esos archivos siguen iguales a
main, asi que nada de esto puede llegar al sitio de ICOKG. Si un texto esperado ya no existe, se
detiene en lugar de publicar una copia a medias.
"""
import re
import sys
from pathlib import Path

raiz = Path(sys.argv[1])
MARCA_ES = "Agua en la ZM de Ciudad de México"
MARCA_EN = "Water in the Mexico City Metropolitan Area"
TITULO = ("Territorial Information Retrieval from Heterogeneous Open Data: Extending a Water Data "
          "Warehouse from Mexico City to its Metropolitan Area")
REPO = "https://github.com/gabrielhuav/Data_Warehouse_ZMVM"


def leer(rel: str) -> str:
    with open(raiz / rel, encoding="utf-8", newline="") as fh:
        return fh.read()


def escribir(rel: str, texto: str) -> None:
    with open(raiz / rel, "w", encoding="utf-8", newline="") as fh:
        fh.write(texto)


def cambiar(texto: str, viejo: str, nuevo: str) -> str:
    if viejo not in texto:
        raise SystemExit(f"no se encontro: {viejo}")
    return texto.replace(viejo, nuevo)


def poner(texto: str, clave: str, es: str, en: str) -> str:
    """Cambia una clave en los dos diccionarios de i18n.js: primero el espanol, luego el ingles."""
    valores = iter((es, en))
    patron = re.compile(r"('" + re.escape(clave) + r"':\s*)'[^']*'")
    texto, n = patron.subn(lambda m: f"{m.group(1)}'{next(valores)}'", texto)
    if n != 2:
        raise SystemExit(f"{clave}: {n} apariciones en i18n.js")
    return texto


i18n = leer("assets/i18n.js")
i18n = cambiar(cambiar(i18n, "'titulo.index'", "'titulo.panel'"), "'meta.index'", "'meta.panel'")
i18n = poner(i18n, "barra.marca", MARCA_ES, MARCA_EN)
i18n = poner(i18n, "titulo.panel", f"Panel CDMX — {MARCA_ES}", f"CDMX dashboard — {MARCA_EN}")
i18n = poner(i18n, "titulo.mapa", f"Mapa CDMX — {MARCA_ES}", f"CDMX map — {MARCA_EN}")
i18n = poner(i18n, "titulo.grafo", f"Grafo CDMX — {MARCA_ES}", f"CDMX graph — {MARCA_EN}")
i18n = poner(i18n, "titulo.vecindad", f"Vecindad CDMX — {MARCA_ES}", f"CDMX adjacency — {MARCA_EN}")
i18n = poner(i18n, "tema.guinda", "Guinda", "Maroon")
i18n = poner(i18n, "nav.index", "Panel CDMX", "CDMX dashboard")
i18n = poner(i18n, "nav.mapa", "Mapa CDMX", "CDMX map")
i18n = poner(i18n, "nav.grafo", "Grafo CDMX", "CDMX graph")
i18n = poner(i18n, "nav.vecindad", "Vecindad CDMX", "CDMX adjacency")
nuevas = iter(("'nav.zm': 'Mapa metropolitano', 'nav.consultas': 'Consultas',",
               "'nav.zm': 'Metropolitan map', 'nav.consultas': 'Queries',"))
i18n, n = re.subn(r"(?m)^(\s*)('nav\.index':)", lambda m: f"{m.group(1)}{next(nuevas)}\n{m.group(1)}{m.group(2)}", i18n)
if n != 2:
    raise SystemExit("nav.index no aparece dos veces")
escribir("assets/i18n.js", i18n)

nav = leer("assets/nav.js")
nav = cambiar(nav, "['index.html',    'nav.index'],",
              "['ijcopi/mapa-zm.html', 'nav.zm'],\n    ['ijcopi/consultas.html', 'nav.consultas'],\n"
              "    ['panel.html',    'nav.index'],")
nav = cambiar(nav, "h.toLowerCase() === actual", "h.split('/').pop().toLowerCase() === actual")
nav = cambiar(nav, "https://github.com/gabrielhuav/Data_Warehouse_static", REPO)
nav, n = re.subn(r"<em>Territorial Information Retrieval.*?</em>", f"<em>{TITULO}</em>", nav, flags=re.S)
if n != 1:
    raise SystemExit("no se encontro el titulo en el pie")
escribir("assets/nav.js", nav)

# La portada del sitio es el mapa metropolitano; el panel de la CDMX pasa a panel.html
(raiz / "index.html").rename(raiz / "panel.html")
escribir("index.html", f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=ijcopi/mapa-zm.html">
    <title>{MARCA_ES}</title>
</head>
<body>
    <a href="ijcopi/mapa-zm.html">{MARCA_ES}</a>
</body>
</html>
""")
for pagina, titulo in (("panel.html", "Panel CDMX"), ("mapa.html", "Mapa CDMX"), ("grafo.html", "Grafo CDMX"),
                       ("vecindad.html", "Vecindad CDMX")):
    html = re.sub(r"<title>.*?</title>", f"<title>{titulo} — {MARCA_ES}</title>", leer(pagina), count=1)
    escribir(pagina, html.replace('href="index.html"', 'href="panel.html"'))
print("copia publica ajustada")

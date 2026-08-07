#!/usr/bin/env python3
"""
unificar_paginas.py -- Hace que index.html y mapa.html usen el mismo sistema de
diseño que grafo.html y vecindad.html.

Quita el bloque <style> incrustado que traían, enlaza las hojas compartidas e
inserta la barra, el pie y los scripts comunes. NO toca el marcado ni los
identificadores, así que el JavaScript de esas páginas sigue funcionando.

REAPLICABLE: cada corrida retira primero lo que inyectó la corrida anterior y
lo vuelve a poner. Una versión previa salía temprano si encontraba su propia
marca, lo que impedía que las correcciones posteriores llegaran a las páginas.

    python scripts/unificar_paginas.py --repo .
"""
from __future__ import annotations
import argparse, os, re, sys

INI = '<!-- sistema de diseño compartido: inicio -->'
FIN = '<!-- sistema de diseño compartido: fin -->'

HOJAS = ('<link rel="stylesheet" href="assets/estilo.css">\n'
         '    <link rel="stylesheet" href="assets/paginas.css">')

SCRIPTS = {
    'index.html': ['assets/nav.js', 'assets/paginacion.js', 'assets/atipicos.js'],
    'mapa.html':  ['assets/nav.js', 'assets/enlace-vecindad.js'],
}
CABEZA = {'index.html': ['assets/tema-graficas.js'], 'mapa.html': []}


def limpiar(h: str) -> str:
    """Retira todo lo que inyectaron corridas anteriores."""
    h = re.sub(re.escape(INI) + r'.*?' + re.escape(FIN) + r'\n?', '', h, flags=re.S)
    h = re.sub(r'[ \t]*<link rel="stylesheet" href="assets/(estilo|paginas)\.css">\n?', '', h)
    h = re.sub(r'[ \t]*<script src="assets/[\w.-]+"></script>\n?', '', h)
    h = re.sub(r'[ \t]*<header data-barra></header>\n?', '', h)
    h = re.sub(r'[ \t]*<footer data-pie></footer>\n?', '', h)
    h = re.sub(r'[ \t]*<!-- sistema de diseño compartido -->\n?', '', h)
    h = re.sub(r'[ \t]*<meta name="description"[^>]*>\n?', '', h)
    h = re.sub(r'[ \t]*<link rel="preload" as="fetch"[^>]*>\n?', '', h)
    h = re.sub(r'[ \t]*<link rel="preconnect"[^>]*>\n?', '', h)
    h = h.replace('<div class="app-container" role="main">', '<div class="app-container">')
    h = h.replace('<main class="app-container">', '<div class="app-container">')
    return h


def parchar(ruta: str, pagina: str) -> str:
    with open(ruta, encoding='utf-8') as f:
        h = f.read()
    h = limpiar(h)

    quitados = 0
    h, quitados = re.subn(r'[ \t]*<style>.*?</style>\n?', '', h, flags=re.S)

    # --- Lighthouse: quitar el bloqueo de renderizado ---------------
    # Plotly y Leaflet en el <head> bloquean el primer pintado: 2.8 s en
    # escritorio y 9.2 s en movil segun el informe. Con defer el navegador
    # pinta primero y ejecuta despues, sin cambiar el orden entre ellos.
    h = re.sub(r'(<script src="https://(?:cdn\.plot\.ly|unpkg\.com)/[^"]+")(?![^>]*defer)',
               r'\1 defer', h)
    # Leaflet CSS: se precarga sin bloquear
    h = h.replace('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">',
                  '<link rel="preload" as="style" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" '
                  'onload="this.rel=\'stylesheet\'">\n    '
                  '<noscript><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"></noscript>')
    # los datos se piden en cuanto se puede, no al final del parseo
    if 'rel="preload" as="fetch"' not in h:
        h = h.replace('</head>',
            '    <link rel="preload" as="fetch" href="consumo.json" crossorigin>\n'
            '    <link rel="preconnect" href="https://cdn.plot.ly">\n'
            '    <link rel="preconnect" href="https://unpkg.com">\n</head>', 1)

    # --- SEO: metadescripcion ---------------------------------------
    if 'name="description"' not in h:
        desc = ('Almacen de datos y grafo de conocimiento del consumo de agua en la '
                'Ciudad de Mexico, construido con datos abiertos de SACMEX. '
                'Consulta por alcaldia y colonia, mapa coropletico y SPARQL en el navegador.')
        h = h.replace('</head>', f'    <meta name="description" content="{desc}">\n</head>', 1)

    # --- Accesibilidad: punto de referencia principal ----------------
    # role="main" en vez de cambiar la etiqueta: satisface la auditoria sin
    # arriesgar el emparejamiento de <div> del marcado original.
    h = h.replace('<main class="app-container">', '<div class="app-container">')
    h = h.replace('<div class="app-container">', '<div class="app-container" role="main">', 1)

    # hojas + scripts que deben cargar antes que el cuerpo
    cabeza = INI + '\n    ' + HOJAS
    for s in CABEZA[pagina]:
        cabeza += f'\n    <script src="{s}"></script>'
    cabeza += '\n    ' + FIN
    if '</head>' not in h:
        return 'ERROR: no tiene </head>'
    h = h.replace('</head>', f'    {cabeza}\n</head>', 1)

    if not re.search(r'<body[^>]*>', h):
        return 'ERROR: no tiene <body>'
    h = re.sub(r'(<body[^>]*>)', r'\1\n<header data-barra></header>', h, count=1)

    cola = '<footer data-pie></footer>\n'
    for s in SCRIPTS[pagina]:
        cola += f'<script src="{s}"></script>\n'
    h = h.replace('</body>', cola + '</body>', 1)

    with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        f.write(h)
    return (f'unificada (se quitaron {quitados} bloques <style>)' if quitados
            else 'reaplicada (ya no traía <style> propio)')


def verificar(ruta: str, pagina: str) -> list[str]:
    with open(ruta, encoding='utf-8') as f:
        h = f.read()
    p = []
    if '<style>' in h: p.append('quedó un <style> incrustado')
    for hoja in ('assets/estilo.css', 'assets/paginas.css'):
        if h.count(hoja) != 1: p.append(f'{hoja} aparece {h.count(hoja)} veces')
    for s in SCRIPTS[pagina] + CABEZA[pagina]:
        if h.count(s) != 1: p.append(f'{s} aparece {h.count(s)} veces')
    if h.count('<header data-barra>') != 1: p.append('barra duplicada o ausente')
    if h.count('<footer data-pie>') != 1: p.append('pie duplicado o ausente')
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default='.')
    a = ap.parse_args()
    fallos = 0
    for pagina in ('index.html', 'mapa.html'):
        r = os.path.join(a.repo, pagina)
        if not os.path.exists(r):
            print(f'{pagina}: no existe'); continue
        print(f'{pagina}: {parchar(r, pagina)}')
        problemas = verificar(r, pagina)
        if problemas:
            fallos += 1
            for x in problemas: print(f'   FALLO: {x}')
        else:
            print('   verificada')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())

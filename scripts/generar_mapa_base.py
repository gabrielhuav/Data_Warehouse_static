"""
generar_mapa_base.py
============================================================================
Builds the offline basemap that mapa.html and vecindad.html fall back to
when no tile provider answers: assets/mapa-base/cdmx.json.

Why it exists
-------------
Both maps used to ask OpenStreetMap for their tiles and nobody else. A
sister artefact lost its map in the middle of a talk when its only provider
(CARTO) began answering keyless requests with an "API KEY REQUIRED" image
served as 200 OK: Leaflet never noticed, because nothing had failed at the
HTTP level. assets/mapa-teselas.js now tries a chain of free providers and
verifies each one; this file is the last link of that chain. It is served
from the same GitHub Pages site as the pages themselves, so if the page
loaded, the basemap loads.

What it contains
----------------
- The outline of Mexico City and the limits between its 16 alcaldías, both
  derived from alcaldias.geojson, which the site already serves and the
  choropleth already draws. Neighbouring alcaldías share their vertices in
  that file, so an edge used by one polygon is the city outline and an edge
  used by two is an internal limit.
- From OpenStreetMap (ODbL), through Overpass: roads from motorway to
  tertiary, rivers and canals, bodies of water, large parks and the airport,
  and named places (colonias and pueblos). Mexico City is dense, so the file
  has a budget of about 1.5 MB: secondary and tertiary roads, minor places
  and parks are kept only inside the city plus a narrow margin; motorways,
  trunks and primaries are kept across the whole frame.

Geometries are simplified with Douglas-Peucker (tolerances in metres, around
two pixels at zoom 16), quantised to 1e-5 degrees (~1.1 m) and
delta-encoded. The browser draws them on canvas tiles; see `capaLocal` in
assets/mapa-teselas.js.

Usage
-----
    python scripts/generar_mapa_base.py                # downloads from Overpass
    python scripts/generar_mapa_base.py --desde DIR    # reuses DIR/area.json,
                                                       # downloading it if missing

It also rewrites, between its marker comments in assets/mapa-teselas.js,
the minimal outline drawn if even this file cannot be fetched
(`CONTORNO_MINIMO`, `LIMITES_MINIMOS`, `ALCALDIAS_MINIMAS`).
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

RAIZ = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ALCALDIAS = os.path.join(RAIZ, 'alcaldias.geojson')
SALIDA = os.path.join(RAIZ, 'assets', 'mapa-base', 'cdmx.json')
MODULO = os.path.join(RAIZ, 'assets', 'mapa-teselas.js')

MARGEN_CAJA = 0.04          # grados alrededor de la ciudad para el encuadre
MARGEN_MENORES = 0.012      # grados alrededor de la ciudad para lo secundario
CELDA = 0.004               # grados por celda de la máscara de la ciudad
Q = 100000                  # 1e-5 grados
PARQUE_MIN_KM2 = 0.15       # parques más pequeños no se ven a escala de ciudad
AGUA_MIN_KM2 = 0.002

ESPEJOS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
]
USUARIO = 'Data_Warehouse_static (github.com/gabrielhuav/Data_Warehouse_static)'

CONSULTA_AREA = (
    '[out:json][timeout:300][bbox:{s},{w},{n},{e}];('
    'way["highway"~"^(motorway|trunk|primary|secondary|tertiary|'
    'motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"];'
    'way["waterway"~"^(river|canal)$"];'
    'way["natural"="water"];rel["natural"="water"];way["landuse"="reservoir"];'
    'way["leisure"="park"];rel["leisure"="park"];'
    'way["aeroway"="aerodrome"];rel["aeroway"="aerodrome"];'
    'node["place"~"^(city|town|village|suburb|quarter|neighbourhood)$"];'
    ');out geom qt;'
)

# Tolerancias de Douglas-Peucker en metros. A zoom 16 un píxel mide ~2.25 m
# en esta latitud.
TOL = {'via1': 5, 'via2': 6, 'via3': 7, 'rio': 8, 'canal': 8,
       'agua': 8, 'parque': 12, 'limite': 6, 'ciudad': 6}
TOL_MINIMO = {'ciudad': 120, 'limite': 250}

R = 6378137.0


# ---------------------------------------------------------------------------
# utilidades geométricas

def merc(lon, lat):
    return math.radians(lon) * R, math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * R


def simplificar(pts, tol):
    """Douglas-Peucker iterativo sobre [(lon, lat)], tolerancia en metros."""
    if len(pts) < 3:
        return pts
    m = [merc(*p) for p in pts]
    queda = [False] * len(pts)
    queda[0] = queda[-1] = True
    pila = [(0, len(pts) - 1)]
    tol2 = tol * tol
    while pila:
        a, b = pila.pop()
        ax, ay = m[a]
        dx, dy = m[b][0] - ax, m[b][1] - ay
        l2 = dx * dx + dy * dy
        mejor, im = -1.0, -1
        for i in range(a + 1, b):
            px, py = m[i]
            t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
            d2 = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d2 > mejor:
                mejor, im = d2, i
        if mejor > tol2:
            queda[im] = True
            pila += [(a, im), (im, b)]
    return [p for p, k in zip(pts, queda) if k]


def codificar(pts):
    """Enteros a 1e-5 grados en deltas: [lon0, lat0, dlon1, dlat1, ...]."""
    out, px, py = [], None, None
    for lon, lat in pts:
        x, y = round(lon * Q), round(lat * Q)
        if px is None:
            out += [x, y]
        elif (x, y) != (px, py):
            out += [x - px, y - py]
        else:
            continue
        px, py = x, y
    return out


def area_km2(anillo):
    """Área aproximada de un anillo (lon, lat), en km²."""
    lat0 = math.radians(sum(p[1] for p in anillo) / len(anillo))
    kx, ky = 111.32 * math.cos(lat0), 110.57
    s = 0.0
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        s += (x1 * kx) * (y2 * ky) - (x2 * kx) * (y1 * ky)
    return abs(s) / 2


def dentro(pt, anillo):
    """Punto en polígono por paridad de cruces."""
    x, y = pt
    d = False
    j = len(anillo) - 1
    for i in range(len(anillo)):
        xi, yi = anillo[i]
        xj, yj = anillo[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            d = not d
        j = i
    return d


def encadenar(aristas):
    """Une aristas sueltas (pares de puntos) en polilíneas: sigue cada
    cadena mientras el extremo tenga exactamente una continuación."""
    vecinos = defaultdict(list)
    for a, b in aristas:
        vecinos[a].append(b)
        vecinos[b].append(a)
    usadas = set()
    cadenas = []

    def seguir(a, b):
        cad = [a, b]
        usadas.add(frozenset((a, b)))
        while len(vecinos[cad[-1]]) == 2:
            sig = [v for v in vecinos[cad[-1]] if frozenset((cad[-1], v)) not in usadas]
            if not sig:
                break
            usadas.add(frozenset((cad[-1], sig[0])))
            cad.append(sig[0])
        return cad

    # primero desde los nodos de grado distinto de 2 (extremos y cruces)…
    for a in list(vecinos):
        if len(vecinos[a]) != 2:
            for b in vecinos[a]:
                if frozenset((a, b)) not in usadas:
                    cadenas.append(seguir(a, b))
    # …y luego los anillos cerrados que no tocan ninguno
    for a, b in aristas:
        if frozenset((a, b)) not in usadas:
            cadenas.append(seguir(a, b))
    return cadenas


def unir_anillos(tramos):
    """Une tramos abiertos por sus extremos hasta cerrar anillos."""
    tramos = [list(t) for t in tramos if len(t) >= 2]
    anillos = []
    while tramos:
        cur = tramos.pop()
        cambiado = True
        while cur[0] != cur[-1] and cambiado:
            cambiado = False
            for i, t in enumerate(tramos):
                if t[0] == cur[-1]:
                    cur += t[1:]
                elif t[-1] == cur[-1]:
                    cur += t[::-1][1:]
                elif t[-1] == cur[0]:
                    cur = t + cur[1:]
                elif t[0] == cur[0]:
                    cur = t[::-1] + cur[1:]
                else:
                    continue
                tramos.pop(i)
                cambiado = True
                break
        if len(cur) >= 4:
            anillos.append(cur)
    return anillos


def punto_interior(anillo):
    """Un punto para rotular el polígono: el centroide si cae dentro; si no,
    el centro del tramo más largo de la línea horizontal que lo cruza."""
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        c = x1 * y2 - x2 * y1
        a += c
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    if a:
        c = (cx / (3 * a), cy / (3 * a))
        if dentro(c, anillo):
            return c
    ys = [p[1] for p in anillo]
    y = (min(ys) + max(ys)) / 2
    xs = sorted((x1 + (y - y1) * (x2 - x1) / (y2 - y1))
                for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1])
                if (y1 > y) != (y2 > y))
    tramos = [(xs[i + 1] - xs[i], (xs[i] + xs[i + 1]) / 2) for i in range(0, len(xs) - 1, 2)]
    return (max(tramos)[1], y)


# ---------------------------------------------------------------------------
# la ciudad, desde alcaldias.geojson

def leer_alcaldias():
    with open(ALCALDIAS, encoding='utf-8') as f:
        g = json.load(f)
    usos = Counter()
    nombres = []
    for ft in g['features']:
        geo = ft['geometry']
        polis = geo['coordinates'] if geo['type'] == 'MultiPolygon' else [geo['coordinates']]
        mayor = None
        for poli in polis:
            for anillo in poli:
                pts = [(round(p[0], 7), round(p[1], 7)) for p in anillo]
                for a, b in zip(pts, pts[1:]):
                    if a != b:
                        usos[(a, b) if a < b else (b, a)] += 1
            if mayor is None or area_km2(poli[0]) > area_km2(mayor):
                mayor = [tuple(p) for p in poli[0]]
        nombres.append((ft['properties']['NOMGEO'], punto_interior(mayor[:-1])))

    contorno = [a for a, n in usos.items() if n == 1]
    internos = [a for a, n in usos.items() if n >= 2]
    anillos = [c for c in encadenar(contorno) if c[0] == c[-1]]
    anillos.sort(key=area_km2, reverse=True)
    limites = encadenar(internos)
    return anillos, limites, nombres


class Mascara:
    """Rejilla de CELDA grados: True si la celda toca la ciudad (o su margen)."""

    def __init__(self, anillo, margen):
        xs, ys = [p[0] for p in anillo], [p[1] for p in anillo]
        self.x0, self.y0 = min(xs) - margen, min(ys) - margen
        self.nx = int((max(xs) + margen - self.x0) / CELDA) + 1
        self.ny = int((max(ys) + margen - self.y0) / CELDA) + 1
        base = [[dentro((self.x0 + (i + .5) * CELDA, self.y0 + (j + .5) * CELDA), anillo)
                 for i in range(self.nx)] for j in range(self.ny)]
        # el contorno mismo también cuenta, aunque el centro de su celda quede fuera
        for x, y in anillo:
            i, j = int((x - self.x0) / CELDA), int((y - self.y0) / CELDA)
            base[j][i] = True
        k = int(math.ceil(margen / CELDA))
        self.m = [[any(base[jj][ii]
                       for jj in range(max(0, j - k), min(self.ny, j + k + 1))
                       for ii in range(max(0, i - k), min(self.nx, i + k + 1)))
                   for i in range(self.nx)] for j in range(self.ny)]

    def toca(self, pts):
        for x, y in pts:
            i, j = int((x - self.x0) / CELDA), int((y - self.y0) / CELDA)
            if 0 <= i < self.nx and 0 <= j < self.ny and self.m[j][i]:
                return True
        return False


# ---------------------------------------------------------------------------
# OpenStreetMap

def descargar(consulta, destino):
    datos = urllib.parse.urlencode({'data': consulta}).encode()
    ultimo = None
    for url in ESPEJOS:
        try:
            req = urllib.request.Request(url, data=datos, headers={
                'User-Agent': USUARIO, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=400) as r:
                cuerpo = r.read()
            json.loads(cuerpo)
            with open(destino, 'wb') as f:
                f.write(cuerpo)
            print(f'  {os.path.basename(destino)} <- {url} ({len(cuerpo) / 1e6:.1f} MB)')
            return
        except Exception as e:  # el siguiente espejo
            ultimo = e
            print(f'  {url}: {e}', file=sys.stderr)
    raise SystemExit(f'Ningún espejo de Overpass respondió: {ultimo}')


def geom(g):
    return [(p['lon'], p['lat']) for p in g]


def clase_via(hw):
    if hw.startswith(('motorway', 'trunk', 'primary')):
        return 'via1'
    if hw.startswith('secondary'):
        return 'via2'
    return 'via3'


def poligonos(e):
    """Anillos (exterior primero) de un way cerrado o de una relación."""
    if e['type'] == 'way':
        g = geom(e.get('geometry', []))
        return [g] if len(g) >= 4 and g[0] == g[-1] else []
    miembros = [m for m in e.get('members', []) if m['type'] == 'way' and 'geometry' in m]
    return (unir_anillos([geom(m['geometry']) for m in miembros if m.get('role') == 'outer']) +
            unir_anillos([geom(m['geometry']) for m in miembros if m.get('role') == 'inner']))


def compactar(area, ciudad, limites, nombres):
    principal = ciudad[0]
    cerca = Mascara(principal, MARGEN_MENORES)
    capas = defaultdict(list)
    lugares = []
    vistos = set()

    for e in area['elements']:
        t = e.get('tags', {})
        if e['type'] == 'node':
            n = t.get('name')
            if not n:
                continue
            clase = {'city': 1, 'town': 1, 'village': 1, 'suburb': 1,
                     'quarter': 2, 'neighbourhood': 2}[t['place']]
            if not cerca.toca([(e['lon'], e['lat'])]) or (n, clase) in vistos:
                continue
            vistos.add((n, clase))
            lugares.append([n, clase, round(e['lon'] * Q), round(e['lat'] * Q)])
        elif 'highway' in t:
            c = clase_via(t['highway'])
            g = geom(e['geometry'])
            if c != 'via1' and not cerca.toca(g):
                continue
            capas[c].append(codificar(simplificar(g, TOL[c])))
        elif 'waterway' in t:
            c = 'rio' if t['waterway'] == 'river' else 'canal'
            capas[c].append(codificar(simplificar(geom(e['geometry']), TOL[c])))
        else:
            if t.get('leisure') == 'park':
                c, minimo = 'parque', PARQUE_MIN_KM2
            elif t.get('aeroway') == 'aerodrome':
                c, minimo = 'parque', 0
            else:
                c, minimo = 'agua', AGUA_MIN_KM2
            anillos = poligonos(e)
            if not anillos or area_km2(anillos[0]) < minimo:
                continue
            if not cerca.toca(anillos[0]):
                continue
            capas[c].append([codificar(simplificar(a, TOL[c])) for a in anillos])

    capas['limite'] = [codificar(simplificar(l, TOL['limite'])) for l in limites]
    # Rótulos: las alcaldías van con clase 0 desde el zoom más alejado.
    for nombre, (x, y) in nombres:
        lugares.append([nombre, 0, round(x * Q), round(y * Q)])
    lugares.sort(key=lambda p: (p[1], p[0]))
    return {
        'v': 1,
        'q': Q,
        'fuente': '© OpenStreetMap contributors (ODbL); alcaldías: alcaldias.geojson',
        'fecha': area['osm3s']['timestamp_osm_base'],
        'ciudad': [codificar(simplificar(a, TOL['ciudad'])) for a in ciudad],
        'capas': dict(capas),
        'lugares': lugares,
    }


def reescribir_minimos(ciudad, limites, nombres):
    """Vuelve a escribir los respaldos incrustados en assets/mapa-teselas.js."""
    if not os.path.exists(MODULO):
        print(f'(no existe {os.path.relpath(MODULO, RAIZ)}; no se escriben los mínimos)')
        return
    valores = {
        'CONTORNO_MINIMO': [codificar(simplificar(a, TOL_MINIMO['ciudad'])) for a in ciudad[:1]],
        'LIMITES_MINIMOS': [codificar(simplificar(l, TOL_MINIMO['limite'])) for l in limites],
        'ALCALDIAS_MINIMAS': [[n, 0, round(x * Q), round(y * Q)] for n, (x, y) in nombres],
    }
    with open(MODULO, encoding='utf-8') as f:
        js = f.read()
    for nombre, valor in valores.items():
        patron = re.compile(r'(var ' + nombre + r' = ).*?(;\s*// fin ' + nombre + ')', re.S)
        texto = json.dumps(valor, ensure_ascii=False, separators=(',', ':'))
        js, n = patron.subn(lambda m: m.group(1) + texto + m.group(2), js)
        if n != 1:
            raise SystemExit(f'No encuentro {nombre} en {MODULO}')
    with open(MODULO, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    tam = sum(len(json.dumps(v, separators=(',', ':'))) for v in valores.values())
    print(f'{os.path.relpath(MODULO, RAIZ)}: respaldo incrustado de {tam / 1024:.1f} KB')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[3])
    ap.add_argument('--desde', help='carpeta de area.json: se reutiliza, o se descarga ahí si falta')
    args = ap.parse_args()

    ciudad, limites, nombres = leer_alcaldias()
    xs = [p[0] for p in ciudad[0]]
    ys = [p[1] for p in ciudad[0]]
    caja = (min(ys) - MARGEN_CAJA, min(xs) - MARGEN_CAJA, max(ys) + MARGEN_CAJA, max(xs) + MARGEN_CAJA)

    carpeta = args.desde
    if not carpeta:
        import tempfile
        carpeta = tempfile.mkdtemp(prefix='mapa_base_')
    if not os.path.exists(os.path.join(carpeta, 'area.json')):
        os.makedirs(carpeta, exist_ok=True)
        print('Descargando de Overpass…')
        s, w, n, e = (round(v, 3) for v in caja)
        descargar(CONSULTA_AREA.format(s=s, w=w, n=n, e=e), os.path.join(carpeta, 'area.json'))

    with open(os.path.join(carpeta, 'area.json'), encoding='utf-8') as f:
        area = json.load(f)

    doc = compactar(area, ciudad, limites, nombres)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))

    print(f'{os.path.relpath(SALIDA, RAIZ)}: {os.path.getsize(SALIDA) / 1024:.0f} KB, '
          f'datos OSM de {doc["fecha"]}')
    for c, v in sorted(doc['capas'].items()):
        tam = len(json.dumps(v, separators=(',', ':')))
        print(f'  {c:8s} {len(v):6d} rasgos  {tam / 1024:7.0f} KB')
    print(f'  lugares  {len(doc["lugares"]):6d}')
    reescribir_minimos(ciudad, limites, nombres)


if __name__ == '__main__':
    main()

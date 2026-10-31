/* Grafo de conocimiento de la Zona Metropolitana de Ciudad de Mexico.

   Carga ijcopi/kg_zm.ttl, materializado con warehouse_ampliado/grafo/mapeo_zm.r2rml.ttl, y lo consulta
   con SPARQL en el navegador. Las aristas del mapa no vienen de otro archivo: salen de una consulta
   al grafo. Las consultas de ejemplo son los .rq que verifica verificar_grafo_zm.py. Admite
   ?mun=<clave>, ?lang= y ?vista=figura. */
(function () {
  'use strict';

  const q = new URLSearchParams(location.search);
  const CONSULTAS = 'warehouse_ampliado/grafo/consultas/';
  const INICIAL = '09007';   /* Iztapalapa: tiene vecinos a los dos lados del limite */
  const COLOR = { cdmx: '#00897b', zm: '#7b1fa2', cruce: '#ef6c00', sel: '#ff6f00', arista: '#90a4ae' };
  const PREFIJOS = 'PREFIX agua: <https://w3id.org/cdmx/agua/>\nPREFIX geo:  <http://www.opengis.net/ont/geosparql#>\n'
    + 'PREFIX mun:  <https://w3id.org/cdmx/agua/municipio/>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\n';

  const TXT = {
    es: {
      titulo: 'Grafo del agua en la zona metropolitana',
      lema: 'El almacén ampliado publicado como grafo de conocimiento. Cruza el límite de la CDMX y se consulta con SPARQL en tu navegador, sin servidor.',
      'nav.mapa': 'Mapa', 'nav.grafo': 'Grafo', 'nav.consultas': 'Consultas al almacén',
      'k.tripletas': 'Tripletas', 'k.municipios': 'Municipios', 'k.fronteras': 'Fronteras entre municipios',
      'k.colonias': 'Colonias', 'k.vecinas': 'Colindancias entre colonias',
      'r.titulo': 'Recorrer el grafo',
      'r.ayuda': 'Haz clic en un municipio. Sus vecinos y sus acuíferos salen de consultas SPARQL sobre el grafo, y aquí ves cada consulta.',
      'l.cdmx': 'Alcaldía de la CDMX', 'l.zm': 'Municipio agregado', 'l.arista': 'Frontera entre municipios',
      'l.cruce': 'Frontera que cruza el límite de la CDMX', 'l.sel': 'Municipio elegido',
      vecinos: 'Vecinos de {n}', acuiferos: 'Acuíferos bajo {n}', sindato: 'sin dato', versparql: 'Ver la consulta SPARQL',
      's.titulo': 'Consultas SPARQL', 's.ayuda': 'Elige un ejemplo o escribe tu consulta. Corre aquí mismo, sobre el grafo completo.',
      's.etiqueta': 'Consulta (la puedes editar)', 's.ejecutar': 'Ejecutar',
      filas: '{n} filas en {ms} ms', sinfilas: 'La consulta no devolvió filas.', corriendo: 'Ejecutando…',
      'o.titulo': 'De dónde sale este grafo',
      'o.texto': 'Se materializa desde PostgreSQL con un mapeo R2RML declarativo: nada está escrito a mano. Donde la fuente no reporta un dato, el grafo no lo afirma. Las colonias se unen con geo:sfTouches estricto. Los municipios usan agua:sharesBoundaryWith, una relación propia, porque los polígonos oficiales se solapan unos centímetros y la prueba estricta falla en pares que sí colindan.',
      'o.hash': '{n} tripletas. SHA-256 {h}…',
      cargando: 'Cargando el grafo…', analizando: 'Analizando {mb} MB de RDF…', error: 'No se pudo cargar el grafo: {msg}',
    },
    en: {
      titulo: 'Water graph of the metropolitan area',
      lema: 'The extended warehouse published as a knowledge graph. It crosses the Mexico City boundary and runs SPARQL in your browser, with no server.',
      'nav.mapa': 'Map', 'nav.grafo': 'Graph', 'nav.consultas': 'Warehouse queries',
      'k.tripletas': 'Triples', 'k.municipios': 'Municipalities', 'k.fronteras': 'Municipal boundaries',
      'k.colonias': 'Neighbourhoods', 'k.vecinas': 'Neighbourhood adjacencies',
      'r.titulo': 'Traverse the graph',
      'r.ayuda': 'Click a municipality. Its neighbours and aquifers come from SPARQL queries over the graph, shown here.',
      'l.cdmx': 'Mexico City borough', 'l.zm': 'Added municipality', 'l.arista': 'Boundary between municipalities',
      'l.cruce': 'Boundary crossing the Mexico City limit', 'l.sel': 'Selected municipality',
      vecinos: 'Neighbours of {n}', acuiferos: 'Aquifers under {n}', sindato: 'no data', versparql: 'Show the SPARQL query',
      's.titulo': 'SPARQL queries', 's.ayuda': 'Pick an example or write your own query. It runs here, over the whole graph.',
      's.etiqueta': 'Query (you can edit it)', 's.ejecutar': 'Run',
      filas: '{n} rows in {ms} ms', sinfilas: 'The query returned no rows.', corriendo: 'Running…',
      'o.titulo': 'Where this graph comes from',
      'o.texto': 'It is materialised from PostgreSQL with a declarative R2RML mapping: nothing is written by hand. Where a source reports no value, the graph asserts none. Neighbourhoods are joined by strict geo:sfTouches. Municipalities use agua:sharesBoundaryWith, a project relation, because the official polygons overlap by centimetres and the strict test fails for pairs that do adjoin.',
      'o.hash': '{n} triples. SHA-256 {h}…',
      cargando: 'Loading the graph…', analizando: 'Parsing {mb} MB of RDF…', error: 'The graph could not be loaded: {msg}',
    },
  };

  let idioma = q.get('lang') === 'en' || q.get('lang') === 'es' ? q.get('lang') : (window.I18N ? I18N.idioma : 'es');
  const t = (k, v) => {
    const s = TXT[idioma][k] || TXT.es[k] || k;
    return v ? s.replace(/\{(\w+)\}/g, (m, n) => (n in v ? v[n] : m)) : s;
  };
  const loc = () => (idioma === 'en' ? 'en-GB' : 'es-MX');
  const fmt = (n, d) => Number(n).toLocaleString(loc(), { maximumFractionDigits: d == null ? 2 : d });
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const $ = id => document.getElementById(id);
  const zona = cve => (cve.startsWith('09') ? 'cdmx' : 'zm');
  const clave = iri => iri.slice(iri.lastIndexOf('/') + 1);

  let store, motor, mapa, lienzo, resumen, seleccion = null, ejemplos = [], actual = 0, ultima = null;
  const nodos = {}, poligonos = {}, aristas = [], nombres = {};

  const consultar = texto => motor.queryBindings(texto, { sources: [store] }).then(b => b.toArray());

  function celda(term) {
    if (!term) return '';
    if (term.termType === 'NamedNode') {
      const m = term.value.match(/[/#]([^/#]+)$/);
      return `<span title="${esc(term.value)}">${esc(m ? m[1] : term.value)}</span>`;
    }
    return /^-?\d+(\.\d+)?$/.test(term.value) ? esc(fmt(term.value)) : esc(term.value);
  }

  /* Columnas en el orden del SELECT: los resultados de Comunica no lo conservan */
  function columnas(texto, filas) {
    const m = texto.match(/SELECT\s+(?:DISTINCT\s+)?([\s\S]*?)\s*WHERE/i);
    const pedidas = m ? (m[1].replace(/\([^()]*(\([^()]*\)[^()]*)*\s+AS\s+(\?\w+)\)/gi, '$2').match(/\?\w+/g) || []).map(v => v.slice(1)) : [];
    return pedidas.length ? pedidas : [...filas[0].keys()].map(k => k.value);
  }

  function tabla(filas, texto) {
    if (!filas.length) return `<p class="zm-meta">${esc(t('sinfilas'))}</p>`;
    const cols = columnas(texto || '', filas);
    return `<table><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>`
      + filas.slice(0, 300).map(f => `<tr>${cols.map(c => {
        const term = [...f.keys()].find(k => k.value === c);
        return `<td>${term ? celda(f.get(term)) : ''}</td>`;
      }).join('')}</tr>`).join('') + '</tbody></table>';
  }

  /* Centroide del anillo exterior mas grande: da el lugar del nodo */
  function centroide(geom) {
    const anillos = geom.type === 'Polygon' ? [geom.coordinates[0]] : geom.coordinates.map(p => p[0]);
    let mejor = null, mayor = -1;
    anillos.forEach(r => {
      let a = 0, x = 0, y = 0;
      for (let i = 0; i < r.length - 1; i++) {
        const f = r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1];
        a += f; x += (r[i][0] + r[i + 1][0]) * f; y += (r[i][1] + r[i + 1][1]) * f;
      }
      if (Math.abs(a) > mayor) { mayor = Math.abs(a); mejor = [y / (3 * a), x / (3 * a)]; }
    });
    return mejor;
  }

  function dibujarRed(geo, municipios, vecinos) {
    lienzo = L.canvas({ padding: 0.3 });
    municipios.forEach(f => {
      const iri = f.get('m').value, cve = clave(iri);
      nombres[cve] = f.get('n').value;
      const g = geo[cve];
      if (!g) return;
      poligonos[cve] = L.geoJSON(g, {
        style: { renderer: lienzo, color: COLOR[zona(cve)], weight: 0.7, fillColor: COLOR[zona(cve)], fillOpacity: 0.08 },
      }).on('click', () => seleccionar(cve)).bindTooltip(esc(nombres[cve]), { sticky: true }).addTo(mapa);
      nodos[cve] = centroide(g);
    });
    vecinos.forEach(f => {
      const a = clave(f.get('a').value), b = clave(f.get('b').value);
      if (a >= b || !nodos[a] || !nodos[b]) return;
      const cruza = zona(a) !== zona(b);
      const linea = L.polyline([nodos[a], nodos[b]], { renderer: lienzo, interactive: false,
        color: cruza ? COLOR.cruce : COLOR.arista, weight: cruza ? 2.2 : 1.1, opacity: 0.9 }).addTo(mapa);
      aristas.push({ a, b, cruza, linea });
    });
    Object.keys(nodos).forEach(cve => {
      nodos[cve] = { punto: nodos[cve], marca: L.circleMarker(nodos[cve], { renderer: lienzo, radius: 4.5, weight: 1,
        color: '#fff', fillColor: COLOR[zona(cve)], fillOpacity: 1 })
        .on('click', () => seleccionar(cve)).bindTooltip(esc(nombres[cve])).addTo(mapa) };
    });
  }

  function resaltar(cve, vecinos) {
    Object.keys(poligonos).forEach(c => {
      const elegido = c === cve, vecino = vecinos.has(c);
      poligonos[c].setStyle({ fillColor: elegido ? COLOR.sel : COLOR[zona(c)], fillOpacity: elegido ? 0.55 : vecino ? 0.38 : 0.08,
        weight: elegido || vecino ? 1.6 : 0.7 });
      nodos[c].marca.setRadius(elegido ? 8 : vecino ? 6 : 4.5);
      nodos[c].marca.setStyle({ fillColor: elegido ? COLOR.sel : COLOR[zona(c)] });
    });
    aristas.forEach(e => {
      const toca = e.a === cve || e.b === cve;
      e.linea.setStyle({ weight: toca ? 3.4 : e.cruza ? 2.2 : 1.1, opacity: toca ? 1 : cve ? 0.45 : 0.9,
        color: e.cruza ? COLOR.cruce : toca ? '#263238' : COLOR.arista });
      if (toca) e.linea.bringToFront();
    });
    Object.keys(nodos).forEach(c => nodos[c].marca.bringToFront());
  }

  async function seleccionar(cve) {
    if (!motor || !nombres[cve]) return;
    seleccion = cve;
    const qVecinos = `${PREFIJOS}SELECT ?vecino ?estado ?litros ?calidadVolumen ?cmPorAnio WHERE {
  mun:${cve} agua:sharesBoundaryWith ?v .
  ?v rdfs:label ?vecino ; agua:state ?estado ; agua:volumeQuality ?calidadVolumen .
  OPTIONAL { ?v agua:billedLitresPerDay ?litros }
  OPTIONAL { ?v agua:verticalLandMotion ?cmPorAnio }
} ORDER BY ?estado ?vecino`;
    const qAcuiferos = `${PREFIJOS}SELECT ?acuifero ?extraccionEntreRecarga (COUNT(?otro) AS ?municipios) WHERE {
  mun:${cve} agua:overliesAquifer ?a .
  ?a rdfs:label ?acuifero ; agua:extractionRechargeRatio ?extraccionEntreRecarga .
  ?otro agua:overliesAquifer ?a .
} GROUP BY ?acuifero ?extraccionEntreRecarga ORDER BY DESC(?extraccionEntreRecarga)`;
    const [vecinos, acuiferos, propios] = await Promise.all([consultar(qVecinos), consultar(qAcuiferos),
      consultar(`${PREFIJOS}SELECT ?v WHERE { mun:${cve} agua:sharesBoundaryWith ?v }`)]);
    resaltar(cve, new Set(propios.map(f => clave(f.get('v').value))));
    const n = esc(nombres[cve]);
    $('recorrido').innerHTML = `<h3 class="zm-det-t">${t('vecinos', { n })}</h3><div class="zm-tabla">${tabla(vecinos, qVecinos)}</div>
      <details><summary>${esc(t('versparql'))}</summary><pre class="zm-pre">${esc(qVecinos)}</pre></details>
      <h3 class="zm-det-t" style="margin-top:.8rem">${t('acuiferos', { n })}</h3><div class="zm-tabla">${tabla(acuiferos, qAcuiferos)}</div>
      <details><summary>${esc(t('versparql'))}</summary><pre class="zm-pre">${esc(qAcuiferos)}</pre></details>`;
  }

  function leyendaGrafo() {
    const f = (c, k, cls) => `<div class="zm-ley"><i class="${cls}" style="${cls === 'linea' ? 'border-top-color' : 'background'}:${c}"></i>${esc(t(k))}</div>`;
    $('leyendaGrafo').innerHTML = f(COLOR.cdmx, 'l.cdmx', 'punto') + f(COLOR.zm, 'l.zm', 'punto') + f(COLOR.sel, 'l.sel', 'punto')
      + f(COLOR.arista, 'l.arista', 'linea') + f(COLOR.cruce, 'l.cruce', 'linea');
  }

  function pintarEjemplos() {
    $('ejemplos').innerHTML = '';
    ejemplos.forEach((e, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'zm-ejemplo';
      b.setAttribute('aria-pressed', String(i === actual));
      const [titulo, detalle] = e[idioma];
      b.innerHTML = `${esc(titulo)}<small>${esc(detalle)}</small>`;
      b.onclick = () => { actual = i; pintarEjemplos(); $('consulta').value = e.texto; ejecutar(); };
      $('ejemplos').appendChild(b);
    });
  }

  /* Solo se pinta la ultima consulta pedida: una lenta no debe pisar a la que vino despues */
  let turno = 0;
  async function ejecutar() {
    const mio = ++turno;
    $('metrica').textContent = t('corriendo');
    const t0 = performance.now();
    try {
      const texto = $('consulta').value;
      const filas = await consultar(texto);
      if (mio !== turno) return;
      ultima = { filas, texto, ms: Math.round(performance.now() - t0) };
      pintarSalida();
    } catch (e) {
      if (mio !== turno) return;
      ultima = null;
      $('metrica').textContent = '';
      $('salida').innerHTML = `<p class="status show error">${esc(e.message || e)}</p>`;
    }
  }

  function pintarSalida() {
    if (!ultima) return;
    $('metrica').textContent = t('filas', { n: fmt(ultima.filas.length, 0), ms: fmt(ultima.ms, 0) });
    $('salida').innerHTML = tabla(ultima.filas, ultima.texto);
  }

  function pintarHash() {
    if (resumen) $('origenHash').textContent = t('o.hash', { n: fmt(resumen.tripletas, 0), h: resumen.sha256.slice(0, 16) });
  }

  function traducir() {
    document.documentElement.lang = idioma;
    document.title = t('titulo');
    document.querySelectorAll('[data-t]').forEach(el => { el.textContent = t(el.dataset.t); });
    leyendaGrafo();
    pintarHash();
    if (ejemplos.length) pintarEjemplos();
    pintarSalida();
    if (seleccion) seleccionar(seleccion);
  }

  async function cargar() {
    const [ttl, geo, res] = await Promise.all([
      fetch('ijcopi/kg_zm.ttl').then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.text(); }),
      fetch('ijcopi/datos/12_geometrias.json').then(r => r.json()),
      fetch('ijcopi/datos/grafo.json').then(r => r.json()),
    ]);
    resumen = res;
    pintarHash();
    $('status').textContent = t('analizando', { mb: (ttl.length / 1048576).toFixed(1) });
    store = new N3.Store();
    await new Promise((listo, mal) => {
      new N3.Parser({ format: 'text/turtle' }).parse(ttl, (err, quad) => {
        if (err) mal(err); else if (quad) store.addQuad(quad); else listo();
      });
    });
    motor = new Comunica.QueryEngine();
    const geometria = {};
    geo.filas.forEach(([capa, cve, g]) => { if (capa === 'municipio') geometria[cve] = JSON.parse(g); });
    const [municipios, vecinos] = await Promise.all([
      consultar(`${PREFIJOS}SELECT ?m ?n WHERE { ?m a agua:Municipality ; rdfs:label ?n }`),
      consultar(`${PREFIJOS}SELECT ?a ?b WHERE { ?a agua:sharesBoundaryWith ?b }`),
    ]);
    dibujarRed(geometria, municipios, vecinos);
    const { namedNode } = N3.DataFactory;
    const AGUA = 'https://w3id.org/cdmx/agua/', TIPO = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
    $('kTripletas').textContent = fmt(store.size, 0);
    $('kMunicipios').textContent = fmt(municipios.length, 0);
    $('kFronteras').textContent = fmt(vecinos.length / 2, 0);
    $('kColonias').textContent = fmt(store.countQuads(null, namedNode(TIPO), namedNode(AGUA + 'Neighbourhood'), null), 0);
    $('kVecinas').textContent = fmt(store.countQuads(null, namedNode('http://www.opengis.net/ont/geosparql#sfTouches'), null, null) / 2, 0);

    ejemplos = await Promise.all(res.consultas.map(async n => {
      const texto = await fetch(CONSULTAS + n).then(r => r.text());
      const lineas = texto.replace(/\r/g, '').split('\n');
      const linea = p => lineas.find(l => l.startsWith(`# ${p}: `)).slice(p.length + 4).split(' | ');
      return { es: linea('es'), en: linea('en'), texto: lineas.filter(l => !l.startsWith('# ')).join('\n') };
    }));
    pintarEjemplos();
    $('consulta').value = ejemplos[0].texto;
    $('ejecutar').disabled = false;
    $('ejecutar').onclick = ejecutar;
    $('consulta').addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); ejecutar(); }
    });
    await ejecutar();
    const pedido = q.get('mun');
    await seleccionar(pedido && nombres[pedido] ? pedido : INICIAL);
    const puntos = Object.values(nodos).map(n => n.punto);
    if (puntos.length) mapa.fitBounds(L.latLngBounds(puntos), { padding: [24, 24] });
  }

  async function iniciar() {
    if (q.get('vista') === 'figura') document.documentElement.classList.add('figura');
    if (window.I18N && idioma !== I18N.idioma) {
      /* ?lang= vale para esta visita: no cambia la preferencia guardada */
      let previa = null;
      try { previa = localStorage.getItem('dwagua-idioma'); } catch (e) { /* sin almacenamiento */ }
      I18N.set(idioma);
      try { if (previa === null) localStorage.removeItem('dwagua-idioma'); else localStorage.setItem('dwagua-idioma', previa); } catch (e) { /* sin almacenamiento */ }
    }
    traducir();
    const st = $('status');
    st.textContent = t('cargando');
    st.className = 'status show loading';
    mapa = L.map('map', { preferCanvas: true, zoomSnap: 0.25 }).setView([19.45, -99.1], 9.5);
    try { MapaTeselas.montar(mapa, { maxZoom: 19 }); } catch (e) { console.error(e); }
    try {
      await cargar();
      st.className = 'status';
    } catch (e) {
      console.error(e);
      st.textContent = t('error', { msg: e.message || e });
      st.className = 'status show error';
    }
  }

  document.addEventListener('idiomacambiado', e => {
    idioma = (e.detail && e.detail.idioma) || idioma;
    traducir();
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();

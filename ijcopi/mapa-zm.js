/* Mapa de la Zona Metropolitana de Ciudad de Mexico.

   Todo lo que dibuja viene de ijcopi/datos/, que warehouse_ampliado/etl/exportar_mapa.py genera
   con las consultas de warehouse_ampliado/consultas/. Aqui no hay datos escritos a mano: solo se
   decide como pintarlos. Los enlaces admiten ?ind=, ?capas=, ?fecha=, ?c=lat,lng,zoom, ?lang=
   y ?vista=figura, la vista limpia que usan las figuras del articulo. */
(function () {
  'use strict';

  const q = new URLSearchParams(location.search);
  const DATOS = 'ijcopi/datos/';
  const BD = 'docker exec data_warehouse_cdmx psql -U postgres -d data_warehouse';

  const TXT = {
    es: {
      titulo: 'Agua en la Zona Metropolitana de Ciudad de México',
      lema: 'Ampliación del almacén de datos: cada capa es el resultado de una consulta SQL al almacén real, no una copia aparte.',
      'nav.mapa': 'Mapa', 'nav.consultas': 'Consultas al almacén',
      'c.indicador': 'Indicador', 'c.fecha': 'Fecha del corte', 'c.capas': 'Capas',
      'capa.acuiferos': 'Acuíferos', 'capa.pozos': 'Pozos: cambio de nivel 2010-2019',
      'capa.presas': 'Presas', 'capa.calidad': 'Calidad del agua',
      'g.municipio': 'Por municipio (63)', 'g.colonia': 'Por colonia',
      'o.titulo': 'De dónde sale esta capa', 'o.versql': 'Ver la consulta SQL',
      'o.texto': 'Resultado de {sql}: {filas} filas, exportadas el {fecha}. SHA-256 {hash}…',
      'o.cmd': 'Para ver lo mismo en la base de datos:',
      'z.cdmx': 'Ciudad de México ({n} alcaldías)', 'z.zm': 'Agregado: Edomex e Hidalgo ({n} municipios)',
      cargando: 'Cargando datos del almacén…', error: 'No se pudieron cargar los datos: {msg}',
      sindato: 'Sin dato', atipico: 'Valor atípico', 'ley.acu': 'Acuíferos: extracción / recarga',
      'ley.pozos': 'Pozos: cambio de nivel 2010-2019', 'ley.presas': 'Presas', 'ley.calidad': 'Calidad del agua',
      'acu.alto': '1.5 o más', 'acu.medio': '1 a 1.5', 'acu.bajo': 'menos de 1',
      'pozo.mucho': 'bajó más de 10 m', 'pozo.poco': 'bajó hasta 10 m', 'pozo.sube': 'subió',
      'cal.ROJO': 'Rojo', 'cal.AMARILLO': 'Amarillo', 'cal.VERDE': 'Verde',
      'n.mun': 'Municipios', 'n.col': 'Colonias', 'n.acu': 'Acuíferos', 'n.poz': 'Pozos con 2010 y 2019',
      'n.pre': 'Presas', 'n.cal': 'Sitios de calidad', 'n.fil': 'Filas en el almacén',
      'sql.ver': 'Compruébalo en la base de datos:', 'det.volumen': 'Volumen último',
      fuente: 'Fuente del volumen', acuifero: 'Acuífero principal', pob: 'Población',
      'presa.2019': 'Medio 2019', 'presa.2023': 'Medio 2023', 'presa.fecha': 'Última lectura',
      'acu.r': 'Extracción / recarga', 'acu.d': 'Déficit (hm³/año)', 'acu.b': 'Descenso medio 2010-2019 (m)',
      'acu.p': 'Pozos con 2010 y 2019',
      'pozo.d': 'Cambio del nivel (m)', 'pozo.a': 'Profundidad 2010 (m)', 'pozo.b': 'Profundidad 2019 (m)',
      'cal.s': 'Semáforo', 'cal.c': 'Fuera de norma', 'cal.p': 'Periodo', 'cal.t': 'Tipo de agua',
      'sev.-1': 'Sin sequía', 'sev.0': 'D0 Anormalmente seco', 'sev.1': 'D1 Sequía moderada',
      'sev.2': 'D2 Sequía severa', 'sev.3': 'D3 Sequía extrema', 'sev.4': 'D4 Sequía excepcional',
      'gm.Muy bajo': 'Muy bajo', 'gm.Bajo': 'Bajo', 'gm.Medio': 'Medio', 'gm.Alto': 'Alto', 'gm.Muy alto': 'Muy alto',
    },
    en: {
      titulo: 'Water in the Mexico City Metropolitan Area',
      lema: 'Extension of the data warehouse: every layer is the result of a SQL query to the real warehouse, not a separate copy.',
      'nav.mapa': 'Map', 'nav.consultas': 'Warehouse queries',
      'c.indicador': 'Indicator', 'c.fecha': 'Date of the reading', 'c.capas': 'Layers',
      'capa.acuiferos': 'Aquifers', 'capa.pozos': 'Wells: level change 2010-2019',
      'capa.presas': 'Dams', 'capa.calidad': 'Water quality',
      'g.municipio': 'By municipality (63)', 'g.colonia': 'By neighbourhood',
      'o.titulo': 'Where this layer comes from', 'o.versql': 'Show the SQL query',
      'o.texto': 'Result of {sql}: {filas} rows, exported on {fecha}. SHA-256 {hash}…',
      'o.cmd': 'To see the same result in the database:',
      'z.cdmx': 'Mexico City ({n} boroughs)', 'z.zm': 'Added: State of Mexico and Hidalgo ({n} municipalities)',
      cargando: 'Loading warehouse data…', error: 'The data could not be loaded: {msg}',
      sindato: 'No data', atipico: 'Atypical value', 'ley.acu': 'Aquifers: extraction / recharge',
      'ley.pozos': 'Wells: level change 2010-2019', 'ley.presas': 'Dams', 'ley.calidad': 'Water quality',
      'acu.alto': '1.5 or more', 'acu.medio': '1 to 1.5', 'acu.bajo': 'below 1',
      'pozo.mucho': 'fell more than 10 m', 'pozo.poco': 'fell up to 10 m', 'pozo.sube': 'rose',
      'cal.ROJO': 'Red', 'cal.AMARILLO': 'Yellow', 'cal.VERDE': 'Green',
      'n.mun': 'Municipalities', 'n.col': 'Neighbourhoods', 'n.acu': 'Aquifers', 'n.poz': 'Wells with 2010 and 2019',
      'n.pre': 'Dams', 'n.cal': 'Quality sites', 'n.fil': 'Rows in the warehouse',
      'sql.ver': 'Check it in the database:', 'det.volumen': 'Latest volume',
      fuente: 'Volume source', acuifero: 'Main aquifer', pob: 'Population',
      'presa.2019': 'Mean 2019', 'presa.2023': 'Mean 2023', 'presa.fecha': 'Latest reading',
      'acu.r': 'Extraction / recharge', 'acu.d': 'Deficit (hm³/year)', 'acu.b': 'Mean fall 2010-2019 (m)',
      'acu.p': 'Wells with 2010 and 2019',
      'pozo.d': 'Level change (m)', 'pozo.a': 'Depth 2010 (m)', 'pozo.b': 'Depth 2019 (m)',
      'cal.s': 'Traffic light', 'cal.c': 'Above the limit', 'cal.p': 'Period', 'cal.t': 'Water type',
      'sev.-1': 'No drought', 'sev.0': 'D0 Abnormally dry', 'sev.1': 'D1 Moderate drought',
      'sev.2': 'D2 Severe drought', 'sev.3': 'D3 Extreme drought', 'sev.4': 'D4 Exceptional drought',
      'gm.Muy bajo': 'Very low', 'gm.Bajo': 'Low', 'gm.Medio': 'Medium', 'gm.Alto': 'High', 'gm.Muy alto': 'Very high',
    },
  };

  /* Dos familias de color: verde para la CDMX, el del mapa original, y morado para lo agregado.
     Tambien distingue fuentes: el volumen de cada lado del limite no se mide igual. */
  const TONOS = {
    cdmx: ['#e0f2f1', '#80cbc4', '#26a69a', '#00897b', '#004d40'],
    zm: ['#f3e5f5', '#ce93d8', '#ab47bc', '#7b1fa2', '#4a148c'],
  };
  const BORDE = { cdmx: '#00695c', zm: '#6a1b9a' };
  const zona = r => (String(r.cve_mun).startsWith('09') ? 'cdmx' : 'zm');
  const COL_SEQUIA = { '-1': '#f2f2f2', 0: '#ffff00', 1: '#fcd37f', 2: '#ffaa00', 3: '#e60000', 4: '#730000' };
  const GRADOS = ['Muy bajo', 'Bajo', 'Medio', 'Alto', 'Muy alto'];
  const COL_CAL = { ROJO: '#c0392b', AMARILLO: '#f1c40f', VERDE: '#27ae60' };

  const INDICADORES = [
    { id: 'm_litros', capa: 'municipio', campo: 'litros_hab_dia_dom', consulta: '03_municipios_zm', calidad: true,
      es: 'Litros facturados por habitante al día', en: 'Billed litres per inhabitant per day',
      nes: 'Alcaldías: SACMEX, enero-junio de 2019, anualizado. Demás municipios: CNGMD 2018. Es facturación doméstica, no consumo. La fuente mide distinto a cada lado del límite.',
      nen: 'Boroughs: SACMEX, January-June 2019, annualised. Other municipalities: CNGMD 2018. This is domestic billing, not use, and the source differs across the boundary.' },
    { id: 'm_viv', capa: 'municipio', campo: 'pct_viv_agua_dentro', consulta: '03_municipios_zm',
      es: 'Viviendas con agua entubada dentro (%)', en: 'Dwellings with piped water inside (%)',
      nes: 'Censo 2020, ITER.', nen: '2020 Census, ITER.' },
    { id: 'm_recaud', capa: 'municipio', campo: 'recaudacion_pc_2018', consulta: '03_municipios_zm',
      es: 'Recaudación por agua por habitante, 2018 (pesos)', en: 'Water revenue per inhabitant, 2018 (pesos)',
      nes: 'SHCP. La CDMX se reporta como entidad, no por alcaldía.', nen: 'SHCP. Mexico City is reported as a whole, not by borough.' },
    { id: 'm_vlm', capa: 'municipio', campo: 'vlm_cm_anio', invertir: true,cortes: [-15, -5, -1, 1], consulta: '03_municipios_zm',
      es: 'Movimiento vertical del terreno (cm/año)', en: 'Vertical land motion (cm/year)',
      nes: 'InSAR 2014-2020 (Khorrami et al.). Negativo: el terreno se hunde.', nen: 'InSAR 2014-2020 (Khorrami et al.). Negative: the ground is sinking.' },
    { id: 'm_sequia', capa: 'municipio', sequia: true, consulta: '09_sequia_zm',
      es: 'Sequía (Monitor de Sequía de México)', en: 'Drought (Mexican Drought Monitor)',
      nes: 'SMN-CONAGUA. Mueve la fecha: hay 437 cortes desde 2003.', nen: 'SMN-CONAGUA. Move the date: there are 437 readings since 2003.' },
    { id: 'c_sinagua', capa: 'colonia', campo: 'pct_sin_agua', cortes: [0.5, 2, 5, 15], consulta: '04_colonias_zm',
      es: 'Ocupantes sin agua entubada (%)', en: 'Occupants without piped water (%)',
      nes: 'CONAPO 2020. Cubre toda la ZM, también fuera de la CDMX.', nen: 'CONAPO 2020. Covers the whole metropolitan area, also outside Mexico City.' },
    { id: 'c_gm', capa: 'colonia', campo: 'gm_2020', categorias: GRADOS, consulta: '04_colonias_zm',
      es: 'Grado de marginación urbana', en: 'Urban marginalisation level',
      nes: 'CONAPO 2020. Cubre toda la ZM.', nen: 'CONAPO 2020. Covers the whole metropolitan area.' },
    { id: 'c_falta', capa: 'colonia', campo: 'falta_por_mil_hab', consulta: '04_colonias_zm',
      es: 'Reportes de falta de agua por mil habitantes, ene-jun 2019', en: 'Water shortage reports per thousand inhabitants, Jan-Jun 2019',
      nes: 'Solo CDMX. Agua potable. Mide lo que se reporta, no lo que falta.', nen: 'Mexico City only. Drinking water. It measures what is reported, not what is missing.' },
    { id: 'c_fugas', capa: 'colonia', campo: 'fugas_por_mil_hab', consulta: '04_colonias_zm',
      es: 'Reportes de fuga por mil habitantes, 2021-2024', en: 'Leak reports per thousand inhabitants, 2021-2024',
      nes: 'Solo CDMX. La fuente no registra fugas antes de 2021.', nen: 'Mexico City only. The source records no leaks before 2021.' },
    { id: 'c_litros', capa: 'colonia', campo: 'litros_hab_dia_dom', consulta: '04_colonias_zm',
      es: 'Litros facturados por habitante al día', en: 'Billed litres per inhabitant per day',
      nes: 'Solo CDMX, enero-junio de 2019. Es facturación, no consumo.', nen: 'Mexico City only, January-June 2019. This is billing, not use.' },
    { id: 'c_vlm', capa: 'colonia', campo: 'vlm_cm_anio', invertir: true,cortes: [-15, -5, -1, 1], consulta: '04_colonias_zm',
      es: 'Movimiento vertical del terreno (cm/año)', en: 'Vertical land motion (cm/year)',
      nes: 'Solo CDMX. InSAR 2014-2020. Negativo: el terreno se hunde.', nen: 'Mexico City only. InSAR 2014-2020. Negative: the ground is sinking.' },
  ];
  const porId = id => INDICADORES.find(i => i.id === id);

  let idioma = q.get('lang') === 'en' || q.get('lang') === 'es' ? q.get('lang') : (window.I18N ? I18N.idioma : 'es');
  const t = (k, v) => {
    const s = (TXT[idioma] && TXT[idioma][k]) || TXT.es[k] || k;
    return v ? s.replace(/\{(\w+)\}/g, (m, n) => (n in v ? v[n] : m)) : s;
  };
  const loc = () => (idioma === 'en' ? 'en-GB' : 'es-MX');
  const fmt = (n, d) => (n == null ? '—' : Number(n).toLocaleString(loc(), { maximumFractionDigits: d == null ? 2 : d }));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  /* Una tabla exportada, como objetos */
  const filas = d => d.filas.map(f => Object.fromEntries(d.columnas.map((c, i) => [c, f[i]])));

  let mapa, lienzo, capaBase = null, contorno = null, estado = { ind: 'm_litros', fecha: 0, capas: new Set() };
  const D = {}, extras = {}, cortesCache = {};

  /* Cortes por quintiles, redondeados para que la leyenda se lea */
  function quintiles(vals) {
    const v = vals.filter(x => x != null && !isNaN(x)).sort((a, b) => a - b);
    const redondo = x => {
      if (x === 0) return 0;
      const e = Math.pow(10, Math.floor(Math.log10(Math.abs(x))) - 1);
      return Math.round(x / e) * e;
    };
    const c = [];
    for (let i = 1; i < 5; i++) {
      const x = +redondo(v[Math.floor(v.length * i / 5)]).toFixed(6);
      if (!c.includes(x)) c.push(x);
    }
    return c;
  }

  function cortes(ind) {
    if (ind.cortes) return ind.cortes;
    if (!cortesCache[ind.id]) {
      const base = ind.capa === 'municipio' ? D.municipios : D.colonias;
      const vals = base.filter(r => !ind.calidad || r.calidad_volumen === 'plausible').map(r => r[ind.campo]);
      cortesCache[ind.id] = quintiles(vals);
    }
    return cortesCache[ind.id];
  }

  function clase(ind, v) {
    const c = cortes(ind);
    let i = 0;
    while (i < c.length && v > c[i]) i++;
    return i;
  }

  /* Tono de la clase i de n, en la familia de color de esa zona */
  function tono(ind, i, n, z) {
    const p = TONOS[z], k = Math.round(i * (p.length - 1) / Math.max(1, n - 1));
    return p[ind.invertir ? p.length - 1 - k : k];
  }

  function colorDe(ind, r) {
    if (ind.sequia) {
      const s = D.sequia[D.fechas[estado.fecha]] && D.sequia[D.fechas[estado.fecha]][r.cve_mun];
      return s == null ? null : COL_SEQUIA[s];
    }
    const v = r[ind.campo];
    if (v == null) return null;
    if (ind.categorias) return tono(ind, ind.categorias.indexOf(v), ind.categorias.length, zona(r));
    return tono(ind, clase(ind, v), cortes(ind).length + 1, zona(r));
  }

  function estilo(ind, r) {
    const atipico = ind.calidad && r.calidad_volumen === 'atipico';
    const color = atipico ? '#ffffff' : colorDe(ind, r);
    const col = ind.capa === 'colonia', z = zona(r);
    return {
      renderer: lienzo,
      color: atipico ? '#c0392b' : col ? 'rgba(60,60,60,.25)' : BORDE[z],
      weight: atipico ? 2 : col ? 0.3 : z === 'cdmx' ? 1.5 : 0.9,
      dashArray: atipico ? '4 3' : null,
      fillColor: color || '#c9ced3',
      fillOpacity: color ? 0.8 : 0.3,
    };
  }

  /* Sobre las colonias, los limites municipales dejan ver donde termina la CDMX */
  function pintarContorno(ind) {
    if (contorno) { mapa.removeLayer(contorno); contorno = null; }
    if (ind.capa !== 'colonia') return;
    contorno = L.geoJSON(coleccion('municipio', D.municipios, 'cve_mun'), {
      interactive: false,
      style: f => {
        const z = zona(f.properties);
        return { renderer: lienzo, fill: false, color: BORDE[z], weight: z === 'cdmx' ? 1.7 : 0.8 };
      },
    }).addTo(mapa);
  }

  function coleccion(capa, datos, clave) {
    return {
      type: 'FeatureCollection',
      features: datos.filter(r => D.geo[capa][r[clave]]).map(r => (
        { type: 'Feature', geometry: D.geo[capa][r[clave]], properties: r })),
    };
  }

  function valorTexto(ind, r) {
    if (ind.sequia) {
      const s = D.sequia[D.fechas[estado.fecha]] && D.sequia[D.fechas[estado.fecha]][r.cve_mun];
      return s == null ? t('sindato') : t('sev.' + s);
    }
    const v = r[ind.campo];
    if (v == null) return t('sindato');
    if (ind.categorias) return t('gm.' + v);
    return fmt(v, 2);
  }

  function pintarBase() {
    const ind = porId(estado.ind);
    if (capaBase) mapa.removeLayer(capaBase);
    const datos = ind.capa === 'municipio' ? D.municipios : D.colonias;
    const clave = ind.capa === 'municipio' ? 'cve_mun' : 'cve_col';
    capaBase = L.geoJSON(coleccion(ind.capa, datos, clave), {
      style: f => estilo(ind, f.properties),
      onEachFeature: (f, capa) => {
        capa.bindTooltip(() => `<b>${esc(f.properties.nom_mun || f.properties.colonia)}</b><br>${esc(valorTexto(ind, f.properties))}`, { sticky: true });
        capa.on('click', () => (ind.capa === 'municipio' ? detalleMunicipio(f.properties) : detalleColonia(f.properties)));
      },
    }).addTo(mapa);
    capaBase.bringToBack();
    pintarContorno(ind);
    leyenda();
    origen();
  }

  function repintarEstilo() {
    const ind = porId(estado.ind);
    if (capaBase) capaBase.setStyle(f => estilo(ind, f.properties));
  }

  /* ---- capas superpuestas ---- */
  const COL_ACU = r => (r >= 1.5 ? '#b71c1c' : r >= 1 ? '#ef6c00' : '#1565c0');
  const COL_POZO = d => (d > 10 ? '#7f0000' : d > 0 ? '#ef8a3c' : '#1e88e5');

  function construirExtra(nombre) {
    if (extras[nombre]) return extras[nombre];
    let capa;
    if (nombre === 'acuiferos') {
      capa = L.geoJSON(coleccion('acuifero', D.acuiferos, 'clv_acui'), {
        interactive: true,
        style: f => ({ renderer: lienzo, color: COL_ACU(f.properties.extraccion_entre_recarga), weight: 2.6, fill: false, dashArray: '7 4' }),
        onEachFeature: (f, c) => {
          c.bindTooltip(`<b>${esc(f.properties.nom_acui)}</b><br>${t('acu.r')}: ${fmt(f.properties.extraccion_entre_recarga)}`, { sticky: true });
          c.on('click', () => detalleAcuifero(f.properties));
        },
      });
    } else if (nombre === 'pozos') {
      capa = L.layerGroup(D.pozos.map(p => L.circleMarker([p.latitud, p.longitud],
        { renderer: lienzo, radius: 4.2, weight: 0.7, color: '#fff', fillColor: COL_POZO(p.descenso_m), fillOpacity: 0.95 })
        .bindTooltip(`<b>${esc(p.nom_pozo)}</b><br>${t('pozo.d')}: ${fmt(-p.descenso_m, 1)}`)
        .on('click', () => detallePozo(p))));
    } else if (nombre === 'presas') {
      capa = L.layerGroup(D.presas.map(p => L.circleMarker([p.latitud, p.longitud],
        { renderer: lienzo, radius: 3 + Math.sqrt(p.volumen_ultimo_hm3 || 1) / 2.2, weight: 1.4, color: '#fff', fillColor: '#0d47a1', fillOpacity: 0.9 })
        .bindTooltip(`<b>${esc(p.nombre)}</b><br>${fmt(p.volumen_ultimo_hm3, 1)} hm³`)
        .on('click', () => detallePresa(p))));
    } else {
      capa = L.layerGroup(D.calidad.map(s => L.circleMarker([s.latitud, s.longitud],
        { renderer: lienzo, radius: 4, weight: 0.8, color: '#333', fillColor: COL_CAL[s.semaforo] || '#9e9e9e', fillOpacity: 0.95 })
        .bindTooltip(`<b>${esc(s.nombre)}</b><br>${esc(t('cal.' + s.semaforo))}`)
        .on('click', () => detalleCalidad(s))));
    }
    extras[nombre] = capa;
    return capa;
  }

  function alternar(nombre, activa) {
    const capa = construirExtra(nombre);
    if (activa) { estado.capas.add(nombre); capa.addTo(mapa); } else { estado.capas.delete(nombre); mapa.removeLayer(capa); }
    leyenda();
    guardarUrl();
  }

  /* ---- leyenda y paneles ---- */
  const fila = (color, texto, cls) => `<div class="zm-ley"><i class="${cls || ''}" style="${cls === 'linea' ? 'border-top-color' : 'background'}:${color}"></i>${esc(texto)}</div>`;
  const clase2 = (colores, texto) => `<div class="zm-ley"><span class="par">${colores.map(c => `<i style="background:${c}"></i>`).join('')}</span>${esc(texto)}</div>`;

  function leyenda() {
    const ind = porId(estado.ind);
    const datos = ind.capa === 'municipio' ? D.municipios : D.colonias;
    const zonas = ind.sequia ? ['cdmx', 'zm'] : ['cdmx', 'zm'].filter(z => datos.some(r => zona(r) === z && r[ind.campo] != null));
    const cuenta = z => D.municipios.filter(r => zona(r) === z).length;
    let h = `<p class="zm-ley-t">${esc(ind[idioma])}</p>`;
    zonas.forEach(z => {
      const texto = t('z.' + z, { n: cuenta(z) });
      h += ind.sequia ? fila(BORDE[z], texto, 'linea') : fila(TONOS[z][3], texto);
    });
    h += '<div class="zm-ley-sep"></div>';
    if (ind.sequia) {
      [4, 3, 2, 1, 0, -1].forEach(s => { h += fila(COL_SEQUIA[s], t('sev.' + s)); });
    } else if (ind.categorias) {
      ind.categorias.forEach((k, i) => { h += clase2(zonas.map(z => tono(ind, i, ind.categorias.length, z)), t('gm.' + k)); });
    } else {
      const c = cortes(ind), n = c.length + 1;
      for (let i = 0; i < n; i++) {
        const de = i === 0 ? null : c[i - 1], a = i === n - 1 ? null : c[i];
        const txt = de == null ? `≤ ${fmt(a)}` : a == null ? `> ${fmt(de)}` : `${fmt(de)} – ${fmt(a)}`;
        h += clase2(zonas.map(z => tono(ind, i, n, z)), txt);
      }
    }
    if (ind.calidad) h += `<div class="zm-ley"><i class="atipico"></i>${esc(t('atipico'))}</div>`;
    if (!ind.categorias || ind.capa === 'colonia') h += fila('#c9ced3', t('sindato'));
    if (estado.capas.has('acuiferos')) {
      h += `<p class="zm-ley-sub">${esc(t('ley.acu'))}</p>` + fila('#b71c1c', t('acu.alto'), 'linea') + fila('#ef6c00', t('acu.medio'), 'linea') + fila('#1565c0', t('acu.bajo'), 'linea');
    }
    if (estado.capas.has('pozos')) {
      h += `<p class="zm-ley-sub">${esc(t('ley.pozos'))}</p>` + fila('#7f0000', t('pozo.mucho'), 'punto') + fila('#ef8a3c', t('pozo.poco'), 'punto') + fila('#1e88e5', t('pozo.sube'), 'punto');
    }
    if (estado.capas.has('presas')) h += `<p class="zm-ley-sub">${esc(t('ley.presas'))}</p>` + fila('#0d47a1', 'hm³', 'punto');
    if (estado.capas.has('calidad')) {
      h += `<p class="zm-ley-sub">${esc(t('ley.calidad'))}</p>`;
      Object.keys(COL_CAL).forEach(k => { h += fila(COL_CAL[k], t('cal.' + k), 'punto'); });
    }
    document.getElementById('leyenda').innerHTML = h;
  }

  function panel(titulo, sub, pares, sql, extra) {
    const dl = pares.filter(p => p[1] != null && p[1] !== '').map(p => `<dt>${esc(p[0])}</dt><dd>${esc(p[1])}</dd>`).join('');
    document.getElementById('detalle').innerHTML = `<p class="zm-det-t">${esc(titulo)}</p><p class="zm-det-s">${esc(sub || '')}</p>`
      + `<dl class="zm-det">${dl}</dl>${extra || ''}<div class="zm-sql">${esc(t('sql.ver'))}<pre>${esc(`${BD} -c "${sql}"`)}</pre></div>`;
  }

  const nombre = id => porId(id)[idioma];

  function detalleMunicipio(r) {
    panel(r.nom_mun, r.nom_ent, [
      [t('pob'), fmt(r.pob_2019, 0)],
      [nombre('m_litros'), r.litros_hab_dia_dom == null ? null : `${fmt(r.litros_hab_dia_dom, 1)} (${r.calidad_volumen})`],
      [t('fuente'), r.fuente_volumen],
      [nombre('m_viv'), fmt(r.pct_viv_agua_dentro, 1)],
      [nombre('c_gm'), r.gm_2020 ? t('gm.' + r.gm_2020) : null],
      [nombre('m_recaud'), r.recaudacion_pc_2018 == null ? null : fmt(r.recaudacion_pc_2018, 1)],
      [nombre('m_vlm'), r.vlm_cm_anio == null ? null : fmt(r.vlm_cm_anio, 2)],
      [t('acuifero'), r.acuifero_principal],
    ], `SELECT nom_mun, pob_2019, litros_hab_dia_dom, calidad_volumen FROM v_zm_indicadores_agua WHERE cve_mun = '${r.cve_mun}'`);
  }

  function detalleColonia(r) {
    panel(r.colonia, r.cve_mun, [
      [t('pob'), fmt(r.pob_total, 0)],
      [nombre('c_sinagua'), fmt(r.pct_sin_agua, 2)],
      [nombre('c_gm'), r.gm_2020 ? t('gm.' + r.gm_2020) : null],
      [nombre('c_litros'), r.litros_hab_dia_dom == null ? null : fmt(r.litros_hab_dia_dom, 1)],
      [nombre('c_falta'), r.falta_por_mil_hab == null ? null : `${fmt(r.falta_por_mil_hab, 2)} (${fmt(r.falta_agua_2019_s1, 0)})`],
      [nombre('c_fugas'), r.fugas_por_mil_hab == null ? null : `${fmt(r.fugas_por_mil_hab, 2)} (${fmt(r.fugas_2021_2024, 0)})`],
      [nombre('c_vlm'), r.vlm_cm_anio == null ? null : fmt(r.vlm_cm_anio, 2)],
    ], `SELECT colonia, pob_total, pct_ocup_sin_agua, gm_2020 FROM dim_colonia_conapo WHERE cve_col = ${r.cve_col}`);
  }

  function detalleAcuifero(r) {
    panel(r.nom_acui, r.clv_acui, [
      [t('acu.r'), fmt(r.extraccion_entre_recarga)],
      [t('acu.d'), fmt(r.deficit_hm3, 1)],
      [t('acu.b'), r.descenso_medio_m == null ? null : fmt(r.descenso_medio_m, 1)],
      [t('acu.p'), r.pozos_2010_2019 == null ? null : fmt(r.pozos_2010_2019, 0)],
    ], `SELECT * FROM v_acuiferos_zmvm WHERE clv_acui = '${r.clv_acui}'`);
  }

  function detallePozo(r) {
    panel(r.nom_pozo, r.nom_acui, [
      [t('pozo.a'), fmt(r.profundidad_2010_m, 2)],
      [t('pozo.b'), fmt(r.profundidad_2019_m, 2)],
      [t('pozo.d'), fmt(-r.descenso_m, 2)],
    ], `SELECT anio, profundidad_nivel_m FROM fact_nivel_piezometrico WHERE id_pozo = ${r.id_pozo} ORDER BY anio`);
  }

  function grafica(clave) {
    const s = D.presasMes.filter(x => x.clave === clave);
    if (s.length < 2) return '';
    const v = s.map(x => x.volumen_hm3), max = Math.max(...v), min = Math.min(...v, 0);
    const pts = v.map((y, i) => `${(i / (v.length - 1) * 268).toFixed(1)},${(62 - (y - min) / (max - min || 1) * 56).toFixed(1)}`).join(' ');
    return `<svg viewBox="0 0 270 66" width="100%" role="img" aria-label="hm³ ${s[0].mes} – ${s[s.length - 1].mes}" style="margin-top:.5rem">
      <polyline points="${pts}" fill="none" stroke="#0d47a1" stroke-width="1.6"/></svg>
      <div class="zm-meta">${s[0].mes} – ${s[s.length - 1].mes}, ${fmt(min, 1)} – ${fmt(max, 1)} hm³</div>`;
  }

  function detallePresa(r) {
    panel(r.nombre, r.cuenca_disponibilidad, [
      [t('det.volumen'), `${fmt(r.volumen_ultimo_hm3, 1)} hm³`],
      [t('presa.fecha'), r.ultima_fecha],
      [t('presa.2019'), `${fmt(r.volumen_medio_2019_hm3, 1)} hm³`],
      [t('presa.2023'), `${fmt(r.volumen_medio_2023_hm3, 1)} hm³`],
    ], `SELECT t.fecha, f.volumen_hm3 FROM fact_presa_diaria f JOIN dim_tiempo t USING (id_tiempo) WHERE f.clave = '${r.clave}' ORDER BY t.fecha DESC LIMIT 5`, grafica(r.clave));
  }

  function detalleCalidad(r) {
    panel(r.nombre, r.municipio, [
      [t('cal.t'), r.tipo_agua], [t('cal.s'), r.semaforo ? t('cal.' + r.semaforo) : null],
      [t('cal.c'), r.contaminantes], [t('cal.p'), r.periodo],
    ], `SELECT nombre, semaforo, contaminantes FROM dim_sitio_calidad WHERE id_sitio = ${r.id_sitio}`);
  }

  function origen() {
    const ind = porId(estado.ind);
    const m = D.manifiesto.consultas.find(c => c.consulta === ind.consulta + '.sql');
    document.getElementById('origenTexto').textContent = t('o.texto', {
      sql: `warehouse_ampliado/consultas/${m.consulta}`, filas: fmt(m.filas, 0), fecha: D.manifiesto.generado_en, hash: m.sha256_datos.slice(0, 16) });
    document.getElementById('origenComando').textContent = `${t('o.cmd')}\n\ndocker cp warehouse_ampliado/consultas/. data_warehouse_cdmx:/consultas\n${BD} -f /consultas/${m.consulta}`;
    const pre = document.getElementById('origenSql');
    pre.textContent = '';
    fetch('warehouse_ampliado/consultas/' + m.consulta).then(r => (r.ok ? r.text() : '')).then(s => { pre.textContent = s; }).catch(() => {});
  }

  function traducir() {
    document.documentElement.lang = idioma;
    document.title = t('titulo');
    document.querySelectorAll('[data-t]').forEach(el => { el.textContent = t(el.dataset.t); });
    const sel = document.getElementById('indicador');
    sel.innerHTML = '';
    ['municipio', 'colonia'].forEach(capa => {
      const g = document.createElement('optgroup');
      g.label = t('g.' + capa);
      INDICADORES.filter(i => i.capa === capa).forEach(i => g.appendChild(new Option(i[idioma], i.id)));
      sel.appendChild(g);
    });
    sel.value = estado.ind;
    document.getElementById('notaIndicador').textContent = porId(estado.ind)[idioma === 'en' ? 'nen' : 'nes'];
    if (D.manifiesto) {
      const tablas = filas(D.tablas).reduce((s, r) => s + Number(r.filas), 0);
      document.getElementById('conteos').innerHTML = [
        ['n.fil', tablas], ['n.mun', D.municipios.length], ['n.col', D.colonias.length], ['n.acu', D.acuiferos.length],
        ['n.poz', D.pozos.length], ['n.pre', D.presas.length], ['n.cal', D.calidad.length],
      ].map(([k, n]) => `<li>${esc(t(k))} <b>${fmt(n, 0)}</b></li>`).join('');
    }
  }

  function textoFecha() {
    document.getElementById('fechaTexto').textContent = D.fechas[estado.fecha];
  }

  function guardarUrl() {
    if (document.documentElement.classList.contains('figura')) return;
    const p = new URLSearchParams(location.search);
    p.set('ind', estado.ind);
    if (estado.capas.size) p.set('capas', [...estado.capas].join(',')); else p.delete('capas');
    if (porId(estado.ind).sequia) p.set('fecha', D.fechas[estado.fecha]); else p.delete('fecha');
    history.replaceState(null, '', location.pathname + '?' + p.toString());
  }

  function elegir(id) {
    estado.ind = id;
    const ind = porId(id);
    document.getElementById('notaIndicador').textContent = ind[idioma === 'en' ? 'nen' : 'nes'];
    document.getElementById('bloqueFecha').hidden = !ind.sequia;
    pintarBase();
    guardarUrl();
  }

  async function cargar() {
    const pedir = n => fetch(DATOS + n + '.json').then(r => {
      if (!r.ok) throw new Error(`${n}: HTTP ${r.status}`);
      return r.json();
    });
    const [man, tablas, mun, col, acu, poz, pre, mes, seq, cal, geo] = await Promise.all(
      ['manifiesto', '02_tablas_del_almacen', '03_municipios_zm', '04_colonias_zm', '05_acuiferos_zm', '06_pozos_zm',
        '07_presas', '08_presas_mensual', '09_sequia_zm', '10_calidad_zm', '12_geometrias'].map(pedir));
    D.manifiesto = man;
    D.tablas = tablas;
    D.municipios = filas(mun);
    D.colonias = filas(col);
    D.acuiferos = filas(acu);
    D.pozos = filas(poz);
    D.presas = filas(pre);
    D.presasMes = filas(mes);
    D.calidad = filas(cal);
    D.sequia = {};
    seq.filas.forEach(([m, f, s]) => { (D.sequia[f] = D.sequia[f] || {})[m] = s; });
    D.fechas = Object.keys(D.sequia).sort();
    D.geo = { municipio: {}, colonia: {}, acuifero: {} };
    geo.filas.forEach(([capa, clave, g]) => { D.geo[capa][clave] = JSON.parse(g); });
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
    const st = document.getElementById('status');
    st.textContent = t('cargando');
    st.className = 'status show loading';

    lienzo = L.canvas({ padding: 0.3 });
    mapa = L.map('map', { preferCanvas: true, zoomSnap: 0.25 });
    mapa.setView([19.5, -99.1], 9);
    try { MapaTeselas.montar(mapa, { maxZoom: 19 }); } catch (e) { console.error(e); }

    try {
      await cargar();
    } catch (e) {
      st.textContent = t('error', { msg: e.message });
      st.className = 'status show error';
      return;
    }
    st.className = 'status';

    const fechaQ = q.get('fecha');
    const i = fechaQ ? D.fechas.indexOf(fechaQ) : -1;
    estado.fecha = i >= 0 ? i : D.fechas.length - 1;
    const rango = document.getElementById('fecha');
    rango.max = D.fechas.length - 1;
    rango.value = estado.fecha;
    textoFecha();
    rango.addEventListener('input', () => { estado.fecha = +rango.value; textoFecha(); repintarEstilo(); guardarUrl(); });

    if (porId(q.get('ind'))) estado.ind = q.get('ind');
    traducir();
    document.getElementById('indicador').addEventListener('change', e => elegir(e.target.value));
    document.querySelectorAll('[data-capa]').forEach(c => c.addEventListener('change', () => alternar(c.dataset.capa, c.checked)));
    elegir(estado.ind);

    const c = (q.get('c') || '').split(',').map(Number);
    if (c.length === 3 && c.every(x => !isNaN(x))) mapa.setView([c[0], c[1]], c[2]);
    else {
      /* En la vista de figura la leyenda queda abajo a la izquierda: el encuadre le deja ese lado */
      const figura = document.documentElement.classList.contains('figura');
      mapa.fitBounds(L.geoJSON(coleccion('municipio', D.municipios, 'cve_mun')).getBounds(),
        figura ? { paddingTopLeft: [350, 10], paddingBottomRight: [10, 10] } : { padding: [12, 12] });
    }

    (q.get('capas') || '').split(',').filter(n => ['acuiferos', 'pozos', 'presas', 'calidad'].includes(n)).forEach(n => {
      const caja = document.querySelector(`[data-capa="${n}"]`);
      if (caja) caja.checked = true;
      alternar(n, true);
    });
  }

  document.addEventListener('idiomacambiado', e => {
    idioma = (e.detail && e.detail.idioma) || idioma;
    traducir();
    if (D.manifiesto) { leyenda(); origen(); document.getElementById('detalle').innerHTML = ''; }
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();

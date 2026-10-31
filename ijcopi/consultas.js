/* Lista las consultas al almacen con su SQL, su resultado y como repetirlas. */
(function () {
  'use strict';

  const TXT = {
    es: {
      titulo: 'Consultas al almacén', 'nav.mapa': 'Mapa', 'nav.grafo': 'Grafo', 'nav.consultas': 'Consultas al almacén',
      lema: 'Lo que muestra el mapa es el resultado de estas consultas. Cada una se puede repetir en la base de datos.',
      pasos: 'Cómo comprobarlo',
      'pasos.t': 'Con el almacén levantado, estos comandos arrancan la base de datos, copian las consultas, corren una, abren la consola de PostgreSQL y comparan el mapa con la base de datos.',
      filas: '{n} filas', sql: 'Ver SQL', primeras: 'Ver las primeras {n} filas', comando: 'Comando',
    },
    en: {
      titulo: 'Warehouse queries', 'nav.mapa': 'Map', 'nav.grafo': 'Graph', 'nav.consultas': 'Warehouse queries',
      lema: 'What the map shows is the result of these queries. Each one can be repeated in the database.',
      pasos: 'How to check it',
      'pasos.t': 'With the warehouse running, these commands start the database, copy the queries, run one of them, open the PostgreSQL console and compare the map with the database.',
      filas: '{n} rows', sql: 'Show SQL', primeras: 'Show the first {n} rows', comando: 'Command',
    },
  };

  const q = new URLSearchParams(location.search).get('lang');
  let idioma = q === 'en' || q === 'es' ? q : (window.I18N ? I18N.idioma : 'es');
  const t = (k, v) => {
    const s = TXT[idioma][k] || k;
    return v ? s.replace(/\{(\w+)\}/g, (m, n) => (n in v ? v[n] : m)) : s;
  };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let cache = null;

  function celda(v) {
    const s = v == null ? '' : String(v);
    return esc(s.length > 70 ? s.slice(0, 70) + '…' : s);
  }

  function tarjeta(c) {
    const titulo = c.sql.split('\n').filter(l => l.startsWith('--')).map(l => l.replace(/^--\s?/, '')).join(' ');
    const n = Math.min(10, c.tabla.filas.length);
    const cab = c.tabla.columnas.map(x => `<th>${esc(x)}</th>`).join('');
    const cuerpo = c.tabla.filas.slice(0, n).map(f => `<tr>${f.map(v => `<td>${celda(v)}</td>`).join('')}</tr>`).join('');
    return `<section class="panel zm-card">
      <h2>${esc(c.consulta)}</h2>
      <p>${esc(titulo)}</p>
      <p class="zm-meta">${t('filas', { n: c.filas.toLocaleString(idioma === 'en' ? 'en-GB' : 'es-MX') })} · SHA-256 ${c.sha256_datos.slice(0, 16)}…</p>
      <pre class="zm-pre">docker exec data_warehouse_cdmx psql -U postgres -d data_warehouse -f /consultas/${esc(c.consulta)}</pre>
      <details><summary>${t('primeras', { n })}</summary><div class="zm-tabla"><table><thead><tr>${cab}</tr></thead><tbody>${cuerpo}</tbody></table></div></details>
      <details><summary>${t('sql')}</summary><pre>${esc(c.sql)}</pre></details>
    </section>`;
  }

  function pintar() {
    document.documentElement.lang = idioma;
    document.title = t('titulo');
    document.querySelectorAll('[data-t]').forEach(el => { el.textContent = t(el.dataset.t); });
    if (cache) document.getElementById('lista').innerHTML = cache.map(tarjeta).join('');
  }

  async function iniciar() {
    pintar();
    const man = await fetch('ijcopi/datos/manifiesto.json').then(r => r.json());
    cache = await Promise.all(man.consultas.map(async c => ({
      ...c,
      sql: await fetch('warehouse_ampliado/consultas/' + c.consulta).then(r => r.text()),
      tabla: await fetch('ijcopi/datos/' + c.datos).then(r => r.json()),
    })));
    pintar();
  }

  document.addEventListener('idiomacambiado', e => {
    idioma = (e.detail && e.detail.idioma) || idioma;
    pintar();
  });
  iniciar();
})();

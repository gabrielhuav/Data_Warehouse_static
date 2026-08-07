/* Barra de navegación compartida. Marca la página actual sola. */
(function () {
  const paginas = [
    ['index.html',    'Panel'],
    ['mapa.html',     'Mapa'],
    ['grafo.html',    'Grafo de conocimiento'],
    ['vecindad.html', 'Vecindad territorial'],
  ];
  const actual = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const enlaces = paginas.map(([href, texto]) =>
    `<a href="${href}"${href.toLowerCase() === actual ? ' aria-current="page"' : ''}>${texto}</a>`
  ).join('');

  document.querySelectorAll('[data-barra]').forEach(el => {
    el.className = 'barra';
    el.innerHTML = `
      <div class="barra-in">
        <div class="marca">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2.5c-3.6 4.4-6.5 8-6.5 11.4a6.5 6.5 0 0 0 13 0C18.5 10.5 15.6 6.9 12 2.5z"
                  fill="#e8c877"/>
            <path d="M9.2 14.2a2.8 2.8 0 0 0 2.8 2.8" stroke="#6f1d46"
                  stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span>Consumo de Agua CDMX
            <small>Instituto Politécnico Nacional · Almacén de datos y grafo de conocimiento</small>
          </span>
        </div>
        <nav class="nav">${enlaces}</nav>
      </div>`;
  });

  document.querySelectorAll('[data-pie]').forEach(el => {
    el.className = 'pie';
    el.innerHTML = `
      Datos: <a href="https://datos.cdmx.gob.mx/dataset/consumo-agua" target="_blank" rel="noopener">SACMEX</a>,
      Portal de Datos Abiertos de la Ciudad de México (2019, bimestres 1–3) &middot;
      Clima: <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a> (CC BY 4.0) &middot;
      Mapa base: &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> (ODbL)<br>
      <strong>Instituto Politécnico Nacional</strong> &middot;
      Artefacto de <em>Territorial Information Retrieval from Heterogeneous Open Data through the
      Construction of a Data Warehouse for Water Management in Mexico City</em>, ICOKG 2026 &middot;
      <a href="https://github.com/gabrielhuav/Data_Warehouse_static" target="_blank" rel="noopener">Repositorio</a>`;
  });
})();

/* Modulo exploratorio de consumos atipicos.
   Calcula A_g = |x - mu| / (sigma + eps) para cada colonia frente a la media de
   su alcaldia y ordena las zonas por atipicidad. Es lo que describe el articulo:
   no un diagnostico, sino una funcion de ordenamiento que dice que unidades
   territoriales mirar primero.
   Autocontenido: lee consumo.json y se inserta como una tarjeta mas del panel,
   sin tocar el JavaScript existente. */
(function () {
  'use strict';
  var EPS = 1e-9, TOPE = 15;
  var fmt = function (n) { return new Intl.NumberFormat('es-MX', { maximumFractionDigits: 0 }).format(n); };
  var fmt2 = function (n) { return new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n); };

  function tarjeta() {
    var el = document.createElement('div');
    el.className = 'panel atipicos';
    el.innerHTML =
      '<h3>Zonas con consumo atipico</h3>' +
      '<div class="atip-cuerpo">' +
        '<p class="atip-nota">Score <b>A<sub>g</sub></b> = |x &minus; &mu;| / (&sigma; + &epsilon;), ' +
        'calculado para cada colonia frente a la media de su alcaldia. Es un criterio de ' +
        '<b>relevancia</b>, no un diagnostico: ordena que zonas revisar primero. ' +
        'El umbral convencional es A<sub>g</sub> &gt; 3.</p>' +
        '<div class="atip-controles">' +
          '<div><label for="atipAlc">Alcaldia</label>' +
          '<select id="atipAlc"><option value="">Todas</option></select></div>' +
          '<div><label for="atipTipo">Mostrar</label>' +
          '<select id="atipTipo"><option value="ambos">Altos y bajos</option>' +
          '<option value="alto">Solo consumo alto</option>' +
          '<option value="bajo">Solo consumo bajo</option></select></div>' +
        '</div>' +
        '<div id="atipEstado" class="atip-nota">Calculando&hellip;</div>' +
        '<div class="tabla-env" id="atipTabla"></div>' +
      '</div>';
    return el;
  }

  function insertar(el) {
    var panels = document.querySelector('.panels');
    var kpis = document.querySelector('.kpis');
    if (panels && panels.parentNode) panels.parentNode.insertBefore(el, panels.nextSibling);
    else if (kpis && kpis.parentNode) kpis.parentNode.insertBefore(el, kpis.nextSibling);
    else document.querySelector('.app-container').appendChild(el);
  }

  function calcular(filas) {
    var porColonia = {}, i, r, k;
    for (i = 0; i < filas.length; i++) {
      r = filas[i];
      k = r.alcaldia + '|' + r.colonia;
      if (!porColonia[k]) porColonia[k] = { alcaldia: r.alcaldia, colonia: r.colonia, total: 0 };
      porColonia[k].total += Number(r.consumo_total) || 0;
    }
    var porAlcaldia = {};
    Object.keys(porColonia).forEach(function (k) {
      var c = porColonia[k];
      (porAlcaldia[c.alcaldia] = porAlcaldia[c.alcaldia] || []).push(c);
    });
    var salida = [];
    Object.keys(porAlcaldia).forEach(function (a) {
      var l = porAlcaldia[a], n = l.length;
      var mu = l.reduce(function (s, c) { return s + c.total; }, 0) / n;
      var sigma = Math.sqrt(l.reduce(function (s, c) { return s + Math.pow(c.total - mu, 2); }, 0) / n);
      l.forEach(function (c) {
        salida.push({
          alcaldia: c.alcaldia, colonia: c.colonia, total: c.total,
          ag: Math.abs(c.total - mu) / (sigma + EPS),
          sentido: c.total >= mu ? 'alto' : 'bajo',
          veces: mu > 0 ? c.total / mu : 0
        });
      });
    });
    return salida.sort(function (a, b) { return b.ag - a.ag; });
  }

  function pintar(datos, alc, tipo) {
    var d = datos;
    if (alc) d = d.filter(function (x) { return x.alcaldia === alc; });
    if (tipo !== 'ambos') d = d.filter(function (x) { return x.sentido === tipo; });
    var sobre = d.filter(function (x) { return x.ag > 3; }).length;
    document.getElementById('atipEstado').innerHTML =
      '<b>' + fmt(sobre) + '</b> zonas superan el umbral A<sub>g</sub> &gt; 3 de ' +
      fmt(d.length) + ' evaluadas. Se muestran las ' + Math.min(TOPE, d.length) + ' mas atipicas.';
    var filas = d.slice(0, TOPE).map(function (x) {
      return '<tr><td class="nombre-largo" title="' + x.colonia + '">' + x.colonia + '</td>' +
        '<td>' + x.alcaldia + '</td>' +
        '<td class="num">' + fmt(x.total) + '</td>' +
        '<td class="num"><b>' + fmt2(x.ag) + '</b></td>' +
        '<td><span class="atip-sent ' + x.sentido + '">' +
          (x.sentido === 'alto' ? '&#9650; alto' : '&#9660; bajo') + '</span></td>' +
        '<td class="atip-por">consume <b>' + fmt2(x.veces) + '&times;</b> la media de su alcaldia</td></tr>';
    }).join('');
    document.getElementById('atipTabla').innerHTML = d.length
      ? '<table><thead><tr><th>Colonia</th><th>Alcaldia</th><th class="num">Consumo (m3)</th>' +
        '<th class="num">A<sub>g</sub></th><th>Sentido</th><th>Lectura</th></tr></thead>' +
        '<tbody>' + filas + '</tbody></table>'
      : '<p class="atip-nota">Sin datos para esta combinacion.</p>';
  }

  function iniciar() {
    if (!document.querySelector('.app-container')) return;
    insertar(tarjeta());
    fetch('consumo.json').then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    }).then(function (j) {
      var datos = calcular(j.consumo_colonia || []);
      var selAlc = document.getElementById('atipAlc');
      var vistos = {};
      datos.forEach(function (d) { vistos[d.alcaldia] = 1; });
      Object.keys(vistos).sort(function (a, b) { return a.localeCompare(b, 'es'); })
        .forEach(function (a) { selAlc.add(new Option(a, a)); });
      var selTipo = document.getElementById('atipTipo');
      var refrescar = function () { pintar(datos, selAlc.value, selTipo.value); };
      selAlc.onchange = selTipo.onchange = refrescar;
      refrescar();
    }).catch(function (e) {
      document.getElementById('atipEstado').textContent =
        'No se pudieron cargar los datos: ' + (e.message || e);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();

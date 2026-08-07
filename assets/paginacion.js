/* Salto directo de página en la tabla del panel.
   Con 10,641 registros y 50 por página son 213 páginas: avanzar de una en una
   no es navegable. Esto añade primera/última y un campo para ir a una página
   concreta, apoyándose en la función cambiarPagina() que ya existe. */
(function () {
  const cont = document.querySelector('.pagination .pages');
  const prev = document.getElementById('btnPrev');
  const next = document.getElementById('btnNext');
  const info = document.getElementById('pagInfo');
  if (!cont || !prev || !next || !info || typeof cambiarPagina !== 'function') return;

  const btn = (txt, tit) => {
    const b = document.createElement('button');
    b.type = 'button'; b.innerHTML = txt; b.title = tit; b.setAttribute('aria-label', tit);
    return b;
  };
  const primera = btn('&#8676;', 'Primera página');
  const ultima  = btn('&#8677;', 'Última página');
  const caja = document.createElement('div');
  caja.className = 'salto';
  caja.innerHTML = '<label for="pagIr">Ir a</label>' +
                   '<input id="pagIr" type="number" min="1" step="1" inputmode="numeric">' +
                   '<span class="de">de <b id="pagTotal">?</b></span>';

  cont.insertBefore(primera, prev);
  cont.appendChild(ultima);
  cont.parentNode.insertBefore(caja, cont.nextSibling);

  const campo = caja.querySelector('#pagIr');
  const total = caja.querySelector('#pagTotal');

  /* pagInfo dice "Mostrando 1–50 de 10,641 registros". El tamaño de página se
     toma del selector de límite, no de la resta hasta−desde: en la última
     página esa resta da un valor menor y el conteo saldría mal. */
  const selLimite = document.getElementById('fLimit');
  function estado() {
    const n = (info.textContent.match(/[\d.,]+/g) || []).map(x => +x.replace(/[.,]/g, ''));
    if (n.length < 3) return null;
    const desde = n[0], hasta = n[1], registros = n[2];
    let tam = selLimite ? parseInt(selLimite.value, 10) : NaN;
    if (!tam || tam < 1) tam = Math.max(1, hasta - desde + 1);
    return {
      actual: Math.floor((desde - 1) / tam) + 1,
      paginas: Math.max(1, Math.ceil(registros / tam)),
    };
  }

  function refrescar() {
    const e = estado();
    if (!e) return;
    total.textContent = e.paginas.toLocaleString('es-MX');
    campo.max = e.paginas;
    if (document.activeElement !== campo) campo.value = e.actual;
    primera.disabled = e.actual <= 1;
    ultima.disabled = e.actual >= e.paginas;
  }

  function irA(destino) {
    const e = estado();
    if (!e) return;
    const objetivo = Math.min(Math.max(1, destino), e.paginas);
    const salto = objetivo - e.actual;
    if (salto) cambiarPagina(salto);
  }

  primera.onclick = () => irA(1);
  ultima.onclick  = () => { const e = estado(); if (e) irA(e.paginas); };
  campo.addEventListener('change', () => irA(parseInt(campo.value, 10) || 1));
  campo.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); irA(parseInt(campo.value, 10) || 1); }
  });

  if (selLimite) selLimite.addEventListener('change', () => setTimeout(refrescar, 0));
  new MutationObserver(refrescar).observe(info, { childList: true, characterData: true, subtree: true });
  refrescar();
})();

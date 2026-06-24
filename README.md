# Consumo de Agua CDMX — versión estática

Sitio estático (HTML + JS + JSON + GeoJSON) sin backend ni dependencias de servidor. Listo para publicar en **GitHub Pages**.

## Contenido

| Archivo | Descripción |
|---|---|
| `index.html` | Dashboard con KPIs, gráficos Plotly y tabla paginada. |
| `mapa.html` | Mapa coroplético de las 16 alcaldías con Leaflet. |
| `consumo.json` | Dataset estático (~3.9 MB): catálogos + registros a nivel colonia + correlación clima. |
| `alcaldias.geojson` | Polígonos de las 16 alcaldías de la CDMX. |

## Datos

Los valores son **simulados** (no son datos reales del SACMEX/CONAGUA), generados con perfiles realistas por alcaldía y bimestre. Sirven para mostrar la UI completa:

- 16 alcaldías
- ~390 colonias distribuidas
- 5 años (2019–2023) × 6 bimestres × ~390 colonias = ~11,700 registros
- Datos de correlación clima (temperatura, lluvia, días extremos) por bimestre

## Publicar en GitHub Pages

1. Sube esta carpeta (`web/`) a tu repo en GitHub.
2. En el repo ve a **Settings → Pages**.
3. En **Source** elige:
   - **Deploy from a branch** → `main` (o la rama que uses) y carpeta `/web`.
4. Espera ~1 min. Tu sitio quedará en `https://<usuario>.github.io/<repo>/`.

> GitHub Pages sirve los archivos tal cual. No hay build, no hay backend.

## Probarlo en local

GitHub Pages requiere un servidor HTTP (los navegadores bloquean `fetch` desde `file://`):

```bash
cd web
python3 -m http.server 8000
# abrí http://127.0.0.1:8000/
```

## Notas

- El login se quitó: ahora todas las páginas son públicas.
- Toda la "consulta a la base de datos" se hace filtrando/agregando `consumo.json` en el cliente.
- Si querés regenerar el JSON con otros parámetros, el script generador está en la raíz del repo (`generar_consumo_json.py`); el resultado lo movés a esta carpeta.

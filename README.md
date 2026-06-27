# Consumo de Agua CDMX — versión estática

Sitio estático (HTML + JavaScript + JSON + GeoJSON) que permite consultar y visualizar el consumo de agua de la Ciudad de México sin depender de un servidor backend. Esta versión corresponde a la demostración pública del proyecto y está lista para publicarse en **GitHub Pages** o cualquier servicio de alojamiento estático.

## Contenido

| Archivo             | Descripción                                                                         |
| ------------------- | ----------------------------------------------------------------------------------- |
| `index.html`        | Dashboard con indicadores, gráficos interactivos (Plotly) y tabla de consulta.      |
| `mapa.html`         | Mapa coroplético interactivo de las 16 alcaldías utilizando Leaflet.                |
| `consumo.json`      | Conjunto de datos exportado desde el almacén de datos para la demostración pública. |
| `alcaldias.geojson` | Polígonos geográficos de las 16 alcaldías de la Ciudad de México.                   |

## Datos

Los datos utilizados en esta versión fueron exportados desde el almacén de datos construido durante el proyecto, el cual integra información proveniente de los conjuntos de datos abiertos publicados por el Sistema de Aguas de la Ciudad de México (SACMEX).

La versión estática contiene la información necesaria para ejecutar las consultas, filtros y visualizaciones del sistema directamente en el navegador, sin requerir conexión a una base de datos.

## Funcionalidades

* Consulta por alcaldía.
* Consulta por colonia.
* Filtros por año y bimestre.
* Visualización mediante mapa coroplético.
* Indicadores y gráficas interactivas.
* Detección exploratoria de consumos atípicos.

## Publicación en GitHub Pages

1. Subir el contenido del repositorio a GitHub.
2. Ir a **Settings → Pages**.
3. Seleccionar:

* **Deploy from a branch**
* Rama `main`
* Carpeta correspondiente al sitio

Una vez publicado, el sistema estará disponible mediante GitHub Pages como demostración pública del proyecto.

## Ejecución local

```bash
python3 -m http.server 8000
```

Después abrir:

```
http://127.0.0.1:8000/
```

## Notas

* La versión publicada corresponde a una implementación completamente estática destinada a la demostración y consulta del sistema.
* Toda la recuperación de información se realiza mediante procesamiento de los archivos JSON cargados en el navegador.
* El backend desarrollado con FastAPI y PostgreSQL forma parte de la implementación completa del proyecto, pero no es necesario para ejecutar esta versión de demostración.

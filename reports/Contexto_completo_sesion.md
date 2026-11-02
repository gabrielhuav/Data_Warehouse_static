# Contexto completo para continuar el trabajo

Complementa a `AGENTS.md`, que sigue siendo la memoria principal: reglas, requisitos de
IJCOPI, hechos establecidos y bitácora. Este archivo guarda lo que allí no cabe: lo que se
decidió en la conversación, qué contiene la v1 y qué quedó sin verificar. Lee primero
`AGENTS.md`. Conversa con Gabriel en español y de forma breve; le importa no gastar créditos.

## 1. Estado de git

- `main` quedó en `f404787`, igual en GitHub, con el almacén ampliado ya subido. Gabriel
  autorizó ese push con los fallos del verificador; la autorización no vale para otros.
- **Todo lo de IJCOPI va en la rama `ijcopi-zmvm`.** `main` queda congelada para ICOKG. La versión
  extendida se publica aparte en `gabrielhuav/Data_Warehouse_ZMVM`, con su propio Pages.
- La regla 2 pide `fallos: 0` y el verificador no llega a eso desde esta PC: el enlace
  `datos.cdmx.gob.mx/dataset/consumo-agua` da 403 porque el cortafuegos de la ADIP bloquea
  esta PC. Gabriel debe decidir antes de cada push: comprobarlo desde otra red o autorizarlo
  con esa excepción.
- Pages publica `main` desde la raíz (`build_type: legacy`) y solo esa rama.
- El tag `v1.5-icokg2026` sigue en `c4de86d`, sin cambios.
- `970697f` es un commit automático de `regenerar-demo.yml` en `consumo.json`. Se comparó el
  JSON antes y después: solo cambió `generado_en`, así que las cifras del artículo no cambian.

## 2. Decisiones de Gabriel

| Decisión | Detalle |
| --- | --- |
| Commits | En `ijcopi-zmvm`, conforme se avanza. Antes de cualquier push, ver la regla 2 |
| Fusiones | Nada a `main` sin que él lo pida; ICOKG no se toca |
| Rama de IJCOPI | Todo en una rama nueva y con enlaces nuevos; es su regla más importante |
| Título y autores | Aprobó el título nuevo. En IJCOPI él firma primero y sigue como autor de correspondencia; el segundo es el Dr. Roberto Eswart Zagal Flores |
| Correos y solicitudes | Mostrarle el texto y esperar su confirmación; nunca enviar antes |
| Enlaces de Springer | No pueden cambiar ni dejar de funcionar, en ningún cambio futuro |
| Versión base | La v0 queda idéntica a Springer; lo de cumplimiento va en la v1 y en amarillo |
| Cubo de datos | Pospuesto hasta tener más datos regionales; ya se puede retomar si lo decide |
| Memoria | Compartida entre Claude, ChatGPT y Gemini, en este repositorio |

## 3. La versión extendida (v1)

Fuente: `paper/ijcopi/dw_agua_ijcopi.tex`. La v1 (`dw_agua_IJCOPI_v1_extendida.docx`) tiene 14
páginas y 8,311 palabras, 48 % más que las 5,615 de la base. Gabriel dijo que la revisaría; no hay
constancia de que lo haya hecho. **La versión actual es la v3** (`dw_agua_IJCOPI_v3_grafo.docx`,
rama `ijcopi-zmvm`): 15 páginas, con el título nuevo, las secciones 5.7 y 5.8 y la Fig. 3. La tabla
de abajo describe lo que agregó la v1.

| Sección | Qué se agregó | Reproducción |
| --- | --- | --- |
| 1 | Párrafo de versión extendida con cuatro aportes | Citar la versión de ICOKG |
| 2.3 | Estudios previos con datos de SACMEX | Referencias verificadas en Crossref |
| 2.x (grafos) | Water Health Open Knowledge Graph | Lippolis et al. (2025) |
| 3.4 | "Billing basis": nota aclaratoria y actualización del portal | CSV y diccionario del portal |
| 5.3, Tabla 4 | Volumen facturado por habitante en las 16 alcaldías | `scripts/per_capita_alcaldia.py` |
| 5.5, Fig. 2, Tabla 6 | Sensibilidad en 12 escenarios y 20 semillas | `evaluacion-ml/sensibilidad_anomalias.py`, `figura_anomalias.py` |
| 5.6 | Ranking desplegado sobre datos reales y diseño de tres listas | `evaluacion-ml/ranking_real.py` |
| 7 | Quinta limitación, trabajo futuro y conclusión ajustados | n/a |

También cambió lo siguiente:

- El resumen se reescribió (149 palabras).
- Las palabras clave son Data warehouse, Open data, Knowledge graph, RDF Data Cube, Water
  consumption y Anomaly detection. Salieron Information retrieval, ETL y Mexico City. Gabriel
  no ha aprobado este cambio.
- Hay 12 referencias nuevas o actualizadas; las claves están en `latex_a_ijcopi.py`.
- La declaración de IA agrega la conversión a la plantilla. Hay que actualizarla si se suma
  más trabajo con IA.

### Afirmaciones que conviene revisar con cuidado

- **Sección 5.3.** La comparación contra 255 millones de m³ usa facturación de **2021**, no de
  2019. No se verificó el denominador de los 123 l/hab/día de Medina-Rivas et al.
- **Cuota fija por tandeo.** El art. 172 se revisó en un texto de 2024; la versión de 2019 no
  se comprobó. El manuscrito lo presenta como hipótesis, y así debe seguir.
- **"No encontramos un grafo RDF sobre datos de agua de empresas mexicanas".** Es una búsqueda
  razonable, no exhaustiva.
- **`medina2025`.** Se publicó en línea en 2024; se cita 2025 por el volumen 22(1).
- **Referencia de ICOKG.** Está "in press", sin serie, volumen ni páginas.
- **W2GIS 2025 y 2026.** Hernández-Vázquez et al. y Daowz Laguna et al. ya se citan en la sección
  2.3, solo a partir de sus resúmenes, porque el texto completo es de pago. El Dr. Zagal, coautor
  de ambos, puede confirmar si alguno contradice lo que dice la sección 2.8 sobre almacenes previos.
- **Data Availability Statement.** Apunta a `v1.5-icokg2026`, que no contiene los análisis
  nuevos. Hace falta un release nuevo; el v1.5 no se toca.

## 4. Datos de otros años y correos

- **Borrador en Gmail, sin enviar.** Se revisó el 31 de octubre. Va a
  `datosabiertos@cdmx.gob.mx` con copia a `infoadip@cdmx.gob.mx`; está en los borradores de Gabriel.
  Falta que Gabriel confirme el envío o que decida mandarlo desde `ghurtadoa@ipn.mx`, cuenta
  que no está conectada.
- **PNT.** Gabriel tiene que presentarla con su cuenta, y no se sabe si lo hizo. El texto está
  en `paper/ijcopi/solicitudes_de_datos.md`. Incluye un folio agregado por alcaldía, uso y tipo
  de facturación, que resolvería la hipótesis de cobertura. Una solicitud nueva ya no llegaría
  antes del 9 de noviembre con el plazo de 9 días hábiles más prórroga.
- **Folios previos que conviene buscar en la PNT:** 090173525000627, 090173522000091 y
  090173522001841.
- **Precedente:** por transparencia se han entregado totales por alcaldía y datos por colonia;
  por manzana, nada. Los recursos de revisión están suspendidos.

## 5. Plan del informe de datos

De `reports/Datos abiertos de agua CDMX.md`, sección "Plan de tres semanas". Compáralo con
`reports/Deep_Research_Ampliacion_DWH_IJCOPI.md`, que es posterior y corrige cifras.

1. Solicitudes PNT y correos: pendiente, ver sección 4.
2. Reescribir el contraste del 38 %: **hecho** en la v1.
3. Cruzar tandeo y reportes de falta de agua con las listas de exceso, déficit y sin volumen:
   solo es viable con falta de agua, porque antes de 2021 no hay registros de fugas. El tandeo
   (`C4`) sigue bloqueado.
4. `dim_colonia` con polígonos IECM: bloqueado por `C2`.
5. Comparar IDS 2020 con `indice_des`: bloqueado por `C3`.
6. Censo por manzana y Marco Geoestadístico: primer candidato a trabajo futuro.
7. Enlaces a Wikidata con P3801 para alcaldías: opcional. Wikidata no tiene población de
   Cuauhtémoc.

## 6. Presentaciones y trabajo 37

- `paper/presentacion/ICOKG2026_DW_Agua_ES.pptx` y `ICOKG2026_Water_DW_EN.pptx` ya están en
  `main`. Solo cambió la portada: logos del IPN y la ESCOM, como en el trabajo 37, y la línea de
  la conferencia a 11 pt para que no se encime. Los originales siguen en
  `C:\Users\gabri\Downloads\ICOKG 2026 REVIEWS\Presentaciones 24 SEPTIEMBRE 2026\`.
- **Trabajo 37:** `C:\Users\gabri\Documents\GitHub Desktop\PublicMunicipalWorks_DWH`. Su base
  está en `paper/ijcopi/Paper37_IJCOPI_v0_fiel.docx` (11 páginas). Falta extenderla 40 % y
  el envío también es el 9 de noviembre. Ese repositorio no tiene memoria compartida.

## 7. Entorno de esta PC

- Disponibles: Word y PowerPoint por COM (exportan PDF y PNG), `gh`, Node y Python 3.10.
- No disponibles: pandoc y LibreOffice. `python-pptx` y `rdflib` no están en el Python del
  sistema; instálalos en un entorno virtual aparte.
- Los archivos temporales de sesiones anteriores no son necesarios: sus cambios ya están
  aplicados en `paper/ijcopi/`.
- Gmail y Drive están conectados en Claude Code; otro agente puede no tenerlos. La carpeta
  de la plantilla en Drive es `1GKNZt7hjTwy3cbeA5-ThEPZzulw_SME1`.

## 8. Prioridad al retomar

La lista viva está en "Siguiente paso" de `AGENTS.md`. Además de eso:

1. Preguntar a Gabriel qué decidió sobre el cubo y el borrador del correo.
2. Revisar con él la sección 0 del informe de ampliación.
3. Definir cuándo se extiende el trabajo 37; sin eso no llega al 9 de noviembre.

# Memoria compartida del proyecto

Este archivo es la memoria común para Claude, ChatGPT, Gemini y cualquier otro
agente que trabaje en este repositorio. Léelo completo antes de empezar.
Al terminar una sesión, actualiza "Estado actual" y "Siguiente paso", y agrega a
"Bitácora" una línea con la fecha, el agente y lo que cambió. Solo escribe aquí lo
que el repositorio no dice por sí mismo.

Conversa con Gabriel en español. Rama de trabajo: `main`.
Repositorio: <https://github.com/gabrielhuav/Data_Warehouse_static>

## Reglas que no se negocian

1. **Los enlaces del artículo enviado a Springer son inmutables.** Todo URL de
   `paper/dw_agua_icokg2026.tex` ya está publicado: páginas de GitHub Pages
   (incluida `vecindad.html?alcaldia=IZTAPALAPA&colonia=AO%20DE%20JUAREZ`), este
   repositorio, el fork `data_warehouse_cdmx` y el release `v1.5-icokg2026`. No
   renombres ni muevas esas páginas, no retires ese tag y no renombres el repo.
   Lo mismo vale para los enlaces del trabajo 37 (repo `PublicMunicipalWorks_DWH`).
   Lo nuevo va en rutas o releases nuevos.
2. **Antes de cada push** corre
   `powershell -ExecutionPolicy Bypass -File scripts/verificar_enlaces_springer.ps1`
   y comprueba que termine con `fallos: 0`.
3. **No toques `paper/dw_agua_icokg2026.tex` ni sus PDF.** Es el camera-ready de
   Springer. La versión de la revista sale de `paper/ijcopi/dw_agua_ijcopi.tex`.
4. **No envíes correos ni solicitudes sin que Gabriel vea el texto y confirme.**
5. **Solo reporta cifras que hayas recalculado.** Cada número del artículo debe poder
   reproducirse con un script del repositorio. Si algo no se pudo verificar, dilo.

## El trabajo

Artículo aceptado en ICOKG 2026 (5.ª conferencia, BUAP; memorias de Springer): un
almacén de datos y un grafo RDF sobre el consumo de agua de SACMEX en la CDMX,
primer semestre de 2019. Es el trabajo **ID 38**. Autores: Eduardo Uriel Velázquez
Arrieta, Omar Fernando Pulido Morales, Emilio García López, Clara Aide Hernández
Martínez y Gabriel Hurtado Avilés (autor de correspondencia), todos de ESCOM-IPN.

Se invitó una versión extendida al número especial de IJCOPI (ISSN 2007-1558). La
participación de los trabajos 37 y 38 ya se confirmó por correo el 13 de octubre.

### Requisitos de IJCOPI

- Inglés, ortografía británica; en Microsoft Word y **con la plantilla obligatoria**
  `paper/2027-IJCOPI_template_simple_British_English.docx`, o se rechaza en automático.
- Extender **al menos 40 %** la versión de ICOKG y **marcar los cambios en amarillo**.
- **Máximo 15 páginas** en ese formato (la guía general dice 20; manda el correo).
- Resumen de 70 a 150 palabras; 4 a 6 palabras clave; citas y referencias en APA 7.
- Declarar el uso de IA. Se revisa con herramientas de similitud y de IA.
- Contribución de $1,000.00 si se acepta; el correo no aclara la moneda.
- Enviar a icokg@correo.buap.mx con asunto `Special Issue IJCOPI – ID 38 ICOKG 2026`.

| Fecha (2026) | Hito |
| --- | --- |
| 9 nov | Envío de manuscritos |
| 20 nov | Notificación y solicitud de cambios |
| 27 nov | Nueva versión |
| 4 dic | Aceptación |
| 8 dic | Versión final |

## Dónde está cada cosa

| Ruta | Qué es |
| --- | --- |
| `paper/ijcopi/dw_agua_ijcopi.tex` | **Fuente de la versión extendida**. `\nuevo{...}` y el entorno `nuevobloque` marcan lo que va en amarillo |
| `paper/ijcopi/latex_a_ijcopi.py` | Conversor a la plantilla Word; aquí viven las citas y referencias APA (`CITAS`, `REFERENCIAS`; `!` = referencia nueva) |
| `paper/ijcopi/word_a_pdf.ps1` | Exporta a PDF con Word y cuenta páginas y palabras |
| `paper/ijcopi/verificar_amarillo.py` | Comprueba que todo lo agregado esté en amarillo |
| `paper/ijcopi/dw_agua_IJCOPI_v0_base.docx` | Base congelada: texto idéntico al de Springer. No se modifica |
| `paper/ijcopi/dw_agua_IJCOPI_v1_extendida.docx` | Versión extendida generada (y su PDF) |
| `paper/ijcopi/solicitudes_de_datos.md` | Plantillas para pedir más datos |
| `reports/Datos abiertos de agua CDMX.md` | Informe de fuentes de datos, con plan ordenado por valor y esfuerzo |
| `research_notes/` | Notas detalladas de esa investigación |
| `paper/presentacion/` | Presentaciones de ICOKG (ES y EN) |
| `evaluacion-ml/`, `scripts/` | Análisis reproducibles y sus evidencias |

Para regenerar la v1 (desde `paper/ijcopi/`):

```bash
py -3 latex_a_ijcopi.py dw_agua_ijcopi.tex ../2027-IJCOPI_template_simple_British_English.docx .. dw_agua_IJCOPI_v1_extendida.docx
py -3 verificar_amarillo.py dw_agua_IJCOPI_v0_base.docx dw_agua_IJCOPI_v1_extendida.docx
```

Si alguien edita el `.docx` a mano, esa edición se pierde al regenerar. Mientras el
texto siga cambiando, edita el `.tex`; pasa al Word solo en el ajuste final. Las
diferencias "sin amarillo" que quedan (46 palabras) son renumeración y cortes de
línea; revísalas si ese número cambia.

## Hechos establecidos (no volver a investigar)

- **Los datos abiertos solo cubren los bimestres 1 a 3 de 2019.** El portal migró el
  recurso en agosto de 2026 con contenido idéntico (mismo MD5 con saltos de línea
  normalizados, `41495b03...`).
- **SACMEX ahora opera como SEGIAGUA.** Las solicitudes de transparencia van ahí, por
  la PNT. `datosabiertos@cdmx.gob.mx` es de la ADIP, no del organismo de agua.
- **El valor de consumo es facturación, no lectura de medidor**: mezcla consumo medido
  y promedio, según la nota aclaratoria (publicada como "Diccionario de datos").
- **El export está casi completo respecto a la facturación**: unos 243 millones de m³
  anualizados frente a 255 millones facturados en 2021 (resolución
  INFOCDMX/RR.IP.0679/2022, verificada en la fuente). Pero implica 47.3 l/hab/día,
  frente a los 123 de Medina-Rivas et al. (2022). La facturación por volumen capta
  solo parte del consumo, y mucho menos en la periferia. No digas que el export
  está incompleto. La explicación por cuota fija en colonias con tandeo es una
  hipótesis sin confirmar.
- **`A_g` no puede señalar consumo bajo**: su tope bajo la media es `1/CV` (mediana
  0.85 entre alcaldías) y el lugar 15 de la lista puntúa 3.85. En escala log,
  `log-A_g` recupera 92 % de las caídas simuladas, pero en los datos reales 45 del
  top 47 quedan bajo la media. La simulación es log-normal, así que su ventaja es
  una cota superior. Hay 29 colonias con volumen facturado cero.
- **El `indice_des` es fiscal** (Código Fiscal CDMX, art. 172), no el IDS de Evalúa.
- **Las colonias de SACMEX coinciden con el catálogo IECM 2019**: el cruce exacto da
  `cve_col` y polígono a las 70,886 filas de hechos.

## Avisos técnicos

- `pandas` lee la cadena `NA` del CSV como nulo. Filtra con `notna()`, no con `!= "NA"`.
- `curl -L` desde Git Bash falla en github.com con error 43; usa PowerShell o `gh`.
- `eval_anomalias.py` necesita `rdflib`, que el `.venv` del repo no trae.
- Mapas Leaflet: si el panel del navegador está oculto, `innerWidth` es 0 y el zoom
  salta a 19; no es un error. Emula 1280x800 antes de juzgar el encuadre.
- PowerShell 5.1 requiere `-UseBasicParsing` en `Invoke-WebRequest`.

## Estado actual

- **Hecho:** v0 base y v1 extendida (8,311 palabras contra 5,615, +48 %; 14 páginas;
  resumen de 149 palabras; 6 palabras clave). Informe de datos. Presentaciones con logos.
- **Trabajo 37:** tiene su base en Word en `PublicMunicipalWorks_DWH/paper/ijcopi/`;
  falta extenderlo.
- **Sin revisar por humanos:** el texto nuevo de la v1 y el informe.

### Pendientes conocidos

- El correo a `datosabiertos@cdmx.gob.mx` sigue como borrador en el Gmail de Gabriel,
  sin enviar (revisado el 2026-10-31). No se sabe si presentó la solicitud en la PNT.
- Confirmar serie, volumen y páginas de la referencia de ICOKG, ahora "in press".
- Crear un release nuevo con los análisis y cambiar a él el Data Availability Statement,
  que hoy apunta a `v1.5-icokg2026`, que no los contiene. El tag v1.5 no se toca.
- Decidir si se implementa en el demo el diseño de tres listas; hoy es trabajo futuro.
- Aclarar la moneda de la contribución y revisar la licencia firmada con Springer.

## Siguiente paso

Gabriel tiene una idea de qué hacer con el artículo; pregúntale cuál es antes de
proponer otro plan.

## Bitácora

- 2026-10-31, Claude (Claude Code): creó esta memoria y subió la v1, los análisis,
  el informe y las plantillas a `main`.

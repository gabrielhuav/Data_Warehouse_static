# CDMX-level open water datasets that can be joined to the SACMEX 2019 consumption warehouse (status as of 18 Oct 2026)

Method note (applies to every section). Metadata was read live from the CKAN API of datos.cdmx.gob.mx (`package_show`, `datastore_search`, `datastore_search_sql`) on 2026-10-18. Every count, date range and match rate below was computed server-side through the API without downloading files: [CKAN API endpoint](https://datos.cdmx.gob.mx/api/3/action/package_search?q=agua). `q=agua` returns 44 datasets. The SACMEX organisation has only 2 datasets (`consumo-agua`, `reportes-de-agua`): [SACMEX organisation page](https://datos.cdmx.gob.mx/dataset/?organization=sistema-de-aguas-de-la-ciudad-de-mexico). Every package inspected reports `metadata_created` = 2026-08-27 and resource `created/last_modified` = 2026-08-28 (a few 2026-08-31/09-01). These dates reflect the Aug 2026 portal migration, not data freshness, so the "data vintage" given in each row is the meaningful date. Licence for every portal dataset listed is `CC-BY-4.0-ESP`. The coordinator has already established that the consumo-agua resource was migrated in Aug 2026 unchanged and that SACMEX now operates as SEGIAGUA, so neither point was re-researched.

## Q1. Is SACMEX water consumption published for any period other than bimesters 1–3 of 2019?

### Takeaway
No. Neither the portal nor its history has ever held more than the 71,102 rows for bimesters 1–3 of 2019. Every colonia-level "consumption" layer on the portal is derived from those same rows (bimester 3 of 2019). The only public multi-year consumption figures are the annual Gaceta Oficial lists of *colonias catastrales*: one average per colonia, only for colonias with ≥70 % metered connections, as PDFs. They are hard to integrate in 3 weeks.

### Cited Findings
- The current resource "Consumo Agua (1° Semestre 2019)" has 71,102 rows. SQL gives 23,338 rows for bimester 1 (`fecha_referencia` 2019-02-28), 23,942 for bimester 2 (2019-04-30) and 23,822 for bimester 3 (2019-06-30). Fields: `fecha_referencia, anio, bimestre, consumo_total(_dom/_no_dom/_mixto), consumo_prom(_dom/_no_dom/_mixto), indice_des, colonia, alcaldia, latitud, longitud`. There is no manzana ID — [Consumo de agua](https://datos.cdmx.gob.mx/dataset/consumo-agua)
- History. The old OpenDataSoft portal showed `records_count` 23,338 on 2019-08-05, which is bimester 1 only. It showed 71,102 after reprocessing on 2019-12-06 and was still at 71,102 in the Nov 2020 snapshot. That version also had `geo_shape` (manzana polygon) and `nomgeo` fields, which the current CSV lacks — [Wayback 2019-08-20](http://web.archive.org/web/20190820152332/https://datos.cdmx.gob.mx/explore/dataset/consumo-agua/); [Wayback 2020-11-28](http://web.archive.org/web/20201128085205/https://datos.cdmx.gob.mx/explore/dataset/consumo-agua/)
- CKAN snapshots from 2021, Jun 2024 and Sep 2025 list one CSV, "Consumo Agua (1° Semestre 2019)" (file `consumo_agua_historico_2019.csv`, resource last updated 2 Feb 2023), plus `nota-aclaratoria.xlsx`. The dataset itself was last updated 7 Jul 2023. No other period ever appears — [Wayback 2024-06-13](http://web.archive.org/web/20240613003830/https://datos.cdmx.gob.mx/dataset/consumo-agua); [Wayback 2025-09-05](http://web.archive.org/web/20250905213619/https://datos.cdmx.gob.mx/dataset/consumo-agua)
- The resource now titled "Diccionario de datos" (id `3c234714-d04e-4321-b5bf-f3788ca2914c`) is the same resource that was served as `nota-aclaratoria.xlsx` in 2021–2025. Its datastore has a single column, `NOTA ACLARATORIA`, and 0 rows, so the clarification text exists only inside the XLSX — [resource page](https://datos.cdmx.gob.mx/dataset/consumo-agua/resource/3c234714-d04e-4321-b5bf-f3788ca2914c)
- IPDP's "Consumo habitacional promedio bimestral de agua por colonia (m3)" is derived from SACMEX bimester 3 of 2019, not from a new period. For colonia AGUILERA (02-001), `SUM_cons_t` = 13,759.05 and `FREQUENCY` = 9. That equals exactly the sum of `consumo_total` over the 9 manzana rows of AGUILERA in bimester 3 (13,759.05); bimester 1 sums to 13,654.92 and bimester 2 to 13,115.45. Its other fields are `VIV2010` and `PROMVIVCON` (consumption per dwelling) — [dataset](https://datos.cdmx.gob.mx/dataset/consumo-habitacional-promedio-bimestral-de-agua-por-colonia-m3)
- IPDP's "Diferencia consumo total SACMEX" has the same `SUM_cons_t`, plus `pob_2010`, domestic/mixed/non-domestic sums, `SUM_MAPAS` (CONAGUA MAPAS reference demand), `CO_PC`, `CO_PC_MAPA` and `DIF_CON`. The dictionary describes `DIF_CON` as the difference in SACMEX total consumption, "TERCER TRIMESTRE 2019" — [dataset](https://datos.cdmx.gob.mx/dataset/diferencia-consumo-total-sacmex)
- Art. 172 of the Código Fiscal requires the water authority to publish each year in the Gaceta Oficial "las listas de las colonias catastrales que vayan contando con un 70% o más de tomas con servicio medido, así como el consumo promedio de cada una de ellas en el ejercicio fiscal inmediato anterior" — [SAF transparency PDF, Art. 172](https://transparencia.finanzas.cdmx.gob.mx/repositorio/public/upload/repositorio/Tesoreria/123/b/Criterio_9/123_XV_Derechos_por_el_suministro_de_%20agua_2024.pdf)
- The list published Feb 2024 covers fiscal year 2023 and identifies colonias by catastral code. Examples: A010522 Álvaro Obregón, 63.33 m³ daily average; A110665 Miguel Hidalgo, 125.29 m³ — [El Financiero, 7 Feb 2024](https://www.elfinanciero.com.mx/cdmx/2024/02/07/mapa-muestra-las-colonias-que-mas-agua-gastan-en-cdmx-segun-sacmex/). The Feb 2025 notice listed 611 colonias catastrales (Álvaro Obregón 141, Miguel Hidalgo 67, etc.) — [El Universal, 25 Feb 2025](https://www.eluniversal.com.mx/metropoli/tienen-611-colonias-servicio-de-agua-medido/)
- The SAF cadastre on the portal has predio-level `clave_valor_unitario_suelo` codes in the same format (e.g., "A120010"), with lat/lon and an IECM-style `colonia`. Iztapalapa alone has 372,197 predios and 114 distinct codes. This could bridge catastral codes to the warehouse — [Información Catastral](https://datos.cdmx.gob.mx/dataset/informacion-catastral-de-la-ciudad-de-mexico)
- A 2024 peer-reviewed study modelled neighbourhood-level measured consumption for 2004–2022. It cites "SACMEX 2023 Plataforma Nacional de Transparencia" as its data source, meaning it was obtained by information request, not from open data — [Ramos-Bueno et al. 2024, Water Supply 24(9):3179–3195](https://doi.org/10.2166/ws.2024.191) (references read via [Crossref](https://api.crossref.org/works/10.2166/ws.2024.191))

### Inferences
- New consumption periods cannot come from the portal. The realistic additions are (a) the 2019 IPDP colonia layers, which add dwellings (2010), population (2010) and a MAPAS benchmark per colonia, but no new time; and (b) Gaceta colonia-catastral averages for fiscal years 2018–2024, a hard option that needs PDF table extraction plus a catastral-code→colonia bridge through the SAF cadastre.
- Reading the Nota Aclaratoria XLSX (12 KB, linked as "Diccionario de datos") is a cheap must-do before the journal version, because the publisher flags it as necessary for "un análisis más preciso".

### Gaps
- I did not open the Nota Aclaratoria XLSX itself, because downloads were avoided.
- I did not locate the exact Gaceta PDF URLs for the colonia-catastral lists for 2019–2025; only press coverage was verified.
- The Internet Archive CDX index was intermittently offline, so archived exports of the old ODS GeoJSON (with manzana polygons) could not be checked.

## Q2. Official colonia polygons and keys (IECM catalogue, ADIP catalogue, IPDP layers built from SACMEX 2019)

### Takeaway
SACMEX's colonia labels are a verbatim copy of the IECM 2019 colonia catalogue (`coloniascdmx`), including quirks such as the dropped "Ñ" ("AO DE JUAREZ") and trailing underscores. An exact SQL join on (alcaldia, colonia) assigns the IECM key `cve_col` (format "07-007") and a polygon to 70,886 of 71,102 SACMEX rows (99.7 %). The IECM 2019 key is the backbone for the IPDP colonia layers and the EVALUA unit-territorial IDS. Data from 2022 onward instead uses the ADIP catalogue (key "002-001", Title Case), which needs a spatial join.

### Cited Findings
- **Colonias del IECM – 2019** (`coloniascdmx`, publisher IECM). Formats: CSV (5.4 MB, datastore, 1,812 rows with `geo_shape` GeoJSON polygons), SHP, GeoJSON and a PDF dictionary. Fields: `id, nombre, entidad, geo_point_2d, geo_shape, cve_alc, alcaldia, cve_col, secc_com, secc_par`. Examples: "AO DE JUAREZ" IZTAPALAPA 07-007; "PEON DE LOS BAOS" VENUSTIANO CARRANZA 17-047; "CENTRO I"…"CENTRO VIII" CUAUHTEMOC 15-037…15-044 — [dataset](https://datos.cdmx.gob.mx/dataset/coloniascdmx); [CSV](https://datos.cdmx.gob.mx/dataset/04a1900a-0c2f-41ed-94dc-3d2d5bad4065/resource/03368e1e-f05e-4bea-ac17-58fc650f6fee/download/03368e1e-f05e-4bea-ac17-58fc650f6fee.csv)
- An exact join `ON i.nombre = c.colonia AND i.alcaldia = c.alcaldia` matched 70,886 of 71,102 SACMEX rows (the remainder are rows labelled "NA"). SACMEX has 1,554 distinct (alcaldía, colonia) pairs, including NA. That covers about 1,553 of the 1,812 IECM colonias — computed via `datastore_search_sql` on [consumo-agua](https://datos.cdmx.gob.mx/dataset/consumo-agua) × [coloniascdmx](https://datos.cdmx.gob.mx/dataset/coloniascdmx)
- **Colonias del IECM – 2022** (IECM). SHP (1.4 MB) plus an XLSX dictionary with fields: Clave entidad, Clave demarcación territorial, Demarcación, Distrito local, Distrito local 2023, Clave unidad territorial, Unidad territorial, Secciones completas/parciales, Población. Use it only if 2022+ data is added; key continuity with 2019 was not checked — [dataset](https://datos.cdmx.gob.mx/dataset/colonias-del-iecm-2022)
- **Catálogo de colonias (Datos abiertos)** (ADIP, the "Sistema Ajolote" catalogue). SHP (2.5 MB) and GeoJSON (10.4 MB) with properties `cve_ent, entidad, cve_alc "002", alc "Azcapotzalco", cve_col "002-001", colonia "Aguilera", clasif "Colonia"`. It merges IECM sub-colonias (e.g., one "Centro" and one "Roma Norte" in Cuauhtémoc, versus CENTRO I–VIII and ROMA NORTE I–III in IECM 2019) — [dataset](https://datos.cdmx.gob.mx/dataset/catalogo-de-colonias-datos-abiertos)
- **IPDP colonia layers keyed by the IECM 2019 `cve_col`** (all SHP/GeoJSON plus a CSV dictionary; first feature verified with `cve_col` "02-001", `colonia` "AGUILERA"):
  - Consumo habitacional promedio bimestral por colonia (from SACMEX bimester 3 of 2019) — [link](https://datos.cdmx.gob.mx/dataset/consumo-habitacional-promedio-bimestral-de-agua-por-colonia-m3)
  - Diferencia consumo total SACMEX (from SACMEX bimester 3 of 2019) — [link](https://datos.cdmx.gob.mx/dataset/diferencia-consumo-total-sacmex)
  - Cobertura de infraestructura de agua potable (m/hab). Fields `pob_2010, SUP_COL_M2, PromFugas` (average leaks), `LongInf_m, m_x_hab` — [link](https://datos.cdmx.gob.mx/dataset/cobertura-de-infraestructura-de-agua-potable-m-hab)
  - Grado de marginalidad y violencia urbana por colonia — [link](https://datos.cdmx.gob.mx/dataset/grado-de-marginalidad-y-violencia-urbana-por-colonia-en-la-ciudad-de-mexico)
  - Nivel de servicios básicos y equipamiento por colonia (% of dwellings with water; `cve_col` is 5 characters, IECM) — [link](https://datos.cdmx.gob.mx/dataset/porcentaje-de-viviendas-con-servicios-basicos-y-numero-de-elementos-de-equipamiento-de-primer-nivel)
  - Total de hogares por colonia — [link](https://datos.cdmx.gob.mx/dataset/total-de-hogares-por-colonia)
  - Densidad habitacional por colonia — [link](https://datos.cdmx.gob.mx/dataset/densidad-habitacional-por-colonia-viv-ha)
- **IPDP colonia layers keyed only by name and alcaldía**:
  - Colonias con distribución de agua por tandeo 2019. Fields `ID, ENTIDAD, NOMBRE, DELEGACIO, tnd_2019`; SHP only — [link](https://datos.cdmx.gob.mx/dataset/colonias-con-distribucion-de-agua-por-tandeo-2019)
  - Factibilidad hídrica. Fields `NOMBRE, DELEGACIO, fact_hidr` = verde/amarillo/naranja/rojo — [link](https://datos.cdmx.gob.mx/dataset/factibilidad-hidrica)
- The SAF cadastre `colonia` labels equal IECM 2019 labels: 62 of 62 distinct pairs for Cuauhtémoc and 292 of 292 for Iztapalapa joined exactly — [Información Catastral](https://datos.cdmx.gob.mx/dataset/informacion-catastral-de-la-ciudad-de-mexico)
- Supporting polygons: INEGI Marco Geoestadístico 2020 manzanas (SHP 18 MB, GeoJSON 81 MB, key CVEGEO) — [link](https://datos.cdmx.gob.mx/dataset/poligonos-de-manzanas-de-la-ciudad-de-mexico); alcaldías — [link](https://datos.cdmx.gob.mx/dataset/alcaldias)
- iecm.mx did not respond from this environment on 2026-10-18; the portal copies are the verified source.

### Inferences
- Recommended conformed `dim_colonia`: IECM 2019 `cve_col` plus polygon, with the SACMEX label kept as an alternate key. That one dimension makes these joins key-based and easy: all IPDP `cve_col` layers, the EVALUA unit-territorial IDS, 2018–2021 SACMEX reports, Locatel 2019 requests and the cadastre.
- Adding IECM polygons to the RDF graph (GeoSPARQL `geo:hasGeometry`) and an alternate "ADIP colonia" key (filled by spatial join) is a contained, publishable extension.

### Gaps
- I did not check how IECM 2019 keys map to IECM 2022 keys.
- Attribute values of the SHP-only IPDP layers (tandeo 2019, factibilidad, garzas) were not inspected; only their dictionaries were. In particular, the number of colonias flagged in `tnd_2019` is unknown.
- The year of the factibilidad hídrica data is not stated in its metadata.

## Q3. Evalúa CDMX Índice de Desarrollo Social (IDS) by colonia/manzana, and whether it explains the SACMEX `indice_des`

### Takeaway
EVALUA's IDS 2020 is open at alcaldía, AGEB, manzana and unidad-territorial (colonia) level. The unit-territorial key `cve_ut` equals IECM 2019 `cve_col` (1,810 of 1,812 match), so it joins to SACMEX by key in one SQL statement. Manzana-level IDS polygons are available through IPDP's SIEG WFS for a point-in-polygon join. SACMEX's 4-level `indice_des` is a separate *fiscal* index (Art. 172 Código Fiscal, manzana classes for tariff subsidies). It agrees only weakly with IDS 2020, which is itself a publishable validation result.

### Cited Findings
- **Índice de Desarrollo Social de la CDMX, 2020** (EVALUA) — [dataset](https://datos.cdmx.gob.mx/dataset/indice-de-desarrollo-social-de-la-ciudad-de-mexico-2020). Resources:
  - CSV by alcaldía: 16 rows, `folio_mun` "09002".
  - CSV by AGEB: 3,029 rows, `folio_ageb`.
  - CSV by manzana: 67,382 rows, 6.1 MB, `folio_mza` = 16-digit CVEGEO, e.g. "0900200010010001".
  - XLSX by unidad territorial: 1,817 rows, with `ent, cvemun, alcaldia, cve_ut "02-001", nombre_ut`.
  - XLSX dictionaries for each level.
  - Common fields: `pob, pob_nbi, ids_ccevj` (housing quality and space), `ids_csj` (sanitary adequacy: water, drainage, toilet), `ids_caej` (energy), `ids_ctelj` (telecom), `ids_cbdj` (durable goods), `ids_rei` (education), `ids_cassi` (health), `ids_casi` (social security), `idsm` (index value) and `e_idsm` (Muy bajo … Muy alto).
- The IDS unit-territorial names show "Ñ" corrupted to "?" (e.g., "A?O DE JUAREZ"), so the join must use `cve_ut`, not names. A `LEFT JOIN` of IECM 2019 to IDS UT on `cve_ut = cve_col` matched 1,810 of 1,812 — computed via `datastore_search_sql` on [UT XLSX resource](https://datos.cdmx.gob.mx/dataset/46ead7d7-8c8c-4660-b1d6-63f8875e0a93/resource/0b408748-2a1f-4c3c-844f-72fb6dff598d/download/0b408748-2a1f-4c3c-844f-72fb6dff598d.xlsx)
- **IDS 2020 a nivel Unidad Territorial** (IPDP adjustment of the EVALUA index). XLSX with 1,814 rows: `NOMDT, CVEUT, NAME, ids, E_IDS_V` (includes "Muy Alto") — [dataset](https://datos.cdmx.gob.mx/dataset/indice-de-desarrollo-social-ids-2020-a-nivel-unidad-territorial)
- **SIEG (IPDP GeoNode) WFS `geonode:ids_2020_mz`**: 66,789 manzana MultiPolygons in EPSG:32614 with `CVEGEO, CVE_ENT, CVE_MUN, CVE_LOC, CVE_AGEB, CVE_MZA, AMBITO, E_IDS_V, IDSM`. The WFS GetFeature returned JSON without authentication — [layer page](https://sieg.cdmx.gob.mx/layers/geonode%3Aids_2020_mz); [WFS](https://sieg.cdmx.gob.mx/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=geonode:ids_2020_mz&count=1&outputFormat=application/json). The same SIEG serves `geonode:im_colonia`, CONAPO's urban marginalisation index 2020 by colonia (2,243 polygons) — [layer](https://sieg.cdmx.gob.mx/layers/geonode%3Aim_colonia)
- Older and other EVALUA material on the portal:
  - 2015 dimension tables, e.g., "Adecuación Sanitaria", by alcaldía × poverty stratum × sex × age (714 rows) — [link](https://datos.cdmx.gob.mx/dataset/diagnostico-cdmx_2015_adec_san)
  - NBI 2020 microdata, 274,026 person rows (68.6 MB), hard to use — [link](https://datos.cdmx.gob.mx/dataset/nbi-en-la-ciudad-de-mexico-2020)
  - EVALUA's IDS 2020 presentation (Oct 2024) — [PDF](https://www.evalua.cdmx.gob.mx/storage/app/media/2024/die/ids/ids-evaluapresentacion17102024.pdf). I did not open it.
- **What SACMEX `indice_des` is.** Art. 172 grants tariff subsidies "de acuerdo a la manzana donde se ubique la toma … Popular, Baja, Media o Alta; para tal efecto, el Congreso emitirá la relación considerando las regiones y manzanas". Users may request reclassification if it "no corresponda al determinado por este Código con base en el Índice de Desarrollo por Manzana". The same article sets fixed-fee subsidies for tandeo colonias: Popular 97.0007 %, Baja 95.2403 %, Media 87.9587 %, Alta 79.3905 % — [SAF Art. 172 PDF](https://transparencia.finanzas.cdmx.gob.mx/repositorio/public/upload/repositorio/Tesoreria/123/b/Criterio_9/123_XV_Derechos_por_el_suministro_de_%20agua_2024.pdf)
- Press from 2009–2010 (search snippets; articles not opened): the manzana classification was set by the Asamblea Legislativa in Dec 2009 and deliberately did not use CONEVAL criteria. Per the snippets, it relied mainly on household income — [La Jornada 17 Jan 2010](https://www.jornada.com.mx/2010/01/17/capital/030n2cap); [La Jornada 21 Dec 2009](https://www.jornada.com.mx/2009/12/21/capital/029n1cap)
- **Cross-tabulation of SACMEX `indice_des` against EVALUA `e_idsm` at unidad-territorial level.** The unit is manzana-bimester rows; 70,827 rows joined.

  | SACMEX `indice_des` | Rows | Matching EVALUA class(es) | Share |
  |---|---|---|---|
  | ALTO | 15,495 | Alto or Muy alto | 84.4 % |
  | MEDIO | 9,745 | Medio | 35.7 % (40.9 % Alto or Muy alto) |
  | BAJO | 29,164 | Bajo or Muy bajo | 33.9 % (39.5 % Medio) |
  | POPULAR | 16,423 | Bajo or Muy bajo | 47.3 % (25.2 % Alto or Muy alto) |

  Computed via `datastore_search_sql` joining [consumo-agua](https://datos.cdmx.gob.mx/dataset/consumo-agua), [coloniascdmx](https://datos.cdmx.gob.mx/dataset/coloniascdmx) and the [IDS 2020 UT resource](https://datos.cdmx.gob.mx/dataset/indice-de-desarrollo-social-de-la-ciudad-de-mexico-2020).

### Inferences
- The SACMEX index is a 2009-vintage fiscal manzana classification, while IDS 2020 is a census-based NBI measure. Their weak concordance below "ALTO" is expected and gives a ready validation subsection. A manzana-level comparison (SACMEX lat/lon → `ids_2020_mz` polygon → `E_IDS_V`) would be stronger and is medium effort: a point-in-polygon on about 24k manzana points per bimester.
- Join recipe that needs no download (the API accepts multi-table SQL): `consumo c JOIN coloniascdmx i ON i.nombre=c.colonia AND i.alcaldia=c.alcaldia JOIN ids_ut u ON u.cve_ut=i.cve_col`. Resource IDs: `2263bf74-c0ed-4e7c-bb9c-73f0624ac1a9`, `03368e1e-f05e-4bea-ac17-58fc650f6fee` and `0b408748-2a1f-4c3c-844f-72fb6dff598d`.
- The IDS sub-index `ids_csj` (sanitary adequacy: water, drainage, toilet) is the dimension most directly related to water and is worth modelling as its own measure.

### Gaps
- I could not verify the original Gaceta (Dec 2009) manzana classification table or whether it is machine-readable.
- I did not compute a manzana-level IDS concordance or a correlation with consumption.
- I could not confirm whether EVALUA published an IDS later than 2020.

## Q4. Water-incident reports (fugas, falta de agua, 311/Locatel), tandeo, pipas and other water datasets: URLs, grain and 2019 coverage

### Takeaway
The highest-value addition is SACMEX "Reportes de agua – Histórico 2018–2021". It has daily point reports with IECM 2019 colonia labels, and 39,685 "Falta de agua" reports fall in Jan–Jun 2019, the same window as the consumption data. It is easy to add as a second fact table. The 2022–2024 reports and Locatel 0311 extend the time series but need spatial joins and stop in early 2024. For tandeo, the 2019 IPDP colonia layer matches the period exactly; later years exist only as Gaceta PDFs. **No open pipa-delivery dataset exists**, only the locations of SACMEX truck-filling points ("garzas"). There is also no open laboratory water-quality data.

### Cited Findings
#### Master inventory

Feasibility ratings are for integration within 3 weeks.

| # | Dataset (publisher) | URL | Format | Temporal coverage (2019?) | Grain | Join key to DW | Data vintage / status | Feasibility |
|---|---|---|---|---|---|---|---|---|
| 1 | Reportes de agua – Histórico 2018–2021 (SACMEX) | [dataset](https://datos.cdmx.gob.mx/dataset/reportes-de-agua); [CSV 32 MB](https://datos.cdmx.gob.mx/dataset/57ffc13a-7207-4b69-a9a9-2fef3fce6331/resource/65a6b1a6-5d6e-49b9-aeed-ca7b22e8de03/download/65a6b1a6-5d6e-49b9-aeed-ca7b22e8de03.csv) | CSV + datastore | 2018-01-01 → 2021-12-31, 254,730 rows. Yes: 39,685 rows Jan–Jun 2019 | Point report per day | `colonia_datos_abiertos` + `alcaldia` (IECM 2019 labels), lat/lon, date → bimester | Frozen historical file | **Easy** |
| 2 | Reportes de incidentes de agua 2022–2024 (SACMEX) | [CSV 52.7 MB](https://datos.cdmx.gob.mx/dataset/57ffc13a-7207-4b69-a9a9-2fef3fce6331/resource/a8069e94-c7cb-45d7-8166-561e80884422/download/a8069e94-c7cb-45d7-8166-561e80884422.csv) | CSV + datastore | 2022-01-01 → 2024-02-01, 313,756 rows (only 13 in Feb 2024). No 2019 | Point incident with time | lat/lon (313,739 rows) → spatial join; `colonia_catalogo` uses the ADIP catalogue | Stale since early 2024 | Medium |
| 3 | Solicitudes *0311 Locatel (ADIP) | [dataset](https://datos.cdmx.gob.mx/dataset/0311); 2019 CSV: [archivo](https://archivo.datos.cdmx.gob.mx/suac/locatel0311-2019.csv) | CSV + datastore | 2019 (Jun–Dec), 2020, 2021, 2022, 2023, 2024 (Jan–Feb). Overlap with the consumption window is June 2019 only | Request | 2019: `colonia_datos` (IECM labels); 2023+: `colonia_catalogo` (ADIP); partial lat/lon | Stale since Feb 2024; 2019–2022 files on archivo.datos.cdmx.gob.mx | Medium |
| 4 | Colonias con distribución de agua por tandeo 2019 (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/colonias-con-distribucion-de-agua-por-tandeo-2019); [SHP](https://datos.cdmx.gob.mx/dataset/cba78780-cdf0-464c-a9c2-3078c0fdf7f1/resource/33808cea-fa25-45db-becd-43d380d65e3a/download/33808cea-fa25-45db-becd-43d380d65e3a.zip) | SHP (1.4 MB) + dictionary CSV | 2019. **Yes** | Colonia polygon | `NOMBRE` + `DELEGACIO`, or polygon overlay | 2019 | Easy–medium |
| 5 | Annual tandeo resolution, Gaceta Oficial (SACMEX/SEGIAGUA) | press: [Expansión 2025](https://politica.expansion.mx/cdmx/2025/03/07/colonias-cdmx-agua-por-tandeo-2025) | PDF lists | 2012 onward; 2025 list = 284 colonias in 10 alcaldías | Colonia name list | Name + alcaldía | Annual | Medium (PDF) |
| 6 | Garzas SACMEX (truck-filling points) (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/garzas-hidraulicas) | SHP (11 KB) | Undated | Point | Spatial; `COLONIA` field (IECM) | n/a | Medium (distance feature) |
| 7 | Histórico de fugas de agua 2007–2015 (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/historico-fuas-2007-2015) | SHP (672 KB) | 2007–2015. No 2019 | Point | `NOMBRE` (colonia), `ALCALDIA`, `ANO`, `DIAM_PULG` | Frozen | Medium |
| 8 | Registro Único de Situaciones de Emergencia (SGIRPC) | [dataset](https://datos.cdmx.gob.mx/dataset/registro-unico-de-situaciones-de-emergencia) | CSV 19 MB + SHP | 2018–2020, 31,589 rows (10,807 in 2019). Yes | Point incident | lat/lon, colonia (47 % name match) | Frozen | Medium |
| 9 | Presencia de encharcamientos 2000–2017 (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/presencia-de-encharcamientos-del-ano-2000-al-2017-en-la-ciudad-de-mexico) | SHP | 2000–2017. No 2019 | Point | `COLONIA` (IECM), `year`, `FECH_REP` | Frozen | Easy–medium |
| 10 | SIEG Incidencia de encharcamientos 2018–2023 (IPDP) | [layer](https://sieg.cdmx.gob.mx/layers/geonode%3Aencharcamientos) | WFS | 2018–2023 aggregated | H3 hexagons, 1,893 (`NUMPOINTS`) | Spatial | Published 2025-10-07 | Medium |
| 11 | Atlas de riesgo – Inundaciones / Precipitación (SGIRPC) | [inundaciones](https://datos.cdmx.gob.mx/dataset/atlas-de-riesgo-inundaciones); [precipitación](https://datos.cdmx.gob.mx/dataset/atlas-de-riesgo-precipitacion) | CSV (15.8 / 15.5 MB) + SHP | "SPCGIR 2019" hazard | AGEB (`cvegeo`), 4,908 polygons | Spatial or AGEB | 2019 edition | Medium |
| 12 | Cobertura de infraestructura de agua potable (m/hab) (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/cobertura-de-infraestructura-de-agua-potable-m-hab) | SHP/GeoJSON | Undated (uses pop 2010) | Colonia | `cve_col` (IECM) | n/a | **Easy** |
| 13 | Factibilidad hídrica (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/factibilidad-hidrica) | SHP/GeoJSON | Undated | Colonia | Name + alcaldía | n/a | Easy–medium |
| 14 | Pozos de agua potable ZMVM (PAI) (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/pozos-de-agua-potable-en-zona-metropolitana-del-valle-de-mexico) | SHP (14 KB) | Undated | Point (`LAYER` = well type) | Spatial | n/a | Medium |
| 15 | Network context: Sistema Lerma, Ramales, Macrocircuito, Cutzamala structures, Acueducto Chapultepec, Cárcamo, Tanques de agua tratada (IPDP) | [Lerma](https://datos.cdmx.gob.mx/dataset/sistema-lerma-red-de-agua-potable), [Macrocircuito](https://datos.cdmx.gob.mx/dataset/macrocircuito-zmvm), [Tanques](https://datos.cdmx.gob.mx/dataset/tanques-de-almacenamiento-de-agua-tratada) | SHP/GeoJSON | Undated | Line/point | Spatial | n/a | Low value |
| 16 | SCALL rainwater harvesting systems (SEDEMA) | [dataset](https://datos.cdmx.gob.mx/dataset/scall) | CSV per year + SHP/GeoJSON | 2019 (10,003 rows; first record 2019-07-24), 2020, 2021, 2022, 2024 (10,265) | Household installation (point) | lat/lon; colonia names only 13 % match | Ends 2024 | Medium |
| 17 | Contaminación de agua (density of PAOT complaints) (IPDP) | [dataset](https://datos.cdmx.gob.mx/dataset/contaminacion-de-agua-en-la-ciudad-de-mexico) | SHP/GeoJSON | Undated | Density polygons (`GRIDCODE` 0–2) | Spatial | n/a | Low |
| 18 | Art. 172 Código Fiscal tariff and subsidy tables (SAF) | [PDF](https://transparencia.finanzas.cdmx.gob.mx/repositorio/public/upload/repositorio/Tesoreria/123/b/Criterio_9/123_XV_Derechos_por_el_suministro_de_%20agua_2024.pdf) | PDF | Year of tariffs as in the document (2019 schedule not checked) | Manzana class × consumption bracket | `indice_des` + `consumo_total` bracket | n/a | Easy (small reference table) |
| 19 | "Agua en tu colonia" supply viewer (SACMEX/SEGIAGUA) | [site](https://aguaentucolonia.sacmex.cdmx.gob.mx/) | Web app (undocumented API `/api/v1`) | Current status only | Colonia | n/a | API reset the connection for scripted requests | Hard / not verified |

#### Supporting detail

- **Report categories, 2018–2021 file.** 2018–2020 contain only "Falta de agua" (2018: 67,799; 2019: 69,378; 2020: 33,559). "Fuga" (33,018) and "Mala calidad" (843) appear only in 2021. Monthly falta-de-agua counts, Jan–Jun 2019: 6,084, 6,368, 9,525, 6,356, 7,000 and 4,352. Of the Jan–Jun 2019 rows, 39,066 of 39,685 (98.4 %) join exactly to IECM 2019 by name. The field `quien_atiende` holds the SACMEX operating zone (e.g., "Centro Pascua", "Oriente") — [Reportes de agua](https://datos.cdmx.gob.mx/dataset/reportes-de-agua)
- **Report categories, 2022–2024 file.**
  - Agua Potable: Falta de agua 173,395; Fuga 105,220; Mala calidad 3,132; Mal uso 1,306.
  - Drenaje: Drenaje obstruido 14,827; Brote en aguas negras 4,823; Encharcamiento 3,109; Socavón 563.
  - Agua Tratada: Fuga 402.
  - Intake channel: 246,292 by call centre and 33,126 via Twitter.
  - [Reportes de agua](https://datos.cdmx.gob.mx/dataset/reportes-de-agua)
- **Locatel 0311, water themes.**
  - 2019: FALTA DE AGUA 13,885; FUGA DE AGUA 12,698; DESAZOLVE 10,079; COLADERA/ALCANTARILLA 3,844; MANTENIMIENTO DRENAJE 1,976; AGUA POTABLE Y SERVICIOS HIDRÁULICOS 1,972.
  - 2023: FALTA DE AGUA 62,019; FUGA DE AGUA 25,060.
  - Geocoded share: 111,393 of 215,262 in 2019 and 216,520 of 569,362 in 2023.
  - No theme containing "PIPA" exists in 2019, 2020, 2023 or 2024.
  - Row counts: 2020 363,065; 2021 561,313; 2022 500,940; 2024 113,147 (Jan–Feb).
  - [Solicitudes *0311](https://datos.cdmx.gob.mx/dataset/0311)
- **RUSE water-related incidents, 2018–2020.** By incident: "EN EL SERVICIO DE AGUA POTABLE" 1,004; "ENCHARCAMIENTO" 603; "INUNDACION PLUVIAL" 368. By taxonomy: INUNDACION 733; LLUVIA TORRENCIAL 1,174 — [RUSE](https://datos.cdmx.gob.mx/dataset/registro-unico-de-situaciones-de-emergencia)
- **Tandeo legal basis.** Art. 172 applies a fixed fee to domestic connections whose colonia appears "en la lista anual publicada en la Gaceta Oficial … que cataloga el suministro de agua como servicio por tandeo" — [SAF Art. 172 PDF](https://transparencia.finanzas.cdmx.gob.mx/repositorio/public/upload/repositorio/Tesoreria/123/b/Criterio_9/123_XV_Derechos_por_el_suministro_de_%20agua_2024.pdf). The Jan 2025 list had 284 colonias (Tlalpan 94, Iztapalapa 58) — [Expansión](https://politica.expansion.mx/cdmx/2025/03/07/colonias-cdmx-agua-por-tandeo-2025); [N+](https://www.nmas.com.mx/ciudad-de-mexico/corte-agua-cdmx-marzo-2025-lista-completa-colonias-alcaldias-habra-tandeo-sacmex/)
- **Pipas.** In May 2023 INFOCDMX recommended that the water authority proactively publish "Programas de abastecimiento por tanques pipa, padrón, cobertura, requisitos, volúmenes…" and "Calidad y monitoreo del agua". The recommendation implies none of this was open data — [INFOCDMX, Reporte Especial de Apertura 1/2023, pp. 38–40](https://infocdmx.org.mx/images/biblioteca/2023/Reporte_Especial_de_Apertura_1_%202023_Agua_%20pasa_por_mi_casa_La_transparencia_de_la_gestion_del_agua_en_la_CDMX.pdf). Free pipas are requested by phone through Locatel or the authority — [UnoTV](https://www.unotv.com/estados/ciudad-de-mexico/agua-por-tandeo-en-cdmx-lista-de-94-colonias-afectadas-en-tlalpan-durante-junio/)
- **Agua en tu colonia.** SACMEX launched the site on 16 Nov 2023 — [SACMEX bulletin 313](https://sacmex.cdmx.gob.mx/storage/app/media/comunicacion/313-boletin-sacmex-20dic23-sitio-agua-en-tu-colonia.pdf). Its JavaScript calls `https://aguaentucolonia.sacmex.cdmx.gob.mx/api/v1` with `/settlements/getWellsBySettlementId/{id}` and `/samples/{id}`; the scripted request was reset (curl error 56) — [site](https://aguaentucolonia.sacmex.cdmx.gob.mx/)
- **Removed or dead sources.**
  - dev-sieg.cdmx.gob.mx (old IPDP GeoNode with `pozos_sacmex_v2`, `consumo_total_sacmex`, `consumo_hab_prom_agua_col`) no longer resolves in DNS (`getaddrinfo ENOTFOUND`). Production sieg.cdmx.gob.mx is up, with 162 layers, but none for tandeo, SACMEX consumption or wells — [SIEG layer API](https://sieg.cdmx.gob.mx/api/layers/?limit=1000)
  - Old ODS `/explore/dataset/...` URLs were retired around Oct 2022, when the Wayback Machine shows 302 redirects.
- **Peer-reviewed use of these data.**
  - The CDMX consumption/SACMEX data appear in [Medina-Rivas et al. 2022, Water Resources and Economics 40:100210](https://doi.org/10.1016/j.wre.2022.100210) (manzana-level domestic consumption inequality; exact period not verified).
  - [Hernández-Vázquez, Luna-Sánchez, Hurtado-Perez et al. 2025, LNCS W2GIS, pp. 123–137](https://doi.org/10.1007/978-3-032-01723-9_9). According to a search snippet, it uses "SACMEX, INEGI and DENUE datasets fused in a GIS"; I did not read the text.
  - Subsidy inequality: [Morales-Novelo et al. 2018, Water 10(8):1023](https://doi.org/10.3390/w10081023).

### Inferences
- **Suggested about-40 % extension in 3 weeks:**
  - (i) `fact_reporte_agua` from the 2018–2021 file: daily grain, rolled up to bimester × colonia, and joined to consumption for Jan–Jun 2019, plus a 2018–2021 time dimension.
  - (ii) `dim_colonia` from IECM 2019 polygons, carrying the IPDP 2019 attributes: tandeo 2019 flag, infrastructure coverage and average leaks, dwellings, factibilidad hídrica.
  - (iii) IDS 2020 (unidad territorial, and manzana via SIEG WFS) as a validation dimension.
  - (iv) An Art. 172 tariff/subsidy reference table, which turns m³ into pesos and subsidy per class.
  - All four are key-based or simple spatial joins on open, CC-BY data.
- **Analyses this enables:** shortage reports per 1,000 dwellings versus consumption per dwelling; tandeo colonias versus consumption; and index concordance. These can become new SPARQL competency questions for the knowledge graph.
- **Spatial-only sources** (2022–2024 reports, 0311 2023+, RUSE, SCALL, garzas, pozos) are medium effort. They add temporal or contextual depth but no overlap with the 2019 consumption window.

### Gaps
- No open dataset was found for pipa deliveries, SACMEX water-quality lab results, supply hours (historical), the padrón de tomas, or rainfall time series at CDMX level. REDMET has temperature, humidity and wind only; precipitation in the REDDA wet-deposition data was not verified.
- The value distribution of `tnd_2019` and the exact number of tandeo colonias in 2019 were not checked (SHP not downloaded).
- PAOT complaint themes related to water were not filtered.

## Q5. How well do colonia names in each dataset match SACMEX labels (uppercase, no accents, Ñ dropped)?

### Takeaway
Only datasets built on the IECM 2019 catalogue match SACMEX labels at about 99 % or better. Datasets from 2022 onward (ADIP catalogue) and free-text sources match only 13–47 %, even after normalisation, so coordinates should be the join path for them.

### Cited Findings
Method: SACMEX distinct (alcaldía, colonia) pairs = 1,551 after normalisation (1,495 distinct names). Normalisation: uppercase, accents removed, Ñ deleted (mimicking SACMEX), punctuation collapsed; alcaldía names harmonised. Computed via `datastore_search_sql` on each resource listed in Q2–Q4.

| Source (field) | Normalised (alcaldía, colonia) pairs matched | Share of SACMEX rows covered | Raw exact name matches |
|---|---|---|---|
| IECM 2019 `coloniascdmx` (`nombre`) | 1,550/1,551 (99.9 %) | 99.7 % | 1,494/1,495 |
| Reportes 2018–21 (`colonia_datos_abiertos`) | 1,541/1,551 (99.4 %) | 99.9 % | 1,485 |
| Locatel 0311 2019 (`colonia_datos`) | 1,539/1,551 (99.2 %) | 99.9 % | 1,483 |
| SAF cadastre (`colonia`) | 100 % of pairs tested (Cuauhtémoc, Iztapalapa) | n/a | 100 % |
| EVALUA IDS 2020 UT (`nombre_ut`) | 1,500/1,551 (96.7 %) | 97.4 % | Ñ shown as "?"; use `cve_ut` |
| RUSE (`colonia`) | 732/1,551 (47.2 %) | 50.7 % | n/a |
| Reportes 2018–21 (`colonia_registro_sacmex`, free text) | 628/1,551 (40.5 %) | 41.4 % | n/a |
| Reportes 2022–24 (`colonia_catalogo`, ADIP) | 615/1,551 (39.7 %) | 41.2 % | n/a |
| Locatel 0311 2023 (`colonia_catalogo`, ADIP) | 612/1,551 (39.5 %) | 41.2 % | n/a |
| PAOT (`colonia`) | 603/1,551 (38.9 %) | 40.6 % | n/a |
| SCALL 2024 (`scall_col`) | 203/1,551 (13.1 %) | 14.3 % | Partly reflects limited coverage (463 pairs) |

Additional notes:
- SACMEX has 9 odd labels, e.g. "ESTADO DE HIDALGO_", "SELENE 1a SECC" and "ALVARO OBREGON_(FRACC)". They also match IECM 2019 exactly, which confirms the verbatim copy — [Consumo de agua](https://datos.cdmx.gob.mx/dataset/consumo-agua); [coloniascdmx](https://datos.cdmx.gob.mx/dataset/coloniascdmx)
- Typical mismatches with the ADIP catalogue are IECM sub-colonias (e.g., "CENTRO IV", "ROMA SUR II", "LINDAVISTA I") against merged ADIP names ("Centro", "Roma Sur") — [Reportes de agua](https://datos.cdmx.gob.mx/dataset/reportes-de-agua)

### Inferences
- Use exact (alcaldía, colonia) joins to IECM 2019 for SACMEX, 2018–21 reports, 0311-2019 and the cadastre. Use `cve_ut`/`cve_col` keys for IDS and the IPDP layers. Use point-in-polygon against IECM 2019 polygons for everything from 2022 on and for RUSE and SCALL. Fuzzy name matching is not needed.

### Gaps
- I did not compute match rates for the SHP-only IPDP name-keyed layers (tandeo 2019, factibilidad hídrica, encharcamientos 2000–2017).

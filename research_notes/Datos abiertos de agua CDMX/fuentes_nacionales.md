# Federal/national open datasets joinable to the SACMEX 2019 water-consumption warehouse (CDMX)

Scope: national (federal) open data that covers Ciudad de México (entidad 09) at alcaldía, AGEB, manzana or colonia grain, to (a) compute per-capita / per-household consumption, (b) explain consumption with socioeconomic variables, (c) add hydrological/climate context. URL checks were run on 18 Oct 2026 with `curl` (HTTP status and content type, partial range requests only) unless stated otherwise.

Warehouse facts used for join design (from the project's own file, not an external source):
- The raw CSV has columns `fecha_referencia, anio, bimestre, consumo_total_mixto, consumo_prom_dom, consumo_total_dom, consumo_prom_mixto, consumo_total, consumo_prom, consumo_prom_no_dom, consumo_total_no_dom, indice_des, colonia, alcaldia, latitud, longitud`. There is **no INEGI key (CVEGEO) and no manzana ID**, only alcaldía/colonia names and lat/lon — [local file warehouse/data/consumo_agua_historico_2019.csv](C:/Users/gabri/Documents/GitHub%20Desktop/Data_Warehouse_static/warehouse/data/consumo_agua_historico_2019.csv)
- 71,102 data rows in the raw CSV (the paper reports 70,886 fact rows after ETL); 1,554 alcaldía–colonia pairs in raw (paper: 1,553); ~22,930 distinct coordinate points in bimester 1, 22,835 in bimester 2, 22,758 in bimester 3, with 22,747 points present in all three bimesters; ~400 points per bimester carry more than one row (duplicates/different `indice_des`); latitude 19.136–19.579, longitude −99.338 to −98.950 (i.e., decimal-degree WGS84-style coordinates inside CDMX) — [local file](C:/Users/gabri/Documents/GitHub%20Desktop/Data_Warehouse_static/warehouse/data/consumo_agua_historico_2019.csv)

---

## 1. INEGI Censo de Población y Vivienda 2020 (ITER, AGEB y manzana urbana) + Marco Geoestadístico: population, households, piped water; how to join SACMEX coordinates to INEGI manzanas

### Takeaway
This is the single most valuable addition and is fully feasible in 3 weeks: the CDMX "Principales resultados por AGEB y manzana urbana" CSV gives POBTOT, TOTHOG, TVIVPARHAB/OCUPVIVPAR and piped-water/tinaco/cisterna/drenaje counts per manzana, and the Marco Geoestadístico 2020 CDMX shapefile gives the manzana polygons with the 16-character CVEGEO, so SACMEX points can be assigned to manzanas by a point-in-polygon join (reprojected to EPSG:6372) and per-capita / per-household consumption computed directly.

### Cited Findings
**Inventory entries (all verified reachable 18 Oct 2026):**

| Dataset | Exact URL | Publisher | Format | Licence | Year | Grain | Join key | 3-wk feasibility |
|---|---|---|---|---|---|---|---|---|
| Principales resultados por AGEB y manzana urbana, CDMX | https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/ageb_manzana/ageb_mza_urbana_09_cpv2020_csv.zip | INEGI | CSV in ZIP | Términos de Libre Uso de la Información del INEGI | 2020 (census) | entidad → municipio/alcaldía → localidad → AGEB → manzana (urban) | ENTIDAD(2)+MUN(3)+LOC(4)+AGEB(4)+MZA(3) = manzana CVEGEO | **High** (core) |
| Data dictionary of that file | https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf | INEGI | PDF | same | 2021 | — | — | — |
| ITER (Principales resultados por localidad), CDMX | https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_09_cpv2020_csv.zip | INEGI | CSV in ZIP | same | 2020 | entidad, municipio/alcaldía, localidad | ENTIDAD+MUN(+LOC) | **High** (alcaldía totals) |
| Marco Geoestadístico, Censo 2020 – Ciudad de México | https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463807469/09_ciudaddemexico.zip (product page: https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=889463807469) | INEGI | Shapefile in ZIP | same | 2020 | entidad, municipio, localidad, AGEB, manzana polygons | CVEGEO | **High** (needed for spatial join) |

- All four URLs above answered HTTP 206 with `application/x-zip-compressed` (ZIPs) or `application/pdf` (dictionary) on 18 Oct 2026 — [INEGI AGEB-manzana CSV](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/ageb_manzana/ageb_mza_urbana_09_cpv2020_csv.zip); [ITER CDMX](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_09_cpv2020_csv.zip); [Marco Geoestadístico 2020 CDMX](https://www.inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/marcogeo/889463807469/09_ciudaddemexico.zip)
- Content of the AGEB-manzana product: 222 indicators for the 64,313 AGEB and 215 indicators for the "more than one million" urban manzanas nationally; themes include population, households and dwelling services (energía eléctrica, agua entubada, sanitario, drenaje) and goods in the dwelling — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- File structure: the database starts with the entidad total, then each municipio total, then each urban localidad with the accumulated AGEB totals, then AGEB and manzana rows (so total rows must be filtered by MZA/AGEB codes before joining) — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Geographic ID fields and lengths: ENTIDAD (2, "00" = national total), NOM_ENT, MUN (3, "000…570"), NOM_MUN ("nombre oficial del municipio o demarcación territorial en el caso de la Ciudad de México"), LOC (4), NOM_LOC, AGEB (4, digits or A–P), MZA (3, "001…999") — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Denominator variables available per manzana: POBTOT (población total), TOTHOG (hogares censales), VIVPAR_HAB, TVIVPARHAB (total viviendas particulares habitadas), VIVPARH_CV, OCUPVIVPAR (ocupantes en viviendas particulares habitadas), PROM_OCUP (promedio de ocupantes) — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Water-access variables per manzana: VPH_AGUADV (dwellings with piped water inside the dwelling), VPH_AEASP (piped water supplied by the public service), VPH_AGUAFV (dwellings without piped water in the dwelling's premises), VPH_TINACO (with rooftop tank), VPH_CISTER (with cistern/aljibe), VPH_DRENAJ (with drainage) — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Socioeconomic covariates in the same file: GRAPROES (average years of schooling), PEA, POCUPADA, PSINDER (population without health-service affiliation), plus goods-in-dwelling indicators — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Confidentiality: at municipio, localidad and AGEB level any indicator with fewer than 3 units is shown with an asterisk, except POBTOT, VIVTOT and TVIVHAB; at manzana level, blocks with only one or two inhabited dwellings show only POBTOT and VIVTOT and asterisks elsewhere — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- Licence: INEGI's "Términos de Libre Uso de la Información del INEGI" allow copying, redistribution, adaptation, extraction and commercial use, provided INEGI is credited as author (citing product and update date where feasible) and any transformation is disclosed without implying INEGI endorsement — [INEGI Términos de libre uso](https://www.inegi.org.mx/inegi/terminos.html)
- Projection: INEGI's Lambert Conformal Conic on ITRF2008 corresponds to EPSG:6372 "Mexico ITRF2008 / LCC" (metres), which replaced EPSG:6362 (ITRF92) — [epsg.io 6372](https://epsg.io/6372); INEGI/CONAPO 2020 metropolitan maps state Lambert projection with "Datum ITRF08 época 2010.0" and cite the Marco Geoestadístico 2020 as source — [Metrópolis de México 2020, Parte 21](https://www.gob.mx/cms/uploads/attachment/file/864738/METRO_POLIS_DE_ME_XICO_2020_18102023_Parte21.pdf)

### Inferences
- **Spatial join recipe (point → manzana).** (1) Load SACMEX points as EPSG:4326 (lat/lon are decimal degrees in CDMX range). (2) Reproject to EPSG:6372 to match the Marco Geoestadístico. (3) `geopandas.sjoin(points, manzanas, predicate="within")` against the manzana layer of `09_ciudaddemexico.zip` to get the 16-char manzana CVEGEO. (4) For points that fall on streets/medians (manzana polygons exclude street space), use `sjoin_nearest(..., max_distance≈20–30 m)` and flag them; report the match rate as a data-quality metric in the paper. (5) Build the same 16-char key in the census CSV as `ENTIDAD+MUN+LOC+AGEB+MZA` (keep leading zeros: read as strings) and join. (6) Derive CVEGEO_AGEB = first 13 chars for AGEB-level joins (CONAPO/CONEVAL indices) and CVE_MUN = chars 3–5 for alcaldía joins.
- Because ~22.9k SACMEX points recur across all three bimesters, the join is done once on a point dimension (a new `dim_manzana_inegi` keyed by CVEGEO) and reused for all facts; this fits the existing star schema as a new conformed geographic dimension and in the KG as a GeoSPARQL feature with an `owl:sameAs`/`skos:exactMatch`-style link to the INEGI manzana.
- Several SACMEX rows share a coordinate but carry different `indice_des` and different consumption values (e.g., two rows at the same point in "7 DE NOVIEMBRE", GAM); these must be summed (or de-duplicated) per point and bimester before dividing by POBTOT/TOTHOG, otherwise per-capita figures double count. Whether the SACMEX coordinate is a manzana centroid or a representative point is not documented in what was reviewed — treat the manzana assignment as an approximation and validate on a sample.
- Per-capita indicator: `consumo_total_dom (bimester) / POBTOT` or, better, `/ OCUPVIVPAR` (residents of private dwellings) since domestic consumption relates to households; per-household: `/ TOTHOG` or `/ TVIVPARHAB`. Express also as litres/person/day (bimester ≈ 60/61 days) to compare with the usual norms — but units of SACMEX consumption (m³) must be confirmed from SACMEX metadata.
- Manzanas with 1–2 dwellings have suppressed covariates; aggregate to AGEB for the explanatory models (AGEB values are less suppressed), keep manzana only for the denominator (POBTOT/VIVTOT are always published).
- Use the 2020 Marco Geoestadístico (not a 2019 or 2023 version) so polygon codes match the 2020 census tables exactly; mixing framework versions can break CVEGEO matches when manzanas are split/renumbered.

### Gaps
- The number of urban manzanas and AGEB for CDMX in the 2020 files was not counted (would require downloading the ZIP); needed to report what share of INEGI manzanas the ~22.9k SACMEX points cover.
- The exact layer names inside `09_ciudaddemexico.zip` (e.g., manzana layer file name) and its `.prj` were not inspected (no download was made); EPSG:6372 is inferred from INEGI's documented Lambert/ITRF2008 projection, not read from the file.
- Census reference date (March 2020) and its exact wording were not fetched from an INEGI page in this session.

---

## 2. Other INEGI products: Censo Nacional de Gobiernos Municipales y Demarcaciones Territoriales (agua potable y saneamiento), ENIGH water expenditure, Encuesta Intercensal

### Takeaway
None of these give sub-alcaldía grain: the CNGMD water module is answered by municipal/demarcación governments (in CDMX the operator is SACMEX, so alcaldía answers add little) and refers to 2018; ENIGH 2018 and 2020 (verified CSV downloads) bracket 2019 and include household water expenditure, but are representative only down to entidad, so they serve as city-level context or validation, not as a join; the 2015 Intercensal is superseded by the 2020 census.

### Cited Findings
| Dataset | Exact URL | Publisher | Format | Licence | Year | Grain | Join key | 3-wk feasibility |
|---|---|---|---|---|---|---|---|---|
| ENIGH 2018 (nueva serie) datos abiertos | https://www.inegi.org.mx/contenidos/programas/enigh/nc/2018/datosabiertos/conjunto_de_datos_enigh_2018_ns_csv.zip | INEGI | CSV in ZIP | INEGI libre uso | 2018 | household microdata; inference at entidad (see gap) | `entidad`/`ubica_geo` → CDMX = 09 | **Medium-Low** (context only) |
| ENIGH 2020 (nueva serie) datos abiertos | https://www.inegi.org.mx/contenidos/programas/enigh/nc/2020/datosabiertos/conjunto_de_datos_enigh_ns_2020_csv.zip | INEGI | CSV in ZIP | INEGI libre uso | 2020 | idem | idem | **Medium-Low** |
| CNGMD 2019, módulo agua potable y saneamiento (questionnaire) | https://www.inegi.org.mx/contenidos/programas/cngmd/2019/doc/cngmd_2019_m5.pdf ; program page https://www.inegi.org.mx/programas/cngmd/2019/ | INEGI | PDF + tabulados/datos abiertos on program page | INEGI libre uso | survey 2019, reference year 2018 | municipio / demarcación territorial | CVE_ENT+CVE_MUN | **Low** for CDMX |
| Encuesta Intercensal 2015 | https://www.inegi.org.mx/programas/intercensal/2015/ | INEGI | various | INEGI libre uso | 2015 | municipio (sample) | CVE_MUN | **Low** (superseded) |

- ENIGH 2018 and 2020 open-data ZIPs answered HTTP 206 `application/x-zip-compressed` on 18 Oct 2026 — [ENIGH 2018](https://www.inegi.org.mx/contenidos/programas/enigh/nc/2018/datosabiertos/conjunto_de_datos_enigh_2018_ns_csv.zip); [ENIGH 2020](https://www.inegi.org.mx/contenidos/programas/enigh/nc/2020/datosabiertos/conjunto_de_datos_enigh_ns_2020_csv.zip)
- ENIGH's household summary file has an `agua` variable = household water expenditure (quarterly); in ENIGH 2005 it was built from expenditure code G007 of the GASTOS file — [IHSN data catalog, ENIGH 2005 `agua`](https://datacatalog.ihsn.org/catalog/3962/variable/F1/V79?name=agua)
- INEGI warns that the ENIGH 2024 "nueva serie" constructs variables differently from earlier ENIGH editions, so names/definitions must be checked per edition — [INEGI ENIGH 2024 document](https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/889463924487.pdf)
- CNGMD 2019 covers government, public security, municipal justice, potable water and sanitation, and solid-waste functions; figures refer to the close of 2018 (e.g., 2,429 municipios or demarcaciones provided potable water from the public network, 1,939 drainage and sewerage, 787 wastewater treatment) — [INEGI press release 115/20, CNGMD 2019](https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2020/EstSegPub/DmTerrCDMX2019.pdf)
- The CNGMD 2019 water module questionnaire (Module 5) PDF is online (HTTP 206 `application/pdf` on 18 Oct 2026) — [cngmd_2019_m5.pdf](https://www.inegi.org.mx/contenidos/programas/cngmd/2019/doc/cngmd_2019_m5.pdf); search results describe Module 5 topics as water capture, potabilisation plants, drainage, wastewater treatment — [INEGI CNGMD 2019 m5](https://www.inegi.org.mx/contenidos/programas/cngmd/2019/doc/cngmd_2019_m5.pdf)
- A guessed direct datos-abiertos URL (`.../cngmd/2019/datosabiertos/cngmd2019_agua_potable.zip`) returned an HTML page, not a ZIP, so the exact CNGMD water-module file name could not be verified — (status check, 18 Oct 2026)

### Inferences
- ENIGH: use 2018 and 2020 CDMX households (weighted with `factor`) to report the city-level mean/median water expenditure and its distribution by income decile; this lets the article contrast billed/consumed volumes (SACMEX) with what households report paying, and gives an external socioeconomic gradient at city level. It cannot be joined to manzanas/colonias. Averaging 2018 and 2020 is a defensible bracket for 2019, but the 2020 edition was collected during the COVID-19 pandemic (field dates not verified in this session), so prefer 2018 as the primary comparator.
- The ENIGH `viviendas` table likely also contains water-supply items (availability and frequency of supply, tinaco/cisterna); this would support an "intermittent supply" discussion at city level — not verified in this session (see gaps).
- CNGMD for CDMX: alcaldías are not the water operator (SACMEX is the city-level operator), so module-5 records for the 16 demarcaciones are likely sparse or "no aplica"; use, if at all, only as a sentence of institutional context.
- Intercensal 2015 adds nothing the 2020 census does not, except a pre-2019 time point for an interpolation of alcaldía population (2015→2020) — useful only if the authors want to interpolate denominators to mid-2019 at alcaldía level.

### Gaps
- Exact ENIGH "nueva serie" (2018/2020) expenditure code for water and whether `concentradohogar.agua` keeps that name in 2018/2020 was not verified from the 2018/2020 descriptors (INEGI ENIGH program page timed out on fetch).
- The ENIGH water-supply-frequency variable name in the `viviendas` table (e.g., something like `dotac_agua`) could not be confirmed.
- ENIGH's official statistical representativeness statement (entidad-level design) was not fetched in this session.
- Exact CNGMD 2019 datos-abiertos ZIP name for the water module, and whether CDMX demarcaciones answered it, remain unverified.

---

## 3. CONAPO Índice de Marginación 2020 by AGEB (IMU) and by colonia (IMC): download and join keys

### Takeaway
CONAPO's 2020 page lists open downloads for the urban marginalisation index by AGEB (IMU_2020.zip) and — for the first time — by colonia (IMC_2020.zip plus a colonia shapefile imc2020_shp.zip); the AGEB index joins on the 13-character AGEB CVEGEO obtained from the manzana spatial join, and the colonia index is best joined spatially (SACMEX point-in-colonia polygon) rather than by colonia name. This directly answers the paper's limitation that the development-index/consumption association lacks an external socioeconomic measure.

### Cited Findings
| Dataset | Exact URL (as listed on CONAPO page) | Publisher | Format | Licence | Year | Grain | Join key | 3-wk feasibility |
|---|---|---|---|---|---|---|---|---|
| Índice de marginación urbana 2020 (AGEB) | https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Marginacion/IMU_2020.zip | CONAPO | ZIP (database) | See below (non-commercial reproduction with citation) | 2020 | AGEB urbana | AGEB CVEGEO (13 chars) | **High** |
| Índice de marginación urbana por colonia 2020 (database) | https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Colonia/IMC_2020.zip | CONAPO | ZIP (database) | idem | 2020 | colonia | colonia ID of CONAPO framework + spatial join | **Medium** |
| Colonia cartography (shp) | https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Colonia/imc2020_shp.zip | CONAPO | Shapefile in ZIP | idem | 2020 | colonia polygons | point-in-polygon with SACMEX lat/lon | **Medium-High** |
| Índice de marginación municipal 2020 | https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Municipio/IMM_2020.xlsx | CONAPO | XLSX | idem | 2020 | municipio/alcaldía | CVE_MUN (5-char CVE_ENT+CVE_MUN) | High but only 16 units |
| Calculation programs | .../Marginacion/Indice_de_marginacion_por_AGEB_2020.rar ; .../Marginacion/Indice_de_marginacion_urbana_por_colonia_2020.rar | CONAPO | RAR (scripts) | idem | 2020 | — | — | — |

- The CONAPO page "Índices de marginación 2020" (dated 4 Oct 2021) lists the files above, plus entidad (IME_2020.xls), localidad (IML_2020.zip) and municipal files, and PDFs including the urban volume — [CONAPO, Índices de marginación 2020](https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372)
- Status check: `conapo.segob.gob.mx/...` returns HTTP 301 to `https://www.gob.mx/conapo/work/models/CONAPO/Datos_Abiertos/...` (same path), and `www.gob.mx` refused scripted (curl) connections on 18 Oct 2026; download through a normal browser — (status check, 18 Oct 2026); file list confirmed on [CONAPO page](https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372)
- Method: built from 2020 census microdata; DP2 (Pena Trapero distance) method; five marginalisation grades; for 2020 CONAPO added, for the first time, the colonia-level calculation alongside AGEB urbana — [CONAPO IMU 2020 technical note (mirror, Tabasco)](https://tabasco.gob.mx/sites/default/files/users/planeacion_spf/Nota_t_cnica_IMU_2020.pdf); [CONAPO "urbana" PDF](https://www.gob.mx/cms/uploads/attachment/file/828844/urbana.pdf)
- The colonia index uses nine census-based indicators (school attendance, schooling, health-service affiliation, dwelling conditions, internet and mobile phone access) and is distributed as a shapefile, per the CDMX/CentroGeo geoportal metadata record of the layer — [SIEG CDMX metadata, im_colonia](https://www.sieg.cdmx.gob.mx/layers/geonode%3Aim_colonia/pdf_metadata_layer)
- Licence: the CONAPO page carries no Creative Commons-type licence, only the gob.mx footer terms — [CONAPO page](https://www.gob.mx/conapo/documentos/indices-de-marginacion-2020-284372); the "Índices de marginación 2020" publication (June 2023 edition) reportedly allows total or partial reproduction for non-commercial purposes citing the source — [CONAPO, Índices… entidad y municipio, pp. 1–153](https://www.gob.mx/cms/uploads/attachment/file/848423/Indices_Coleccion_280623_entymun-p_ginas-1-153.pdf) (statement taken from a search-result summary; verify in the PDF's legal page)

### Inferences
- **AGEB join (IMU):** after the manzana spatial join (section 1), take `CVEGEO[:13]` = ENT+MUN+LOC+AGEB and join to IMU_2020. Then model consumption per capita ~ IMU (or its components) and compare with SACMEX's 4-level `indice_des`; this gives a concordance test (e.g., cross-tab, Cramér's V or Spearman) of SACMEX's development index against an official, census-based index — directly addressing the stated limitation.
- **Colonia join (IMC):** do a second point-in-polygon of SACMEX points into `imc2020_shp` polygons, then compare the resulting CONAPO colonia with SACMEX's `colonia` name to measure naming agreement; use the spatial match as authoritative. Name-based matching of 1,553 SACMEX colonias against CONAPO colonia names would be slower and error-prone (accents, "U. HAB.", homonyms across alcaldías).
- IMU 2020 and CONEVAL's GRS AGEB 2020 (section 5) are both built from the 2020 census at AGEB level; choose one as the main covariate and the other as a robustness check.
- In the KG, both indices fit the RDF Data Cube as new datasets with `qb:dimension` = AGEB/colonia (GeoSPARQL features) and grade codes as a SKOS concept scheme aligned to SACMEX's 4-level `indice_des` scheme (e.g., `skos:closeMatch`).

### Gaps
- Column names inside IMU_2020.zip and IMC_2020.zip (e.g., the colonia identifier and whether it includes CVE_ENT/CVE_MUN) were not inspected; downloads from gob.mx were blocked to scripts.
- The exact licence wording for CONAPO datasets was not read directly.
- Whether the CONAPO colonia polygons match SACMEX's colonia catalogue (or the CDMX IECM colonia framework) was not established.

---

## 4. CONAGUA / SMN: SINA, Estadísticas del Agua en México, aquifer availability (ZMCM aquifer), Monitor de Sequía, SMN daily stations in CDMX, Sistema Cutzamala storage

### Takeaway
Two CONAGUA products are verified, machine-readable and immediately usable for 2019 context: SMN daily station files (precipitation, evaporation, Tmax, Tmin; e.g., station 09010 "Colonia America", Miguel Hidalgo, data to Oct 2026) and the Monitor de Sequía municipal spreadsheet (joins on municipal key). SINA, the Sistema de Información Hidrológica and the "Estadísticas del Agua" PDFs sit behind bot protection (Incapsula) — they work in a browser but could not be verified by script — and no official machine-readable daily Cutzamala storage series was located; the 2019 aquifer figures for the ZMCM aquifer (0901) also remain unverified.

### Cited Findings
| Dataset | Exact URL | Publisher | Format | Licence | Year | Grain | Join key | 3-wk feasibility |
|---|---|---|---|---|---|---|---|---|
| SMN Base de Datos Climatológica Nacional – daily station records | Pattern: https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/df/dia09XXX.txt (e.g., https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/df/dia09010.txt); station catalogue via KMZ/map at https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica | CONAGUA–SMN | Fixed-text (TSV-like), KMZ catalogue | Not stated on page (federal government data) | daily, 1969→Oct 2026 for 09010 | station (point with lat/lon, municipio) | station lat/lon → nearest station / Thiessen per alcaldía or AGEB; header gives MUNICIPIO | **Medium-High** |
| Monitor de Sequía de México – municipal table | https://smn.conagua.gob.mx/tools/RESOURCES/Monitor%20de%20Sequia%20en%20Mexico/MunicipiosSequia.xlsx (linked from https://smn.conagua.gob.mx/es/climatologia/monitor-de-sequia/monitor-de-sequia-en-mexico) | CONAGUA–SMN | XLSX | Not stated | updated to Oct 2026 | municipio/alcaldía, biweekly/periodic | CVE_ENT+CVE_MUN | **High** (if 2019 columns present) |
| SINA (Sistema Nacional de Información del Agua) | https://sinav30.conagua.gob.mx:8080/ ; publications e.g. https://sina.conagua.gob.mx/publicaciones/EAM_2019.pdf | CONAGUA | web app, PDF | Not stated | various | national / hydrological region / state | entidad, aquifer, region | **Low-Medium** (context) |
| Sistema de Información Hidrológica (dams, hydrometry) | https://sih.conagua.gob.mx/ | CONAGUA | web | Not stated | — | dam / station | dam ID | **Unverified** |
| Disponibilidad de acuíferos (DOF) – acuífero 0901 ZM de la Cd. de México | DOF agreement of 9 Nov 2023 (and earlier 2020 publication) — exact URL not verified | CONAGUA / DOF | PDF | public | 2020/2023 publications | aquifer | aquifer code 0901 ↔ alcaldías by overlay | **Low** (single context value) |

- SMN daily file verified: the header of `dia09010.txt` reads "Base de Datos Climatológica Nacional – Registro diario histórico", emission 09/10/2026, data available to October 2026; station 9010 "COLONIA AMERICA", Ciudad de México, municipio Miguel Hidalgo, status "OPERANDO", Organismo de Cuenca Aguas del Valle de México, lat 19.4125, lon −99.2017, altitude 2271 m; columns FECHA, PRECIP (mm), EVAP (mm), TMAX (°C), TMIN (°C); missing values coded "NULO"; records from 1969-08-01 — [SMN daily file 09010](https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/df/dia09010.txt)
- The station number must be zero-padded in the URL: `dia9010.txt` returns HTTP 500, `dia09010.txt` returns `text/plain` — (status check, 18 Oct 2026, [SMN file](https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/df/dia09010.txt))
- The SMN statistics page offers station data via an interactive map or a KMZ file (Google Earth), covering >5,000 stations of which >2,000 still report; variables: Tmax, Tmin, 24-h precipitation, evaporation, normals; contact ventanillaunica.smn@conagua.gob.mx — [SMN Información estadística climatológica](https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica)
- Monitor de Sequía municipal XLSX verified: HTTP 206, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, 2,150,283 bytes, Last-Modified 6 Oct 2026; it is the only data file linked from the Monitor page — [MunicipiosSequia.xlsx](https://smn.conagua.gob.mx/tools/RESOURCES/Monitor%20de%20Sequia%20en%20Mexico/MunicipiosSequia.xlsx); [Monitor de Sequía en México page](https://smn.conagua.gob.mx/es/climatologia/monitor-de-sequia/monitor-de-sequia-en-mexico)
- `sih.conagua.gob.mx`, `sinav30.conagua.gob.mx:8080` and `sina.conagua.gob.mx/publicaciones/EAM_2019.pdf` answer scripted requests with HTTP 302 + Incapsula cookies (redirect loop); WebFetch on `sih.conagua.gob.mx/presas.html` failed with "too many redirects" — (status checks, 18 Oct 2026)
- A SEMARNAT compendium cites the series as "Estadísticas del Agua en México, Ediciones 2003–2018", so the existence of a 2019 edition was not confirmed — [SEMARNAT DGEIA compendio 2021](https://apps1.semarnat.gob.mx:8443/dgeia/compendio_2021/archivos/01_agua/d3_agua01_12.pdf)
- Aquifer availability: the DOF agreement updating the mean annual availability of Mexico's 653 aquifers was published on 9 Nov 2023, with 286 aquifers in deficit; the Ley de Aguas Nacionales requires review every three years — [ECIJA](https://www.ecija.com/actualidad-insights/disponibilidad-media-anual-de-aguas-subterraneas-en-mexico-reto-para-los-concesionarios-de-aguas-nacionales/)
- For the ZMCM aquifer, the CDMX geoportal states extraction is more than double recharge — [SIEG CDMX map 1329](https://dev-sieg.cdmx.gob.mx/maps/1329); a 139% overexploitation figure circulates without a dated official source — [iAgua blog](https://www.iagua.es/blogs/jose-antonio-rodriguez-tirado/acuiferos-mexico) (not primary; do not cite in the paper)
- Cutzamala: seven dams with total capacity ≈782.5 hm³ (press, citing CONAGUA/OCAVM) — [Posta](https://www.posta.com.mx/cdmx/sistema-cutzamala-alcanza-mas-del-90-de-su-capacidad-y-asi-fue-la-ultima-vez-que-esto-ocurrio/vl2107937); storage figures are released in OCAVM technical reports cited by the press, and press-compiled historical series show gaps (no September figures in 2022 and 2023) — [UnoTV](https://www.unotv.com/nacional/sistema-cutzamala-supera-el-80-de-almacenamiento-hidrico/)

### Inferences
- **Climate (feasible in ~2 days):** list CDMX stations from the KMZ (prefix 09xxx), download `dia09xxx.txt` for those operating in 2019, aggregate PRECIP/TMAX to the three 2019 bimesters, assign to SACMEX points by nearest station or Thiessen polygons (or to alcaldía by the station's MUNICIPIO field). Jan–Jun 2019 is dry season plus the hot spring peak, so a temperature–consumption relation by bimester is a plausible, cheap addition. Check completeness (NULO share) per station before use.
- **Drought (feasible in ~1 day):** join MunicipiosSequia.xlsx to alcaldía by CVE_MUN and report the drought category per alcaldía for each 2019 bimester (supply-side context). Expect little spatial variation inside CDMX; it is mainly a temporal/contextual covariate.
- **Cutzamala / aquifer:** treat as narrative context (one table/figure: 2019 storage trajectory and aquifer status) rather than a joined dimension; extracting numbers manually from CONAGUA reports in a browser is feasible but should be budgeted as manual work and clearly sourced.
- Because CONAGUA sites are bot-protected, the replication package should archive the downloaded files (with retrieval date) rather than rely on scripted retrieval.

### Gaps
- No official, machine-readable daily Cutzamala storage series (CSV/XLSX) was located or verified; whether SIH or SINA expose one could not be checked (bot protection).
- Official 2019-relevant recharge/extraction/availability figures (hm³/yr) for aquifer 0901 were not obtained; the DOF 2020 and 2023 PDFs were not located by URL.
- Whether `MunicipiosSequia.xlsx` contains the full historical series (including 2019 dates) was not checked (file not downloaded).
- The list of CDMX SMN stations operating in 2019 was not compiled.
- Existence of an "Estadísticas del Agua en México 2019" edition is unconfirmed.
- Licence terms for SMN/CONAGUA data were not found on the pages reviewed.

---

## 5. CONEVAL poverty by municipio/alcaldía (and AGEB-level rezago social)

### Takeaway
CONEVAL's municipal poverty 2010–2020 annex and its Grado de Rezago Social (GRS) 2020 by AGEB urbana are still downloadable from coneval.org.mx in Oct 2026 even though CONEVAL was extinguished in July 2025 and its measurement functions moved to INEGI; the municipal file only gives 16 data points for CDMX, so the AGEB-level GRS 2020 is the more useful CONEVAL product for the warehouse.

### Cited Findings
| Dataset | Exact URL | Publisher | Format | Licence | Year | Grain | Join key | 3-wk feasibility |
|---|---|---|---|---|---|---|---|---|
| Pobreza municipal 2010–2020, anexo estadístico | https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip | CONEVAL (now INEGI) | ZIP | not checked | 2020 (and 2010, 2015) | municipio/alcaldía | CVE_ENT+CVE_MUN | **High** (but n=16) |
| Methodology | https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Metodologia_pobreza_municipal_2020.pdf | CONEVAL | PDF | — | 2021 | — | — | — |
| Grado de Rezago Social por AGEB urbana 2020 | https://www.coneval.org.mx/Medicion/Documents/GRS_AGEB_2020/GRS_AGEB_urbana_2020.zip (page: https://www.coneval.org.mx/Medicion/IRS/Paginas/Rezago_social_AGEB_2020.aspx) | CONEVAL | ZIP | not checked | 2020 | AGEB urbana | AGEB CVEGEO (13 chars) | **High** |

- Municipal poverty page lists the 2010–2020 statistical annex ZIP, methodology and presentation PDFs, plus a page of databases/calculation programs and an ArcGIS Hub viewer — [CONEVAL Pobreza a nivel municipio 2010–2020](https://www.coneval.org.mx/Medicion/Paginas/Pobreza-municipio-2010-2020.aspx)
- Status: the annex ZIP answered HTTP 200 `application/x-zip-compressed`, 4,401,534 bytes; the methodology PDF HTTP 200 (778,908 bytes); the municipal page HTTP 200 — (status checks, 18 Oct 2026) [annex ZIP](https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip)
- The GRS AGEB 2020 page (HTTP 200 on 18 Oct 2026) links `GRS_AGEB_urbana_2020.zip`, `Mapas_GRS_loc_100mil_hab_2020.zip`, `Visualizacion_GRS_AGEB_urbana_2020.zip` and `Nota_GRS_AGEB_urbana_2020.pdf` — [CONEVAL GRS AGEB 2020 page](https://www.coneval.org.mx/Medicion/IRS/Paginas/Rezago_social_AGEB_2020.aspx)
- GRS AGEB 2020 (published 26 Jul 2022): five grades (muy bajo…muy alto); of 61,430 urban AGEB nationally, 3,947 "muy alto" and 10,264 "alto"; urban AGEB hold 78.6% of national population — [CONEVAL Comunicado 07/2022](https://WWW.CONEVAL.ORG.MX/SalaPrensa/Comunicadosprensa/Documents/2022/COMUNICADO_07_GRADO_REZAGO_SOCIAL_AGEB_URBANA_2020.pdf); method note — [Nota GRS AGEB urbana 2020](https://WWW.CONEVAL.ORG.MX/Medicion/Documents/GRS_AGEB_2020/Nota_GRS_AGEB_urbana_2020.pdf)
- CONEVAL also published 2020 poverty for urban localities (methodology and presentation) — [Metodología pobreza localidad 2020](https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/pob_loc_urbana/Metodologia_pobreza_localidad_2020.pdf)
- Institutional status: the reforms extinguishing CONEVAL were formalised on 16 Jul 2025 and INEGI took over poverty measurement from 17 Jul 2025 — [Crónica, 28 Jul 2026](https://www.cronica.com.mx/nacional/2026/07/28/del-coneval-al-inegi-el-futuro-de-la-evaluacion-social-en-mexico/); the Senate approved the transfer in June 2025 — [Zeta Tijuana](https://zetatijuana.com/2025/06/senado-concretan-extincion-del-coneval-trasladan-sus-funciones-al-inegi/); under the reform INEGI measures poverty every two years by entidad and every five years by municipio — [UnoTV](https://unotv.com/nacional/senado-aprueba-desaparicion-del-coneval-y-da-facultades-al-inegi/)

### Inferences
- Use the municipal 2020 poverty file only for an alcaldía-level descriptive table (16 rows: % poverty, % extreme poverty, carencias incl. "carencia por acceso a los servicios básicos en la vivienda") next to per-capita consumption by alcaldía; inferential statistics with n=16 are weak.
- GRS AGEB 2020 is a census-based composite like CONAPO's IMU; both join on the 13-char AGEB key. Using both strengthens the validation of SACMEX `indice_des`.
- Because CONEVAL is extinct, cite files with retrieval date and keep local copies; future URLs may migrate to inegi.org.mx. A 2025 municipal poverty measurement (by INEGI) was not found and would in any case be far from 2019.

### Gaps
- `GRS_AGEB_urbana_2020.zip` was found as a link on the page but its HTTP status was not separately checked.
- Licence/terms of CONEVAL data and their post-extinction status (whether INEGI's libre-uso terms now apply) were not found.
- The exact field names (e.g., `clave_entidad`, `clave_municipio`) inside the CONEVAL annex were not inspected; confirmation that the 16 CDMX alcaldías are rows of the municipal file was not read from the file (expected, since the measurement covers municipios and demarcaciones territoriales).

---

## 6. Cross-cutting: year mismatch (2019 vs 2020), joining keys, and 3-week feasibility ranking

### Takeaway
Use the 2020 census (and the 2020 IMU/IMC/GRS indices built from it) as structural, slowly-changing covariates and denominators for Jan–Jun 2019 consumption, state the ~1-year gap explicitly, and run a sensitivity check; the realistic 3-week package is census AGEB-manzana + Marco Geoestadístico 2020 (per-capita/per-household), CONAPO IMU/IMC or CONEVAL GRS (socioeconomic explanation), and SMN daily climate + Monitor de Sequía (context).

### Cited Findings
- The census AGEB-manzana product and its identifiers (ENTIDAD, MUN, LOC, AGEB, MZA) allow keys at manzana, AGEB and municipio/alcaldía level — [INEGI data dictionary](https://www.inegi.org.mx/contenidos/programas/ccpv/2020/doc/fd_agebmza_urbana_cpv2020.pdf)
- CONAPO IMU/IMC 2020 are computed from the 2020 census microdata, so they share the census reference year — [CONAPO IMU 2020 technical note](https://tabasco.gob.mx/sites/default/files/users/planeacion_spf/Nota_t_cnica_IMU_2020.pdf)
- CONEVAL GRS AGEB 2020 is likewise based on 2020 data at urban AGEB level — [CONEVAL Comunicado 07/2022](https://WWW.CONEVAL.ORG.MX/SalaPrensa/Comunicadosprensa/Documents/2022/COMUNICADO_07_GRADO_REZAGO_SOCIAL_AGEB_URBANA_2020.pdf)
- ENIGH 2018 and 2020 exist as open CSVs and bracket 2019 — [ENIGH 2018](https://www.inegi.org.mx/contenidos/programas/enigh/nc/2018/datosabiertos/conjunto_de_datos_enigh_2018_ns_csv.zip); [ENIGH 2020](https://www.inegi.org.mx/contenidos/programas/enigh/nc/2020/datosabiertos/conjunto_de_datos_enigh_ns_2020_csv.zip)
- SMN daily data and the Monitor de Sequía are available for 2019 dates directly (no mismatch) — [SMN daily file](https://smn.conagua.gob.mx/tools/RESOURCES/Normales_Climatologicas/Diarios/df/dia09010.txt); [Monitor de Sequía XLSX](https://smn.conagua.gob.mx/tools/RESOURCES/Monitor%20de%20Sequia%20en%20Mexico/MunicipiosSequia.xlsx)

### Inferences
**Year-mismatch handling (proposed wording/approach for the paper):**
- Treat 2020 census counts as the nearest available measurement of 2019 stocks (population, households, dwellings, services). Population and dwelling stocks at manzana level change slowly over ~1 year, and the marginalisation indices are structural.
- Sensitivity: (i) scale manzana POBTOT by the alcaldía growth factor implied by ITER 2020 vs. Intercensal 2015 (geometric interpolation to mid-2019) and show per-capita results change marginally; (ii) restrict to manzanas with stable dwelling counts if a second framework year is used.
- Note that 2020 census fieldwork preceded most COVID-19 effects but ENIGH 2020 did not; prefer ENIGH 2018 for city-level expenditure comparisons.

**Join-key summary for the warehouse:**
- Manzana: 16-char CVEGEO via point-in-polygon of SACMEX lat/lon on Marco Geoestadístico 2020 (EPSG:6372).
- AGEB: CVEGEO[:13] → INEGI AGEB rows, CONAPO IMU 2020, CONEVAL GRS 2020.
- Alcaldía: CVE_ENT "09" + CVE_MUN (3 digits) → ITER, CONAPO IMM, CONEVAL municipal poverty, Monitor de Sequía. SACMEX alcaldía names need a 16-row crosswalk to INEGI CVE_MUN built from NOM_MUN in ITER (do not hand-type codes; read them from the ITER file).
- Colonia: spatial join to CONAPO `imc2020_shp` polygons (preferred over name matching).
- Climate: nearest SMN station / Thiessen polygons from station lat/lon.

**3-week feasibility ranking (effort estimates are judgement, not sourced):**
1. Censo 2020 AGEB-manzana CDMX + Marco Geoestadístico 2020 — High; ~3–5 days (spatial join, QA of unmatched points, per-capita/per-household measures, new dimension + RDF links).
2. CONAPO IMU 2020 (AGEB) — High; ~1 day after step 1. Alternative/robustness: CONEVAL GRS AGEB 2020 — High; ~1 day.
3. CONAPO IMC 2020 (colonia shapefile) — Medium; ~2 days (second spatial join, name-agreement analysis vs. SACMEX colonias).
4. SMN daily station data for CDMX — Medium-High; ~2 days (station list from KMZ, NULO handling, bimester aggregation).
5. Monitor de Sequía municipal — High; <1 day (if 2019 columns are present).
6. ITER 2020 / CONAPO IMM / CONEVAL municipal poverty — High; <1 day each, but only 16 alcaldía units (descriptive tables).
7. ENIGH 2018/2020 water expenditure — Medium-Low; ~2–3 days with survey weights; city-level context only.
8. CONAGUA aquifer availability, Cutzamala storage, SINA/EAM — Low/Medium-Low; manual extraction from bot-protected sites/PDFs; narrative context only.
9. CNGMD 2019 water module, Intercensal 2015 — Low; little CDMX-specific value.

### Gaps
- No verification that the national open-data portal datos.gob.mx was reachable (scripted request failed on 18 Oct 2026); none of the datasets above depend on it.
- CONAPO population projections/estimates by alcaldía for mid-2019 (an alternative denominator for the year mismatch) were not researched.
- Whether a 2019 version of the Marco Geoestadístico exists and differs materially from the 2020 version for CDMX manzanas was not checked.

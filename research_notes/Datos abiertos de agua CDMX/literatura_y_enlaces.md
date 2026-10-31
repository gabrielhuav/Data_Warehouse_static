# Mexico City water-consumption open data: prior studies, linked-data identifiers, and related work for the IJCOPI extension

Research date: 2026-10-18. Wikidata figures come from live queries run that day against the QLever Wikidata endpoint (`https://qlever.dev/api/wikidata`; dump of 10 Aug 2026 plus live updates) and against the official WDQS (`query.wikidata.org`). Bibliographic metadata comes from OpenAlex/Crossref records resolved by DOI. Most publisher landing pages (Elsevier, T&F, Wiley, Springer, IWA) returned HTTP 403 to the fetch tool. Where only the abstract was read, the entry says so.

## Q1. Which studies used SACMEX consumption data by colonia/manzana, did any obtain other years, and how?

### Takeaway
One UAM-Azcapotzalco group (Medina-Rivas, Morales-Novelo, Rodríguez-Tapia, Revollo-Fernández) and one UNAM/COLMEX group (Ramos-Bueno, Perevochtchikova) produce almost all the peer-reviewed spatial work on SACMEX consumption data. Both got their data straight from the utility, not from the open-data portal. The UNAM/COLMEX group documents formal transparency requests (InfomexDF folios) for colonia-level annual consumption, and its later paper covers 2004–2022. The open portal still offers only "1° Semestre 2019" at block (manzana) level. IPDP, however, publishes derived colonia polygon layers with 2010 census dwelling and population counts, which are directly usable for per-capita and polygon-topology work.

### Cited Findings

**A. Peer-reviewed studies that used SACMEX consumption records (spatial, colonia/neighbourhood level)**

- **Medina-Rivas, C.M., Rodríguez-Tapia, L., Morales-Novelo, J.A., Revollo-Fernández, D.A. (2022).** "Spatial inequality of domestic water consumption in Mexico city." *Water Resources and Economics* 40, 100210. DOI 10.1016/j.wre.2022.100210.
  - Data: 2019 water consumption records "provided by the city's operating utility".
  - Findings: per-capita consumption in 2019 was 123 l/day. The paper identifies two clusters of unequal household consumption, explained in order of importance by discontinuous supply, dependence on external sources, altitude, and neighbourhood socioeconomic status.
  - Method: spatial analysis and GIS (cluster detection).
  - Coverage context: 94% supply coverage per the 2020 Census.
  - [OpenAlex abstract via DOI](https://doi.org/10.1016/j.wre.2022.100210)
  - A search snippet said "three clusters", which conflicts with the abstract's "two clusters" ([search result summary of ScienceDirect/ResearchGate](https://www.sciencedirect.com/science/article/pii/S2212428422000172)). The abstract wording is the more reliable of the two.
- **Morales-Novelo, J.A., Medina-Rivas, C.M., Rodríguez-Tapia, L., Revollo-Fernández, D.A. (2022).** "Household water consumption on the outskirts of Mexico City." *International Journal of Hydrology* 6(3), 110–117. DOI 10.15406/ijh.2022.06.00310.
  - Data: 2019 data from the city's water operating agency.
  - Method: exploratory spatial data analysis in GeoDa.
  - Findings: high consumption in the central-west and low consumption in the southern and south-eastern periphery; consumption rises from the poor periphery toward the centre.
  - [DOI](https://doi.org/10.15406/ijh.2022.06.00310) (OpenAlex abstract). This is a lower-tier venue.
- **Medina-Rivas, C.M., Morales-Novelo, J.A., Rodríguez-Tapia, L., Revollo-Fernández, D.A. (2025; online 2024).** "Mexico city's decline in per capita domestic water use: a comprehensive spatial-temporal study." *Urban Water Journal* 22(1), 1–15. DOI 10.1080/1573062X.2024.2423400.
  - Period: household per-capita consumption, 2010 vs 2019.
  - Methods: GIS, statistical analysis and spatial regression.
  - Findings: average consumption fell 40%, with a spatial reconfiguration toward greater inequality. Five drivers were identified: intermittent supply, income, water feasibility, households without piped water, and growth in dwellings.
  - [DOI](https://doi.org/10.1080/1573062X.2024.2423400) (OpenAlex / Semantic Scholar abstract)
- **Ramos-Bueno, A., Perevochtchikova, M., Chang, H. (2021).** "Socio-spatial analysis of residential water demand in Mexico City." *Tecnología y Ciencias del Agua* 12(2), 59–110. DOI 10.24850/j-tyca-2021-02-02. Diamond open access, CC BY-NC-SA 4.0. [PDF](http://revistatyca.org.mx/index.php/tyca/article/download/2414/2293)
  - **Data acquisition (verified in the PDF):**
    - Colonia-level annual consumption, number of domestic connections, connections with meters, and colonia names for 2008–2013: SACMEX transparency request **0324000022614** (InfomexDF, 2014).
    - Total supplied volume 2008–2013: request **0324000105214**.
    - Monthly well extraction 2003–2015: request **0324000111816** (2016).
    - A colonia shapefile of **1,456 neighbourhoods**: SEDUVI request **0105000279114** (2015).
    - The Social Development Index (IDS) by colonia/manzana: Evalúa CDMX.
  - Study area: n = 1,346 colonias, after excluding those with zero consumption or no metering coverage.
  - Results:
    - OLS R² = 0.87; GWR R² = 0.89.
    - The IDS has the largest coefficient. Dwelling density and intermittent supply have negative coefficients.
    - In 2010, 64.25% of residential users were metered, generating 9.95 m³/s of residential demand.
  - [PDF](http://revistatyca.org.mx/index.php/tyca/article/download/2414/2293)
- **Ramos-Bueno, A., Galeana-Pizaña, J.M., Perevochtchikova, M. (2024).** "Urban water consumption analysis through a spatial panel modeling approach: a case study of Mexico City, 2004–2022." *Water Supply* 24(9), 3179–3195. DOI 10.2166/ws.2024.191.
  - Data: measured consumption at **neighbourhood level for 2004–2022**, modelled as a spatial panel.
  - Findings:
    - Estimated total consumption is 15.44 m³/s, against SACMEX's own 18.52 m³/s and a total supply of 30.05 m³/s.
    - The paper also reports intra-urban patterns of users and meter coverage.
  - [DOI](https://doi.org/10.2166/ws.2024.191) (OpenAlex / Semantic Scholar abstract)
  - How the 2014–2022 data were obtained could not be verified because the PDF returned 403. By precedent it was most likely further InfomexDF/PNT requests (see Inferences).
- **Hernández-Vázquez, I., Luna-Sánchez, A.J., Hurtado-Pérez, A.B., Claramunt, C., Zagal-Flores, R., Mata, F. (2025).** "Analyzing Water Consumption Patterns in Mexico City: A GIS and Data Science Approach." In *Web and Wireless Geographical Information Systems (W2GIS 2025)*, LNCS, pp. 123–137, published 17 Aug 2025. DOI 10.1007/978-3-032-01723-9_9.
  - Group: IPN (Mata, Zagal-Flores) with Claramunt.
  - Its Crossref reference list cites both Medina-Rivas papers, both Ramos-Bueno papers, and time-series clustering work on water consumption (Wang et al.; Waraga et al. 2021).
  - [Crossref record](https://api.crossref.org/works/10.1007/978-3-032-01723-9_9)
  - **Unverified:** no abstract was available, so the dataset (likely the CDMX open S1-2019 data) and the methods are not confirmed. **This is the closest competitor or companion to the ICOKG/IJCOPI paper (same open data, CS venue), and reviewers are likely to expect it to be cited.**

**B. Other peer-reviewed CDMX water consumption/inequality studies (2015–2026; survey or other data)**

- **Morales-Novelo, J.A., Rodríguez-Tapia, L., Revollo-Fernández, D.A. (2018).** "Inequality in Access to Drinking Water and Subsidies between Low and High Income Households in Mexico City." *Water* 10(8), 1023. DOI 10.3390/w10081023.
  - Data: the 2011 household survey EHCSCA, not SACMEX billing.
  - Methods: Lorenz curve, Gini coefficient, targeting coefficient.
  - Finding: the distribution of both water and subsidies is regressive.
  - [DOI](https://doi.org/10.3390/w10081023)
- **Revollo-Fernández, D.A., Rodríguez-Tapia, L., Morales-Novelo, J.A. (2019).** "Impacto de los subsidios al agua en los hogares pobres de la Ciudad de México." *Gestión y Política Pública* 28(1), 39. DOI 10.29265/gypp.v28i1.542.
  - Data: EHCSCA 2011, Census 2010, and ENIGH 2010/2012/2014.
  - Finding: the top income quintile receives about 45% of the subsidy and the bottom quintile just under 12%.
  - [DOI](https://doi.org/10.29265/gypp.v28i1.542)
- **Revollo-Fernández, D.A., Rodríguez-Tapia, L., Mazari-Hiriart, M., Espinosa-García, A.C. (2023).** "Behavior of household water consumption in Mexico during the COVID-19 pandemic." *Water Policy* 25(7), 701–714. DOI 10.2166/wp.2023.012.
  - Data: tap-water consumption before and during COVID (chi-square) plus a bottled-water survey.
  - Finding: tap-water use did not rise, which is linked to perceived poor service.
  - [DOI](https://doi.org/10.2166/wp.2023.012)
- **Rodríguez-Tapia, L., Revollo-Fernández, D.A., Morales-Novelo, J.A. (2017).** "Household's Perception of Water Quality and Willingness to Pay for Clean Water in Mexico City." *Economies* 5(2), 12. DOI 10.3390/economies5020012. [DOI](https://doi.org/10.3390/economies5020012)
- **Magaña, V.O., Ábrego-Góngora, C.J., Méndez Antonio, B. (2024).** "El clima cambiante y los consumos domésticos de agua en ciudades de México." *Investigaciones Geográficas* 114. DOI 10.14350/rig.60850.
  - Finding: maximum temperature modulates demand, while per-capita use in large Mexican cities has been falling because supply does not keep pace with users.
  - [DOI](https://doi.org/10.14350/rig.60850)
- **Sámano Romero, G., Chávez-Mejía, A. (2025).** "Water Access in Mexico City: A Review of Local Research Approaches." *WIREs Water* 12(6). DOI 10.1002/wat2.70046.
  - A review that groups the literature into historical, socio-spatial and quantitative domains and notes persistent data gaps.
  - Useful as a single citation for "state of the literature".
  - [DOI](https://doi.org/10.1002/wat2.70046)
- **Delgado Ramos, G.C. (2015).** "Water and the political ecology of urban metabolism: the case of Mexico City." *Journal of Political Ecology* 22(1). DOI 10.2458/v22i1.21080. [DOI](https://doi.org/10.2458/v22i1.21080)
- **Concha Larrauri, P., Campos Gutiérrez, J.P., Lall, U., Ennenbach, M.W. (2020).** "A City Wide Assessment of the Financial Benefits of Rainwater Harvesting in Mexico City." *JAWRA* 56(2), 247–269. DOI 10.1111/1752-1688.12823. [DOI](https://doi.org/10.1111/1752-1688.12823)
  - **Unverified** whether it used SACMEX consumption data.
- **Gutiérrez Armenta, E.M. et al. (2026).** "Dynamic logistics model for projecting water consumption in México city." *IOSR Journal of Computer Engineering* 28(3), 31–35. DOI 10.9790/0661-2803043135.
  - A logistic ODE solved with RK4, using scenarios of 100/300/380 L/person/day.
  - Low-tier venue; not based on colonia data.
  - [DOI](https://doi.org/10.9790/0661-2803043135)
- **Qualitative and political work using colonia framing (context only):**
  - Sierra Martínez, A.E. (2026), "Defending water, defending place…", *Political Geography* 130, 103647. [DOI](https://doi.org/10.1016/j.polgeo.2026.103647)
  - García, R.I., Pérez Ortiz, A., Becerra Gálvez, A.L. (2026), *Tecnología y Ciencias del Agua* (water insecurity and health). [DOI](https://doi.org/10.24850/j-tyca-18-03-05)

**C. Open/official data sources and grey literature showing how other years are obtainable**

- **CDMX open data portal, dataset "Consumo de agua" (SACMEX).**
  - Description: "bimonthly information on water supply at manzana level" (metered and average-billed).
  - Resources: a single data resource, "Consumo Agua (1° Semestre 2019)" in CSV, plus a data dictionary in XLSX. Licence CC-BY-4.0-ESP.
  - Metadata modified 2026-09-01.
  - [Dataset page](https://datos.cdmx.gob.mx/dataset/consumo-agua); [CKAN API](https://datos.cdmx.gob.mx/api/3/action/package_show?id=consumo-agua)
- **IPDP derived layer "Consumo habitacional promedio bimestral de agua por colonia (m3)"** (SHP/GeoJSON, CC-BY-4.0-ESP).
  - **1,815 colonia polygons**, each keyed by `cve_col`, a "colonia key per INE" in the format `02-001`.
  - Fields: `alcaldia`, `SUM_cons_t` (total consumption per bimester), `MEAN_cons_`, **`VIV2010` (2010 census dwellings)**, `PROMVIVCON` (consumption per dwelling), and `C_PROMVIVC` (quintile class).
  - [Dataset](https://datos.cdmx.gob.mx/dataset/consumo-habitacional-promedio-bimestral-de-agua-por-colonia-m3)
- **IPDP layer "Diferencia consumo total SACMEX"** (SHP/GeoJSON).
  - Fields: `cve_col` (5-character key, "Catálogo de Colonias IECM"), **`pob_2010`**, `SUM_cons_t`, and `DIF_CON`, defined as a "difference between total SACMEX consumption m³ third trimester 2019".
  - [Dataset](https://datos.cdmx.gob.mx/dataset/diferencia-consumo-total-sacmex)
- **DatDat-DatDat (César Cantú, Substack, 15 Aug 2025), grey literature.**
  - Obtained **colonia-level consumption for 2020–2024** "vía transparencia" from the Secretaría de Gestión Integral del Agua (Segiagua). No folio was given.
  - Found **21 colonias with near-zero consumption in 2020–2024**, 11 of them in Tlalpan, interpreted as lack of supply rather than lack of use.
  - Central colonias (Centro Histórico, Del Valle Centro, Roma Norte, Santa María la Ribera) consumed more than 5 million m³ over the same period.
  - [Substack](https://kzrcntw.substack.com/p/con-medidor-en-ceros)
- **Annual Gaceta Oficial lists of colonias catastrales with the highest consumption.**
  - SACMEX publishes these yearly. The 2023 list covers colonias catastrales with at least 70% metered connections; Lomas de Bezares had 125.29 m³/day.
  - Note that this uses colonias catastrales, not IECM colonias.
  - Read only via news summaries: [Excélsior](https://www.excelsior.com.mx/comunidad/lista-sacmex-colonias-mas-consumo-agua-cdmx/1633764), [El Financiero](https://www.elfinanciero.com.mx/cdmx/2024/02/07/mapa-muestra-las-colonias-que-mas-agua-gastan-en-cdmx-segun-sacmex/)
- **SACMEX differentiated tariffs** are based on the *Índice de Desarrollo por Manzana* (popular/baja/media/alta), published in the Gaceta Oficial del DF on 29 Dec 2009. This index is the source of the project's development index. [Excélsior](https://www.excelsior.com.mx/comunidad/asi-se-factura-el-agua-en-la-cdmx/1260692)
- **Ibero sustainability note (search snippet only, page not fetched):**
  - Average supply of 150 l/inhabitant/day across 16 alcaldías.
  - 23.1% of dwellings with measured or estimated consumption below 100 l/person.
  - About 1,370,137 dwellings in colonias mostly without meters.
  - [Ibero](https://sustentabilidad.ibero.mx/la-cdmx-vive-tiempos-de-escasez-hidrica-y-desigualdad-en-el-suministro-de-agua/)
- **Aqueducto (snippet only):** 62% of colonias with tandeo have a low or very low social development index, and most consume under 100 l/inhabitant/day. [Aqueducto](https://aqueducto.mx/tandeo_cdmx/)

### Inferences
- **Same source year.** Medina-Rivas et al. (2022) and Morales-Novelo et al. (2022) work on 2019 SACMEX records, the same year as the ICOKG paper. Their published 123 l/day per-capita figure is a direct external benchmark for a per-capita extension.
  - The ICOKG paper uses the open S1-2019 manzana data. The UAM papers appear to use utility-provided data, possibly the full year, so any comparison should state the difference in coverage.
- **Precedent for other years.** Formal transparency requests to SACMEX (InfomexDF, now the Plataforma Nacional de Transparencia) are the documented academic route: Ramos-Bueno et al. 2021 give folio numbers.
  - A 2020–2024 colonia-level series was obtained the same way in 2025, now addressed to Segiagua.
  - That Segiagua has succeeded or absorbed SACMEX as the obligated party is suggested by the DatDat article but **not verified**.
- **Per-capita and polygon directions.** The IPDP layers already join SACMEX 2019 consumption to IECM colonia polygons with `VIV2010` and `pob_2010`.
  - This gives a ready, citable denominator and polygon geometry for (i) per-capita or per-dwelling indicators and (ii) GeoSPARQL polygon topology (sfTouches/sfWithin) to replace or complement the centroid-based `agua:nearbyWithin1500m`.
  - The denominators are 2010 values. Updating to 2020 needs INEGI AGEB/manzana data aggregated to colonias.
- **Zero-consumption records.** The near-zero colonias (DatDat) and the exclusion rule in Ramos-Bueno (zero consumption or no metering) both show that zeros in SACMEX data often mean non-measurement or non-supply. This is directly relevant to "better anomaly evaluation" in the extension.

### Gaps
- **Not accessible.** Full texts of Medina-Rivas 2022/2025 and Ramos-Bueno 2024 returned 403, so the exact acquisition route for those authors' 2019 and 2014–2022 data (agreement vs transparency request) is unverified.
- **Hernández-Vázquez et al. 2025 (W2GIS).** The abstract and methods could not be retrieved, so the dataset used is unconfirmed.
- **UNAM thesis TES01000789586.** A UNAM thesis surfaced in search ([PDF](https://ru.dgb.unam.mx/bitstream/20.500.14330/TES01000789586/3/0789586.pdf)), but the PDF is AES-encrypted and could not be read. Its relevance is unknown.
- **No other colonia/manzana study found.** No peer-reviewed study was found that used the open-portal "Consumo de agua" S1-2019 manzana dataset specifically, beyond the probable W2GIS paper.
- **Portal history.** It is unknown whether SACMEX ever published other semesters on the portal. The current CKAN record lists only S1-2019, and its metadata was recreated on 2026-08-27.

## Q2. Which Wikidata properties link CDMX alcaldías to INEGI codes, how many CDMX colonias have Wikidata items, and which other identifiers or LOD endpoints exist?

### Takeaway
Alcaldías are well covered in Wikidata. All 16 are typed `Q2734310` and all 16 carry **P3801 "INEGI municipality ID"**, whose value is the 5-digit INEGI CVEGEO (e.g., `09002`), plus OSM relation, GADM and HASC. **P1976 is the INEGI *locality* ID, not the municipality ID.** Colonias are poorly covered:
- Only about 134 items are typed "Mexico City colonia" (`Q5148433`), and about 168 colonia-like items in total.
- That compares with about 1,780–1,815 colonias in the IECM and IPDP catalogues, roughly 9% coverage.
- None of these items carries an INEGI ID or a geoshape, and only 48 have coordinates.

No Mexican government SPARQL or linked-data endpoint was found. INEGI exposes JSON REST APIs, including a geostatistical catalogue that returns CVEGEO plus 2020 population.

### Cited Findings
- **Alcaldía class.** The class `wd:Q2734310` ("demarcación territorial de la Ciudad de México") has 16 instances located in Mexico City (`Q1489`). Own query, 2026-10-18 ([WDQS](https://query.wikidata.org/); [Q2734310](https://www.wikidata.org/wiki/Q2734310)).
- **External identifiers on the 16 alcaldía items** (own QLever query, 2026-10-18; [QLever Wikidata](https://qlever.dev/api/wikidata)):

  | Property | Coverage | Example |
  |---|---|---|
  | **P3801 INEGI municipality ID** | 16/16 | `09005` |
  | P402 OpenStreetMap relation ID | 16/16 | |
  | P8714 GADM ID | 16/16 | `MEX.9.8_2` |
  | P8119 HASC | 16/16 | |
  | P2326 GNS ID | 16/16 | |
  | P646 Freebase | 16/16 | |
  | P7471 iNaturalist place | 16/16 | |
  | P1566 GeoNames ID | 15/16 | |
  | P214 VIAF | 8/16 | |
  | P227 GND | 6/16 | |
  | **P1976 INEGI locality ID** | 5/16 | `090120001`, the cabecera locality |
  | P6766 Who's on First | 4/16 | |
  | P1667 Getty TGN | 3/16 | |
- **Property definitions:**
  - P3801 is "identifier for a municipality in Mexico published by INEGI", used 2,474 times Wikidata-wide.
  - P1976 is "identifier for a locality of Mexico", used 203,908 times.
  - No Wikidata property exists for IECM colonia keys, SEPOMEX settlements, AGEB or manzana CVEGEO. The search covered external-ID properties whose label or description mentions INEGI or Mexico (own query).
  - [Property:P3801](https://www.wikidata.org/wiki/Property:P3801), [Property:P1976](https://www.wikidata.org/wiki/Property:P1976)
- **Per-alcaldía data-quality issues** (own query; [QLever](https://qlever.dev/api/wikidata)):
  - Miguel Hidalgo (`Q1832732`) has no GeoNames ID.
  - Benito Juárez (`Q2356998`) has two GeoNames IDs (8379133 and 3827406) and three P625 coordinates. One of them (19.2406, -99.0928) falls far outside the borough.
  - Cuajimalpa (`Q762749`) and Iztacalco (`Q953866`) each have two coordinates. Cuajimalpa's second coordinate (19.2228, -99.1703) is also implausible.
- **Colonia coverage.** Counts are of items with P31 = class and P131+ = Mexico City (own QLever query, 2026-10-18; [Q5148433](https://www.wikidata.org/wiki/Q5148433)).

  | Class | Items | With P625 | With OSM relation | With INEGI ID | With population | With geoshape (P3896) | With GeoNames |
  |---|---|---|---|---|---|---|---|
  | `Q5148433` "Mexico City colonia" | 134 | 48 | 5 | 0 | 0 | 0 | 3 |
  | `Q5148198` "colonia of Mexico" | 35 | | | | | | |
  | `Q123705` neighbourhood | 21 | | | | | | |
  | **Distinct colonia-class items (`Q5148433` or `Q5148198`)** | **168** | | | | | | |

  Wikidata-wide, there are 137 instances of `Q5148433`.
- **"Human settlement" items.** There are 575 `Q486972` items inside CDMX, of which 558 carry P1976 (INEGI locality ID), 574 have coordinates and 393 have a GeoNames ID (own query).
- **Reference colonia catalogues:**
  - IECM *Marco Geográfico de Participación Ciudadana*: in 2022 there were 1,837 territorial units (1,781 colonias, housing units or fraccionamientos, and 56 pueblos originarios). The 2025 version has 1,851 units (1,756 colonias and others, 77 pueblos, 18 barrios). Read via search summaries of [Crónica (6 Oct 2026)](https://www.cronica.com.mx/metropoli/2026/10/06/iecm-actualiza-marco-de-participacion-ciudadana-tras-registrar-ocho-pueblos-originarios/) and [Iztapalapa PDF of the 2025 Marco](https://iztapalapa.cdmx.gob.mx/1paginas/PP2026/MarcoGegrafico2025.pdf).
  - The IPDP water layer has 1,815 colonia polygons ([IPDP GeoJSON via CKAN](https://datos.cdmx.gob.mx/dataset/consumo-habitacional-promedio-bimestral-de-agua-por-colonia-m3)).
  - SEDUVI supplied 1,456 colonia polygons in 2014–2015 ([Ramos-Bueno et al. 2021](http://revistatyca.org.mx/index.php/tyca/article/download/2414/2293)).
- **INEGI CVEGEO structure** ([INEGI Manual de cartografía censal](https://www.inegi.org.mx/contenidos/temas/mg/doc/manual_cartografia_censal.pdf); field names CVE_ENT, CVE_MUN, CVE_LOC, CVE_AGEB, CVE_MZA per [OSM wiki INEGI/MGN](https://wiki.openstreetmap.org/wiki/INEGI/MGN)):
  - Urban: EE (state, 2) + MMM (municipality, 3) + LLLL (locality, 4) + AAA-A (AGEB, 3 digits plus a check character) + NNN (block, 3), concatenated from state down to manzana.
  - Rural: AGEB and locality swap positions.
  - So an alcaldía CVEGEO (`09xxx`) equals the Wikidata P3801 value. A manzana CVEGEO is the 16-character extension of the same key.
- **INEGI geostatistical catalogue API (JSON, no token).** `https://gaia.inegi.org.mx/wscatgeo/v2/mgem/09` returns, for the 16 alcaldías, `cvegeo`, `nomgeo`, `pob_total` (2020), male and female population, and `total_viviendas_habitadas`. Example: 09002 Azcapotzalco, 432,205 people and 134,204 inhabited dwellings. CDMX total: 9,209,944 ([INEGI wscatgeo](https://gaia.inegi.org.mx/wscatgeo/v2/mgem/09)).
- **INEGI Banco de Indicadores API.** A token-based REST API returning JSON, JSONP or XML, with geography given as national, state or municipal codes ([INEGI API](https://inegi.org.mx/servicios/api_indicadores.html)).
  - No INEGI RDF or SPARQL service was found. A search for INEGI linked data or SPARQL returned only Spanish and other non-Mexican portals ([search: datos.gob.es SPARQL results](https://datos.gob.es/es/doc-tags/sparql)).
- **CDMX open-data portal.** It runs CKAN; its Action API works and returns JSON ([CKAN API](https://datos.cdmx.gob.mx/api/3/action/package_show?id=consumo-agua)).
  - A probe of `https://datos.gob.mx/api/3/action/status_show` returned an HTTP 308 redirect (own test), so the national portal's API status is inconclusive.
- **LinkedGeoData.** The OSM-to-RDF project announced static and live SPARQL endpoints in 2011 ([OSM-talk 2011 announcement](https://lists.openstreetmap.org/pipermail/talk/2011-April/057987.html); [linkedgeodata.org](https://linkedgeodata.org/)). A test of `http://linkedgeodata.org/sparql` on 2026-10-18 **timed out** (own test).

### Inferences
- **Linking alcaldías.** The robust key is `agua:Alcaldia owl:sameAs wd:Qxxx` via **P3801 = INEGI CVEGEO (5 digits)**, plus optional links to GeoNames (P1566), OSM relations (P402) and GADM (P8714).
  - The ICOKG paper (and the prompt) referred to P1976 for municipalities. That should be corrected: P1976 is the locality ID.
- **Linking colonias.** Wikidata cannot serve as the authority. It covers under 10% of colonias, with no geometry and no official key.
  - Better: mint colonia URIs from the IECM/INE `cve_col` key used by the IPDP layers, and link opportunistically to Wikidata (where an item exists), OSM and GeoNames.
  - A useful journal contribution would be to report this coverage gap quantitatively, with the counts above, as a finding.
- **Linking manzanas.** INEGI CVEGEO (16 characters) is the natural authority key, but it is not in Wikidata. INEGI's JSON APIs and Marco Geoestadístico shapefiles are the only official sources.
- **Contamination of naive counts.** The 575 "human settlement" items with INEGI locality IDs are most likely INEGI rural localities and pueblos in the southern alcaldías, not urban colonias. Naive "settlements in CDMX" counts will therefore overstate colonia coverage.

### Gaps
- **GeoNames colonias.** Coverage of CDMX colonias as PPLX/section features in GeoNames was not measured, because the GeoNames API needs a username.
- **OSM colonias.** OSM coverage of colonia boundaries (place=neighbourhood/suburb relations) was not measured.
- **Mexican linked data.** No official Mexican linked-data or SPARQL endpoint was found (INEGI, datos.gob.mx). Absence is inferred from search, not confirmed by INEGI.
- **IECM figures.** These come from search-engine summaries of news and a PDF, not from the IECM catalogue itself.

## Q3. What federated SPARQL demonstrations against Wikidata are feasible, and what are their limits?

### Takeaway
A "population by alcaldía" enrichment is feasible today. Join local alcaldía nodes to Wikidata on P3801 and read P1082 with the P585 = 2020 qualifier. Fifteen of 16 values match INEGI's 2020 census exactly, but **Cuauhtémoc has no P1082 at all**, and the qualifier modelling is inconsistent. The public WDQS allows CORS (`Access-Control-Allow-Origin: *`) but enforces tight per-client limits. On the research date it was also running an emergency limit of 1 request per minute. The demo should therefore cache or materialise its results and use INEGI's API as the authoritative fallback.

### Cited Findings
- **Population by alcaldía (own QLever query, 2026-10-18).**
  - **15/16 alcaldías match INEGI's 2020 total population exactly.** Example: Iztapalapa has 1,835,486 in both sources.
  - **Cuauhtémoc (`Q645293`, P3801 = 09015) has no P1082 statement.** INEGI gives 545,884.
  - Only 3 alcaldías also carry a 2010 value (Coyoacán, Gustavo A. Madero, Iztacalco).
  - Sources: [QLever Wikidata](https://qlever.dev/api/wikidata); [INEGI wscatgeo](https://gaia.inegi.org.mx/wscatgeo/v2/mgem/09)
- **Qualifier heterogeneity (own query):**
  - P585 point-in-time is 2020-01-01 for most alcaldías but 2020-03-15 for Tlalpan, Xochimilco and Venustiano Carranza.
  - P459 determination method is sometimes the generic item "census" and sometimes the specific item "Censo de Población y Vivienda 2020".
  - A robust query must filter on `YEAR(?date) = 2020`, not match one exact item.
- **WDQS limits** ([WDQS User Manual, query limits](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual#Query_limits)):
  - Hard 60-second timeout.
  - Each client (user agent plus IP) gets 60 s of processing time per 60 s.
  - 30 error queries per minute.
  - 5 parallel queries per IP.
  - Over-limit clients receive HTTP 429 with Retry-After, and clients that ignore 429 "can be temporarily banned".
  - Clients must send a proper User-Agent.
- **Observed throttling on 2026-10-18 (own test).** WDQS returned HTTP 429 with the message "Aggressively rate-limiting to 1 req / min - this rule was created during active wdqs outage". A later single request succeeded (HTTP 200) with `Access-Control-Allow-Origin: *`, so browser clients such as Comunica can call it directly.
- **Graph split.** Scholarly-article data was moved out of the main WDQS into a separate service, live on 9 May 2025, because the Blazegraph backend was near capacity ([Meta-Wiki: WDQS graph split](https://meta.wikimedia.org/wiki/WikiCite/WDQS_graph_split)). The split was reported finalised on 20 Jan 2026 ([Signpost, 2026-02-17](https://signpost.news/2026-02-17/Technology_report)). Geographic and administrative items stay in the main graph.
- **QLever alternative.** QLever hosts a full Wikidata mirror. On the research date its stats reported "latest-all.ttl.bz2 from 10.08.2026 … updated LIVE" ([QLever stats](https://qlever.dev/api/wikidata?cmd=stats)). It answered all of this research's aggregate queries without throttling.
- **Comunica.** Comunica is a modular, browser-capable SPARQL engine over heterogeneous sources (Taelman, Van Herwegen, Vander Sande, Verborgh, ISWC 2018, LNCS, pp. 239–255, DOI 10.1007/978-3-030-00668-6_15). [DOI](https://doi.org/10.1007/978-3-030-00668-6_15)
- **Federated GeoKG querying from GIS.** Páez & Vilches-Blázquez (2022) give a precedent ("Bringing Federated Semantic Queries to the GIS-Based Scenario", *ISPRS IJGI* 11(2), 86, DOI 10.3390/ijgi11020086). [DOI](https://doi.org/10.3390/ijgi11020086)

### Inferences
- **Feasible demonstrations, in order of robustness:**
  1. **Identifier enrichment.** Fetch P1566, P402, P8714 and labels for the 16 alcaldías via `VALUES ?cvegeo {"09002" …}` with P3801. This is one small query that is safe under the limits.
  2. **Population and per-capita.** Read P1082 for 2020 and divide the KG's alcaldía-level consumption. The query must handle the missing Cuauhtémoc value, for example with an OPTIONAL plus a fallback to an INEGI-sourced literal stored locally with provenance.
  3. **Cross-checking.** Compare Wikidata against INEGI and report the discrepancies above (missing values, duplicate coordinates) as a data-quality finding.
  4. **Colonia-level enrichment.** Possible only for about 134 items without geometry, so it is unsuitable as a core demo.
- **Design for the IJCOPI version:**
  - Materialise the `owl:sameAs` links and a dated snapshot of the Wikidata values into the KG, with PROV metadata.
  - Run live federation only as an optional "refresh".
  - Mention WDQS limits, the emergency throttling and QLever as an alternative endpoint in the threats-to-validity section.
- **Comunica behaviour (not verified here).** When given several sources, Comunica may decompose a query into many triple-pattern requests, which could exhaust WDQS per-client budgets. An explicit `SERVICE` clause or a pre-fetched snapshot is safer. This should be tested.

### Gaps
- **Comunica + SERVICE.** Whether Comunica's browser bundle, as used in the project, executes `SERVICE <https://query.wikidata.org/sparql>` against WDQS without hitting CORS or rate-limit issues was not tested.
- **Stability.** The longevity of QLever's public endpoint and any terms of use for it were not checked.

## Q4. Which 2022–2026 papers on water knowledge graphs, urban/geo KGs, RDF Data Cube and SHACL would reviewers expect to see cited?

### Takeaway
The most directly comparable work is the **WHOW Water Health Open Knowledge Graph** (*Scientific Data*, 2025), an EU KG that models water consumption. **KnowWhereGraph** (JWS 2024; TGIS 2026; plus the GIScience 2025 paper on precomputed topological relations) is the reference for GeoKGs and for polygon topology. The statistical-LOD thread is covered by recent applications of the RDF Data Cube vocabulary to open-government and census data (2023–2025) and by a critical 2024 assessment of whether linked open government data is still viable. The SHACL thread is covered by Rabbani et al. (PVLDB 2023), Trav-SHACL and shape learning (Semantic Web journal).

### Cited Findings

**Water knowledge graphs and ontologies**

- **Lippolis, A.S., Lodi, G., Nuzzolese, A.G. (2025).** "The Water Health Open Knowledge Graph." *Scientific Data* 12, 274. DOI 10.1038/s41597-025-04537-4.
  - An EU WHOW project KG that models **water consumption**, pollution, extreme weather, infectious disease and drug distribution.
  - It consists of five ontologies plus linked open data and is fully distributed.
  - [DOI](https://doi.org/10.1038/s41597-025-04537-4)
- **Papageorgiou, N., Pournara, D., Apostolou, D., Mentzas, G. (2025).** "Managing industrial water treatment processes knowledge with knowledge graphs." *Intelligent Decision Technologies* 19(2), 687–717. DOI 10.1177/18724981251321368. [DOI](https://doi.org/10.1177/18724981251321368)
- **Zabin, A., Zou, Y., Amor, R., González, V.A. (2025).** "WAM-ONTO: A semantic framework for water infrastructure asset management." *Advanced Engineering Informatics* 70, 104109. DOI 10.1016/j.aei.2025.104109. [DOI](https://doi.org/10.1016/j.aei.2025.104109)
- **Wang, L., Liu, X., Liu, Y., Li, H., Liu, J., Yang, L. (2024).** "Multimodal knowledge graph construction for risk identification in water diversion projects." *Journal of Hydrology* 635, 131155. DOI 10.1016/j.jhydrol.2024.131155. [DOI](https://doi.org/10.1016/j.jhydrol.2024.131155)
  - This is the Chinese "water conservancy KG" strand, which is mostly property-graph or NLP-based rather than RDF. It is useful for contrast.
- **Marston, L.T. et al. (2022).** "Water-Use Data in the United States: Challenges and Future Directions." *JAWRA* 58(4), 485–495. DOI 10.1111/1752-1688.13004. A data-infrastructure motivation for water-use data. [DOI](https://doi.org/10.1111/1752-1688.13004)

**Geospatial and urban knowledge graphs**

- **Shimizu, C., Stephen, S., … Zhu, R. (2024).** "The KnowWhereGraph ontology." *Journal of Web Semantics* 84, 100842. DOI 10.1016/j.websem.2024.100842.
  - One of the largest public GeoKGs: 30 layers including demographics and hazards, with a public SPARQL endpoint.
  - [DOI](https://doi.org/10.1016/j.websem.2024.100842)
- **Zhu, R., Shimizu, C., … Zalewski, J. (2026).** "The KnowWhereGraph: A Large-Scale Geo-Knowledge Graph for Interdisciplinary Knowledge Discovery and Geo-Enrichment." *Transactions in GIS* 30(1). DOI 10.1111/tgis.70184.
  - Frames the GeoKG as an "AI-ready data warehouse rooted in knowledge graphs", which closely matches the DW plus KG framing.
  - [DOI](https://doi.org/10.1111/tgis.70184)
- **Janowicz, K. et al. (2022).** "Know, Know Where, KnowWhereGraph…" *AI Magazine* 43(1), 30–39. DOI 10.1002/aaai.12043. [DOI](https://doi.org/10.1002/aaai.12043)
- **"Precomputed Topological Relations for Integrated Geospatial Analysis Across Knowledge Graphs" (GIScience 2025, LIPIcs).** DOI 10.4230/LIPIcs.GIScience.2025.4.
  - Precomputes topological relations using S2 DGGS cells, because discovering topology via SPARQL is computationally expensive.
  - This is directly relevant to replacing `nearbyWithin1500m` with polygon topology.
  - [DOI](https://doi.org/10.4230/lipics.giscience.2025.4)
  - **Author attribution conflicts in OpenAlex.** One record lists Schweikert, Kedrowski, Stephen, Hahmann; another, an arXiv 2024 record under the same DOI, lists Stephen, Faulk, Janowicz et al. Verify on DROPS before citing.
- **Car, N.J., Homburg, T. (2022).** "GeoSPARQL 1.1: Motivations, Details and Applications of the Decadal Update to the Most Important Geospatial LOD Standard." *ISPRS IJGI* 11(2), 117. DOI 10.3390/ijgi11020117. [DOI](https://doi.org/10.3390/ijgi11020117)
- **Liu, Y., Ding, J., Fu, Y., Li, Y. (2023).** "UrbanKG: An Urban Knowledge Graph System." *ACM TIST* 14(4), 1–25. DOI 10.1145/3588577. [DOI](https://doi.org/10.1145/3588577)
- **Phua, S.Z. et al. (2024).** "Fostering urban resilience and accessibility in cities: A dynamic knowledge graph approach." *Sustainable Cities and Society* 113, 105708. DOI 10.1016/j.scs.2024.105708. [DOI](https://doi.org/10.1016/j.scs.2024.105708)
- **Ma, X. (2022).** "Knowledge graph construction and application in geosciences: A review." *Computers & Geosciences* 161, 105082. DOI 10.1016/j.cageo.2022.105082. [DOI](https://doi.org/10.1016/j.cageo.2022.105082)
- **Carrillo-Brenes, F., Vilches-Blázquez, L.M. (2024).** "A Louvain-Based Approach to Discover Communities and Spatial Relations in a Homicide Knowledge Graph." *Lecture Notes in Geoinformation and Cartography*, pp. 31–39. DOI 10.1007/978-3-031-61440-8_3. [DOI](https://doi.org/10.1007/978-3-031-61440-8_3)
  - A Latin American GeoKG; the abstract was unavailable, so **the study area is unverified**.

**Statistical linked data (RDF Data Cube, SDMX) and linked open government data**

- **Rajabi, E., Midha, R., de Souza, J.F. (2023).** "Constructing a knowledge graph for open government data: the case of Nova Scotia disease datasets." *Journal of Biomedical Semantics* 14, 4. DOI 10.1186/s13326-023-00284-w.
  - An RDF Data Cube model for statistical open-government data, with lessons on cross-dimensional integration.
  - [DOI](https://doi.org/10.1186/s13326-023-00284-w)
- **Kević, K., Kuveždić Divjak, A. (2025).** "Open Technologies Supporting Linked Open Data Publishing: Croatian Population Census Case Study." *ISPRS Archives* XLVIII-4/W13-2025, 157–164. DOI 10.5194/isprs-archives-xlviii-4-w13-2025-157-2025.
  - Combines RDF Data Cube with GeoSPARQL; spatial-unit geometries are modelled separately and linked by URI.
  - [DOI](https://doi.org/10.5194/isprs-archives-xlviii-4-w13-2025-157-2025)
- **Wong, A., Fox, M.S., Katsumi, M. (2024).** "Semantically Interoperable Census Data…" *International Journal of Population Data Science* 9(1), 2378. DOI 10.23889/ijpds.v9i1.2378. [DOI](https://doi.org/10.23889/ijpds.v9i1.2378)
- **Lopez-Rodriguez, V., Ceballos, H.G. (2022).** "Modeling scientometric indicators using a statistical data ontology." *Journal of Big Data* 9. DOI 10.1186/s40537-022-00562-x.
  - SDMX-based statistical linked data from a **Mexican** institution (Tec de Monterrey).
  - [DOI](https://doi.org/10.1186/s40537-022-00562-x)
- **Quarati, A., Albertoni, R. (2024).** "Linked Open Government Data: Still a Viable Option for Sharing and Integrating Public Data?" *Future Internet* 16(3), 99. DOI 10.3390/fi16030099.
  - Documents waning interest in linked open government data after the early 2010s. Useful for motivation and for the threats-to-validity section.
  - [DOI](https://doi.org/10.3390/fi16030099)
- **Sanovia, Y., Sembiring, J., Arman, A.A., Sunindyo, W.D. (2026).** "An Indicator-Centric Knowledge Graph Model for Semantic Integration and Traceability of Official Statistical Indicators." *Data* 11(9), 242. DOI 10.3390/data11090242.
  - Reuses existing vocabularies and is evaluated with SPARQL competency questions.
  - [DOI](https://doi.org/10.3390/data11090242)

**SHACL validation and shape extraction**

- **Rabbani, K., Lissandrini, M., Hose, K. (2023).** "Extraction of Validating Shapes from Very Large Knowledge Graphs." *PVLDB* 16(5), 1023–1032. DOI 10.14778/3579075.3579078. [DOI](https://doi.org/10.14778/3579075.3579078)
- **Rabbani, K., Lissandrini, M., Hose, K. (2022).** "SHACL and ShEx in the Wild: A Community Survey on Validating Shapes Generation and Adoption." *WWW '22 Companion*, 260–263. DOI 10.1145/3487553.3524253. [DOI](https://doi.org/10.1145/3487553.3524253)
- **Figuera, M., Rohde, P.D., Vidal, M.-E. (2021).** "Trav-SHACL: Efficiently Validating Networks of SHACL Constraints." *WWW '21*, 3337–3348. DOI 10.1145/3442381.3449877. [DOI](https://doi.org/10.1145/3442381.3449877)
- **Omran, P.G., Taylor, K., Rodríguez Méndez, S.J., Haller, A. (2022/2023).** "Learning SHACL shapes from knowledge graphs." *Semantic Web* 14(1), 101–121. DOI 10.3233/SW-223063. [DOI](https://doi.org/10.3233/sw-223063)
- **Duan, X., Chaves-Fraga, D., Dimou, A. (2025).** "SCOOP-UI: SHACL Shape Extraction in Just a Click!" LNCS, 197–201. DOI 10.1007/978-3-031-78952-6_26. [DOI](https://doi.org/10.1007/978-3-031-78952-6_26)
- **Hmimou, A., Jovanović, P., Nadal, S., Romero, O., Queralt, A. (2025).** "Operationalizing and Automating Data Validation in Data Spaces." *Data Science and Engineering*. DOI 10.1007/s41019-025-00317-7. [DOI](https://doi.org/10.1007/s41019-025-00317-7)

**Knowledge-graph construction (R2RML/RML)**

- **Oo, S.M., De Meester, B., Taelman, R., Colpaert, P. (2025).** "Algebraic Mapping Operators for Knowledge Graph Generation." *Semantic Web* 16(5). DOI 10.1177/22104968251361350. [DOI](https://doi.org/10.1177/22104968251361350)
- **Arenas-Guerrero, J. et al. (2021).** "Knowledge Graph Construction with R2RML and RML: An ETL System-based Overview." KGCW workshop; no DOI in OpenAlex. [OpenAlex search result](https://api.openalex.org/works?search=Knowledge%20Graph%20Construction%20with%20R2RML%20and%20RML)

**Foundational**

- **Hogan, A. et al. (2021).** "Knowledge Graphs." *ACM Computing Surveys* 54(4), 1–37. DOI 10.1145/3447772. [DOI](https://doi.org/10.1145/3447772)

**Anomaly detection in water consumption (for the anomaly-evaluation direction)**

- **Carrasco-Jiménez, J.C., Baldaro, F., Cucchietti, F. (2020).** "Detection of Anomalous Patterns in Water Consumption: An Overview of Approaches." *Advances in Intelligent Systems and Computing*, 19–33. DOI 10.1007/978-3-030-55180-3_2. [DOI](https://doi.org/10.1007/978-3-030-55180-3_2)

### Inferences
- **Must-cite set for a Related Work section:**
  - WHOW-KG: the closest "water consumption KG".
  - KnowWhereGraph (JWS 2024 and/or TGIS 2026) plus the GIScience 2025 topology paper: GeoKG and topology.
  - GeoSPARQL 1.1 (Car & Homburg 2022).
  - Rajabi et al. 2023 and Kević & Kuveždić Divjak 2025: Data Cube for open-government and census data, the latter combined with GeoSPARQL.
  - Quarati & Albertoni 2024: linked open government data viability.
  - Rabbani et al. 2023: SHACL.
  - Comunica (2018).
  - On the domain side: the two Medina-Rivas papers, the two Ramos-Bueno papers, and the W2GIS 2025 IPN paper.
- **Novelty claim.** No RDF/Linked-Data KG over Mexico City or any Mexican water-utility consumption data was found among the 2015–2026 records retrieved. The journal version can therefore claim novelty on (i) a Data Cube plus GeoSPARQL KG for Mexican utility data and (ii) a measured assessment of Wikidata/INEGI linkability for Mexican sub-municipal units. The claim should be phrased as "to our knowledge".
- **Upgrading validation.** The ICOKG paper validates with the IC-1/2/3/11 SPARQL integrity checks. A natural upgrade is to express the Data Cube integrity constraints, plus domain constraints (non-negative consumption, valid CVEGEO pattern `^09\d{3}$` for alcaldías, the IECM `cve_col` pattern), as SHACL shapes. Rabbani et al. (shape extraction) and Trav-SHACL are the relevant citations.

### Gaps
- **Water-specific statistical linked data.** No 2022–2026 paper was found that applies the RDF Data Cube vocabulary specifically to water-utility consumption data. WHOW-KG may do so internally; its ontology network was not inspected.
- **Data Cube to SHACL translation.** No peer-reviewed 2022–2026 work on translating the Data Cube integrity constraints (IC-1…IC-21) into SHACL was found. The community resources that may exist (GitHub, W3C mailing lists) were not checked.
- **Water KGs not searched.** Geoconnex/Internet of Water (US hydrologic linked data) and SAWGraph (US water-contamination KG, NSF Proto-OKN) were looked for but no peer-reviewed DOI was retrieved. Searching DROPS/TGDK or AGU proceedings may help.
- **Mexican Semantic Web / KG work.** Beyond Páez & Vilches-Blázquez (2022), Carrillo-Brenes & Vilches-Blázquez (2024) and Lopez-Rodriguez & Ceballos (2022), little turned up. A targeted search of Mexican venues (Research in Computing Science, Computación y Sistemas, and IJCOPI itself) was not done and would help with journal fit.

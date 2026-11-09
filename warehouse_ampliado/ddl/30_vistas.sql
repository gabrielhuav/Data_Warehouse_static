-- ============================================
-- Almacen ampliado: vistas de integracion
-- ============================================
-- No son el cubo de datos: solo muestran que los hechos nuevos y los originales se
-- cruzan por llaves reales.

DROP VIEW IF EXISTS v_colonia_conapo_contexto, v_zm_indicadores_agua, v_consumo_colonia_integrado, v_acuiferos_zmvm CASCADE;

-- Consumo facturado por colonia, primer semestre de 2019, con el contexto de otras fuentes
CREATE VIEW v_consumo_colonia_integrado AS
WITH consumo AS (
    SELECT id_ubicacion,
           SUM(consumo_total)     AS consumo_total_m3,
           SUM(consumo_total_dom) AS consumo_dom_m3
    FROM   fact_consumo_agua
    GROUP  BY id_ubicacion
), reportes AS (
    -- La fuente no registra fugas antes de 2021: de 2018 a 2020 solo trae "Falta de agua".
    -- Por eso las fugas se cuentan en 2021-2024 y no en el semestre del consumo.
    -- Solo agua potable: "Fuga" y "Falta de agua" tambien existen en agua tratada.
    SELECT r.id_ubicacion,
           COUNT(*) FILTER (WHERE tr.reporte = 'Falta de agua'
                              AND t.fecha BETWEEN DATE '2019-01-01' AND DATE '2019-06-30') AS falta_agua_2019_s1,
           COUNT(*) FILTER (WHERE tr.reporte = 'Fuga' AND t.anio >= 2021) AS fugas_2021_2024
    FROM   fact_reporte_agua r
    JOIN   dim_tiempo t USING (id_tiempo)
    JOIN   dim_tipo_reporte tr USING (id_tipo_reporte)
    WHERE  r.id_ubicacion IS NOT NULL AND tr.clasificacion = 'Agua Potable'
    GROUP  BY r.id_ubicacion
), clima AS (
    SELECT id_ubicacion,
           ROUND(AVG(tavg_c), 2) AS tavg_c,
           ROUND(SUM(precip_mm), 1) AS precip_mm
    FROM   fact_clima_colonia c
    JOIN   dim_tiempo t USING (id_tiempo)
    WHERE  t.anio = 2019 AND t.mes <= 6
    GROUP  BY id_ubicacion
)
SELECT u.id_ubicacion, u.alcaldia, u.colonia, u.cve_mun,
       c.consumo_total_m3, c.consumo_dom_m3,
       u.pob_censo_2020, u.viv_hab_censo_2020,
       ROUND(c.consumo_dom_m3 * 1000 / NULLIF(u.pob_censo_2020 * 181, 0), 1) AS litros_hab_dia_dom,
       COALESCE(r.falta_agua_2019_s1, 0) AS falta_agua_2019_s1,
       COALESCE(r.fugas_2021_2024, 0)    AS fugas_2021_2024,
       cl.tavg_c, cl.precip_mm,
       s.vlm_media_cm_anio, s.vlm_p90_cm_anio - s.vlm_p10_cm_anio AS vlm_rango_cm_anio,
       cc.gm_2020 AS grado_marginacion_conapo
FROM   dim_ubicacion u
LEFT   JOIN consumo c  USING (id_ubicacion)
LEFT   JOIN reportes r USING (id_ubicacion)
LEFT   JOIN clima cl   USING (id_ubicacion)
LEFT   JOIN fact_subsidencia_colonia s USING (id_ubicacion)
LEFT   JOIN dim_colonia_conapo cc ON cc.cve_col = u.cve_col_conapo;

-- Contexto SACMEX mostrado sobre los poligonos CONAPO de la ZM. NO es una
-- desagregacion espacial de volumen o reportes al poligono: cada unidad SACMEX
-- se enlaza entera al poligono con mas puntos (>=50 %; empate: menor clave
-- numerica CONAPO) o por nombre de respaldo.
-- pob_total es la poblacion CONAPO del poligono; pob_sacmex es la suma de las
-- poblaciones urbanas asignadas a puntos SACMEX a <=750 m dentro de la alcaldia.
-- Las tasas son proxies sobre ese segundo soporte, no tasas reales del poligono.
-- Los reportes se asignan por nombre o punto cercano (<=1 km): tampoco son un
-- conteo de eventos recortado al poligono CONAPO. No dividir por pob_total.
-- Una poblacion parcial no puede normalizar un numerador del conjunto completo;
-- la tasa domestica requiere ademas un subtotal domestico disponible en cada unidad.
-- Eso no garantiza cobertura completa de sus registros, cuentas o bimestres.
CREATE VIEW v_colonia_conapo_contexto AS
WITH sacmex AS (
    SELECT u.cve_col_conapo AS cve_col,
           COUNT(*) AS colonias_sacmex,
           COUNT(*) FILTER (WHERE v.pob_censo_2020 > 0) AS colonias_con_pob,
           COUNT(v.consumo_dom_m3) AS colonias_con_dom,
           SUM(v.consumo_dom_m3) AS consumo_dom_m3,
           SUM(v.pob_censo_2020) FILTER (WHERE v.pob_censo_2020 > 0) AS pob_sacmex,
           SUM(v.falta_agua_2019_s1) AS falta_agua_2019_s1,
           SUM(v.fugas_2021_2024) AS fugas_2021_2024,
           AVG(v.vlm_media_cm_anio) AS vlm_media_cm_anio
    FROM   v_consumo_colonia_integrado v
    JOIN   dim_ubicacion u USING (id_ubicacion)
    WHERE  u.cve_col_conapo IS NOT NULL
    GROUP  BY u.cve_col_conapo
)
SELECT c.cve_col, c.cve_mun, c.colonia,
       ROUND(c.pob_total) AS pob_total,
       ROUND(c.pct_ocup_sin_agua, 2) AS pct_sin_agua,
       ROUND(c.pct_ocup_sin_drenaje, 2) AS pct_sin_drenaje,
       ROUND(c.im_2020, 2) AS im_2020, c.gm_2020,
       s.colonias_sacmex, s.colonias_con_pob, s.colonias_con_dom,
       s.pob_sacmex, s.consumo_dom_m3,
       CASE WHEN s.colonias_con_pob = s.colonias_sacmex
                  AND s.colonias_con_dom = s.colonias_sacmex
            THEN ROUND(s.consumo_dom_m3 * 1000.0 / NULLIF(s.pob_sacmex * 181, 0), 1)
            END AS litros_hab_dia_dom,
       s.falta_agua_2019_s1,
       CASE WHEN s.colonias_con_pob = s.colonias_sacmex
            THEN ROUND(s.falta_agua_2019_s1 * 1000.0 / NULLIF(s.pob_sacmex, 0), 2)
            END AS falta_por_mil_hab,
       s.fugas_2021_2024,
       CASE WHEN s.colonias_con_pob = s.colonias_sacmex
            THEN ROUND(s.fugas_2021_2024 * 1000.0 / NULLIF(s.pob_sacmex, 0), 2)
            END AS fugas_por_mil_hab,
       ROUND(s.vlm_media_cm_anio, 2) AS vlm_cm_anio
FROM   dim_colonia_conapo c
JOIN   dim_municipio m USING (cve_mun)
LEFT   JOIN sacmex s USING (cve_col)
WHERE  m.en_zm_ciudad_mexico;

-- Indicadores por municipio de la ZM de Ciudad de Mexico. En las alcaldias el volumen
-- viene de SACMEX y en los municipios del Estado de Mexico del CNGMD (referencia 2018).
--
-- El volumen del CNGMD no se puede usar sin revisar: un 0 suele ser "no reporto" (Nezahualcoyotl
-- tiene 211,749 tomas domesticas y ningun volumen) y hay valores imposibles, de menos de 1 a casi
-- 1,000 l/hab/dia. Los datos crudos no se tocan: calidad_volumen los clasifica. La banda de 10 a
-- 400 l/hab/dia es una decision del analisis para separar lo evidentemente mal reportado, no
-- una medida de consumo real. Lo mismo vale para razon_ingreso_shcp fuera de 0.1 a 10.
-- Normalizacion municipal: volumen anualizado /365 y poblacion CONAPO de mitad
-- de 2019. En SACMEX S1 se conserva x2/365 (equivalente a 182.5 dias), no el
-- promedio del semestre /181 con OCUPVIVPAR 2020 de la Tabla 4. Son bases distintas;
-- tampoco son el soporte censal urbano por proximidad de la vista de colonias.
CREATE VIEW v_zm_indicadores_agua AS
WITH sacmex AS (
    SELECT u.cve_mun, SUM(f.consumo_total_dom) * 2 AS vol_dom_anualizado_m3
    FROM   fact_consumo_agua f JOIN dim_ubicacion u USING (id_ubicacion)
    GROUP  BY u.cve_mun
), cngmd AS (
    SELECT cve_mun, SUM(volumen_m3) AS vol_dom_m3
    FROM   fact_facturacion_agua f
    JOIN   dim_tipo_toma t USING (id_tipo_toma)
    WHERE  f.anio = 2018 AND t.descripcion ILIKE 'dom%'
    GROUP  BY cve_mun
), base AS (
    SELECT m.cve_mun, m.nom_ent, m.nom_mun, m.municipio_central,
           p.pob_mitad_anio AS pob_2019,
           COALESCE(s.vol_dom_anualizado_m3, NULLIF(c.vol_dom_m3, 0)) AS vol_dom_m3_anio,
           CASE WHEN s.cve_mun IS NOT NULL THEN 'SACMEX 2019 S1 x 2' ELSE 'CNGMD 2018' END AS fuente_volumen,
           a.pct_poblacion_servida,
           a.tomas_total_medidor_func, a.tomas_total_medidor_sin_func, a.tomas_total_sin_medidor,
           a.ingreso_agua_pesos AS ingreso_cngmd_2018,
           r18.monto_agua_pesos AS recaudacion_shcp_2018,
           r18.tomas_pagadas    AS tomas_pagadas_2018,
           m.pct_ocup_sin_agua_2020, m.gm_2020,
           sb.vlm_media_cm_anio
    FROM   dim_municipio m
    LEFT   JOIN fact_poblacion_municipio p ON p.cve_mun = m.cve_mun AND p.anio = 2019
    LEFT   JOIN sacmex s ON s.cve_mun = m.cve_mun
    LEFT   JOIN cngmd c  ON c.cve_mun = m.cve_mun
    LEFT   JOIN fact_agua_municipio a ON a.cve_mun = m.cve_mun AND a.anio = 2018
    LEFT   JOIN fact_recaudacion_agua r18 ON r18.cve_mun = m.cve_mun AND r18.anio = 2018
    LEFT   JOIN fact_subsidencia_municipio sb ON sb.cve_mun = m.cve_mun
    WHERE  m.en_zm_ciudad_mexico
)
SELECT b.*,
       l.litros_hab_dia_dom,
       CASE WHEN b.vol_dom_m3_anio IS NULL THEN 'sin dato'
            WHEN l.litros_hab_dia_dom NOT BETWEEN 10 AND 400 THEN 'atipico'
            ELSE 'plausible' END AS calidad_volumen,
       r.razon_ingreso_shcp
FROM   base b
CROSS  JOIN LATERAL (SELECT ROUND(b.vol_dom_m3_anio * 1000 / NULLIF(b.pob_2019 * 365, 0), 1) AS litros_hab_dia_dom) l
CROSS  JOIN LATERAL (SELECT ROUND(b.ingreso_cngmd_2018 / NULLIF(b.recaudacion_shcp_2018, 0), 2) AS razon_ingreso_shcp) r;

-- Acuiferos de la ZMVM: balance oficial y lecturas de 2019 de sus pozos. Un acuifero entra si
-- cubre al menos 1 % de algun municipio de la ZM, para no contar astillas de los bordes.
CREATE VIEW v_acuiferos_zmvm AS
SELECT a.clv_acui, a.nom_acui, a.area_km2,
       d.recarga_total, d.vol_extraccion, d.dma_negativa,
       ROUND(d.vol_extraccion / NULLIF(d.recarga_total, 0), 2) AS extraccion_entre_recarga,
       COUNT(DISTINCT p.id_pozo) AS pozos,
       COUNT(n.anio) AS lecturas_2019,
       ROUND(AVG(n.profundidad_nivel_m), 1) AS nivel_medio_2019_m
FROM   dim_acuifero a
JOIN   fact_disponibilidad_acuifero d USING (clv_acui)
LEFT   JOIN dim_pozo p USING (clv_acui)
LEFT   JOIN fact_nivel_piezometrico n ON n.id_pozo = p.id_pozo AND n.anio = 2019
WHERE  a.clv_acui IN (SELECT DISTINCT clv_acui FROM puente_municipio_acuifero x
                      JOIN dim_municipio m USING (cve_mun)
                      WHERE m.en_zm_ciudad_mexico AND x.pct_municipio >= 1)
GROUP  BY a.clv_acui, a.nom_acui, a.area_km2, d.recarga_total, d.vol_extraccion, d.dma_negativa;

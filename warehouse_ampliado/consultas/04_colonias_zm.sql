-- Colonias de la ZM (poligonos de CONAPO). Marginacion y acceso al agua cubren toda la ZM; consumo
-- y reportes solo existen en la CDMX. Una colonia de CONAPO puede reunir varias de SACMEX, y por
-- eso se suman. Las fugas son de 2021-2024: la fuente no las registra antes.
WITH sacmex AS (
    SELECT u.cve_col_conapo AS cve_col,
           COUNT(*) AS colonias_sacmex,
           SUM(v.consumo_dom_m3) AS consumo_dom_m3,
           SUM(v.pob_censo_2020) AS pob_sacmex,
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
       s.colonias_sacmex,
       ROUND(s.consumo_dom_m3 * 1000 / NULLIF(s.pob_sacmex * 181, 0), 1) AS litros_hab_dia_dom,
       s.falta_agua_2019_s1,
       ROUND(s.falta_agua_2019_s1 * 1000.0 / NULLIF(s.pob_sacmex, 0), 2) AS falta_por_mil_hab,
       s.fugas_2021_2024,
       ROUND(s.fugas_2021_2024 * 1000.0 / NULLIF(s.pob_sacmex, 0), 2) AS fugas_por_mil_hab,
       ROUND(s.vlm_media_cm_anio, 2) AS vlm_cm_anio
FROM   dim_colonia_conapo c
JOIN   dim_municipio m USING (cve_mun)
LEFT   JOIN sacmex s USING (cve_col)
WHERE  m.en_zm_ciudad_mexico
ORDER  BY c.cve_col;

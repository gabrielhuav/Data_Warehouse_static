-- Los 63 municipios de la ZM de Ciudad de Mexico. El volumen viene de SACMEX en las alcaldias y
-- del CNGMD en los demas; calidad_volumen dice cuales son utilizables.
WITH acuifero AS (
    SELECT DISTINCT ON (x.cve_mun) x.cve_mun, a.nom_acui, ROUND(x.pct_municipio, 1) AS pct_acuifero
    FROM   puente_municipio_acuifero x
    JOIN   dim_acuifero a USING (clv_acui)
    ORDER  BY x.cve_mun, x.pct_municipio DESC
)
SELECT z.cve_mun, z.nom_ent, z.nom_mun, z.municipio_central, z.pob_2019,
       z.fuente_volumen, z.litros_hab_dia_dom, z.calidad_volumen,
       ROUND(z.pct_poblacion_servida, 1) AS pct_poblacion_servida,
       ROUND(100.0 * m.vph_agua_dentro_2020 / NULLIF(m.viv_part_hab_2020, 0), 1) AS pct_viv_agua_dentro,
       ROUND(z.pct_ocup_sin_agua_2020, 2) AS pct_ocup_sin_agua,
       ROUND(m.im_2020, 2) AS im_2020, z.gm_2020,
       ROUND(z.recaudacion_shcp_2018 / NULLIF(z.pob_2019, 0), 1) AS recaudacion_pc_2018,
       z.razon_ingreso_shcp,
       ROUND(z.vlm_media_cm_anio, 2) AS vlm_cm_anio,
       a.nom_acui AS acuifero_principal, a.pct_acuifero
FROM   v_zm_indicadores_agua z
JOIN   dim_municipio m USING (cve_mun)
LEFT   JOIN acuifero a USING (cve_mun)
ORDER  BY z.cve_mun;

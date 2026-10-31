-- Acceso al agua entubada en las colonias de la ZM, por entidad. personas_sin_agua estima los
-- ocupantes de viviendas sin agua entubada: poblacion de la colonia por su porcentaje.
SELECT m.nom_ent,
       COUNT(*) AS colonias,
       ROUND(SUM(c.pob_total)) AS poblacion,
       ROUND(SUM(c.pob_total * c.pct_ocup_sin_agua / 100)) AS personas_sin_agua,
       COUNT(*) FILTER (WHERE c.pct_ocup_sin_agua > 5) AS colonias_mas_de_5_pct,
       ROUND(SUM(c.pob_total) FILTER (WHERE c.pct_ocup_sin_agua > 5)) AS poblacion_mas_de_5_pct
FROM   dim_colonia_conapo c
JOIN   dim_municipio m USING (cve_mun)
WHERE  m.en_zm_ciudad_mexico
GROUP  BY m.nom_ent
ORDER  BY m.nom_ent;

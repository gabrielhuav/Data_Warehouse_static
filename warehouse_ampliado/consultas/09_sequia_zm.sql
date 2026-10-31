-- Monitor de Sequia en los municipios de la ZM. Severidad: -1 sin sequia, 0 anormalmente seco,
-- de 1 a 4 sequia moderada a excepcional.
SELECT s.cve_mun, t.fecha, c.severidad
FROM   fact_sequia_municipio s
JOIN   dim_tiempo t USING (id_tiempo)
JOIN   dim_categoria_sequia c USING (id_categoria)
JOIN   dim_municipio m USING (cve_mun)
WHERE  m.en_zm_ciudad_mexico
ORDER  BY t.fecha, s.cve_mun;

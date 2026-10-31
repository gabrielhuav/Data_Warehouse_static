-- Lo que une a la CDMX con el resto de la ZM en el grafo: vecindades que cruzan el limite, en
-- municipios y en colonias, y acuiferos que quedan bajo los dos lados.
WITH lados AS (
    SELECT v.cve_col, v.cve_vecina
    FROM   puente_colonia_vecina v
    JOIN   dim_colonia_conapo a ON a.cve_col = v.cve_col
    JOIN   dim_colonia_conapo b ON b.cve_col = v.cve_vecina
    WHERE  LEFT(a.cve_mun, 2) = '09' AND LEFT(b.cve_mun, 2) <> '09'
), acuiferos AS (
    SELECT x.clv_acui
    FROM   puente_municipio_acuifero x
    JOIN   dim_municipio m USING (cve_mun)
    WHERE  m.en_zm_ciudad_mexico AND x.pct_municipio >= 1
    GROUP  BY x.clv_acui
    HAVING BOOL_OR(m.cve_ent = '09') AND BOOL_OR(m.cve_ent <> '09')
)
SELECT 'pares de municipios vecinos' AS medida, COUNT(*)::NUMERIC / 2 AS valor FROM puente_municipio_vecino
UNION ALL
SELECT 'pares de municipios que cruzan el limite de la CDMX', COUNT(*)
FROM   puente_municipio_vecino WHERE LEFT(cve_mun, 2) = '09' AND LEFT(cve_vecino, 2) <> '09'
UNION ALL
SELECT 'kilometros de frontera de la CDMX con otros municipios de la ZM', ROUND(SUM(frontera_km), 1)
FROM   puente_municipio_vecino WHERE LEFT(cve_mun, 2) = '09' AND LEFT(cve_vecino, 2) <> '09'
UNION ALL
SELECT 'pares de colonias vecinas', COUNT(*)::NUMERIC / 2 FROM puente_colonia_vecina
UNION ALL
SELECT 'pares de colonias que cruzan el limite de la CDMX', COUNT(*) FROM lados
UNION ALL
SELECT 'colonias de la CDMX en la frontera', COUNT(DISTINCT cve_col) FROM lados
UNION ALL
SELECT 'colonias de otras entidades en la frontera', COUNT(DISTINCT cve_vecina) FROM lados
UNION ALL
SELECT 'acuiferos bajo la CDMX y bajo otra entidad', COUNT(*) FROM acuiferos;

-- Las 15 presas con serie diaria del SIH. El volumen es la columna VolumenAlm(Mm3) de la fuente.
SELECT e.clave, e.nombre, e.estado, e.latitud, e.longitud, e.cuenca_disponibilidad,
       MAX(t.fecha) AS ultima_fecha,
       ROUND((ARRAY_AGG(f.volumen_hm3 ORDER BY t.fecha DESC) FILTER (WHERE f.volumen_hm3 IS NOT NULL))[1], 1) AS volumen_ultimo_hm3,
       ROUND(AVG(f.volumen_hm3) FILTER (WHERE t.anio = 2019), 1) AS volumen_medio_2019_hm3,
       ROUND(AVG(f.volumen_hm3) FILTER (WHERE t.anio = 2023), 1) AS volumen_medio_2023_hm3
FROM   dim_estacion_hidrometrica e
JOIN   fact_presa_diaria f USING (clave)
JOIN   dim_tiempo t USING (id_tiempo)
GROUP  BY e.clave, e.nombre, e.estado, e.latitud, e.longitud, e.cuenca_disponibilidad
ORDER  BY e.clave;

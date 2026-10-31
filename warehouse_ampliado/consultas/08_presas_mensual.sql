-- Volumen medio mensual de cada presa desde 2018, para la grafica de cada una.
SELECT f.clave, TO_CHAR(t.fecha, 'YYYY-MM') AS mes, ROUND(AVG(f.volumen_hm3), 2) AS volumen_hm3
FROM   fact_presa_diaria f
JOIN   dim_tiempo t USING (id_tiempo)
WHERE  t.anio >= 2018 AND f.volumen_hm3 IS NOT NULL
GROUP  BY f.clave, TO_CHAR(t.fecha, 'YYYY-MM')
ORDER  BY f.clave, mes;

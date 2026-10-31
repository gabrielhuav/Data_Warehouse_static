-- Pozos de esos acuiferos con lectura en 2010 y en 2019. descenso_m positivo: el nivel bajo.
SELECT p.id_pozo, p.nom_pozo, p.clv_acui, a.nom_acui, p.latitud, p.longitud,
       n10.profundidad_nivel_m AS profundidad_2010_m,
       n19.profundidad_nivel_m AS profundidad_2019_m,
       ROUND(n19.profundidad_nivel_m - n10.profundidad_nivel_m, 2) AS descenso_m
FROM   dim_pozo p
JOIN   dim_acuifero a USING (clv_acui)
JOIN   fact_nivel_piezometrico n10 ON n10.id_pozo = p.id_pozo AND n10.anio = 2010
JOIN   fact_nivel_piezometrico n19 ON n19.id_pozo = p.id_pozo AND n19.anio = 2019
WHERE  p.clv_acui IN (SELECT clv_acui FROM v_acuiferos_zmvm)
ORDER  BY p.id_pozo;

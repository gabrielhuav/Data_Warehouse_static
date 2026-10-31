-- Acuiferos que cubren al menos 1 % de algun municipio de la ZM: balance oficial en hm3/anio y
-- cambio del nivel en los pozos con lectura en 2010 y en 2019. Mas profundidad es nivel mas bajo.
WITH cambio AS (
    SELECT p.clv_acui, COUNT(*) AS pozos_2010_2019,
           ROUND(AVG(b.profundidad_nivel_m - a.profundidad_nivel_m), 1) AS descenso_medio_m
    FROM   dim_pozo p
    JOIN   fact_nivel_piezometrico a ON a.id_pozo = p.id_pozo AND a.anio = 2010
    JOIN   fact_nivel_piezometrico b ON b.id_pozo = p.id_pozo AND b.anio = 2019
    GROUP  BY p.clv_acui
)
SELECT v.clv_acui, v.nom_acui, ROUND(v.area_km2) AS area_km2,
       ROUND(v.recarga_total, 1) AS recarga_hm3, ROUND(v.vol_extraccion, 1) AS extraccion_hm3,
       ROUND(v.dma_negativa, 1) AS deficit_hm3, v.extraccion_entre_recarga,
       v.pozos, c.pozos_2010_2019, c.descenso_medio_m
FROM   v_acuiferos_zmvm v
LEFT   JOIN cambio c USING (clv_acui)
ORDER  BY v.extraccion_entre_recarga DESC, v.clv_acui;

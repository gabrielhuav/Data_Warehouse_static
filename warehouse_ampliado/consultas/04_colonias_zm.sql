-- Poligonos CONAPO con contexto agregado de unidades SACMEX enlazadas, no
-- volumen/reportes recortados a sus limites. pob_total es del poligono;
-- pob_sacmex es el denominador proxy de las tasas (manzanas urbanas a <=750 m
-- de puntos SACMEX). colonias_con_pob/dom permiten comprobar la cobertura.
-- La vista suprime tasas con poblacion parcial; la tasa domestica requiere un
-- subtotal disponible en cada unidad, sin afirmar cobertura temporal completa.
-- Las fugas son de 2021-2024: la fuente no las registra antes.
SELECT *
FROM   v_colonia_conapo_contexto
ORDER  BY cve_col;

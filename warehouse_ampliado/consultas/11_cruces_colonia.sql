-- Los cruces que solo existen por integrar las fuentes. Spearman: correlacion de rangos promedio
-- entre colonias de SACMEX con al menos 500 habitantes y volumen conocido.
WITH base AS (
    SELECT litros_hab_dia_dom AS litros,
           falta_agua_2019_s1 * 1000.0 / pob_censo_2020 AS falta,
           fugas_2021_2024    * 1000.0 / pob_censo_2020 AS fugas
    FROM   v_consumo_colonia_integrado
    WHERE  pob_censo_2020 >= 500 AND litros_hab_dia_dom IS NOT NULL
), r AS (
    SELECT litros, falta, fugas,
           (RANK() OVER (ORDER BY litros) + COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY litros DESC)) / 2.0 AS r_litros,
           (RANK() OVER (ORDER BY falta)  + COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY falta DESC))  / 2.0 AS r_falta,
           (RANK() OVER (ORDER BY fugas)  + COUNT(*) OVER () + 1 - RANK() OVER (ORDER BY fugas DESC))  / 2.0 AS r_fugas
    FROM   base
)
SELECT 'colonias comparadas' AS medida, COUNT(*)::NUMERIC AS valor FROM r
UNION ALL
SELECT 'Spearman litros facturados contra falta de agua 2019', ROUND(CORR(r_litros, r_falta)::NUMERIC, 3) FROM r
UNION ALL
SELECT 'Spearman litros facturados contra fugas 2021-2024', ROUND(CORR(r_litros, r_fugas)::NUMERIC, 3) FROM r
UNION ALL
SELECT 'Spearman falta de agua 2019 contra fugas 2021-2024', ROUND(CORR(r_falta, r_fugas)::NUMERIC, 3) FROM r
UNION ALL
SELECT 'colonias bajo 10 litros', COUNT(*) FILTER (WHERE litros < 10) FROM r
UNION ALL
SELECT 'falta de agua por mil hab, colonias bajo 10 litros', ROUND(AVG(falta) FILTER (WHERE litros < 10), 2) FROM r
UNION ALL
SELECT 'colonias con 10 litros o mas', COUNT(*) FILTER (WHERE litros >= 10) FROM r
UNION ALL
SELECT 'falta de agua por mil hab, colonias con 10 litros o mas', ROUND(AVG(falta) FILTER (WHERE litros >= 10), 2) FROM r;

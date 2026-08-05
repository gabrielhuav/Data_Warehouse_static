-- =====================================================================
-- queries.sql -- Parameterised retrieval queries
--
-- These are the four workloads benchmarked in the performance table of
-- the ICOKG 2026 paper, and the queries behind the FastAPI endpoints that
-- scripts/generar_datos_faltantes.py times:
--
--   Q1 -> /api/consumption?limit=100
--   Q2 -> /api/consumption/by-borough
--   Q3 -> /api/consumption/by-colonia-bimestre
--   Q4 -> /api/consumption/top?limit=10
--
-- Placeholders use psycopg2 named style (%(name)s). Every user-supplied
-- value is bound, never interpolated: no query in this file is built by
-- string concatenation.
--
-- PROVENANCE: reconstruction written for the camera-ready artefact.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1. Paginated retrieval with optional filters (the interface's table)
--     Params: anio, bimestre, alcaldia, colonia, limit, offset
--             (any filter may be NULL, in which case it is ignored)
-- ---------------------------------------------------------------------
SELECT t.anio,
       t.bimestre,
       t.fecha,
       l.alcaldia,
       l.colonia,
       d.nivel                AS indice_des,
       f.consumo_total,
       f.consumo_promedio,
       f.consumo_dom,
       f.consumo_no_dom,
       f.consumo_mixto
FROM   fact_water_consumption f
JOIN   dim_time      t USING (time_id)
JOIN   dim_location  l USING (location_id)
JOIN   dim_dev_index d USING (dev_index_id)
WHERE  (%(anio)s     IS NULL OR t.anio     = %(anio)s)
  AND  (%(bimestre)s IS NULL OR t.bimestre = %(bimestre)s)
  AND  (%(alcaldia)s IS NULL OR l.alcaldia = %(alcaldia)s)
  AND  (%(colonia)s  IS NULL OR l.colonia  = %(colonia)s)
ORDER  BY t.anio, t.bimestre, l.alcaldia, l.colonia
LIMIT  %(limit)s OFFSET %(offset)s;

-- ---------------------------------------------------------------------
-- Q2. Full aggregation by borough (full scan of the fact table)
--     Params: anio (nullable)
-- ---------------------------------------------------------------------
SELECT l.alcaldia,
       COUNT(*)                                                   AS n_registros,
       SUM(f.consumo_total)                                       AS total,
       AVG(f.consumo_promedio)                                    AS promedio,
       SUM(f.consumo_dom)                                         AS total_dom,
       SUM(f.consumo_no_dom)                                      AS total_no_dom,
       100.0 * SUM(f.consumo_no_dom)
             / NULLIF(SUM(f.consumo_total), 0)                    AS pct_no_dom
FROM   fact_water_consumption f
JOIN   dim_location l USING (location_id)
JOIN   dim_time     t USING (time_id)
WHERE  (%(anio)s IS NULL OR t.anio = %(anio)s)
GROUP  BY l.alcaldia
ORDER  BY total DESC;

-- ---------------------------------------------------------------------
-- Q3. Aggregation by neighbourhood and bimester (full scan + wide group)
--     Params: alcaldia (nullable), anio (nullable)
-- ---------------------------------------------------------------------
SELECT l.alcaldia,
       l.colonia,
       t.anio,
       t.bimestre,
       SUM(f.consumo_total)    AS total,
       AVG(f.consumo_promedio) AS promedio
FROM   fact_water_consumption f
JOIN   dim_location l USING (location_id)
JOIN   dim_time     t USING (time_id)
WHERE  (%(alcaldia)s IS NULL OR l.alcaldia = %(alcaldia)s)
  AND  (%(anio)s     IS NULL OR t.anio     = %(anio)s)
GROUP  BY l.alcaldia, l.colonia, t.anio, t.bimestre
ORDER  BY l.alcaldia, l.colonia, t.anio, t.bimestre;

-- ---------------------------------------------------------------------
-- Q4. Top-N neighbourhoods by total consumption (full scan + ordering)
--     Params: anio (nullable), bimestre (nullable), limit
-- ---------------------------------------------------------------------
SELECT l.alcaldia,
       l.colonia,
       SUM(f.consumo_total) AS total
FROM   fact_water_consumption f
JOIN   dim_location l USING (location_id)
JOIN   dim_time     t USING (time_id)
WHERE  (%(anio)s     IS NULL OR t.anio     = %(anio)s)
  AND  (%(bimestre)s IS NULL OR t.bimestre = %(bimestre)s)
GROUP  BY l.alcaldia, l.colonia
ORDER  BY total DESC
LIMIT  %(limit)s;

-- ---------------------------------------------------------------------
-- Q5. Atypicality score A_g used by the exploratory anomaly module.
--     A_g = |x_g - mu| / (sigma + epsilon), computed within each
--     territorial group. Params: anio (nullable), threshold
-- ---------------------------------------------------------------------
WITH por_grupo AS (
    SELECT l.alcaldia,
           l.colonia,
           t.anio,
           t.bimestre,
           SUM(f.consumo_total) AS x
    FROM   fact_water_consumption f
    JOIN   dim_location l USING (location_id)
    JOIN   dim_time     t USING (time_id)
    WHERE  (%(anio)s IS NULL OR t.anio = %(anio)s)
    GROUP  BY l.alcaldia, l.colonia, t.anio, t.bimestre
),
stats AS (
    SELECT alcaldia, colonia, anio, bimestre, x,
           AVG(x)       OVER (PARTITION BY colonia) AS mu,
           STDDEV_POP(x) OVER (PARTITION BY colonia) AS sigma
    FROM   por_grupo
)
SELECT alcaldia, colonia, anio, bimestre, x, mu, sigma,
       ABS(x - mu) / (COALESCE(sigma, 0) + 1e-9) AS a_g
FROM   stats
WHERE  ABS(x - mu) / (COALESCE(sigma, 0) + 1e-9) > %(threshold)s
ORDER  BY a_g DESC;

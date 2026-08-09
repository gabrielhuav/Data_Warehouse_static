-- ============================================
-- 2_geo.sql -- Coordenadas en dim_ubicacion
-- ============================================
-- Añadido para el camera-ready de ICOKG 2026.
-- NO modifica ningún archivo de Omar Pulido Morales: se ejecuta entre
-- 2_dim.sql y 3_fact.sql, mientras staging_consumo todavía existe.
--
-- SOBRE EL NOMBRE DEL ARCHIVO: el entrypoint de PostgreSQL ejecuta
--   for f in /docker-entrypoint-initdb.d/*
-- y el glob usa la colación del locale, no el orden ASCII. La colación de
-- diccionario ignora el guion bajo; un nombre con una letra adicional se
-- compararía antes de 2_dim.sql, con dim_ubicacion todavía
-- vacía. Con "2_geo" la comparación es "2geo" vs "2dim" (d < g) y el orden es
-- correcto bajo ambas colaciones. No renombrar sin comprobar esto.
--
-- Motivo: el CSV fuente trae latitud y longitud para los 71,102 registros
-- (todas dentro del bounding box de la CDMX), pero el esquema original las
-- descarta. La Sección 4 del artículo proyecta el almacén a RDF con GeoSPARQL
-- y necesita geometría. Esto la recupera sin tocar el pipeline existente.
--
-- No requiere PostGIS: la geometría se expone como WKT construido con
-- concatenación, que es lo que consume mapping.r2rml.ttl.
-- ============================================

-- Falla ruidosamente si el orden de ejecución se rompe otra vez.
DO $$
BEGIN
    IF (SELECT count(*) FROM dim_ubicacion) = 0 THEN
        RAISE EXCEPTION
          '2_geo.sql corrio con dim_ubicacion vacia: el orden de los scripts de '
          'init esta mal. Debe ejecutarse DESPUES de 2_dim.sql.';
    END IF;
END $$;

ALTER TABLE dim_ubicacion ADD COLUMN IF NOT EXISTS latitud  NUMERIC(9,6);
ALTER TABLE dim_ubicacion ADD COLUMN IF NOT EXISTS longitud NUMERIC(9,6);

-- Centroide de la colonia: media de las lecturas que le corresponden.
-- La dispersión intra-colonia es pequeña (mediana 0.004°, ~400 m), así que
-- el centroide es una representación razonable de la unidad territorial.
UPDATE dim_ubicacion u
SET    latitud  = c.lat,
       longitud = c.lon
FROM  (SELECT alcaldia,
              colonia,
              ROUND(AVG(latitud)::numeric,  6) AS lat,
              ROUND(AVG(longitud)::numeric, 6) AS lon
       FROM   staging_consumo
       WHERE  latitud  IS NOT NULL
         AND  longitud IS NOT NULL
         AND  latitud  BETWEEN  19.04 AND  19.60
         AND  longitud BETWEEN -99.36 AND -98.94
       GROUP  BY alcaldia, colonia) c
WHERE u.alcaldia = c.alcaldia
  AND u.colonia  = c.colonia;

-- Vista con la geometría en WKT, consumida por el GeometryMap de R2RML.
CREATE OR REPLACE VIEW v_ubicacion_geom AS
SELECT id_ubicacion,
       alcaldia,
       colonia,
       latitud,
       longitud,
       'POINT(' || longitud || ' ' || latitud || ')' AS wkt
FROM   dim_ubicacion
WHERE  latitud IS NOT NULL
  AND  longitud IS NOT NULL;

-- ============================================
-- Adyacencia territorial
-- ============================================
-- El ejemplo SPARQL del artículo usa agua:nearbyWithin1500m. El mapeo R2RML no puede
-- calcularlo por sí solo (materializa atributos y joins, no relaciones derivadas), así
-- que se deriva aquí: dos colonias son vecinas si sus centroides distan menos
-- de 1.5 km. Es una aproximación por proximidad, no adyacencia de polígonos,
-- y el artículo debe decirlo con esas palabras.
DROP TABLE IF EXISTS dim_ubicacion_adyacencia;
CREATE TABLE dim_ubicacion_adyacencia AS
SELECT a.id_ubicacion AS id_origen,
       b.id_ubicacion AS id_vecino,
       ROUND((111.32 * SQRT(
              POWER(a.latitud - b.latitud, 2) +
              POWER((a.longitud - b.longitud) * COS(RADIANS(a.latitud)), 2)
       ))::numeric, 3) AS distancia_km
FROM   dim_ubicacion a
JOIN   dim_ubicacion b
  ON   a.id_ubicacion <> b.id_ubicacion
WHERE  a.latitud IS NOT NULL AND b.latitud IS NOT NULL
  AND  111.32 * SQRT(
         POWER(a.latitud - b.latitud, 2) +
         POWER((a.longitud - b.longitud) * COS(RADIANS(a.latitud)), 2)
       ) <= 1.5;

CREATE INDEX idx_adyacencia_origen ON dim_ubicacion_adyacencia (id_origen);

-- Comprobación (sale en el log de arranque del contenedor)
DO $$
DECLARE n_geo INT; n_ady INT;
BEGIN
    SELECT COUNT(*) INTO n_geo FROM dim_ubicacion WHERE latitud IS NOT NULL;
    SELECT COUNT(*) INTO n_ady FROM dim_ubicacion_adyacencia;
    IF n_geo = 0 THEN
        RAISE EXCEPTION '2_geo.sql no asigno ninguna coordenada';
    END IF;
    RAISE NOTICE '2_geo: % ubicaciones con coordenada, % pares adyacentes',
                 n_geo, n_ady;
END $$;

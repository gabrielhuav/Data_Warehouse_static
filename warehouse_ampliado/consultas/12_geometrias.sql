-- Geometria simplificada de lo que dibuja el mapa, en GeoJSON.
SELECT capa, clave, geojson
FROM   geo_territorio
ORDER  BY capa, clave;

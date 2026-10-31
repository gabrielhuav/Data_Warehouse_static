-- Sitios de la red de calidad del agua en la ZM, con el semaforo que publica CONAGUA.
SELECT s.id_sitio, s.clave_sitio, s.tipo_agua, s.nombre, s.municipio, s.latitud, s.longitud,
       s.periodo, s.semaforo, s.contaminantes
FROM   dim_sitio_calidad s
JOIN   dim_municipio m USING (cve_mun)
WHERE  m.en_zm_ciudad_mexico AND s.latitud IS NOT NULL
ORDER  BY s.id_sitio;

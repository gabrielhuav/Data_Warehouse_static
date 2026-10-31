-- Municipios de la ZM que comparten frontera, medidos sobre los poligonos oficiales. Cada par
-- aparece en los dos sentidos. Es la relacion que el grafo publica como agua:sharesBoundaryWith.
SELECT v.cve_mun, m.nom_mun, m.nom_ent,
       v.cve_vecino, n.nom_mun AS vecino, n.nom_ent AS entidad_vecino, v.frontera_km
FROM   puente_municipio_vecino v
JOIN   dim_municipio m ON m.cve_mun = v.cve_mun
JOIN   dim_municipio n ON n.cve_mun = v.cve_vecino
ORDER  BY v.cve_mun, v.cve_vecino;

-- ============================================
-- Almacen ampliado: deja el almacen como lo construye warehouse/
-- ============================================
-- Solo quita lo que agrega warehouse_ampliado. Las fechas nuevas se identifican porque
-- ningun hecho original las usa: fact_clima referencia los 181 dias de dim_tiempo.

DROP VIEW IF EXISTS v_zm_indicadores_agua, v_consumo_colonia_integrado, v_acuiferos_zmvm CASCADE;

DROP TABLE IF EXISTS
    fact_vulnerabilidad_alcaldia, fact_subsidencia_municipio, fact_subsidencia_colonia,
    fact_clima_municipio, fact_clima_colonia, fact_reporte_agua, fact_vivienda_agua_ageb,
    fact_calidad_agua, dim_parametro_calidad, dim_sitio_calidad, fact_presa_diaria,
    fact_caudal_diario, fact_sequia_municipio, fact_nivel_piezometrico,
    fact_disponibilidad_acuifero, fact_planta_agua, fact_fuente_captacion,
    fact_abasto_localidad, fact_prestador_agua, fact_facturacion_agua, fact_agua_municipio,
    fact_recaudacion_agua, fact_poblacion_municipio,
    dim_medio_recepcion, dim_tipo_reporte, dim_tipo_toma, dim_tipo_fuente_captacion,
    dim_categoria_sequia, dim_estacion_hidrometrica, puente_municipio_acuifero, dim_pozo,
    dim_acuifero, control_ingesta_fuentes, geo_territorio,
    puente_municipio_vecino, puente_colonia_vecina
    CASCADE;

ALTER TABLE dim_ubicacion
    DROP COLUMN IF EXISTS cve_mun,
    DROP COLUMN IF EXISTS colonia_norm,
    DROP COLUMN IF EXISTS cve_col_conapo,
    DROP COLUMN IF EXISTS enlace_conapo,
    DROP COLUMN IF EXISTS n_manzanas_censo,
    DROP COLUMN IF EXISTS pob_censo_2020,
    DROP COLUMN IF EXISTS viv_hab_censo_2020,
    DROP COLUMN IF EXISTS vph_agua_dentro_2020,
    DROP COLUMN IF EXISTS vph_tinaco_2020,
    DROP COLUMN IF EXISTS vph_cisterna_2020,
    DROP COLUMN IF EXISTS ue_denue_2026,
    DROP COLUMN IF EXISTS ue_agua_intensiva_denue_2026;

DROP TABLE IF EXISTS dim_colonia_conapo, dim_municipio, dim_anio CASCADE;

DELETE FROM dim_tiempo t
WHERE NOT EXISTS (SELECT 1 FROM fact_clima c WHERE c.id_tiempo = t.id_tiempo)
  AND NOT EXISTS (SELECT 1 FROM fact_consumo_agua f WHERE f.id_tiempo = t.id_tiempo);

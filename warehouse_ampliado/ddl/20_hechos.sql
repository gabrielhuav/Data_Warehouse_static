-- ============================================
-- Almacen ampliado: hechos
-- ============================================

-- Poblacion a mitad de anio por municipio (CONAPO): denominador para 2019
CREATE TABLE fact_poblacion_municipio (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    pob_mitad_anio BIGINT NOT NULL,
    PRIMARY KEY (cve_mun, anio)
);

-- Recaudacion por derechos de agua (SHCP), por municipio y ciclo
CREATE TABLE fact_recaudacion_agua (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    tomas_pagadas BIGINT,
    monto_agua_pesos NUMERIC,
    monto_percapita_pesos NUMERIC,
    poblacion BIGINT,
    PRIMARY KEY (cve_mun, anio)
);

-- CNGMD, por municipio y anio de referencia (2018 y 2020)
CREATE TABLE fact_agua_municipio (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    con_red_publica BOOLEAN,
    pct_poblacion_servida NUMERIC,
    prestadores INT,
    km_red_conduccion NUMERIC,
    km_red_distribucion NUMERIC,
    km_conduccion_rehabilitada NUMERIC,
    km_distribucion_rehabilitada NUMERIC,
    tomas_dom_medidor_func BIGINT,
    tomas_dom_medidor_sin_func BIGINT,
    tomas_dom_sin_medidor BIGINT,
    tomas_total_medidor_func BIGINT,
    tomas_total_medidor_sin_func BIGINT,
    tomas_total_sin_medidor BIGINT,
    factura_servicio BOOLEAN,
    gasto_total_pesos NUMERIC,
    ingreso_agua_pesos NUMERIC,
    ingreso_total_pesos NUMERIC,
    subsidio_federal_pesos NUMERIC,
    subsidio_estatal_pesos NUMERIC,
    subsidio_municipal_pesos NUMERIC,
    compra_agua_bloque BOOLEAN,
    vol_bloque_superficial_m3 NUMERIC,
    vol_bloque_subterraneo_m3 NUMERIC,
    tanques INT,
    capacidad_tanques_m3 NUMERIC,
    PRIMARY KEY (cve_mun, anio)
);

-- CNGMD: facturacion por tipo de toma y esquema. Es el analogo municipal de la
-- separacion domestico/no domestico de SACMEX.
CREATE TABLE fact_facturacion_agua (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    id_tipo_toma INT NOT NULL REFERENCES dim_tipo_toma (id_tipo_toma),
    esquema VARCHAR(16) NOT NULL CHECK (esquema IN ('cuota fija', 'servicio medido')),
    num_tomas BIGINT,
    recibos BIGINT,
    monto_facturado_pesos NUMERIC,
    monto_recaudado_pesos NUMERIC,
    volumen_m3 NUMERIC,
    PRIMARY KEY (cve_mun, anio, id_tipo_toma, esquema)
);

-- CNGMD: prestadores del servicio. Dias y horas de suministro solo existen en 2020.
CREATE TABLE fact_prestador_agua (
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    id_prestador INT NOT NULL,
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    regimen TEXT,
    ambito  TEXT,
    dias_semana_suministro NUMERIC,
    horas_dia_suministro NUMERIC,
    distribuye_pipas BOOLEAN,
    volumen_pipas_m3_mes NUMERIC,
    PRIMARY KEY (anio, id_prestador)
);

-- CNGMD 2020: suministro por localidad atendida
CREATE TABLE fact_abasto_localidad (
    id_abasto INT PRIMARY KEY,
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    id_prestador INT NOT NULL,
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    cve_loc VARCHAR(9),
    dias_semana_suministro NUMERIC,
    horas_dia_suministro NUMERIC
);
CREATE INDEX idx_abasto_mun ON fact_abasto_localidad (cve_mun);

-- CNGMD: obras de toma, una fila por fuente
CREATE TABLE fact_fuente_captacion (
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    id_fuente INT NOT NULL,
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    id_tipo_fuente INT REFERENCES dim_tipo_fuente_captacion (id_tipo_fuente),
    nombre  TEXT,
    profundidad_m NUMERIC,
    macromedidor INT,
    capacidad_ls NUMERIC,
    gasto_promedio_ls NUMERIC,
    volumen_anual_m3 NUMERIC,
    horas_dia NUMERIC,
    dias_anio NUMERIC,
    PRIMARY KEY (anio, id_fuente)
);
CREATE INDEX idx_fuente_mun ON fact_fuente_captacion (cve_mun);

-- CNGMD: plantas potabilizadoras y de tratamiento
CREATE TABLE fact_planta_agua (
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    tipo_planta VARCHAR(14) NOT NULL CHECK (tipo_planta IN ('potabilizadora', 'tratamiento')),
    id_planta INT NOT NULL,
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    nombre  TEXT,
    opera   BOOLEAN,
    capacidad_ls NUMERIC,
    caudal_promedio_ls NUMERIC,
    PRIMARY KEY (anio, tipo_planta, id_planta)
);
CREATE INDEX idx_planta_mun ON fact_planta_agua (cve_mun);

-- Disponibilidad media anual por acuifero, en hm3/anio
CREATE TABLE fact_disponibilidad_acuifero (
    clv_acui CHAR(4) PRIMARY KEY REFERENCES dim_acuifero (clv_acui),
    recarga_total NUMERIC,
    descarga_natural NUMERIC,
    vol_concesionado NUMERIC,
    vol_libre_alumbramiento NUMERIC,
    vol_pendiente_titulacion NUMERIC,
    vol_reservas NUMERIC,
    vol_extraccion NUMERIC,
    dma_positiva NUMERIC,
    dma_negativa NUMERIC
);

-- Profundidad del nivel estatico por pozo y anio
CREATE TABLE fact_nivel_piezometrico (
    id_pozo INT NOT NULL REFERENCES dim_pozo (id_pozo),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    profundidad_nivel_m NUMERIC NOT NULL,
    PRIMARY KEY (id_pozo, anio)
);

-- Monitor de Sequia: un corte por municipio y fecha
CREATE TABLE fact_sequia_municipio (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    id_categoria INT NOT NULL REFERENCES dim_categoria_sequia (id_categoria),
    PRIMARY KEY (cve_mun, id_tiempo)
);

-- Serie diaria de nivel y gasto, con la bandera de calidad de Hidro-MX
CREATE TABLE fact_caudal_diario (
    clave   VARCHAR(10) NOT NULL REFERENCES dim_estacion_hidrometrica (clave),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    nivel_m NUMERIC,
    gasto_m3s NUMERIC,
    calidad SMALLINT,
    PRIMARY KEY (clave, id_tiempo)
);

-- Serie diaria de presas del SIH. volumen_hm3 es la columna VolumenAlm(Mm3) de la fuente.
CREATE TABLE fact_presa_diaria (
    clave   VARCHAR(10) NOT NULL REFERENCES dim_estacion_hidrometrica (clave),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    nivel_m NUMERIC,
    precipitacion_mm NUMERIC,
    volumen_hm3 NUMERIC,
    obra_toma_m3s NUMERIC,
    vertedor_m3s NUMERIC,
    derrame_m3s NUMERIC,
    evaporacion_mm NUMERIC,
    PRIMARY KEY (clave, id_tiempo)
);

-- Calidad del agua por sitio y parametro en el periodo 2012-2025. Un valor con < o > en la
-- fuente esta fuera del limite de deteccion y queda con su signo en limite.
CREATE TABLE fact_calidad_agua (
    id_sitio INT NOT NULL REFERENCES dim_sitio_calidad (id_sitio),
    id_parametro INT NOT NULL REFERENCES dim_parametro_calidad (id_parametro),
    valor   NUMERIC,
    limite  CHAR(1),
    calidad TEXT,
    PRIMARY KEY (id_sitio, id_parametro)
);

-- Censo 2020 por AGEB urbana de la CDMX y el Estado de Mexico
CREATE TABLE fact_vivienda_agua_ageb (
    cvegeo_ageb CHAR(13) PRIMARY KEY,
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    pob_total BIGINT,
    viv_part_hab BIGINT,
    vph_agua_dentro BIGINT,
    vph_agua_fuera BIGINT,
    vph_agua_servpub BIGINT,
    vph_tinaco BIGINT,
    vph_cisterna BIGINT,
    vph_drenaje BIGINT
);
CREATE INDEX idx_ageb_mun ON fact_vivienda_agua_ageb (cve_mun);

-- Reportes ciudadanos de agua (SACMEX), 2018 a 2024
CREATE TABLE fact_reporte_agua (
    id_reporte BIGSERIAL PRIMARY KEY,
    recurso VARCHAR(24) NOT NULL,
    folio   TEXT NOT NULL,
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    id_ubicacion INT REFERENCES dim_ubicacion (id_ubicacion),
    id_tipo_reporte INT NOT NULL REFERENCES dim_tipo_reporte (id_tipo_reporte),
    id_medio_recepcion INT NOT NULL REFERENCES dim_medio_recepcion (id_medio_recepcion),
    metodo_ubicacion VARCHAR(16),
    distancia_m NUMERIC,
    latitud NUMERIC(9,6),
    longitud NUMERIC(9,6),
    cve_mun CHAR(5) REFERENCES dim_municipio (cve_mun),
    UNIQUE (recurso, folio)
);
CREATE INDEX idx_reporte_ubic ON fact_reporte_agua (id_ubicacion);
CREATE INDEX idx_reporte_tiempo ON fact_reporte_agua (id_tiempo);

-- Clima mensual de MexHiResClimDB. id_tiempo es el ultimo dia del mes.
CREATE TABLE fact_clima_colonia (
    id_ubicacion INT NOT NULL REFERENCES dim_ubicacion (id_ubicacion),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    tmax_c NUMERIC,
    tmin_c NUMERIC,
    tavg_c NUMERIC,
    precip_mm NUMERIC,
    PRIMARY KEY (id_ubicacion, id_tiempo)
);
CREATE TABLE fact_clima_municipio (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    id_tiempo INT NOT NULL REFERENCES dim_tiempo (id_tiempo),
    tmax_c NUMERIC,
    tmin_c NUMERIC,
    tavg_c NUMERIC,
    precip_mm NUMERIC,
    n_celdas INT NOT NULL,
    PRIMARY KEY (cve_mun, id_tiempo)
);

-- Velocidad vertical del terreno (InSAR 2014-2020), en cm/anio
CREATE TABLE fact_subsidencia_colonia (
    id_ubicacion INT PRIMARY KEY REFERENCES dim_ubicacion (id_ubicacion),
    n_pixeles INT NOT NULL,
    vlm_media_cm_anio NUMERIC,
    vlm_min_cm_anio NUMERIC,
    vlm_p10_cm_anio NUMERIC,
    vlm_p90_cm_anio NUMERIC,
    vlm_std_media_cm_anio NUMERIC
);
CREATE TABLE fact_subsidencia_municipio (
    cve_mun CHAR(5) PRIMARY KEY REFERENCES dim_municipio (cve_mun),
    n_pixeles INT NOT NULL,
    vlm_media_cm_anio NUMERIC,
    vlm_min_cm_anio NUMERIC,
    vlm_p10_cm_anio NUMERIC,
    vlm_p90_cm_anio NUMERIC,
    vlm_std_media_cm_anio NUMERIC
);

-- Huerta-Vergara et al. (2022): 16 alcaldias en 2005, 2010 y 2015
CREATE TABLE fact_vulnerabilidad_alcaldia (
    cve_mun CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    anio    INT NOT NULL REFERENCES dim_anio (anio),
    area_urbana_km2 NUMERIC,
    poblacion BIGINT,
    unidades_economicas BIGINT,
    reportes_fugas BIGINT,
    reportes_falta_agua BIGINT,
    reportes_mala_calidad BIGINT,
    agua_tratada_ls NUMERIC,
    agua_disponible_ls NUMERIC,
    pib_mdp NUMERIC,
    dotacion_lpcd NUMERIC,
    indice_z NUMERIC,
    percentil_beta NUMERIC,
    grado_vulnerabilidad TEXT,
    PRIMARY KEY (cve_mun, anio)
);

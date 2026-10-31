-- ============================================
-- Almacen ampliado: dimensiones
-- ============================================
-- Se aplica sobre el almacen de warehouse/ ya cargado, sin modificar sus archivos.
-- Todo es aditivo: fact_consumo_agua, fact_clima y dim_indice_des no cambian, los
-- id_tiempo e id_ubicacion existentes se conservan y solo se agregan columnas y filas.
-- ejecutar.py corre 00_limpiar.sql antes de esto, asi que cada corrida parte de cero.

-- Bitacora de carga. La llena comun.registrar() con lo que realmente entro; no hay
-- entradas a mano, a diferencia de un catalogo estatico de referencias.
CREATE TABLE control_ingesta_fuentes (
    id_ingesta           SERIAL PRIMARY KEY,
    id_fuente            VARCHAR(8)  NOT NULL,
    nombre               TEXT        NOT NULL,
    publicador           TEXT,
    archivo              TEXT        NOT NULL,
    url                  TEXT        NOT NULL,
    doi                  TEXT,
    licencia             TEXT,
    bytes                BIGINT      NOT NULL,
    md5                  CHAR(32)    NOT NULL,
    sha256               CHAR(64)    NOT NULL,
    md5_oficial_coincide BOOLEAN,
    tabla_destino        TEXT        NOT NULL,
    filas                BIGINT      NOT NULL,
    nota                 TEXT,
    cargado_en           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Roll-up anual de dim_tiempo, para los hechos cuyo grano es el anio
CREATE TABLE dim_anio (
    anio     INT PRIMARY KEY,
    dias     INT NOT NULL,
    bisiesto BOOLEAN NOT NULL
);

-- Dimension territorial conformada: alcaldias de la CDMX, municipios del Estado de
-- Mexico y el resto del pais, con la clave geoestadistica de INEGI.
CREATE TABLE dim_municipio (
    cve_mun               CHAR(5) PRIMARY KEY,
    cve_ent               CHAR(2) NOT NULL,
    nom_ent               TEXT,
    nom_mun               TEXT NOT NULL,
    nom_mun_norm          TEXT NOT NULL,
    es_total_entidad      BOOLEAN NOT NULL DEFAULT FALSE,
    -- Las metropolis de Mexico 2020 (CONAPO)
    clave_metropoli       VARCHAR(10),
    nombre_metropoli      TEXT,
    tipo_metropoli        TEXT,
    en_zm_ciudad_mexico   BOOLEAN NOT NULL DEFAULT FALSE,
    municipio_central     BOOLEAN,
    superficie_km2        NUMERIC,
    densidad_urbana       NUMERIC,
    -- Censo 2020, ITER
    pob_total_2020        BIGINT,
    viv_part_hab_2020     BIGINT,
    vph_agua_dentro_2020  BIGINT,
    vph_agua_fuera_2020   BIGINT,
    vph_agua_servpub_2020 BIGINT,
    vph_tinaco_2020       BIGINT,
    vph_cisterna_2020     BIGINT,
    vph_drenaje_2020      BIGINT,
    -- Indice de marginacion municipal 2020 (CONAPO)
    im_2020               NUMERIC,
    gm_2020               TEXT,
    pct_ocup_sin_agua_2020 NUMERIC,
    pct_ocup_sin_drenaje_2020 NUMERIC,
    -- PRONACOSE: probabilidad de ocurrencia de la sequia segun el indicador
    prob_sequia_social    NUMERIC,
    clase_sequia_social   TEXT,
    prob_sequia_economica NUMERIC,
    clase_sequia_economica TEXT,
    prob_sequia_ambiental NUMERIC,
    clase_sequia_ambiental TEXT,
    -- Censos Economicos 2019 (solo entidades 09 y 15)
    ue_2019               BIGINT,
    personal_ocupado_2019 BIGINT,
    produccion_bruta_mdp_2019 NUMERIC,
    -- DENUE, edicion vigente al descargar (mayo de 2026), no 2019
    ue_denue_2026         BIGINT,
    ue_agua_intensiva_denue_2026 BIGINT
);
CREATE INDEX idx_mun_ent ON dim_municipio (cve_ent);
CREATE INDEX idx_mun_zm ON dim_municipio (clave_metropoli);

-- Colonias del indice de marginacion urbana 2020. Da a la ZMVM una unidad
-- submunicipal comparable; en la CDMX se enlaza a dim_ubicacion por nombre.
CREATE TABLE dim_colonia_conapo (
    cve_col     BIGINT PRIMARY KEY,
    cve_mun     CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    colonia     TEXT,
    colonia_norm TEXT,
    cp          VARCHAR(5),
    clasificacion TEXT,
    pob_total   NUMERIC,
    pct_ocup_sin_agua NUMERIC,
    pct_ocup_sin_drenaje NUMERIC,
    im_2020     NUMERIC,
    gm_2020     TEXT
);
CREATE INDEX idx_colonia_mun ON dim_colonia_conapo (cve_mun);

-- dim_ubicacion original: mismas filas e id_ubicacion, columnas nuevas
ALTER TABLE dim_ubicacion ADD COLUMN cve_mun CHAR(5) REFERENCES dim_municipio (cve_mun);
ALTER TABLE dim_ubicacion ADD COLUMN colonia_norm TEXT;
ALTER TABLE dim_ubicacion ADD COLUMN cve_col_conapo BIGINT REFERENCES dim_colonia_conapo (cve_col);
ALTER TABLE dim_ubicacion ADD COLUMN enlace_conapo VARCHAR(10);
ALTER TABLE dim_ubicacion ADD COLUMN n_manzanas_censo INT;
ALTER TABLE dim_ubicacion ADD COLUMN pob_censo_2020 BIGINT;
ALTER TABLE dim_ubicacion ADD COLUMN viv_hab_censo_2020 BIGINT;
ALTER TABLE dim_ubicacion ADD COLUMN vph_agua_dentro_2020 BIGINT;
ALTER TABLE dim_ubicacion ADD COLUMN vph_tinaco_2020 BIGINT;
ALTER TABLE dim_ubicacion ADD COLUMN vph_cisterna_2020 BIGINT;
ALTER TABLE dim_ubicacion ADD COLUMN ue_denue_2026 INT;
ALTER TABLE dim_ubicacion ADD COLUMN ue_agua_intensiva_denue_2026 INT;

-- Acuiferos oficiales (653)
CREATE TABLE dim_acuifero (
    clv_acui   CHAR(4) PRIMARY KEY,
    nom_acui   TEXT NOT NULL,
    clv_edo    CHAR(2),
    nom_edo    TEXT,
    clv_region VARCHAR(3),
    nom_region TEXT,
    area_km2   NUMERIC
);

-- Pozos de la red piezometrica. cve_mun e id_ubicacion salen de cruce espacial.
CREATE TABLE dim_pozo (
    id_pozo    INT PRIMARY KEY,
    nom_pozo   TEXT,
    clv_acui   CHAR(4) NOT NULL REFERENCES dim_acuifero (clv_acui),
    cve_edo    CHAR(2),
    nom_edo    TEXT,
    elev_brocal_m NUMERIC,
    latitud    NUMERIC(9,6),
    longitud   NUMERIC(9,6),
    cve_mun    CHAR(5) REFERENCES dim_municipio (cve_mun),
    id_ubicacion_cercana INT REFERENCES dim_ubicacion (id_ubicacion),
    distancia_ubicacion_m NUMERIC
);
CREATE INDEX idx_pozo_acui ON dim_pozo (clv_acui);
CREATE INDEX idx_pozo_mun ON dim_pozo (cve_mun);

-- Interseccion de poligonos de municipios y acuiferos en CDMX, Estado de Mexico e Hidalgo.
-- Los poligonos de CONAGUA son simplificados, asi que los bordes dejan astillas pequenas.
CREATE TABLE puente_municipio_acuifero (
    cve_mun  CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    clv_acui CHAR(4) NOT NULL REFERENCES dim_acuifero (clv_acui),
    area_km2 NUMERIC NOT NULL,
    pct_municipio NUMERIC NOT NULL,
    n_pozos  INT NOT NULL DEFAULT 0,
    PRIMARY KEY (cve_mun, clv_acui)
);

-- Estaciones hidrometricas y presas del Sistema de Informacion Hidrologica
CREATE TABLE dim_estacion_hidrometrica (
    clave      VARCHAR(10) PRIMARY KEY,
    nombre     TEXT,
    latitud    NUMERIC(9,6),
    longitud   NUMERIC(9,6),
    altitud_m  NUMERIC,
    estado     TEXT,
    municipio  TEXT,
    region_hidrologica TEXT,
    cuenca     TEXT,
    cuenca_disponibilidad TEXT,
    es_presa   BOOLEAN NOT NULL DEFAULT FALSE,
    cve_mun    CHAR(5) REFERENCES dim_municipio (cve_mun)
);

-- Sitios de la Red Nacional de Medicion de Calidad del Agua. El acuifero sale del poligono.
CREATE TABLE dim_sitio_calidad (
    id_sitio   SERIAL PRIMARY KEY,
    clave_sitio TEXT NOT NULL,
    tipo_agua  VARCHAR(12) NOT NULL CHECK (tipo_agua IN ('superficial', 'subterranea')),
    nombre     TEXT,
    organismo_cuenca TEXT,
    estado     TEXT,
    municipio  TEXT,
    unidad_hidrologica TEXT,
    subtipo    TEXT,
    latitud    NUMERIC(9,6),
    longitud   NUMERIC(9,6),
    periodo    TEXT,
    semaforo   VARCHAR(10),
    contaminantes TEXT,
    cve_mun    CHAR(5) REFERENCES dim_municipio (cve_mun),
    clv_acui   CHAR(4) REFERENCES dim_acuifero (clv_acui),
    UNIQUE (tipo_agua, clave_sitio)
);
CREATE INDEX idx_sitio_mun ON dim_sitio_calidad (cve_mun);
CREATE INDEX idx_sitio_acui ON dim_sitio_calidad (clv_acui);

-- Parametros de calidad, con la descripcion de la hoja de diccionario de cada archivo
CREATE TABLE dim_parametro_calidad (
    id_parametro SERIAL PRIMARY KEY,
    tipo_agua  VARCHAR(12) NOT NULL,
    parametro  TEXT NOT NULL,
    descripcion TEXT,
    UNIQUE (tipo_agua, parametro)
);

-- Categorias del Monitor de Sequia, leidas de la hoja NOTAS del archivo
CREATE TABLE dim_categoria_sequia (
    id_categoria SERIAL PRIMARY KEY,
    categoria    VARCHAR(4) NOT NULL UNIQUE,
    descripcion  TEXT NOT NULL,
    severidad    INT NOT NULL
);

-- Catalogos del CNGMD, leidos de los archivos de INEGI
CREATE TABLE dim_tipo_fuente_captacion (
    id_tipo_fuente INT PRIMARY KEY,
    descripcion    TEXT NOT NULL
);
CREATE TABLE dim_tipo_toma (
    id_tipo_toma INT PRIMARY KEY,
    descripcion  TEXT NOT NULL
);

-- Geometria simplificada de lo que dibuja el mapa. Esta aqui para que el mapa salga de una
-- consulta, igual que sus datos. El original sigue siendo el archivo de cada fuente.
CREATE TABLE geo_territorio (
    capa    VARCHAR(10) NOT NULL CHECK (capa IN ('municipio', 'colonia', 'acuifero')),
    clave   TEXT NOT NULL,
    geojson TEXT NOT NULL,
    PRIMARY KEY (capa, clave)
);

-- Vecindad real entre poligonos oficiales. Cada par aparece en los dos sentidos.
-- Municipios: comparten al menos 50 m de frontera. INEGI trae solapes de centimetros, asi que la
-- prueba estricta de "touches" falla en pares que si colindan.
CREATE TABLE puente_municipio_vecino (
    cve_mun     CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    cve_vecino  CHAR(5) NOT NULL REFERENCES dim_municipio (cve_mun),
    frontera_km NUMERIC NOT NULL,
    PRIMARY KEY (cve_mun, cve_vecino)
);
-- Colonias: relacion "touches" estricta sobre los poligonos de CONAPO
CREATE TABLE puente_colonia_vecina (
    cve_col    BIGINT NOT NULL REFERENCES dim_colonia_conapo (cve_col),
    cve_vecina BIGINT NOT NULL REFERENCES dim_colonia_conapo (cve_col),
    PRIMARY KEY (cve_col, cve_vecina)
);

-- Reportes ciudadanos de SACMEX
CREATE TABLE dim_tipo_reporte (
    id_tipo_reporte SERIAL PRIMARY KEY,
    clasificacion   TEXT NOT NULL,
    reporte         TEXT NOT NULL,
    UNIQUE (clasificacion, reporte)
);
CREATE TABLE dim_medio_recepcion (
    id_medio_recepcion SERIAL PRIMARY KEY,
    medio              TEXT NOT NULL UNIQUE
);

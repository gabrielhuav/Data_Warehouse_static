-- =====================================================================
-- schema.sql -- Star schema for the CDMX water-consumption data warehouse
-- Target: PostgreSQL 14+ (PostGIS optional but recommended)
--
-- Column and table names are authoritative: mapping.r2rml.ttl and
-- scripts/generar_datos_faltantes.py both reference the identifiers
-- defined here. Do not rename without updating those two files.
--
-- PROVENANCE: reconstruction written for the ICOKG 2026 camera-ready
-- artefact. See the "Provenance and scope" note in the README.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS fact_water_consumption CASCADE;
DROP TABLE IF EXISTS dim_location  CASCADE;
DROP TABLE IF EXISTS dim_time      CASCADE;
DROP TABLE IF EXISTS dim_dev_index CASCADE;

-- ---------------------------------------------------------------------
-- Dimension: territory (colonia / neighbourhood)
-- ---------------------------------------------------------------------
CREATE TABLE dim_location (
    location_id  SERIAL PRIMARY KEY,
    colonia      TEXT NOT NULL,
    alcaldia     TEXT NOT NULL,
    latitud      DOUBLE PRECISION,
    longitud     DOUBLE PRECISION,
    geom         GEOMETRY(Point, 4326),
    CONSTRAINT uq_location UNIQUE (alcaldia, colonia),
    CONSTRAINT ck_lat CHECK (latitud  IS NULL OR latitud  BETWEEN  19.04 AND  19.60),
    CONSTRAINT ck_lon CHECK (longitud IS NULL OR longitud BETWEEN -99.36 AND -98.94)
);

-- ---------------------------------------------------------------------
-- Dimension: time (one row per distinct reading date in the source)
-- ---------------------------------------------------------------------
CREATE TABLE dim_time (
    time_id   SERIAL PRIMARY KEY,
    fecha     DATE    NOT NULL UNIQUE,
    anio      INTEGER NOT NULL,
    bimestre  SMALLINT NOT NULL CHECK (bimestre BETWEEN 1 AND 6)
);

-- ---------------------------------------------------------------------
-- Dimension: development index (ordinal SKOS scheme)
-- ---------------------------------------------------------------------
CREATE TABLE dim_dev_index (
    dev_index_id SERIAL PRIMARY KEY,
    nivel        TEXT NOT NULL UNIQUE,
    orden        SMALLINT
);

-- The source distinguishes three substantive levels plus an explicit
-- "unspecified" bucket for records whose index is absent. The four rows
-- are what Table "Data volume" of the paper reports for dim_dev_index.
INSERT INTO dim_dev_index (nivel, orden) VALUES
    ('Alto', 3), ('Medio', 2), ('Bajo', 1), ('No especificado', 0);

-- ---------------------------------------------------------------------
-- Fact table
-- ---------------------------------------------------------------------
CREATE TABLE fact_water_consumption (
    fact_id           BIGSERIAL PRIMARY KEY,
    time_id           INTEGER NOT NULL REFERENCES dim_time(time_id),
    location_id       INTEGER NOT NULL REFERENCES dim_location(location_id),
    dev_index_id      INTEGER NOT NULL REFERENCES dim_dev_index(dev_index_id),
    consumo_total     NUMERIC(14,2) NOT NULL CHECK (consumo_total >= 0),
    consumo_promedio  NUMERIC(14,2) CHECK (consumo_promedio >= 0),
    consumo_dom       NUMERIC(14,2) CHECK (consumo_dom     >= 0),
    consumo_no_dom    NUMERIC(14,2) CHECK (consumo_no_dom  >= 0),
    consumo_mixto     NUMERIC(14,2) CHECK (consumo_mixto   >= 0)
);

-- ---------------------------------------------------------------------
-- Indexes supporting the retrieval workloads benchmarked in the paper
-- ---------------------------------------------------------------------
CREATE INDEX idx_fact_time     ON fact_water_consumption (time_id);
CREATE INDEX idx_fact_location ON fact_water_consumption (location_id);
CREATE INDEX idx_fact_devidx   ON fact_water_consumption (dev_index_id);
CREATE INDEX idx_loc_alcaldia  ON dim_location (alcaldia);
CREATE INDEX idx_time_anio_bim ON dim_time (anio, bimestre);
CREATE INDEX idx_loc_geom      ON dim_location USING GIST (geom);

-- ---------------------------------------------------------------------
-- Staging table used by loader.py (COPY target, phase 3 of the ETL)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS staging_consumo;
CREATE TABLE staging_consumo (
    fecha            TEXT,
    anio             TEXT,
    bimestre         TEXT,
    alcaldia         TEXT,
    colonia          TEXT,
    indice_des       TEXT,
    latitud          TEXT,
    longitud         TEXT,
    consumo_total    TEXT,
    consumo_promedio TEXT,
    consumo_dom      TEXT,
    consumo_no_dom   TEXT,
    consumo_mixto    TEXT
);

-- ---------------------------------------------------------------------
-- Adjacency, derived AFTER load. The R2RML mapping does not produce
-- geo:sfTouches; this statement (or the triple store's spatial index)
-- does. See the note at the end of mapping.r2rml.ttl.
-- ---------------------------------------------------------------------
-- CREATE TABLE loc_adjacency AS
-- SELECT a.location_id AS src, b.location_id AS dst
-- FROM dim_location a JOIN dim_location b
--   ON ST_DWithin(a.geom::geography, b.geom::geography, 1500)
--  AND a.location_id <> b.location_id;

-- =========================================================
-- ENABLE POSTGIS
-- =========================================================

CREATE EXTENSION IF NOT EXISTS postgis;


-- =========================================================
-- INDUSTRIAL FACILITIES
-- =========================================================

CREATE TABLE IF NOT EXISTS industrial_facilities (

    id SERIAL PRIMARY KEY,

    name VARCHAR(255) NOT NULL,

    facility_type VARCHAR(100) NOT NULL,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    location GEOGRAPHY(
        POINT,
        4326
    ) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- =========================================================
-- THERMAL ANOMALIES
-- =========================================================

CREATE TABLE IF NOT EXISTS thermal_anomalies (

    id SERIAL PRIMARY KEY,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    acquisition_date DATE,

    acquisition_time VARCHAR(10),

    brightness_temperature DOUBLE PRECISION,

    background_temperature DOUBLE PRECISION,

    frp DOUBLE PRECISION,

    confidence VARCHAR(20),

    satellite VARCHAR(50),

    instrument VARCHAR(50),

    daynight VARCHAR(10),

    source VARCHAR(100),

    source_dataset VARCHAR(100),

    anomaly_type VARCHAR(100),

    event_id INTEGER,

    location GEOGRAPHY(
        POINT,
        4326
    ) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- =========================================================
-- SPATIAL INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS
idx_industrial_facilities_location

ON industrial_facilities
USING GIST(location);


CREATE INDEX IF NOT EXISTS
idx_thermal_anomalies_location

ON thermal_anomalies
USING GIST(location);


-- =========================================================
-- OPENSTREETMAP FEATURES
-- =========================================================

CREATE TABLE IF NOT EXISTS osm_features (

    id SERIAL PRIMARY KEY,

    osm_id BIGINT NOT NULL,

    osm_type VARCHAR(20) NOT NULL,

    feature_type VARCHAR(100) NOT NULL,

    name VARCHAR(255),

    tags JSONB NOT NULL DEFAULT '{}'::jsonb,

    geometry GEOMETRY(Geometry, 4326) NOT NULL,

    source VARCHAR(50) NOT NULL DEFAULT 'overpass',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_osm_features_object
        UNIQUE (osm_type, osm_id)
);


CREATE INDEX IF NOT EXISTS
idx_osm_features_geometry

ON osm_features
USING GIST(geometry);


CREATE INDEX IF NOT EXISTS
idx_osm_features_type

ON osm_features(feature_type);


-- =========================================================
-- MODEL PREDICTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS predictions (

    id SERIAL PRIMARY KEY,

    event_code VARCHAR(50) NOT NULL,

    prediction VARCHAR(100) NOT NULL,

    confidence DOUBLE PRECISION NOT NULL,

    model_version VARCHAR(50) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_predictions_event_model
        UNIQUE (event_code, model_version)
);


CREATE INDEX IF NOT EXISTS
idx_predictions_event_code

ON predictions(event_code);


CREATE UNIQUE INDEX IF NOT EXISTS
uq_thermal_anomalies_firms_detection

ON thermal_anomalies (
    latitude,
    longitude,
    acquisition_date,
    acquisition_time,
    satellite
);
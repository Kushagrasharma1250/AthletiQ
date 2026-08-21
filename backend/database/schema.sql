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
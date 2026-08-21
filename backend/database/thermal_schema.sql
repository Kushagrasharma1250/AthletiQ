CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS thermal_anomalies (

    id SERIAL PRIMARY KEY,

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    geometry GEOMETRY(Point, 4326),

    bright_ti4 DOUBLE PRECISION,

    bright_ti5 DOUBLE PRECISION,

    scan DOUBLE PRECISION,

    track DOUBLE PRECISION,

    acq_date DATE,

    acq_time VARCHAR(10),

    detection_timestamp TIMESTAMP,

    satellite VARCHAR(50),

    instrument VARCHAR(50),

    confidence VARCHAR(20),

    version VARCHAR(50),

    frp DOUBLE PRECISION,

    daynight VARCHAR(10),

    event_id INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE INDEX IF NOT EXISTS
idx_thermal_geometry
ON thermal_anomalies
USING GIST(geometry);

CREATE INDEX IF NOT EXISTS
idx_thermal_timestamp
ON thermal_anomalies(detection_timestamp);
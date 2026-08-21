CREATE TABLE IF NOT EXISTS events (

    id SERIAL PRIMARY KEY,

    event_code VARCHAR(50) UNIQUE NOT NULL,

    geometry GEOMETRY(
        POINT,
        4326
    ) NOT NULL,

    first_detected TIMESTAMP NOT NULL,

    last_detected TIMESTAMP NOT NULL,

    detection_count INTEGER NOT NULL DEFAULT 0,

    persistence_status VARCHAR(50),

    current_class VARCHAR(100),

    confidence DOUBLE PRECISION,

    risk_score DOUBLE PRECISION,

    risk_level VARCHAR(30),

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE INDEX IF NOT EXISTS
idx_events_geometry

ON events
USING GIST(geometry);


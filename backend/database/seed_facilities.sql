INSERT INTO industrial_facilities
(
    name,
    facility_type,
    latitude,
    longitude,
    location
)
VALUES

(
    'Plant A',
    'Petrochemical',
    28.1234,
    77.1234,
    ST_SetSRID(
        ST_MakePoint(
            77.1234,
            28.1234
        ),
        4326
    )::geography
),

(
    'Plant B',
    'Power Plant',
    28.3456,
    77.4567,
    ST_SetSRID(
        ST_MakePoint(
            77.4567,
            28.3456
        ),
        4326
    )::geography
),

(
    'Plant C',
    'Steel',
    28.5678,
    77.6789,
    ST_SetSRID(
        ST_MakePoint(
            77.6789,
            28.5678
        ),
        4326
    )::geography
),

(
    'Plant D',
    'Refinery',
    28.7890,
    77.8901,
    ST_SetSRID(
        ST_MakePoint(
            77.8901,
            28.7890
        ),
        4326
    )::geography
);
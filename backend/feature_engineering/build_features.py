import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parents[1]))

from landcover import calculate_landcover_features
from persistence.detector import calculate_persistence, calculate_persistence_score
from spatial import calculate_spatial_features
from temporal import calculate_recurrence_frequency, calculate_temporal_features
from temporal import calculate_recurrence_frequency, calculate_temporal_features
from thermal import calculate_thermal_features


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
FEATURE_COLUMNS = [
    "event_id", "event_code", "frp_mean", "frp_max", "confidence_mean",
    "brightness_temp_mean", "facility_distance_m", "facilities_within_1km",
    "facilities_within_5km", "industrial_ratio", "forest_ratio",
    "agriculture_ratio", "builtup_ratio", "detection_count",
    "event_duration_hours", "recurrence_frequency", "persistence",
    "persistence_score",
]


def load_events():
    query = text("""
        SELECT id AS event_id, event_code,
               ST_Y(geometry) AS latitude, ST_X(geometry) AS longitude,
               first_detected, last_detected, detection_count
        FROM events ORDER BY id
    """)
    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def load_detections(event_id):
    query = text("""
        SELECT id, latitude, longitude, acquisition_date, acquisition_time,
               brightness_temperature, frp, confidence, event_id
        FROM thermal_anomalies
        WHERE event_id = :event_id
        ORDER BY acquisition_date, acquisition_time
    """)
    with engine.connect() as connection:
        detections = pd.read_sql(query, connection, params={"event_id": event_id})

    if not detections.empty:
        times = detections["acquisition_time"].astype(str).str.replace(".0", "", regex=False).str.zfill(4)
        detections["timestamp"] = pd.to_datetime(
            detections["acquisition_date"].astype(str) + " "
            + times.str[:2] + ":" + times.str[2:4], errors="coerce"
        )
    return detections


def load_facilities():
    query = text("SELECT latitude, longitude FROM industrial_facilities")
    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def build_event_features(event, detections, facilities, events):
    features = {"event_id": int(event["event_id"]), "event_code": event["event_code"]}
    features.update(calculate_thermal_features(detections))
    features.update(calculate_spatial_features(event, facilities))
    features.update(calculate_landcover_features(event))
    temporal = calculate_temporal_features(detections)
    temporal["recurrence_frequency"] = calculate_recurrence_frequency(event, events)
    features.update(temporal)
    features["persistence"] = calculate_persistence(
        temporal["detection_count"],
        temporal["event_duration_hours"],
        temporal["recurrence_frequency"],
    )
    features["persistence_score"] = calculate_persistence_score(
        temporal["detection_count"],
        temporal["event_duration_hours"],
        temporal["recurrence_frequency"],
    )
    return features


def build_feature_table():
    events = load_events()
    facilities = load_facilities()
    rows = []
    for _, event in events.iterrows():
        detections = load_detections(event["event_id"])
        if not detections.empty:
            rows.append(build_event_features(event, detections, facilities, events))
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)


def main():
    feature_table = build_feature_table()
    output_path = Path(__file__).parents[1] / "data" / "features" / "event_features.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feature_table.to_csv(output_path, index=False)
    print(f"Feature rows: {len(feature_table)}")
    print(f"Feature columns: {len(feature_table.columns)}")
    print(f"Saved to: {output_path}")
    print("Missing values:")
    print(feature_table.isna().sum().to_string())


if __name__ == "__main__":
    main()

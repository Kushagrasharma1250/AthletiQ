import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from .landcover import calculate_landcover_features
from .osm import calculate_osm_features
from ..ml.feature_contract import MODEL_FEATURE_COLUMNS
from ..persistence.detector import calculate_persistence, calculate_persistence_score
from .spatial import calculate_spatial_features
from .temporal import calculate_recurrence_frequency, calculate_temporal_features
from .thermal import calculate_thermal_features


load_dotenv(Path(__file__).parents[1] / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
FEATURE_COLUMNS = ["event_id", "event_code"] + MODEL_FEATURE_COLUMNS + [
    "persistence", "persistence_score",
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


def load_osm_features():
    query = text("""
        SELECT feature_type,
               ST_Y(ST_PointOnSurface(geometry)) AS latitude,
               ST_X(ST_PointOnSurface(geometry)) AS longitude,
               ST_AsText(geometry) AS geometry_wkt
        FROM osm_features
    """)
    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def build_event_features(event, detections, facilities, osm_features, events):
    features = {"event_id": int(event["event_id"]), "event_code": event["event_code"]}
    thermal = calculate_thermal_features(detections)
    features.update({
        "frp_mean": thermal["frp_mean"],
        "frp_max": thermal["frp_max"],
        "confidence": thermal["confidence_mean"],
    })
    spatial = calculate_spatial_features(event, facilities)
    features.update({
        "facility_distance": spatial["facility_distance_m"],
        "facility_count": spatial["facilities_within_5km"],
    })
    osm = calculate_osm_features(event, osm_features)
    features.update({
        "osm_industrial_distance": osm["osm_industrial_distance_m"],
        "osm_industrial_count": osm["osm_industrial_count"],
        "osm_industrial_area_ratio": osm["osm_industrial_area_ratio"],
        "osm_road_distance": osm["osm_road_distance_m"],
        "osm_building_count": osm["osm_building_count_500m"],
        "osm_building_density": osm["osm_building_density_500m"],
        "osm_powerplant_distance": osm["osm_powerplant_distance_m"],
        "osm_substation_distance": osm["osm_substation_distance_m"],
        "osm_mine_distance": osm["osm_mine_distance_m"],
        "osm_quarry_distance": osm["osm_quarry_distance_m"],
    })
    features.update(calculate_landcover_features(event))
    temporal = calculate_temporal_features(detections)
    features["recurrence_count"] = calculate_recurrence_frequency(event, events)
    features["detection_count"] = temporal["detection_count"]
    features["event_duration_hours"] = temporal["event_duration_hours"]
    temporal["recurrence_frequency"] = features["recurrence_count"]
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
    osm_features = load_osm_features()
    rows = []
    for _, event in events.iterrows():
        detections = load_detections(event["event_id"])
        if not detections.empty:
            rows.append(
                build_event_features(
                    event,
                    detections,
                    facilities,
                    osm_features,
                    events,
                )
            )
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

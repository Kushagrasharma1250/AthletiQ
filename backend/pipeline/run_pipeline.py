import argparse
import os
from pathlib import Path

from sqlalchemy import text

from ..event_engine import process_events, load_detections
from ..feature_engineering.build_features import build_feature_table
from ..firm_ingestion import (
    clean_viirs_data,
    fetch_viirs_data,
    save_normalized_data,
    save_raw_data,
    save_to_database,
    transform_to_thermal_anomalies,
)
from ..geospatial.ingestion.osm_ingestion import ingest as ingest_osm
from ..ml.inference.predict import predict
from ..ml.feature_contract import MODEL_FEATURE_COLUMNS, MODEL_FEATURE_VERSION
from ..event_engine import engine


FEATURE_OUTPUT = Path(__file__).parents[1] / "data" / "features" / "event_features.csv"


def ingest_firms(west, south, east, north, days):
    raw = fetch_viirs_data(
        west,
        south,
        east,
        north,
        days,
        source=os.getenv("FIRMS_SOURCE", "VIIRS_NOAA21_NRT"),
    )
    if raw.empty:
        return 0
    save_raw_data(raw)
    cleaned = clean_viirs_data(raw)
    normalized = transform_to_thermal_anomalies(cleaned)
    save_normalized_data(normalized)
    save_to_database(normalized)
    return len(normalized)


def save_predictions(feature_table):
    feature_rows = feature_table.to_dict("records")
    if not feature_rows:
        return 0

    rows = []
    for row in feature_rows:
        result = predict(row)
        rows.append({
            "event_code": row["event_code"],
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "model_version": MODEL_FEATURE_VERSION,
        })

    query = text("""
        INSERT INTO predictions
            (event_code, prediction, confidence, model_version)
        VALUES
            (:event_code, :prediction, :confidence, :model_version)
        ON CONFLICT (event_code, model_version) DO UPDATE SET
            prediction = EXCLUDED.prediction,
            confidence = EXCLUDED.confidence,
            updated_at = CURRENT_TIMESTAMP
    """)
    with engine.begin() as connection:
        connection.execute(query, rows)
    return len(rows)


def run(args):
    print("[1] FIRMS ingestion")
    print(f"    {ingest_firms(args.west, args.south, args.east, args.north, args.days)} detections")

    print("[2] OSM ingestion")
    print(f"    {ingest_osm(args.south, args.west, args.north, args.east, args.osm_cache)} features")

    print("[3] Event clustering")
    detections = load_detections()
    pending = detections[detections["event_id"].isna()].copy()
    if not pending.empty:
        process_events(pending)
    print(f"    {len(pending)} detections processed")

    print("[4] Feature generation")
    feature_table = build_feature_table()
    feature_table.to_csv(FEATURE_OUTPUT, index=False)
    print(f"    {len(feature_table)} feature rows")

    if feature_table["event_code"].duplicated().any():
        raise ValueError("Duplicate event codes in generated feature table")
    model_columns = MODEL_FEATURE_COLUMNS
    missing_columns = [
        column for column in model_columns if column not in feature_table.columns
    ]
    if missing_columns:
        raise ValueError(f"Generated feature table is missing: {missing_columns}")
    if feature_table[model_columns].isnull().any().any():
        raise ValueError("Generated feature table contains null model inputs; configure LANDCOVER_RASTER_PATH and ingest OSM first")

    print("[5] Model inference and persistence")
    print(f"    {save_predictions(feature_table)} predictions saved")
    print("Pipeline completed")


def main():
    parser = argparse.ArgumentParser(description="Run the complete AthletiQ backend pipeline")
    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)
    parser.add_argument("--days", type=int, default=5)
    parser.add_argument("--osm-cache", type=Path)
    run(parser.parse_args())


if __name__ == "__main__":
    main()

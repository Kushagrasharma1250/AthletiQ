import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Industrial Fire Intelligence API",
    description="AI-powered satellite thermal anomaly detection and classification API",
    version="1.0.0"
)

EVENTS_CSV_PATH = Path(__file__).parent / "data" / "events" / "events.csv"
EVENT_FEATURES_CSV_PATH = (
    Path(__file__).parent / "data" / "features" / "event_features.csv"
)
TRAINING_DATA_PATH = (
    Path(__file__).parent / "data" / "processed" / "training_with_recurrence.csv"
)


def parse_float(value):

    return None if value == "" else float(value)


@app.get("/")
def root():
    return {
        "message": "Industrial Fire Intelligence API is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/events")
def get_events():

    if not EVENTS_CSV_PATH.exists():
        return {"events": []}

    with EVENTS_CSV_PATH.open(
        newline="",
        encoding="utf-8-sig"
    ) as events_file:
        events = []

        for row in csv.DictReader(events_file):
            events.append(
                {
                    "event_id": row["event_id"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "detection_count": int(row["detection_count"]),
                }
            )

    return {
        "events": events
    }


@app.get("/events/persistent")
def get_persistent_events():

    if not EVENT_FEATURES_CSV_PATH.exists():
        return {
            "count": 0,
            "events": []
        }

    with EVENT_FEATURES_CSV_PATH.open(
        newline="",
        encoding="utf-8-sig"
    ) as features_file:
        events = [
            {
                "event_id": row["event_code"],
                "persistence": row["persistence"],
                "persistence_score": int(row["persistence_score"]),
            }
            for row in csv.DictReader(features_file)
            if row["persistence"].strip().upper() == "PERSISTENT"
        ]

    return {
        "count": len(events),
        "events": events
    }


@app.get("/statistics")
def get_statistics():

    statistics = {
        "total_events": 0,
        "industrial_fires": 0,
        "wildfires": 0,
        "agricultural_burning": 0,
        "persistent_sources": 0,
        "recurring_events": 0,
        "high_risk_events": 0,
    }

    if TRAINING_DATA_PATH.exists():
        with TRAINING_DATA_PATH.open(
            newline="",
            encoding="utf-8-sig"
        ) as training_file:
            training_events = list(csv.DictReader(training_file))

        statistics["total_events"] = len(training_events)
        statistics["industrial_fires"] = sum(
            row["label"] == "INDUSTRIAL_FIRE"
            for row in training_events
        )
        statistics["wildfires"] = sum(
            row["label"] == "WILDFIRE"
            for row in training_events
        )
        statistics["agricultural_burning"] = sum(
            row["label"] == "AGRICULTURAL_BURNING"
            for row in training_events
        )

    if EVENT_FEATURES_CSV_PATH.exists():
        with EVENT_FEATURES_CSV_PATH.open(
            newline="",
            encoding="utf-8-sig"
        ) as features_file:
            feature_events = list(csv.DictReader(features_file))

        statistics["persistent_sources"] = sum(
            row["persistence"].strip().upper() == "PERSISTENT"
            for row in feature_events
        )
        statistics["recurring_events"] = sum(
            row["persistence"].strip().upper() == "RECURRING"
            for row in feature_events
        )
        statistics["high_risk_events"] = sum(
            int(row["persistence_score"]) >= 70
            for row in feature_events
        )

    return statistics


@app.get("/events/{event_id}")
def get_event(event_id: str):

    if not EVENT_FEATURES_CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found"
        )

    with EVENT_FEATURES_CSV_PATH.open(
        newline="",
        encoding="utf-8-sig"
    ) as features_file:
        event = next(
            (
                row
                for row in csv.DictReader(features_file)
                if row["event_code"] == event_id
            ),
            None
        )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail=f"Event {event_id} not found"
        )

    return {
        "event_id": event["event_code"],
        "thermal": {
            "frp_mean": float(event["frp_mean"]),
            "frp_max": float(event["frp_max"]),
            "confidence": parse_float(event["confidence_mean"]),
        },
        "spatial": {
            "facility_distance": parse_float(event["facility_distance_m"]),
            "facility_count": int(event["facilities_within_5km"]),
        },
        "land_cover": {
            "industrial_ratio": parse_float(event["industrial_ratio"]),
            "forest_ratio": parse_float(event["forest_ratio"]),
            "agriculture_ratio": parse_float(event["agriculture_ratio"]),
            "builtup_ratio": parse_float(event["builtup_ratio"]),
        },
        "temporal": {
            "detection_count": int(event["detection_count"]),
            "duration_hours": parse_float(event["event_duration_hours"]),
            "recurrence_frequency": int(event["recurrence_frequency"]),
        },
        "persistence": event["persistence"],
        "persistence_score": int(event["persistence_score"]),
    }
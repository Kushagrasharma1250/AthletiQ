import csv
import math
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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


class PredictionRequest(BaseModel):
    frp_mean: float
    frp_max: float
    confidence: float
    facility_distance: float
    facility_count: int
    osm_industrial_distance: float
    osm_industrial_count: int
    osm_industrial_area_ratio: float
    osm_road_distance: float
    osm_building_count: int
    osm_building_density: float
    osm_powerplant_distance: float
    osm_substation_distance: float
    osm_mine_distance: float
    osm_quarry_distance: float
    forest_ratio: float
    agriculture_ratio: float
    builtup_ratio: float
    detection_count: int
    event_duration_hours: float
    recurrence_count: int


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


@app.get("/thermal/live")
def get_live_thermal(
    west: float,
    south: float,
    east: float,
    north: float,
    days: int = 1,
):
    if not -180 <= west < east <= 180 or not -90 <= south < north <= 90:
        raise HTTPException(
            status_code=422,
            detail="Invalid bounding box"
        )

    try:
        from .firm_ingestion import FIRMS_SOURCE, fetch_viirs_data

        detections = fetch_viirs_data(
            west=west,
            south=south,
            east=east,
            north=north,
            days=days,
            source=FIRMS_SOURCE,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="NASA FIRMS request failed"
        ) from error

    events = []
    for row in detections.to_dict("records"):
        brightness = row.get("bright_ti4")
        events.append({
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "temperature_celsius": (
                None
                if brightness is None or not math.isfinite(float(brightness))
                else round(float(brightness) - 273.15, 2)
            ),
            "frp": row.get("frp"),
            "confidence": row.get("confidence"),
            "acquisition_date": row.get("acq_date"),
            "acquisition_time": row.get("acq_time"),
            "satellite": row.get("satellite"),
            "instrument": row.get("instrument"),
        })

    return {
        "count": len(events),
        "source": FIRMS_SOURCE,
        "bbox": {
            "west": west,
            "south": south,
            "east": east,
            "north": north,
        },
        "events": events,
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


@app.post("/predict")
def predict_event(request: PredictionRequest):

    try:
        from .ml.inference.predict import predict

        return predict(request.model_dump())
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="The trained classification model is unavailable"
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error


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
            "confidence": parse_float(event.get("confidence", event.get("confidence_mean", ""))),
        },
        "spatial": {
            "facility_distance": parse_float(event.get("facility_distance", event.get("facility_distance_m", ""))),
            "facility_count": int(event.get("facility_count", event.get("facilities_within_5km", 0))),
        },
        "land_cover": {
            "industrial_ratio": parse_float(event.get("osm_industrial_area_ratio", event.get("industrial_ratio", ""))),
            "forest_ratio": parse_float(event["forest_ratio"]),
            "agriculture_ratio": parse_float(event["agriculture_ratio"]),
            "builtup_ratio": parse_float(event["builtup_ratio"]),
        },
        "temporal": {
            "detection_count": int(event["detection_count"]),
            "duration_hours": parse_float(event["event_duration_hours"]),
            "recurrence_frequency": int(event.get("recurrence_count", event.get("recurrence_frequency", 0))),
        },
        "persistence": event["persistence"],
        "persistence_score": int(event["persistence_score"]),
    }
import numpy as np
import pandas as pd


RECURRENCE_RADIUS_KM = 5.0
EARTH_RADIUS_KM = 6371.0088


def calculate_temporal_features(detections):

    detections = detections.sort_values("timestamp")

    first_detection = detections["timestamp"].min()
    last_detection = detections["timestamp"].max()

    duration = (
        last_detection - first_detection
    ).total_seconds() / 3600

    return {
        "detection_count": len(detections),
        "event_duration_hours": max(duration, 0.0),
        "recurrence_frequency": 0.0,
    }


def calculate_recurrence_frequency(event, events):
    if events.empty:
        return 0

    event_date = pd.Timestamp(event["first_detected"])
    latitude = np.radians(float(event["latitude"]))
    longitude = np.radians(float(event["longitude"]))
    previous_events = events[
        pd.to_datetime(events["first_detected"]) < event_date
    ]

    if previous_events.empty:
        return 0

    previous_latitude = np.radians(previous_events["latitude"].to_numpy())
    previous_longitude = np.radians(previous_events["longitude"].to_numpy())
    delta_latitude = previous_latitude - latitude
    delta_longitude = previous_longitude - longitude
    haversine = (
        np.sin(delta_latitude / 2) ** 2
        + np.cos(latitude)
        * np.cos(previous_latitude)
        * np.sin(delta_longitude / 2) ** 2
    )
    distances = 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(haversine))
    return int((distances <= RECURRENCE_RADIUS_KM).sum())
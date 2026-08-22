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
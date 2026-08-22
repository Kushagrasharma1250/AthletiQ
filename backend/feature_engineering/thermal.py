def calculate_thermal_features(detections):

    confidence = detections["confidence"].astype(str).str.lower().map({
        "l": 0.5,
        "n": 0.75,
        "h": 1.0,
    })

    return {
        "frp_mean": detections["frp"].mean(),
        "frp_max": detections["frp"].max(),
        "confidence_mean": confidence.mean(),
        "brightness_temp_mean": detections[
            "brightness_temperature"
        ].mean(),
    }
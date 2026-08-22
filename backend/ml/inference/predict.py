import json
import sys
from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).parents[1] / "models" / "industrial_fire_classifier.joblib"


def _normalise_confidence(value):
  confidence = float(value)
  return confidence / 100 if confidence > 1 else confidence


def predict(payload):
  required_fields = {
    "frp_mean",
    "confidence",
    "facility_distance",
    "industrial_ratio",
    "forest_ratio",
  }
  missing_fields = required_fields - payload.keys()
  if missing_fields:
    raise ValueError(
      f"Missing required fields: {sorted(missing_fields)}"
    )

  package = joblib.load(MODEL_PATH)
  feature_values = {
    "frp_mean": float(payload["frp_mean"]),
    "frp_max": float(payload.get("frp_max", payload["frp_mean"])),
    "confidence": _normalise_confidence(payload["confidence"]),
    "facility_distance": float(payload["facility_distance"]),
    "facility_count": int(payload.get("facility_count", 0)),
    "industrial_ratio": float(payload["industrial_ratio"]),
    "forest_ratio": float(payload["forest_ratio"]),
    "agriculture_ratio": float(payload.get("agriculture_ratio", 0)),
    "builtup_ratio": float(payload.get("builtup_ratio", 0)),
    "detection_count": int(payload.get("detection_count", 1)),
    "event_duration_hours": float(payload.get("event_duration_hours", 0)),
  }

  features = pd.DataFrame(
    [[feature_values[name] for name in package["features"]]],
    columns=package["features"],
  )
  probabilities = package["model"].predict_proba(features)[0]
  prediction_index = int(probabilities.argmax())

  return {
    "prediction": str(
      package["label_encoder"].inverse_transform([prediction_index])[0]
    ),
    "confidence": round(float(probabilities[prediction_index]), 3),
  }


def main():
  payload = json.load(sys.stdin)
  print(json.dumps(predict(payload), indent=2))


if __name__ == "__main__":
  main()
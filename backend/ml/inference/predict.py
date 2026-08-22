import json
import sys
from pathlib import Path

import joblib
import pandas as pd

from ..feature_contract import MODEL_FEATURE_COLUMNS, MODEL_FEATURE_VERSION


MODEL_PATH = Path(__file__).parents[1] / "models" / "industrial_fire_classifier_v2.joblib"


def _normalise_confidence(value):
  confidence = float(value)
  return confidence / 100 if confidence > 1 else confidence


def predict(payload):
  required_fields = {
    "frp_mean",
    "frp_max",
    "confidence",
    "facility_distance",
    "facility_count",
    "osm_industrial_distance",
    "osm_industrial_count",
    "osm_industrial_area_ratio",
    "osm_road_distance",
    "osm_building_count",
    "osm_building_density",
    "osm_powerplant_distance",
    "osm_substation_distance",
    "osm_mine_distance",
    "osm_quarry_distance",
    "forest_ratio",
    "agriculture_ratio",
    "builtup_ratio",
    "detection_count",
    "event_duration_hours",
    "recurrence_count",
  }
  missing_fields = required_fields - payload.keys()
  if missing_fields:
    raise ValueError(
      f"Missing required fields: {sorted(missing_fields)}"
    )

  package = joblib.load(MODEL_PATH)
  if package.get("features") != MODEL_FEATURE_COLUMNS:
    raise ValueError(
      "The trained model feature contract does not match the API contract"
    )
  if package.get("feature_version") not in (None, MODEL_FEATURE_VERSION):
    raise ValueError(
      f"Unsupported model feature version: {package['feature_version']}"
    )
  feature_values = {
    "frp_mean": float(payload["frp_mean"]),
    "frp_max": float(payload["frp_max"]),
    "confidence": _normalise_confidence(payload["confidence"]),
    "facility_distance": float(payload["facility_distance"]),
    "facility_count": int(payload["facility_count"]),
    "osm_industrial_distance": float(payload["osm_industrial_distance"]),
    "osm_industrial_count": int(payload["osm_industrial_count"]),
    "osm_industrial_area_ratio": float(payload["osm_industrial_area_ratio"]),
    "osm_road_distance": float(payload["osm_road_distance"]),
    "osm_building_count": int(payload["osm_building_count"]),
    "osm_building_density": float(payload["osm_building_density"]),
    "osm_powerplant_distance": float(payload["osm_powerplant_distance"]),
    "osm_substation_distance": float(payload["osm_substation_distance"]),
    "osm_mine_distance": float(payload["osm_mine_distance"]),
    "osm_quarry_distance": float(payload["osm_quarry_distance"]),
    "forest_ratio": float(payload["forest_ratio"]),
    "agriculture_ratio": float(payload["agriculture_ratio"]),
    "builtup_ratio": float(payload["builtup_ratio"]),
    "detection_count": int(payload["detection_count"]),
    "event_duration_hours": float(payload["event_duration_hours"]),
    "recurrence_count": int(payload["recurrence_count"]),
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
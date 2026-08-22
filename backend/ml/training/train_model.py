import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/processed/training.csv"
MODEL_PATH = "ml/models/industrial_fire_classifier.joblib"

RANDOM_STATE = 42


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("=" * 60)
print("INDUSTRIAL FIRE CLASSIFIER - XGBOOST TRAINING")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# 2. SELECT FEATURES
# ============================================================

feature_columns = [
    "frp_mean",
    "frp_max",
    "confidence",
    "facility_distance",
    "facility_count",
    "industrial_ratio",
    "forest_ratio",
    "agriculture_ratio",
    "builtup_ratio",
    "detection_count",
    "event_duration_hours"
]

target_column = "label"


# ============================================================
# 3. VALIDATE DATA
# ============================================================

missing_columns = [
    column
    for column in feature_columns + [target_column]
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


print("\nMissing values:")
print(df[feature_columns + [target_column]].isnull().sum())


# Remove rows with missing values for the first prototype
df = df.dropna(
    subset=feature_columns + [target_column]
).copy()


# ============================================================
# 4. CREATE X AND y
# ============================================================

X = df[feature_columns]
y = df[target_column]


# ============================================================
# 5. ENCODE LABELS
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\nClass encoding:")

for class_name, class_id in zip(
    label_encoder.classes_,
    label_encoder.transform(label_encoder.classes_)
):
    print(f"{class_id} -> {class_name}")


# ============================================================
# 6. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================================
# 7. CREATE XGBOOST MODEL
# ============================================================

model = XGBClassifier(
    objective="multi:softprob",
    num_class=len(label_encoder.classes_),

    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,

    subsample=0.8,
    colsample_bytree=0.8,

    random_state=RANDOM_STATE,
    eval_metric="mlogloss"
)


# ============================================================
# 8. TRAIN MODEL
# ============================================================

print("\nTraining XGBoost model...")

model.fit(
    X_train,
    y_train
)

print("Training complete.")


# ============================================================
# 9. EVALUATION
# ============================================================

print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(f"\nAccuracy: {accuracy:.4f}")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_
    )
)


print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 10. FEATURE IMPORTANCE
# ============================================================

print("\nFeature Importance:")

importance = pd.Series(
    model.feature_importances_,
    index=feature_columns
).sort_values(
    ascending=False
)

print(importance)


# ============================================================
# 11. SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_PATH),
    exist_ok=True
)

model_package = {
    "model": model,
    "label_encoder": label_encoder,
    "features": feature_columns
}

joblib.dump(
    model_package,
    MODEL_PATH
)

print("\nModel saved to:")

print(MODEL_PATH)

print("\nTraining finished successfully.")
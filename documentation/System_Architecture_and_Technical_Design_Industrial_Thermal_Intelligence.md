# 🏗️ System Architecture & Technical Design
## AI-Enabled Geospatial System for Industrial Fire & Persistent Thermal Source Monitoring

**Version:** 1.0  
**Date:** 21 August 2026  
**Project:** AI + GIS + Remote Sensing  
**Architecture Style:** Modular, API-driven, geospatial intelligence platform

---

# 1. Document Purpose

This document defines the technical architecture and system design for an AI-enabled geospatial platform that detects, classifies, monitors, and visualizes industrial fires and persistent thermal sources.

The system integrates:

- Satellite thermal anomaly data
- Satellite optical imagery
- Industrial infrastructure databases
- Land-cover information
- Historical thermal observations
- Geospatial processing
- Machine learning
- Temporal analytics
- Risk scoring
- PostGIS
- Interactive GIS visualization

The architecture is designed to support an MVP and provide a clear path toward regional and national-scale deployment.

---

# 2. System Goals

The technical architecture must enable the platform to:

1. Ingest thermal anomaly data.
2. Normalize and validate heterogeneous geospatial data.
3. Associate anomalies with nearby industrial infrastructure.
4. Determine surrounding land-cover characteristics.
5. Extract satellite-image features.
6. Generate spatial and temporal features.
7. Classify thermal events using AI/ML.
8. Detect persistent and recurring thermal sources.
9. Calculate event risk.
10. Store results in a spatial database.
11. Expose results through APIs.
12. Visualize events through a GIS dashboard.
13. Support future alerts and automated reporting.
14. Scale from a pilot region to large geographic areas.

---

# 3. High-Level Architecture

```text
                         ┌──────────────────────────┐
                         │      DATA SOURCES        │
                         ├──────────────────────────┤
                         │ NASA FIRMS / VIIRS       │
                         │ MODIS                    │
                         │ Sentinel-2               │
                         │ Landsat                  │
                         │ Land Cover               │
                         │ Industrial Databases     │
                         │ OpenStreetMap / GIS      │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │     DATA INGESTION       │
                         │      & VALIDATION        │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ GEOSPATIAL PREPROCESSING │
                         ├──────────────────────────┤
                         │ Coordinate normalization │
                         │ Spatial filtering        │
                         │ Raster processing        │
                         │ Deduplication            │
                         └────────────┬─────────────┘
                                      │
                  ┌───────────────────┼───────────────────┐
                  ▼                   ▼                   ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │ Spatial Context │ │ Image Features  │ │ Temporal        │
        │ Extraction      │ │ Extraction      │ │ Analytics       │
        ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
        │ Facility        │ │ Spectral bands  │ │ Persistence      │
        │ Land cover      │ │ NDVI            │ │ Recurrence      │
        │ Population      │ │ Built-up index  │ │ Duration        │
        │ Proximity       │ │ Image patches   │ │ Trends          │
        └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                 └───────────────────┼───────────────────┘
                                     ▼
                         ┌──────────────────────────┐
                         │    FEATURE FUSION        │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │       AI / ML ENGINE     │
                         ├──────────────────────────┤
                         │ Baseline ML              │
                         │ XGBoost / LightGBM       │
                         │ CNN / ViT extension      │
                         │ Confidence estimation    │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    RISK & EVENT ENGINE   │
                         ├──────────────────────────┤
                         │ Classification           │
                         │ Persistence              │
                         │ Risk score               │
                         │ Event severity           │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │      POSTGRESQL          │
                         │        + POSTGIS         │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────┴─────────────┐
                         ▼                          ▼
               ┌──────────────────┐       ┌──────────────────┐
               │    FastAPI       │       │ Analytics / Jobs │
               │    Backend       │       │ Scheduler        │
               └────────┬─────────┘       └──────────────────┘
                        │
                        ▼
               ┌──────────────────┐
               │  GIS WEB CLIENT  │
               │ React + MapLibre │
               │ + Deck.gl        │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ Users / Analysts │
               └──────────────────┘
```

---

# 4. Architecture Principles

The system should follow these principles:

## 4.1 Modular

Each major capability should be independently replaceable.

Example:

```text
Satellite Source
       ↓
Ingestion Module
       ↓
Feature Module
       ↓
ML Model
```

A new satellite source should not require redesigning the entire system.

---

## 4.2 API-First

The backend should expose functionality through documented REST APIs.

This allows future integration with:

- Mobile applications
- Government GIS systems
- External dashboards
- Notification systems
- Other analytical applications

---

## 4.3 Geospatial-Native

Spatial relationships should be handled using PostGIS rather than treating latitude and longitude as ordinary numeric fields.

Examples:

- Within radius
- Intersects
- Contains
- Nearest facility
- Spatial clustering
- Geographic filtering

---

## 4.4 Data-Driven

AI decisions should be based on multiple evidence sources rather than thermal intensity alone.

---

## 4.5 Human-in-the-Loop

High-risk or low-confidence predictions should remain available for human review.

---

## 4.6 Scalable

The MVP may process one region, but the architecture should support distributed processing and larger datasets later.

---

# 5. System Components

## 5.1 Data Source Layer

The data source layer provides raw observations.

### Primary Sources

#### Thermal

- NASA FIRMS
- VIIRS
- MODIS

#### Optical

- Sentinel-2
- Landsat

#### Geospatial

- Industrial facility datasets
- Land-cover datasets
- OpenStreetMap
- Administrative boundaries
- Optional population datasets

---

# 6. Data Ingestion Layer

The ingestion layer is responsible for obtaining external data and converting it into internal formats.

## Responsibilities

- Download/fetch data
- Validate data
- Normalize schemas
- Convert coordinate systems
- Remove duplicates
- Record source metadata
- Store raw and processed data

### Pipeline

```text
External Source
      ↓
Fetcher
      ↓
Parser
      ↓
Schema Validation
      ↓
Coordinate Normalization
      ↓
Deduplication
      ↓
Database / Object Storage
```

---

# 7. Thermal Anomaly Pipeline

Thermal observations form the starting point of the event pipeline.

## Input

Typical fields:

```text
latitude
longitude
timestamp
satellite
confidence
FRP
brightness_temperature
observation_source
```

## Processing

```text
Raw Thermal Data
       ↓
Validation
       ↓
Remove Invalid Records
       ↓
Normalize Coordinates
       ↓
Normalize Timestamp
       ↓
Duplicate Detection
       ↓
Spatial Indexing
       ↓
Store
```

---

# 8. Geospatial Processing Layer

This layer converts raw geographic information into features useful for AI.

## 8.1 Facility Proximity

For every thermal anomaly:

```text
Thermal Point
     ↓
Search nearby facilities
     ↓
Calculate distance
     ↓
Select nearest / relevant facilities
```

Example output:

```text
nearest_facility_type = petrochemical
nearest_facility_distance = 420 m
facilities_within_1km = 3
facilities_within_5km = 12
```

---

## 8.2 Land-Cover Extraction

The system determines the land-cover category surrounding an anomaly.

Example:

```text
land_cover = industrial
industrial_ratio_500m = 0.72
vegetation_ratio_500m = 0.08
builtup_ratio_500m = 0.85
```

---

## 8.3 Spatial Context

Additional contextual features can include:

- Distance to roads
- Distance to settlements
- Distance to water
- Distance to forest
- Distance to agricultural land
- Administrative region
- Population exposure
- Industrial-zone membership

---

# 9. Satellite Image Processing

Optical satellite imagery can provide additional context around an anomaly.

## Image Processing Pipeline

```text
Satellite Image
      ↓
Cloud / Quality Filtering
      ↓
Geographic Cropping
      ↓
Image Patch Generation
      ↓
Band Selection
      ↓
Feature Extraction
      ↓
AI Image Model
```

---

# 10. Spectral Feature Engineering

Potential derived features include:

- NDVI
- NDWI
- NDBI
- Burn-related indices where appropriate
- Band ratios
- Texture features
- Reflectance statistics

Example:

```text
NDVI
NDBI
NDWI
Mean Red Reflectance
Mean NIR Reflectance
Built-up Percentage
Vegetation Percentage
```

The final feature set should be determined through experimentation and validation.

---

# 11. Temporal Analytics Engine

Thermal events should not always be treated as independent points.

The temporal engine identifies whether observations represent:

- One-time event
- Short-duration event
- Recurring event
- Persistent thermal source
- Abnormal change from historical behavior

## Example

```text
Day 1   ●
Day 2   ●
Day 3   ●
Day 4   ●
Day 5   ●
         ↓
   Persistent Source
```

---

# 12. Event Clustering

Multiple nearby satellite detections can represent the same real-world event.

The system should cluster observations using spatial and temporal proximity.

Example:

```text
Detection A ─┐
Detection B ─┼──► EVENT-00042
Detection C ─┘
```

Potential approaches:

- DBSCAN
- HDBSCAN
- Grid-based clustering
- Spatial-temporal clustering

DBSCAN is a strong initial choice because it does not require the number of clusters to be known in advance.

---

# 13. Feature Engineering

The feature engineering layer combines information from all available sources.

## Example Feature Vector

```text
Thermal Features
----------------
FRP
brightness_temperature
confidence

Spatial Features
----------------
industrial_distance
facility_count_1km
facility_count_5km
distance_to_road
distance_to_settlement

Land-Cover Features
-------------------
land_cover_class
industrial_ratio
vegetation_ratio
builtup_ratio

Temporal Features
-----------------
detection_count
event_duration
recurrence_frequency
historical_frequency

Satellite Features
------------------
NDVI
NDBI
NDWI
spectral_statistics
```

---

# 14. AI / ML Architecture

The recommended implementation is staged.

## Stage 1 — Baseline Model

Use structured features with:

- XGBoost
- LightGBM
- Random Forest as a benchmark

### Why?

Structured geospatial and temporal features are highly important for this problem.

---

## Stage 2 — Image Model

Use satellite image patches with:

- CNN
- Vision Transformer
- Remote-sensing pretrained models where appropriate

---

## Stage 3 — Feature Fusion

Combine:

```text
Tabular Model
     +
Image Model
     +
Temporal Model
     ↓
Final Prediction
```

---

# 15. Classification Taxonomy

Initial categories:

```text
1. Industrial Fire
2. Gas Flare
3. Industrial Thermal Source
4. Agricultural Burning
5. Wildfire / Forest Fire
6. Mining-Related Thermal Event
7. Other / Unknown
```

The taxonomy should remain configurable because real-world data may show that some categories are difficult to distinguish reliably.

---

# 16. AI Inference Pipeline

```text
Thermal Event
      ↓
Feature Extraction
      ↓
Feature Validation
      ↓
Model Inference
      ↓
Class Probabilities
      ↓
Confidence Calculation
      ↓
Classification
      ↓
Risk Engine
```

Example:

```json
{
  "industrial_fire": 0.947,
  "gas_flare": 0.021,
  "wildfire": 0.008,
  "agricultural_burning": 0.014,
  "unknown": 0.010
}
```

Final prediction:

```text
Industrial Fire
Confidence = 94.7%
```

---

# 17. Confidence and Unknown Handling

The model should not be forced to classify every event confidently.

Example policy:

```text
Confidence >= 0.80
        ↓
High-confidence prediction

0.50 - 0.79
        ↓
Medium-confidence prediction

< 0.50
        ↓
Low-confidence / Unknown
```

Thresholds should be selected using validation data rather than assumed permanently.

---

# 18. Risk Engine

The risk engine converts event characteristics into an operational risk score.

A possible initial formulation is:

```text
Risk Score =
    0.30 × Thermal Intensity
  + 0.20 × Persistence
  + 0.20 × Industrial Proximity
  + 0.15 × Event Growth
  + 0.15 × Population Exposure
```

All components should be normalized before combining them.

## Risk Levels

```text
0–30      LOW
31–60     MEDIUM
61–80     HIGH
81–100    CRITICAL
```

The weights and thresholds should be calibrated using domain knowledge and historical validation.

---

# 19. Database Architecture

## Recommended Database

**PostgreSQL + PostGIS**

PostGIS provides spatial data types, spatial indexing, and geographic functions required by the system.

---

# 20. Core Database Entities

```text
industrial_facilities
thermal_observations
events
event_detections
land_cover
satellite_images
predictions
risk_scores
model_versions
users
audit_logs
```

---

# 21. Database Schema

## 21.1 industrial_facilities

```text
id
name
facility_type
operator
geometry
latitude
longitude
source
created_at
updated_at
```

---

## 21.2 thermal_observations

```text
id
source
satellite
timestamp
latitude
longitude
geometry
confidence
frp
brightness_temperature
raw_reference
created_at
```

---

## 21.3 events

```text
id
event_code
geometry
first_detected
last_detected
detection_count
persistence_status
current_class
confidence
risk_score
risk_level
status
created_at
updated_at
```

---

## 21.4 event_detections

```text
id
event_id
thermal_observation_id
timestamp
geometry
frp
confidence
```

---

## 21.5 predictions

```text
id
event_id
model_version
predicted_class
confidence
probability_json
created_at
```

---

## 21.6 risk_scores

```text
id
event_id
thermal_component
persistence_component
industrial_component
growth_component
population_component
total_score
risk_level
created_at
```

---

# 22. Spatial Indexing

Spatial indexes should be created on geometry columns.

Example:

```sql
CREATE INDEX idx_thermal_observations_geom
ON thermal_observations
USING GIST (geometry);
```

This enables efficient queries such as:

```text
Find all industrial facilities within 1 km
of a thermal anomaly.
```

---

# 23. Backend Architecture

## Recommended Framework

**FastAPI**

The backend should expose REST APIs for:

- Thermal events
- Industrial facilities
- AI classification
- Risk scores
- Historical analytics
- Map layers
- User authentication
- Reports

---

# 24. API Design

## Event APIs

```text
GET /api/v1/events
GET /api/v1/events/{event_id}
GET /api/v1/events/{event_id}/history
GET /api/v1/events/{event_id}/nearby-facilities
```

## Classification APIs

```text
POST /api/v1/classify
GET /api/v1/predictions/{event_id}
```

## Facility APIs

```text
GET /api/v1/facilities
GET /api/v1/facilities/{facility_id}
GET /api/v1/facilities/{facility_id}/events
```

## Analytics APIs

```text
GET /api/v1/analytics/hotspots
GET /api/v1/analytics/persistence
GET /api/v1/analytics/trends
GET /api/v1/analytics/risk-map
```

## Map APIs

```text
GET /api/v1/map/events
GET /api/v1/map/facilities
GET /api/v1/map/land-cover
```

---

# 25. API Response Example

```json
{
  "event_id": "EVT-00042",
  "location": {
    "latitude": 28.1234,
    "longitude": 77.5678
  },
  "classification": {
    "label": "Industrial Fire",
    "confidence": 0.947
  },
  "risk": {
    "score": 82,
    "level": "HIGH"
  },
  "persistence": {
    "status": "RECURRING",
    "detections": 8
  },
  "nearest_facility": {
    "name": "Example Petrochemical Facility",
    "type": "Petrochemical",
    "distance_m": 420
  }
}
```

---

# 26. Frontend Architecture

## Recommended Stack

- React
- TypeScript
- MapLibre GL JS
- Deck.gl
- Charting library
- REST API client

---

# 27. GIS Dashboard Layout

```text
┌─────────────────────────────────────────────────────────┐
│ Header: Search | Date | Risk | Classification | Profile │
├───────────────┬───────────────────────────────┬─────────┤
│ Filters       │                               │ Event   │
│               │                               │ Details │
│ Event Type    │          GIS MAP              │         │
│ Risk Level    │                               │ Class   │
│ Date          │   🔥  🏭  🔥  🟠             │ Conf.   │
│ Facility      │                               │ Risk    │
│ Persistence   │                               │ History │
│               │                               │         │
├───────────────┴───────────────────────────────┴─────────┤
│ Analytics: Events | Industrial Fires | Persistent | Risk│
└─────────────────────────────────────────────────────────┘
```

---

# 28. GIS Map Layers

The dashboard should support:

### Base Layers

- Street map
- Satellite imagery
- Terrain

### Analysis Layers

- Thermal anomalies
- Industrial fires
- Gas flares
- Wildfires
- Agricultural burning
- Persistent sources

### Context Layers

- Industrial facilities
- Power plants
- Mines
- Refineries
- LNG terminals
- Land cover
- Administrative boundaries

---

# 29. Map Symbology

The UI should use consistent categories.

Example:

```text
Industrial Fire          🔥
Gas Flare                🟠
Persistent Source        🔴
Wildfire                 🌲
Agricultural Burning     🟡
Industrial Facility      🏭
```

Actual implementation should use accessible visual symbology rather than relying only on color.

---

# 30. Event Investigation Workflow

```text
User selects event
       ↓
Load event details
       ↓
Load AI prediction
       ↓
Load confidence
       ↓
Load risk score
       ↓
Query nearby facilities
       ↓
Query historical detections
       ↓
Load satellite imagery
       ↓
Display timeline
       ↓
User reviews evidence
```

---

# 31. Data Flow

## End-to-End Data Flow

```text
                    DATA SOURCES
                         │
                         ▼
                 Data Ingestion
                         │
                         ▼
                  Raw Data Store
                         │
                         ▼
                Data Normalization
                         │
                         ▼
              Thermal Event Pipeline
                         │
                         ▼
               Spatial Event Clustering
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       Facilities    Land Cover    Imagery
            │            │            │
            └────────────┼────────────┘
                         ▼
                 Feature Engineering
                         │
                         ▼
                    AI Model
                         │
                         ▼
                Classification
                         │
                         ▼
                Temporal Analysis
                         │
                         ▼
                   Risk Engine
                         │
                         ▼
                    PostGIS
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          FastAPI               Analytics
              │
              ▼
          GIS Frontend
              │
              ▼
             User
```

---

# 32. Batch vs Near-Real-Time Processing

The architecture should support both.

## Batch Mode

Suitable for:

- Historical analysis
- Model training
- Large-scale backfills
- Daily/periodic processing

```text
Data Download
     ↓
Batch Pipeline
     ↓
Feature Extraction
     ↓
AI Inference
     ↓
Database
```

## Near-Real-Time Mode

Suitable for:

- New thermal observations
- High-risk event monitoring
- Alerts

```text
New Observation
     ↓
Queue
     ↓
Processing Worker
     ↓
AI Inference
     ↓
Risk Engine
     ↓
Alert
```

---

# 33. Recommended Processing Architecture

For the MVP:

```text
FastAPI
   │
   ├── PostgreSQL/PostGIS
   │
   ├── ML Service
   │
   └── Scheduled Data Jobs
```

For scale:

```text
API Gateway
     │
     ├── Event Service
     ├── ML Service
     ├── GIS Service
     ├── Analytics Service
     └── Alert Service
             │
             ▼
       Message Queue
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
   Worker  Worker  Worker
      │      │      │
      └──────┼──────┘
             ▼
       PostGIS / Object Storage
```

---

# 34. Object Storage

Large satellite images should not be stored directly inside PostgreSQL.

Use object storage for:

- Satellite images
- Raster products
- Image patches
- Model artifacts
- Large exported reports

PostGIS should store:

- Metadata
- Geometry
- Spatial relationships
- Event records
- Predictions
- References to objects

---

# 35. ML Model Registry

Each prediction should record the model version.

Example:

```text
model_name:
industrial-thermal-classifier

model_version:
1.3.0

trained_date:
2026-08-20

feature_version:
2.1

threshold_version:
1.0
```

This allows reproducibility and auditing.

---

# 36. Model Training Architecture

```text
Historical Data
      ↓
Labeling
      ↓
Feature Engineering
      ↓
Train / Validation / Test
      ↓
Baseline Model
      ↓
Evaluation
      ↓
Hyperparameter Tuning
      ↓
Model Selection
      ↓
Model Registry
      ↓
Deployment
```

---

# 37. Recommended Model Development Sequence

## Model 0 — Rule-Based Baseline

Example:

```text
IF thermal anomaly is close to
industrial facility
AND occurs repeatedly
THEN flag as industrial-related
```

This establishes a simple baseline.

---

## Model 1 — Random Forest / XGBoost

Use structured features.

---

## Model 2 — Image Model

Use satellite image patches.

---

## Model 3 — Feature Fusion

Combine:

```text
Geospatial
+
Thermal
+
Temporal
+
Satellite Image
```

This should become the production candidate after validation.

---

# 38. Training Data Pipeline

```text
Thermal Observations
        ↓
Candidate Events
        ↓
Spatial / Temporal Grouping
        ↓
Ground Truth / Expert Labeling
        ↓
Feature Extraction
        ↓
Dataset Versioning
        ↓
Train / Validation / Test
```

---

# 39. Dataset Split Strategy

Random splitting alone can produce misleading results because nearby observations may be highly correlated.

The preferred evaluation strategy should consider:

### Spatial Split

Train on some geographic areas and test on separate areas.

### Temporal Split

Train on historical periods and test on future periods.

### Facility Split

Where possible, test on facilities not represented in training.

This helps measure generalization.

---

# 40. Model Evaluation

Required metrics:

- Precision
- Recall
- F1-score
- Accuracy
- Confusion matrix
- ROC-AUC where appropriate
- Class-wise performance

For the operational system, additional metrics should include:

- False alarms per region
- High-risk event recall
- Facility association accuracy
- Detection-to-classification latency

---

# 41. Security Architecture

```text
User
 ↓
HTTPS
 ↓
Authentication
 ↓
Authorization
 ↓
API
 ↓
Database
```

Security requirements:

- HTTPS
- Secure authentication
- Role-based access control
- Input validation
- Rate limiting
- Secure secrets
- Database permissions
- Audit logging

---

# 42. User Roles

## Administrator

- Manage users
- Manage datasets
- Manage models
- Configure system

## Analyst

- View events
- Investigate events
- Export reports
- Analyze historical data

## Viewer

- View maps
- View approved event information
- Basic filtering

---

# 43. Observability

The system should monitor:

### Infrastructure

- CPU
- Memory
- GPU
- Storage
- API latency

### Data Pipeline

- Records ingested
- Failed records
- Data freshness
- Duplicate rate

### AI

- Prediction distribution
- Confidence distribution
- Model version
- Drift indicators

### Application

- API errors
- Dashboard errors
- User activity
- Alert failures

---

# 44. Logging

Each processing step should generate structured logs.

Example:

```text
timestamp
service
event_id
operation
status
processing_time
model_version
error_code
```

Avoid storing unnecessary sensitive information in logs.

---

# 45. Deployment Architecture

## MVP Deployment

```text
                    Internet
                       │
                       ▼
                Reverse Proxy
                       │
              ┌────────┴────────┐
              ▼                 ▼
          React App          FastAPI
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
            PostGIS          ML Model        Scheduler
                                │
                                ▼
                         Object Storage
```

---

# 46. Containerization

Recommended containers:

```text
frontend
backend
ml-service
worker
postgres-postgis
scheduler
reverse-proxy
```

Docker Compose can be used for the MVP.

For large-scale deployment, containers can later be orchestrated using a platform such as Kubernetes.

---

# 47. Recommended Technology Stack

## Frontend

```text
React
TypeScript
MapLibre GL JS
Deck.gl
```

## Backend

```text
Python
FastAPI
Pydantic
```

## AI/ML

```text
Python
Scikit-learn
XGBoost
LightGBM
PyTorch
OpenCV
```

## Geospatial

```text
GeoPandas
Rasterio
GDAL
Shapely
PyProj
```

## Database

```text
PostgreSQL
PostGIS
```

## Data Processing

```text
Pandas
NumPy
GeoPandas
Rasterio
```

## Infrastructure

```text
Docker
Docker Compose
Object Storage
GPU infrastructure when required
```

---

# 48. Technology Selection Rationale

| Technology | Reason |
|---|---|
| Python | Strong AI + geospatial ecosystem |
| FastAPI | Fast, typed API development |
| PostgreSQL | Mature relational database |
| PostGIS | Native spatial querying |
| React | Modular frontend |
| MapLibre | Flexible interactive maps |
| Deck.gl | Large-scale geospatial visualization |
| GeoPandas | Vector geospatial processing |
| Rasterio | Raster processing |
| XGBoost | Strong tabular ML baseline |
| PyTorch | Deep-learning extensibility |
| Docker | Reproducible deployment |

---

# 49. Folder Structure

A recommended project structure:

```text
industrial-thermal-intelligence/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── maps/
│   └── services/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   └── main.py
│   │
│   └── tests/
│
├── ml/
│   ├── data/
│   ├── features/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   └── models/
│
├── geospatial/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── raster/
│   ├── vector/
│   └── spatial_features/
│
├── workers/
│   ├── ingestion/
│   ├── processing/
│   ├── inference/
│   └── alerts/
│
├── database/
│   ├── migrations/
│   └── seed/
│
├── infrastructure/
│   ├── docker/
│   └── deployment/
│
├── docs/
│
└── README.md
```

---

# 50. API-to-Database Flow

```text
Frontend
   │
   │ HTTP/JSON
   ▼
FastAPI
   │
   ├── Authentication
   │
   ├── Validation
   │
   ├── Business Logic
   │
   └── Spatial Queries
          │
          ▼
      PostGIS
          │
          ▼
       Results
          │
          ▼
      FastAPI
          │
          ▼
       Frontend
```

---

# 51. Spatial Query Examples

## Find Facilities Near Event

```sql
SELECT
    id,
    name,
    facility_type,
    ST_Distance(
        geometry::geography,
        ST_SetSRID(
            ST_MakePoint(:longitude, :latitude),
            4326
        )::geography
    ) AS distance_m
FROM industrial_facilities
WHERE ST_DWithin(
    geometry::geography,
    ST_SetSRID(
        ST_MakePoint(:longitude, :latitude),
        4326
    )::geography,
    5000
)
ORDER BY distance_m;
```

---

# 52. Event Lifecycle

```text
DETECTED
   ↓
VALIDATED
   ↓
CLUSTERED
   ↓
FEATURES EXTRACTED
   ↓
CLASSIFIED
   ↓
RISK SCORED
   ↓
DISPLAYED
   ↓
MONITORED
   ↓
RESOLVED / ARCHIVED
```

Possible status values:

```text
NEW
UNDER_REVIEW
CONFIRMED
MONITORING
RESOLVED
FALSE_POSITIVE
ARCHIVED
```

---

# 53. Alert Architecture

Future alert system:

```text
New Event
   ↓
Classification
   ↓
Risk Score
   ↓
Is Risk >= Threshold?
   │
   ├── NO → Store
   │
   └── YES
          ↓
       Alert Engine
          ↓
   Email / SMS / Webhook
          ↓
      User / Agency
```

Alerts should include:

- Event location
- Event class
- Confidence
- Risk score
- Facility information
- Detection time
- Map link/reference

---

# 54. Scalability Strategy

## Level 1 — Prototype

```text
Single server
PostGIS
FastAPI
React
Local ML inference
```

## Level 2 — Regional

```text
Cloud VM
Managed PostgreSQL
Object storage
Background workers
GPU inference
```

## Level 3 — National

```text
Load balancer
Multiple API instances
Message queue
Distributed workers
Central PostGIS
Object storage
Model-serving infrastructure
Monitoring stack
```

---

# 55. Reliability Strategy

The system should avoid losing observations when an external data source is temporarily unavailable.

Recommended mechanisms:

- Retry logic
- Job queues
- Idempotent ingestion
- Data checksums
- Source timestamps
- Failed-job tracking
- Backfill support

---

# 56. Data Versioning

Every major dataset should have:

```text
dataset_name
version
source
retrieval_date
coverage
processing_version
license
```

Example:

```text
dataset:
industrial_facilities

version:
2026.08

source:
External GIS dataset

retrieved:
2026-08-21
```

---

# 57. Model Versioning

Every prediction should be traceable to:

```text
model_version
feature_version
dataset_version
threshold_version
inference_timestamp
```

This is important when model behavior changes over time.

---

# 58. Disaster Recovery

Minimum requirements:

- Automated database backups
- Object-storage versioning where available
- Configuration backups
- Model artifact backups
- Recovery procedure documentation

---

# 59. Technical MVP Architecture

The recommended first implementation is intentionally simple:

```text
             FIRMS / Thermal Data
                       │
                       ▼
                Python Ingestion
                       │
                       ▼
              GeoPandas Processing
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Industrial DB         Land Cover
             │                   │
             └─────────┬─────────┘
                       ▼
                 Feature Table
                       │
                       ▼
                  XGBoost Model
                       │
                       ▼
                 Event Prediction
                       │
                       ▼
                    PostGIS
                       │
                       ▼
                    FastAPI
                       │
                       ▼
             React + MapLibre GIS
```

This architecture is sufficient for an SIH prototype and can be expanded later.

---

# 60. Advanced Architecture

For a production-grade version:

```text
                    ┌─────────────────┐
                    │ Satellite APIs  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Data Ingestion  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Message Queue   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Thermal Worker  Image Worker   Spatial Worker
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    Feature Store
                             │
                             ▼
                     ML Model Server
                             │
                             ▼
                      Risk Engine
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
             PostGIS                 Object Store
                │                         │
                └────────────┬────────────┘
                             ▼
                         API Layer
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
              GIS        Analytics      Alerts
             Client       Dashboard      Service
```

---

# 61. Technical Design Decisions

## Decision 1

**Use PostGIS rather than a standard SQL database.**

Reason:

The product is fundamentally spatial.

---

## Decision 2

**Start with XGBoost/LightGBM for classification.**

Reason:

The first feature set is primarily structured thermal, spatial, and temporal data.

---

## Decision 3

**Add CNN/ViT only after the baseline works.**

Reason:

This reduces development risk and allows measurable incremental improvement.

---

## Decision 4

**Use existing satellite thermal products rather than building satellite detection from scratch.**

Reason:

The main innovation is contextual classification and industrial intelligence.

---

## Decision 5

**Separate large imagery from relational event data.**

Reason:

Satellite imagery can be much larger than event metadata and is better suited to object storage.

---

# 62. Main Technical Risks

| Risk | Technical Impact | Mitigation |
|---|---|---|
| Poor labels | Model performance | Expert annotation + dataset versioning |
| Satellite cloud cover | Missing imagery | Multi-source imagery |
| Low spatial resolution | Small-event ambiguity | Multi-source data fusion |
| Class imbalance | Poor minority-class recall | Weighted loss / sampling |
| Spatial leakage | Inflated evaluation | Spatial train/test split |
| Temporal leakage | Inflated evaluation | Temporal split |
| Data latency | Delayed alerts | Source timestamp + freshness monitoring |
| API failure | Missing data | Retry + backfill |
| Model drift | Performance degradation | Monitoring + retraining |
| False positives | Operational burden | Confidence + human review |

---

# 63. Final Architecture Summary

The proposed system is a **multi-layer geospatial intelligence architecture**:

```text
1. DATA SOURCES
      ↓
2. DATA INGESTION
      ↓
3. GEOSPATIAL PREPROCESSING
      ↓
4. EVENT DETECTION & CLUSTERING
      ↓
5. SPATIAL + TEMPORAL + IMAGE FEATURES
      ↓
6. FEATURE FUSION
      ↓
7. AI CLASSIFICATION
      ↓
8. PERSISTENCE ANALYSIS
      ↓
9. RISK SCORING
      ↓
10. POSTGIS
      ↓
11. FASTAPI
      ↓
12. GIS DASHBOARD
      ↓
13. ALERTS / REPORTS
```

---

# 64. Final Recommended Tech Stack

| Layer | Technology |
|---|---|
| Satellite thermal data | FIRMS / VIIRS / MODIS |
| Optical imagery | Sentinel-2 / Landsat |
| Vector processing | GeoPandas / Shapely |
| Raster processing | Rasterio / GDAL |
| Data processing | Python / Pandas / NumPy |
| ML baseline | XGBoost / LightGBM |
| Deep learning | PyTorch |
| Spatial database | PostgreSQL + PostGIS |
| Backend | FastAPI |
| Frontend | React + TypeScript |
| Maps | MapLibre GL JS |
| Large-scale visualization | Deck.gl |
| Background jobs | Python workers / scheduler |
| Object storage | S3-compatible storage |
| Containerization | Docker |
| Production orchestration | Kubernetes or managed container platform |
| Monitoring | Logs + metrics + model monitoring |

---

# 65. Architecture Acceptance Criteria

The technical architecture is considered ready for MVP implementation when:

- [ ] At least one thermal data source can be ingested.
- [ ] Thermal observations are stored with spatial geometry.
- [ ] Industrial facilities can be queried spatially.
- [ ] Land-cover information can be associated with events.
- [ ] Event clustering works on historical observations.
- [ ] A baseline ML model can receive engineered features.
- [ ] Model predictions and confidence are stored.
- [ ] Persistence can be calculated.
- [ ] Risk scores can be generated.
- [ ] FastAPI exposes event and map APIs.
- [ ] React GIS dashboard displays events.
- [ ] Users can filter and inspect events.
- [ ] Model and dataset versions are tracked.
- [ ] Docker-based local deployment works.
- [ ] The complete pipeline can be demonstrated end-to-end.

---

# 66. Conclusion

The proposed architecture separates the system into clear layers for data ingestion, geospatial processing, feature engineering, AI inference, temporal intelligence, risk scoring, spatial storage, APIs, and GIS visualization.

The most important architectural principle is that **thermal anomaly detection is only the starting point**.

The system's intelligence comes from combining:

```text
Thermal Data
      +
Industrial Context
      +
Land Cover
      +
Satellite Imagery
      +
Temporal History
      +
AI
      +
GIS
```

This architecture provides a practical path from an SIH prototype to a scalable industrial thermal-intelligence platform.

The recommended MVP should remain focused:

> **Thermal anomaly → geospatial context → XGBoost classification → persistence → PostGIS → FastAPI → GIS dashboard**

Once this pipeline is stable, advanced satellite-image models, distributed processing, automated alerts, and national-scale deployment can be added without redesigning the core product.

# 📋 Product & Requirements Document
## AI-Enabled Geospatial System for Industrial Fire & Persistent Thermal Source Monitoring

**Version:** 1.0  
**Date:** 21 August 2026  
**Project Type:** AI + GIS + Remote Sensing  
**Primary Objective:** Automatically identify, classify, and monitor industrial fires and persistent thermal sources using satellite thermal anomalies, land-cover information, industrial infrastructure data, and satellite imagery.

---

## 1. Executive Summary

Industrial facilities such as oil refineries, petrochemical complexes, thermal power plants, steel industries, mining areas, and LNG terminals produce thermal signatures that can be detected from space. Accidental industrial fires, gas leaks, explosions, abnormal flaring, and other thermal events can create serious risks to infrastructure, public safety, and the environment.

Existing satellite fire-monitoring systems such as NASA FIRMS provide valuable thermal anomaly detections, but a thermal anomaly by itself does not reveal whether the source is an industrial fire, gas flare, agricultural burning, mining activity, or wildfire.

This project proposes an **AI-enabled geospatial intelligence platform** that combines:

- Satellite thermal anomaly data
- Satellite optical imagery
- Land-cover information
- Industrial infrastructure databases
- Historical thermal-event information
- Spatial and temporal features
- Machine-learning classification

The system will classify detected thermal events, estimate confidence and risk, store results in a spatial database, and visualize them through an interactive GIS dashboard.

---

# 2. Problem Statement

Current satellite-based fire-monitoring systems can detect thermal anomalies, but they generally do not provide sufficient contextual classification of the source.

A detected thermal hotspot could represent:

- Industrial fire
- Gas flare
- Oil/refinery thermal activity
- Thermal power plant activity
- Mining-related thermal activity
- Agricultural burning
- Forest/wildfire
- Other persistent or unexplained thermal sources

This creates a significant information gap for authorities, industries, environmental agencies, and emergency-response organizations.

The proposed system addresses this gap by combining thermal observations with geographic, industrial, land-cover, satellite-image, and historical information to automatically classify and monitor thermal events.

---

# 3. Proposed Solution

The proposed platform will operate as a multi-source AI and GIS pipeline.

### High-Level Workflow

```text
Satellite Thermal Data
        │
        ▼
Thermal Anomaly Detection
        │
        ▼
Spatial Context Extraction
        │
        ├──────────────► Industrial Infrastructure
        ├──────────────► Land Cover
        ├──────────────► Satellite Imagery
        └──────────────► Historical Events
        │
        ▼
Feature Engineering
        │
        ▼
AI Classification
        │
        ├── Industrial Fire
        ├── Gas Flare
        ├── Industrial Thermal Source
        ├── Agricultural Burning
        ├── Wildfire
        └── Other / Unknown
        │
        ▼
Confidence + Risk Scoring
        │
        ▼
PostGIS Spatial Database
        │
        ▼
Interactive GIS Dashboard
        │
        ▼
Monitoring / Alerts / Reports
```

---

# 4. Product Vision

> **To provide an AI-powered geospatial intelligence platform that converts satellite thermal anomalies into actionable information about industrial fires, persistent thermal sources, and other fire-related events.**

The system should help users move from:

**"There is a hotspot here."**

to:

**"This is likely an industrial fire near a petrochemical facility, detected repeatedly over the last six hours, with a high risk score."**

---

# 5. Product Objectives

## 5.1 Primary Objectives

1. Detect thermal anomalies from satellite data.
2. Identify whether a thermal anomaly is associated with industrial infrastructure.
3. Classify thermal events into meaningful categories.
4. Distinguish industrial fires from natural and agricultural fires.
5. Detect persistent thermal sources through historical analysis.
6. Combine multiple geospatial and satellite data sources.
7. Provide confidence scores for AI predictions.
8. Generate a risk score for detected events.
9. Store events using a spatial database.
10. Visualize events through an interactive GIS dashboard.

## 5.2 Secondary Objectives

- Support historical thermal-event analysis.
- Provide facility-level monitoring.
- Enable filtering by event type, date, location, and risk.
- Support future automated alerts.
- Provide explainable features behind AI classifications.
- Create a scalable architecture for regional or national deployment.

---

# 6. Target Users and Stakeholders

## 6.1 Government and Regulatory Agencies

### Needs

- Monitor industrial zones.
- Identify abnormal thermal activity.
- Support environmental monitoring.
- Investigate potentially dangerous events.
- Maintain historical event records.

### Value

The system provides a centralized geospatial view of potentially hazardous thermal activity.

---

## 6.2 Disaster Management and Emergency Response Teams

### Needs

- Quickly identify abnormal events.
- Determine event location.
- Estimate severity.
- Prioritize high-risk events.
- Monitor event progression.

### Value

AI-based classification and risk scoring can help prioritize investigation and response.

---

## 6.3 Industrial Facility Operators

### Needs

- Monitor their own facilities.
- Identify abnormal thermal events.
- Track recurring hotspots.
- Compare current activity with historical patterns.

### Value

The system can provide an independent satellite-based monitoring layer.

---

## 6.4 Environmental Monitoring Organizations

### Needs

- Monitor industrial emissions and thermal activity.
- Identify recurring hotspots.
- Analyze spatial patterns.
- Support environmental investigations.

---

## 6.5 Researchers and Analysts

### Needs

- Access historical events.
- Analyze spatial and temporal patterns.
- Evaluate AI predictions.
- Perform remote-sensing research.

---

# 7. User Personas

## Persona 1 — Government Monitoring Officer

**Role:** Environmental / infrastructure monitoring officer

**Goal:** Identify abnormal industrial thermal activity in a large geographic region.

**Pain Point:** Manual investigation of thousands of thermal anomalies is slow.

**Expected Solution:** A dashboard showing classified thermal events with confidence, location, facility information, and risk level.

---

## Persona 2 — Emergency Response Analyst

**Role:** Disaster-response analyst

**Goal:** Determine which detected events require immediate attention.

**Pain Point:** Raw thermal hotspot data does not indicate event severity or source type.

**Expected Solution:** Risk-ranked events with temporal persistence and industrial proximity information.

---

## Persona 3 — Industrial Safety Manager

**Role:** Industrial facility safety manager

**Goal:** Monitor thermal activity around a facility.

**Pain Point:** Existing satellite fire products provide limited facility-specific context.

**Expected Solution:** Facility-centric monitoring and historical thermal-event analysis.

---

# 8. Use Cases

## UC-01: Detect Thermal Anomaly

**Actor:** System

**Input:** Satellite thermal data

**Output:** Geographic thermal anomaly

### Flow

1. System receives thermal anomaly data.
2. Validates geographic coordinates.
3. Stores the anomaly.
4. Searches for relevant spatial context.
5. Sends the anomaly to the classification pipeline.

---

## UC-02: Classify Thermal Event

**Actor:** AI Model

**Input:** Thermal + spatial + temporal + satellite features

**Output:** Event class and confidence

### Example

```text
Event:
Latitude: XX.XXXX
Longitude: YY.YYYY

Prediction:
Industrial Fire

Confidence:
94.7%
```

---

## UC-03: Identify Industrial Association

**Actor:** GIS Engine

**Input:** Thermal anomaly coordinates

**Output:** Nearby industrial facilities

The system calculates proximity to:

- Refineries
- Petrochemical plants
- Power plants
- Steel plants
- Mines
- LNG facilities
- Other industrial infrastructure

---

## UC-04: Detect Persistent Thermal Source

**Actor:** Analytics Engine

**Input:** Historical thermal events

**Output:** Persistence classification

Example:

```text
Detections:
12

Time period:
7 days

Pattern:
Recurring

Classification:
Persistent Thermal Source
```

---

## UC-05: Visualize Event on GIS Map

**Actor:** User

**Input:** Event selection

**Output:** Map overlay and event details

The user can view:

- Event location
- Event category
- Confidence
- Risk score
- Nearby facility
- Detection time
- Historical detections
- Satellite imagery

---

## UC-06: Filter Events

Users should be able to filter events by:

- Date
- Location
- Event type
- Risk level
- Confidence
- Facility type
- Persistence
- Satellite source

---

## UC-07: Investigate Historical Event

The user selects an event and views:

- First detection
- Last detection
- Number of detections
- Historical intensity
- Classification history
- Nearby industrial facilities
- Satellite imagery

---

# 9. Functional Requirements

## FR-01 — Thermal Data Ingestion

The system shall ingest satellite thermal anomaly data from supported sources.

### Minimum information

- Latitude
- Longitude
- Timestamp
- Satellite/source
- Detection confidence
- Fire radiative power where available
- Brightness temperature where available

---

## FR-02 — Data Validation

The system shall validate incoming observations for:

- Missing coordinates
- Invalid timestamps
- Duplicate observations
- Invalid geographic values
- Missing mandatory fields

---

## FR-03 — Geospatial Context Extraction

For each thermal anomaly, the system shall identify nearby geographic features.

Examples:

- Industrial facilities
- Roads
- Built-up areas
- Forests
- Agricultural areas
- Mining areas
- Water bodies
- Administrative boundaries

---

## FR-04 — Industrial Facility Matching

The system shall calculate the distance between thermal anomalies and nearby industrial facilities.

Example:

```text
Thermal anomaly
      ↓
Nearest facility
      ↓
Petrochemical complex
      ↓
Distance = 420 m
```

---

## FR-05 — Land-Cover Classification

The system shall determine the land-cover category surrounding an anomaly.

Possible categories:

- Forest
- Agriculture
- Built-up
- Industrial
- Barren land
- Water
- Mining
- Other

---

## FR-06 — Satellite Image Analysis

Where suitable imagery is available, the system shall extract image-based information surrounding a detected event.

Potential sources include:

- Sentinel-2
- Landsat
- Other supported optical imagery

---

## FR-07 — AI Classification

The system shall classify thermal events.

### Initial classification categories

1. Industrial Fire
2. Gas Flare
3. Industrial Thermal Source
4. Agricultural Burning
5. Wildfire / Forest Fire
6. Mining-Related Thermal Event
7. Other / Unknown

The classification taxonomy may be expanded after dataset analysis.

---

## FR-08 — Confidence Score

Each AI prediction shall contain a confidence score.

Example:

```text
Class:
Industrial Fire

Confidence:
92.4%
```

The UI should distinguish between:

- High confidence
- Medium confidence
- Low confidence

---

## FR-09 — Persistence Detection

The system shall analyze repeated thermal detections at or near the same location.

The system should identify:

- One-time events
- Short-duration events
- Recurring events
- Persistent thermal sources

---

## FR-10 — Risk Scoring

The system should calculate a risk score based on relevant features.

Potential factors:

- Thermal intensity
- Persistence
- Industrial proximity
- Event growth
- Population exposure where available
- Historical abnormality
- Facility type

Example:

```text
Risk Score: 82/100
Risk Level: HIGH
```

---

## FR-11 — GIS Visualization

The system shall display classified events as map overlays.

The map should support:

- Zoom
- Pan
- Search
- Layer controls
- Event filtering
- Facility overlays
- Satellite imagery
- Land-cover layers

---

## FR-12 — Event Details

Clicking an event should display:

- Event ID
- Coordinates
- Timestamp
- Classification
- Confidence
- Risk score
- Thermal intensity
- Persistence
- Nearest facility
- Facility type
- Historical detections

---

## FR-13 — Historical Analytics

Users shall be able to analyze:

- Event frequency
- Event distribution
- Event categories
- Persistent hotspots
- Facility-specific patterns
- Time-based trends

---

## FR-14 — Data Export

The system should support export of selected results in formats such as:

- CSV
- GeoJSON
- JSON
- PDF report

---

## FR-15 — Alerting

Future versions should support alerts when:

- A high-risk event is detected.
- A new industrial fire is identified.
- An abnormal persistent source is detected.
- A previously monitored facility shows unusual activity.

---

# 10. Non-Functional Requirements

## NFR-01 — Performance

The system should process incoming thermal observations efficiently enough to support near-real-time or periodic monitoring depending on data-source latency.

---

## NFR-02 — Scalability

The architecture should support expansion from:

```text
Pilot region
     ↓
State / regional monitoring
     ↓
National monitoring
```

---

## NFR-03 — Availability

The dashboard and backend should be designed for reliable access during monitoring operations.

---

## NFR-04 — Security

The system should implement:

- Authentication
- Authorization
- Secure APIs
- Input validation
- Database access control
- Secure secrets management
- Audit logging

---

## NFR-05 — Maintainability

The system should use modular components so that:

- New satellite sources can be added.
- New ML models can be deployed.
- New event classes can be introduced.
- New GIS layers can be integrated.

---

## NFR-06 — Explainability

The system should expose important factors contributing to predictions wherever technically feasible.

Example:

```text
Prediction: Industrial Fire

Important factors:
+ 250 m from industrial facility
+ High thermal intensity
+ Industrial land cover
+ Repeated detections
+ Satellite-image evidence
```

---

# 11. MVP Definition

The Minimum Viable Product should focus on proving the core concept.

## MVP Features

### Data

- One thermal anomaly source
- One industrial facility dataset
- One land-cover dataset
- One satellite imagery source

### AI

- Thermal anomaly feature extraction
- Industrial vs non-industrial classification
- Baseline ML model
- Confidence score
- Basic persistence detection

### GIS

- Interactive map
- Thermal anomaly markers
- Industrial facility layer
- Classification-based visualization
- Event detail panel

### Database

- PostgreSQL
- PostGIS
- Event storage
- Facility storage
- Prediction storage

### Backend

- FastAPI
- REST APIs
- AI inference endpoint
- Geospatial query endpoints

---

# 12. Post-MVP Features

After the MVP, the system can be expanded with:

1. Multi-class fire classification.
2. Satellite-image deep-learning models.
3. Advanced temporal models.
4. Automated alerts.
5. Risk forecasting.
6. Population exposure analysis.
7. Facility-specific monitoring.
8. Historical trend analytics.
9. Multi-region deployment.
10. Automated report generation.

---

# 13. Success Criteria

The project should be considered successful if it can demonstrate the following:

### Detection

- Successfully ingest thermal anomalies.
- Correctly map observations geographically.

### Classification

- Distinguish industrial-related events from natural/agricultural events with useful predictive performance.
- Provide measurable precision, recall, and F1-score.

### GIS

- Display events correctly on an interactive map.
- Provide industrial facility and land-cover overlays.

### Temporal Analysis

- Identify recurring/persistent thermal sources.

### Usability

- A user should be able to locate an event and understand its classification and risk within a few interactions.

### System

- End-to-end pipeline works from data ingestion to dashboard visualization.

---

# 14. Key Product Outputs

For every detected thermal event, the platform should produce a structured record similar to:

```json
{
  "event_id": "EVT-000001",
  "timestamp": "2026-08-21T14:32:00Z",
  "latitude": 28.XXXX,
  "longitude": 77.XXXX,
  "classification": "Industrial Fire",
  "confidence": 0.947,
  "risk_score": 82,
  "risk_level": "HIGH",
  "nearest_facility": "Example Petrochemical Facility",
  "facility_type": "Petrochemical",
  "facility_distance_m": 420,
  "persistence": "RECURRING",
  "source": "VIIRS"
}
```

---

# 15. User Journey

```text
User opens dashboard
        ↓
Views regional thermal events
        ↓
Applies "Industrial Fire" filter
        ↓
Selects HIGH-risk events
        ↓
Clicks an event
        ↓
Views AI classification
        ↓
Views confidence + risk score
        ↓
Views nearby industrial facility
        ↓
Checks historical persistence
        ↓
Views satellite imagery
        ↓
Exports / reports event
```

---

# 16. Product Modules

The product should be divided into the following modules:

## Module 1 — Data Ingestion

Responsible for collecting satellite and geospatial data.

## Module 2 — Thermal Anomaly Processing

Responsible for cleaning, validating, and standardizing thermal observations.

## Module 3 — Geospatial Intelligence

Responsible for spatial joins, facility proximity, land-cover analysis, and geographic context.

## Module 4 — AI Classification

Responsible for classification and prediction.

## Module 5 — Temporal Analytics

Responsible for persistence and recurring-event detection.

## Module 6 — Risk Engine

Responsible for calculating event risk.

## Module 7 — Spatial Database

Responsible for storing events and geospatial information.

## Module 8 — API Layer

Responsible for exposing data and AI services.

## Module 9 — GIS Dashboard

Responsible for visualization and user interaction.

## Module 10 — Alert & Reporting

Responsible for notifications and reports.

---

# 17. Initial Technology Direction

The requirements document does not lock the implementation to a single technology, but the recommended direction is:

### AI / ML

- Python
- Scikit-learn
- XGBoost / LightGBM
- PyTorch for deep-learning extensions

### Geospatial

- GeoPandas
- Rasterio
- GDAL
- Shapely
- PyProj

### Database

- PostgreSQL
- PostGIS

### Backend

- FastAPI

### Frontend

- React
- MapLibre GL JS
- Deck.gl

### Deployment

- Docker
- GPU-enabled infrastructure where required

---

# 18. Data Requirements

## Thermal Data

Required fields should include, where available:

- Coordinates
- Timestamp
- Satellite
- Confidence
- Fire Radiative Power
- Brightness temperature

## Industrial Data

Required fields:

- Facility name
- Facility type
- Coordinates / geometry
- Operational information where available

## Land-Cover Data

Required:

- Land-cover class
- Geographic geometry/raster
- Dataset version
- Observation period

## Satellite Imagery

Potential features:

- Spectral bands
- Vegetation indices
- Built-up indicators
- Water indicators
- Burn/thermal-related indices where appropriate

## Historical Data

Required:

- Event location
- Timestamp
- Event type if available
- Thermal intensity
- Source

---

# 19. Classification Strategy

The initial AI system should use a staged approach.

## Stage 1 — Baseline

Use structured geospatial and thermal features with a model such as:

**XGBoost / LightGBM**

Example features:

```text
thermal_intensity
confidence
industrial_distance
facility_type
land_cover
NDVI
built_up_ratio
historical_frequency
persistence
```

## Stage 2 — Image Intelligence

Add a computer-vision model using satellite imagery.

Potential architectures:

- CNN
- Vision Transformer
- Other suitable remote-sensing models

## Stage 3 — Feature Fusion

Combine:

```text
Tabular geospatial features
          +
Satellite-image features
          +
Temporal features
          ↓
      Final classifier
```

This staged approach allows the team to deliver an MVP before attempting the most complex model.

---

# 20. Product Constraints

The system must recognize the following constraints:

1. Satellite imagery may have cloud cover.
2. Satellite observations are not necessarily real-time.
3. Thermal anomalies may be spatially coarse.
4. Multiple sources can produce similar thermal signatures.
5. Industrial facilities can generate normal thermal activity.
6. Ground truth data for industrial fires may be limited.
7. Different satellites have different spatial and temporal characteristics.
8. AI predictions are probabilistic and should not be treated as definitive ground truth.
9. Some events may remain classified as Unknown when evidence is insufficient.

---

# 21. Out-of-Scope for MVP

The following should not be required for the first working version:

- Automatic satellite tasking
- Fully autonomous emergency response
- Direct control of industrial systems
- Guaranteed fire detection in all weather conditions
- High-resolution continuous monitoring everywhere
- Predicting exact fire ignition time
- Replacing official emergency or industrial safety systems

---

# 22. Risks and Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Insufficient labeled data | High | Build annotation pipeline and use multiple data sources |
| False positives | High | Combine thermal, spatial, temporal and imagery features |
| Cloud cover | Medium | Use multiple satellite sources and historical observations |
| Industrial normal activity classified as fire | High | Model persistence and facility context |
| Poor satellite resolution | Medium | Combine datasets with different spatial resolutions |
| Data latency | Medium | Clearly communicate observation time and source |
| Model bias | High | Evaluate across geographic regions and facility types |
| Unknown event types | Medium | Include an Unknown class and confidence threshold |
| API/data-source outage | Medium | Caching and modular ingestion architecture |

---

# 23. Responsible AI Requirements

The platform should:

- Display prediction confidence.
- Clearly distinguish AI predictions from confirmed incidents.
- Preserve source information for each observation.
- Avoid presenting low-confidence predictions as facts.
- Maintain model-version information.
- Record important prediction metadata.
- Allow human review for high-impact decisions.
- Document known geographic and data limitations.

### Important principle

> **The system is a decision-support tool, not a replacement for official incident verification.**

---

# 24. MVP Acceptance Checklist

- [ ] Thermal anomaly data can be ingested.
- [ ] Thermal observations are stored in PostGIS.
- [ ] Industrial facilities can be displayed on the map.
- [ ] Land-cover information can be associated with events.
- [ ] Spatial distance to industrial facilities can be calculated.
- [ ] AI model can classify at least industrial vs non-industrial events.
- [ ] Model produces a confidence score.
- [ ] Historical observations can be queried.
- [ ] Persistent sources can be identified.
- [ ] Events are displayed on the GIS dashboard.
- [ ] Users can filter events.
- [ ] Users can inspect event details.
- [ ] End-to-end demo works from input data to dashboard.

---

# 25. Future Vision

The long-term platform can evolve into a national-scale **Industrial Thermal Intelligence Network**.

```text
Multiple Satellites
        ↓
National Thermal Event Database
        ↓
AI Classification
        ↓
Persistent Source Monitoring
        ↓
Industrial Risk Intelligence
        ↓
GIS Command Dashboard
        ↓
Automated Alerts
        ↓
Human Verification
        ↓
Response / Investigation
```

Potential future capabilities include:

- Near-real-time monitoring
- Automated anomaly alerts
- Facility-level risk profiles
- Predictive anomaly detection
- Multi-satellite data fusion
- Advanced deep-learning models
- Population exposure analysis
- Environmental impact estimation
- Automated compliance reports
- Regional and national-scale deployment

---

# 26. Final Product Definition

The proposed product is an **AI-enabled geospatial monitoring and decision-support platform** that detects satellite thermal anomalies and determines their likely source using thermal characteristics, industrial infrastructure, land cover, satellite imagery, and historical behavior.

The final system should answer five critical questions:

1. **Where is the thermal anomaly?**
2. **What is it likely to be?**
3. **Is it associated with an industrial facility?**
4. **Is it persistent or abnormal?**
5. **How significant is the event?**

The combination of **AI + Remote Sensing + GIS + Temporal Analytics + Spatial Databases** forms the core of the proposed solution.

# AthletiQ — System Architecture & Technical Design

**Project:** AthletiQ — AI-Powered Digital Sports Scientist  
**Problem Statement:** The Digital Sports Scientist: Bringing Elite Performance Analysis to Every Grassroots Coach  
**Context:** Ministry of Youth Affairs & Sports (MYAS) / Sports Authority of India (SAI)  
**Document Version:** 1.0  
**Status:** Draft / Hackathon MVP  
**Date:** August 2026

---

# 1. Executive Summary

AthletiQ is a smartphone-first sports-performance intelligence platform that converts ordinary training videos into measurable movement data.

The system combines:

- Smartphone video capture/upload.
- Video preprocessing.
- Human pose estimation.
- Landmark tracking.
- Sport-specific movement analysis.
- Biomechanical metric extraction.
- Athlete-specific baseline generation.
- Session comparison.
- Deviation and trend detection.
- Coach decision-support insights.
- Athlete, coach, academy, and future federation dashboards.

The architecture is designed as a modular system so that individual components can be improved or replaced without rebuilding the entire platform.

The MVP should prioritize a reliable end-to-end pipeline for a small number of sports/movements rather than attempting universal sports analysis from the beginning.

---

# 2. Architecture Goals

## 2.1 Primary Goals

1. Process smartphone training videos reliably.
2. Separate video processing from the main web application.
3. Support AI inference as an independently scalable service.
4. Store raw videos separately from structured athlete data.
5. Maintain athlete-level session history.
6. Generate personalized movement baselines.
7. Provide explainable metrics and coach-review flags.
8. Support role-based access.
9. Enable future academy and federation-level scaling.
10. Allow AI models to be replaced without redesigning the whole system.

## 2.2 Secondary Goals

- Support asynchronous video processing.
- Enable cloud and local/edge inference.
- Support multiple sports.
- Maintain reproducible analysis versions.
- Provide auditability.
- Minimize unnecessary data movement.
- Support future integration with wearables and external systems.

---

# 3. Design Principles

### Modular

Each major capability should be independently replaceable.

### API-first

Frontend and backend communicate through documented APIs.

### AI as a Service

Computer-vision inference should be separated from business logic.

### Human-in-the-loop

AI produces measurements and flags; coaches make final decisions.

### Privacy by Design

Athlete data access should be controlled from the beginning.

### Evidence-based

Metrics and insights should be traceable to source measurements.

### Scalable

The MVP should be deployable simply while allowing future horizontal scaling.

---

# 4. High-Level System Architecture

```text
                         ATHLETIQ PLATFORM
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          Web / Mobile UI                Authentication
          Coach Dashboard                & Authorization
                 │
                 ▼
            API Gateway
                 │
                 ▼
        Application Backend
                 │
       ┌─────────┼──────────┐
       │         │          │
       ▼         ▼          ▼
   Athlete    Session    Reporting
   Service    Service     Service
       │         │          │
       └─────────┼──────────┘
                 │
                 ▼
          Job / Task Queue
                 │
                 ▼
        Video Processing Service
                 │
                 ▼
          AI Inference Service
                 │
        ┌────────┼─────────┐
        │        │         │
        ▼        ▼         ▼
      Pose    Movement   Quality
    Estimation  Analysis   Check
        │        │         │
        └────────┼─────────┘
                 ▼
       Biomechanical Engine
                 │
                 ▼
       Baseline & Analytics
                 │
                 ▼
           Insight Engine
                 │
        ┌────────┼──────────┐
        ▼        ▼          ▼
    PostgreSQL  Object     Redis
                Storage
                 │
                 ▼
            Reports / UI
```

---

# 5. Core Components

## 5.1 Frontend

The frontend provides the user interface for coaches, athletes, academy administrators, and future federation administrators.

### Recommended technology

- Next.js
- React
- TypeScript
- Tailwind CSS
- Charting library

### Responsibilities

- Authentication UI.
- Athlete management.
- Video upload.
- Session management.
- Processing status.
- Analysis visualization.
- Baseline comparison.
- Trend charts.
- Coach notes.
- Report access.
- Role-specific dashboards.

---

# 6. Backend Application

## Recommended stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

The backend acts as the primary business-logic layer.

### Responsibilities

- Authentication.
- Authorization.
- User management.
- Athlete management.
- Academy management.
- Session management.
- Video metadata.
- Analysis job creation.
- Result retrieval.
- Baseline management.
- Report generation.
- Audit logging.
- API validation.

The backend should **not perform heavy video inference directly inside normal HTTP request handlers**.

Instead:

```text
API Request
    ↓
Create Analysis Job
    ↓
Queue Job
    ↓
Return Job ID
    ↓
Worker Processes Video
    ↓
Store Results
    ↓
Frontend Polls / Receives Status
```

---

# 7. Authentication & Authorization

The platform should use role-based access control.

## Roles

### Athlete

Can access:

- Own profile.
- Own sessions.
- Own metrics.
- Own reports.

### Coach

Can access:

- Assigned athletes.
- Training sessions.
- Analysis results.
- Coach notes.

### Academy Administrator

Can access:

- Academy athletes.
- Academy coaches.
- Academy-level analytics.

### Federation Administrator

Future role with access to authorized centres and aggregate data.

### System Administrator

Responsible for platform operations and configuration.

---

# 8. Video Input Architecture

## Supported input

The system should initially support common smartphone video formats such as:

- MP4
- MOV
- WebM where required

## Upload flow

```text
Coach
  ↓
Select Athlete
  ↓
Select Sport
  ↓
Select Movement
  ↓
Upload Video
  ↓
Frontend Requests Upload
  ↓
Object Storage
  ↓
Create Session
  ↓
Create Processing Job
```

Large videos should preferably be uploaded directly to object storage using secure temporary upload URLs rather than passing the entire file through the application server.

---

# 9. Video Storage

Raw video files should not be stored directly inside PostgreSQL.

Use object storage.

Possible implementations:

- Amazon S3.
- MinIO.
- Cloud-compatible object storage.

## Example storage structure

```text
athletiq/
│
├── videos/
│   ├── athlete_<id>/
│   │   ├── session_<id>/
│   │   │   └── original.mp4
│
├── processed/
│   └── session_<id>/
│       ├── normalized.mp4
│       ├── overlay.mp4
│       └── thumbnails/
│
└── reports/
    └── athlete_<id>/
        └── report_<id>.pdf
```

Database records should contain references to these objects rather than storing the video binary itself.

---

# 10. Video Processing Pipeline

The video-processing service converts raw video into a standardized input for AI analysis.

## Pipeline

```text
Raw Video
    ↓
Format Validation
    ↓
Metadata Extraction
    ↓
Frame Sampling
    ↓
Resolution Normalization
    ↓
Optional Stabilization
    ↓
Color / Image Preprocessing
    ↓
Quality Assessment
    ↓
AI Pose Inference
```

### Quality checks

The system should detect:

- Extremely low resolution.
- Excessive blur.
- Poor lighting.
- Athlete too far from camera.
- Athlete partially outside frame.
- Excessive occlusion.
- Multiple people.
- Unsupported camera angle.

If quality is insufficient, the system should provide a useful error or warning rather than generating unreliable metrics.

---

# 11. AI Inference Service

The AI service performs pose estimation and tracking.

## Candidate models

Potential options include:

- MediaPipe Pose.
- MoveNet.
- RTMPose.
- YOLO Pose.
- Other validated pose-estimation models.

The final model should be selected through benchmarking.

## AI pipeline

```text
Frame
  ↓
Person Detection
  ↓
Target Athlete Selection
  ↓
Pose Estimation
  ↓
Landmark Confidence
  ↓
Temporal Tracking
  ↓
Landmark Sequence
```

---

# 12. Landmark Data Model

For every relevant frame, the AI layer should produce structured landmark data.

Example conceptual structure:

```json
{
  "frame": 120,
  "timestamp_ms": 4000,
  "landmarks": {
    "left_knee": {
      "x": 0.42,
      "y": 0.68,
      "z": 0.03,
      "confidence": 0.94
    },
    "right_knee": {
      "x": 0.57,
      "y": 0.67,
      "z": 0.04,
      "confidence": 0.96
    }
  }
}
```

The exact landmark schema should depend on the selected pose model.

---

# 13. Movement Analysis Engine

The movement-analysis layer converts landmark sequences into sport-specific events and metrics.

```text
Landmark Sequence
       ↓
Temporal Smoothing
       ↓
Movement Segmentation
       ↓
Event Detection
       ↓
Metric Calculation
       ↓
Quality Filtering
```

### Examples

For running:

- Foot strike events.
- Stride timing.
- Cadence.
- Knee angle.
- Hip angle.
- Arm movement.
- Left/right symmetry.

For squat:

- Standing phase.
- Descent.
- Bottom position.
- Ascent.
- Knee angle.
- Hip angle.
- Trunk angle.
- Depth.
- Repetition consistency.

---

# 14. Biomechanical Calculation Layer

The biomechanics engine should remain independent of the pose-estimation model.

This is important because it allows the project to change the AI model without rewriting the metric logic.

## Example

```text
Pose Model A
      │
      ├──→ Landmark Schema
      │
Pose Model B
      │
      └──→ Landmark Schema
                 ↓
        Biomechanical Engine
                 ↓
              Metrics
```

### Core metric categories

- Angular metrics.
- Distance metrics.
- Temporal metrics.
- Symmetry metrics.
- Range-of-motion metrics.
- Movement consistency metrics.

---

# 15. Metric Calculation

For three body landmarks A, B, and C, where B is the joint:

```text
A
 \
  B
 /
C
```

The angle at B can be calculated using vectors:

```text
BA = A - B
BC = C - B
```

and:

```text
θ = arccos((BA · BC) / (|BA| |BC|))
```

The implementation should include safeguards for:

- Zero-length vectors.
- Missing landmarks.
- Low confidence.
- Numerical rounding errors.

---

# 16. Baseline Engine

The baseline engine creates an athlete-specific reference profile.

## Baseline pipeline

```text
Historical Sessions
       ↓
Quality Filtering
       ↓
Metric Extraction
       ↓
Outlier Handling
       ↓
Aggregation
       ↓
Personal Baseline
```

The baseline may include:

- Mean.
- Median.
- Standard deviation.
- Percentiles.
- Valid measurement range.
- Session count.
- Confidence.

The baseline should be specific to the relevant:

- Athlete.
- Sport.
- Movement.
- Camera setup where necessary.

---

# 17. Session Comparison Engine

A new session is compared against the athlete's baseline.

```text
New Session
     ↓
Metrics
     ↓
Baseline Lookup
     ↓
Metric Normalization
     ↓
Deviation Calculation
     ↓
Threshold / Statistical Check
     ↓
Flag
```

The system should distinguish between:

- Normal variation.
- Measurement noise.
- Meaningful deviation.
- Persistent trend.

A single unusual session should generally be treated more cautiously than a repeated pattern.

---

# 18. Deviation Detection

Deviation detection should be configurable.

Possible methods:

### Rule-based

```text
IF metric_change > threshold
THEN flag
```

### Statistical

Compare a measurement against the athlete's baseline distribution.

### Trend-based

Identify persistent changes across multiple sessions.

### Hybrid

Recommended for MVP:

```text
Confidence Check
      ↓
Rule / Statistical Threshold
      ↓
Persistence Check
      ↓
Coach Review Flag
```

The system should not convert deviations into medical diagnoses.

---

# 19. Insight Engine

The insight layer translates metrics into understandable coach-facing messages.

## Input

```text
Metric
Baseline
Current Value
Confidence
Trend
Sport
Movement
```

## Output

```text
Insight
Severity
Supporting Metrics
Recommended Review Area
```

Example:

```text
Metric:
Stride symmetry

Baseline:
96%

Current:
89%

Change:
-7 percentage points

Insight:
"Stride symmetry is lower than the athlete's recent
baseline. Review the current session for possible
technique changes."
```

The insight should always link back to the underlying metric.

---

# 20. Human-in-the-Loop Architecture

AthletiQ should explicitly separate:

### AI responsibility

- Detect.
- Measure.
- Compare.
- Flag.
- Explain the measured change.

### Coach responsibility

- Interpret.
- Review footage.
- Consider training context.
- Decide whether action is required.

```text
AI Analysis
    ↓
Metric
    ↓
Deviation
    ↓
Coach Review
    ↓
Human Decision
```

---

# 21. Database Architecture

PostgreSQL should store structured application data.

## Main entities

```text
User
 │
 ├── Coach
 ├── Athlete
 └── Administrator
       │
       ▼
    Academy
       │
       ▼
     Athlete
       │
       ├── Sessions
       │     │
       │     ├── Video
       │     ├── Analysis
       │     ├── Metrics
       │     └── Flags
       │
       └── Baseline
```

---

# 22. Suggested Database Tables

## users

- id
- name
- email
- password_hash / identity_reference
- role
- created_at
- updated_at

## academies

- id
- name
- location
- created_at

## athletes

- id
- user_id
- academy_id
- date_of_birth where required
- sport
- profile_metadata
- created_at

## coach_athletes

- coach_id
- athlete_id
- assigned_at

## sessions

- id
- athlete_id
- coach_id
- sport
- movement
- session_date
- status
- created_at

## videos

- id
- session_id
- storage_key
- duration
- fps
- width
- height
- file_size
- quality_score

## analysis_jobs

- id
- session_id
- model_version
- status
- progress
- started_at
- completed_at
- error_message

## metrics

- id
- session_id
- metric_name
- value
- unit
- confidence

## baselines

- id
- athlete_id
- sport
- movement
- metric_name
- center_value
- variability
- sample_count
- version

## flags

- id
- session_id
- metric_name
- severity
- baseline_value
- current_value
- deviation
- explanation
- coach_status

## reports

- id
- athlete_id
- session_id
- storage_key
- created_by
- created_at

---

# 23. Entity Relationship Overview

```text
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├──────────────┐
       ▼              ▼
┌───────────┐    ┌───────────┐
│   Coach   │    │  Athlete  │
└─────┬─────┘    └─────┬─────┘
      │                 │
      └──────┬──────────┘
             ▼
         ┌─────────┐
         │ Session │
         └────┬────┘
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Video   Analysis   Metrics
              │
          ┌───┴───┐
          ▼       ▼
       Baseline  Flags
```

---

# 24. API Architecture

The backend should expose REST APIs initially.

## Authentication

```text
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
```

## Athletes

```text
GET    /api/v1/athletes
POST   /api/v1/athletes
GET    /api/v1/athletes/{athlete_id}
PATCH  /api/v1/athletes/{athlete_id}
DELETE /api/v1/athletes/{athlete_id}
```

## Sessions

```text
GET  /api/v1/athletes/{athlete_id}/sessions
POST /api/v1/athletes/{athlete_id}/sessions
GET  /api/v1/sessions/{session_id}
```

## Video

```text
POST /api/v1/sessions/{session_id}/upload-url
POST /api/v1/sessions/{session_id}/upload-complete
GET  /api/v1/sessions/{session_id}/video
```

## Analysis

```text
POST /api/v1/sessions/{session_id}/analyze
GET  /api/v1/analysis/{analysis_id}
GET  /api/v1/sessions/{session_id}/metrics
```

## Baseline

```text
GET  /api/v1/athletes/{athlete_id}/baseline
POST /api/v1/athletes/{athlete_id}/baseline/rebuild
```

## Trends

```text
GET /api/v1/athletes/{athlete_id}/trends
GET /api/v1/athletes/{athlete_id}/metrics/{metric_name}/history
```

## Reports

```text
POST /api/v1/sessions/{session_id}/report
GET  /api/v1/reports/{report_id}
```

---

# 25. Asynchronous Processing Architecture

Video analysis can be computationally expensive.

Therefore, the recommended architecture is:

```text
Frontend
   ↓
Backend API
   ↓
Create Job
   ↓
Redis / Message Queue
   ↓
Worker
   ↓
Video Processor
   ↓
AI Inference
   ↓
Metrics
   ↓
Database
   ↓
Job Completed
```

Possible technologies:

- Redis + Celery.
- Redis + RQ.
- Redis Streams.
- RabbitMQ.
- Cloud-managed queues.

For the MVP, a lightweight Redis-backed worker architecture is sufficient.

---

# 26. Job State Machine

```text
CREATED
   ↓
QUEUED
   ↓
PROCESSING
   ↓
POSE_ANALYSIS
   ↓
METRIC_ANALYSIS
   ↓
BASELINE_COMPARISON
   ↓
INSIGHT_GENERATION
   ↓
COMPLETED
```

Failure path:

```text
Any Stage
   ↓
FAILED
   ↓
Retry / Manual Review
```

---

# 27. Frontend State Flow

The frontend should show processing progress.

```text
Upload
  ↓
Uploading
  ↓
Queued
  ↓
Processing
  ↓
Analyzing
  ↓
Generating Insights
  ↓
Complete
```

This prevents the user from thinking that the application has frozen during AI processing.

---

# 28. Dashboard Architecture

## Coach Dashboard

```text
┌─────────────────────────────────────────────┐
│ ATHLETIQ — Coach Dashboard                  │
├─────────────────────────────────────────────┤
│ Athletes: 42     Sessions: 186    Flags: 4 │
├─────────────────────────────────────────────┤
│                                             │
│ Recent Athlete Activity                     │
│                                             │
│ Rahul     ↑ Improving                       │
│ Aman      ⚠ Review                          │
│ Rohit     ✓ Stable                          │
│                                             │
├─────────────────────────────────────────────┤
│ Recent Sessions                             │
└─────────────────────────────────────────────┘
```

---

# 29. Video Analysis Screen

```text
┌──────────────────────────────────────────────┐
│              ATHLETE VIDEO                  │
│                                              │
│                Pose Overlay                  │
│                                              │
│                 🧍                           │
│                /│\                           │
│                / \                           │
│                                              │
├──────────────────────────────────────────────┤
│ Knee Angle        94°                        │
│ Hip Angle         72°                        │
│ Symmetry          89%                        │
│ Cadence           174                         │
│ Confidence        93%                        │
├──────────────────────────────────────────────┤
│ ⚠ Review Recommended                        │
│ Symmetry is below recent baseline.          │
└──────────────────────────────────────────────┘
```

---

# 30. Data Flow

## End-to-End Data Flow

```text
1. Coach
      ↓
2. Frontend
      ↓
3. API
      ↓
4. Object Storage
      ↓
5. Processing Queue
      ↓
6. Video Worker
      ↓
7. Pose Model
      ↓
8. Landmark Data
      ↓
9. Biomechanics Engine
      ↓
10. Metrics Database
      ↓
11. Baseline Engine
      ↓
12. Deviation Engine
      ↓
13. Insight Engine
      ↓
14. Coach Dashboard
```

---

# 31. Analysis Versioning

AI results should be reproducible.

Every analysis should store:

- Model name.
- Model version.
- Metric-engine version.
- Analysis configuration.
- Timestamp.
- Processing environment where necessary.

Example:

```json
{
  "pose_model": "model_name",
  "pose_model_version": "1.0",
  "metric_engine_version": "1.0",
  "analysis_version": "1.0",
  "created_at": "2026-08-21T10:00:00Z"
}
```

This prevents old athlete reports from becoming impossible to interpret after the AI model changes.

---

# 32. Confidence & Data Quality Architecture

Every AI-derived metric should ideally have a confidence or quality indicator.

```text
Pose Confidence
      ↓
Landmark Quality
      ↓
Metric Quality
      ↓
Session Quality
```

Example:

```text
Pose Confidence:     94%
Metric Confidence:   91%
Session Quality:     Good
```

Low-quality metrics should either be excluded from baseline calculations or explicitly marked as uncertain.

---

# 33. Security Architecture

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
 ├── PostgreSQL
 ├── Object Storage
 └── Processing Queue
```

### Security controls

- HTTPS/TLS.
- Secure authentication.
- Role-based authorization.
- Secure password handling or managed identity.
- Short-lived upload URLs.
- Object-storage access controls.
- Database access restrictions.
- Audit logging.
- Secret management.
- Rate limiting.
- Input validation.

---

# 34. Privacy Architecture

Athlete videos should be treated as sensitive data.

### Recommended principles

- Collect only required information.
- Obtain appropriate consent.
- Restrict access by role.
- Encrypt data in transit.
- Encrypt data at rest where supported.
- Define retention policies.
- Provide deletion mechanisms.
- Maintain access logs.
- Avoid using identifiable athlete videos for model training without appropriate authorization.

The final deployment should follow applicable Indian privacy/data-protection requirements and the policies of the implementing organization.

---

# 35. Offline / Edge Architecture

A future version can support processing directly on the smartphone or local computer.

```text
Smartphone
    ↓
Local Pose Model
    ↓
Local Metrics
    ↓
Local Results
    ↓
Internet Available?
    │
 ┌──┴───┐
 │      │
 YES    NO
 │      │
 ↓      ↓
Sync   Store Locally
```

Advantages:

- Lower latency.
- Reduced bandwidth.
- Better privacy.
- Useful in low-connectivity areas.

This should be treated as a later phase unless the MVP specifically targets offline environments.

---

# 36. Deployment Architecture

## MVP Deployment

```text
                Internet
                   │
                   ▼
             Frontend Server
                   │
                   ▼
              Backend API
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
 PostgreSQL     Redis      Object Storage
                   │
                   ▼
              AI Worker
                   │
                   ▼
              GPU / CPU
```

## Production Scaling

```text
                Load Balancer
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       API-1      API-2      API-3
          │          │          │
          └──────────┼──────────┘
                     ▼
                  Queue
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Worker-1   Worker-2   Worker-3
                     │
                     ▼
                 AI Models
```

---

# 37. Recommended Technology Stack

| Layer | Recommended Technology |
|---|---|
| Frontend | Next.js + React + TypeScript |
| Styling | Tailwind CSS |
| Backend | FastAPI |
| Language | Python |
| Validation | Pydantic |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Cache/Queue | Redis |
| Object Storage | MinIO / S3-compatible storage |
| Computer Vision | OpenCV |
| Pose Estimation | MediaPipe / MoveNet / RTMPose / YOLO Pose |
| Numerical Processing | NumPy / SciPy |
| Data Analysis | Pandas |
| API Documentation | OpenAPI / Swagger |
| Containerization | Docker |
| Testing | Pytest + frontend testing framework |
| Monitoring | Application logs + metrics |
| CI/CD | GitHub Actions or equivalent |

The final AI model should be selected after benchmarking rather than being fixed solely by this architecture document.

---

# 38. Repository Architecture

Recommended repository structure:

```text
athletiq/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   └── types/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── core/
│   └── tests/
│
├── ai/
│   ├── pose/
│   ├── tracking/
│   ├── movement/
│   ├── biomechanics/
│   ├── baseline/
│   └── insights/
│
├── workers/
│   ├── video_worker/
│   └── analysis_worker/
│
├── database/
│   ├── migrations/
│   └── seed/
│
├── models/
│
├── datasets/
│
├── tests/
│
├── docker/
│
├── docs/
│
├── scripts/
│
└── README.md
```

---

# 39. API Request Lifecycle

Example: Analyze Video

```text
POST /api/v1/sessions/{id}/analyze
             ↓
       Authentication
             ↓
        Authorization
             ↓
        Validate Session
             ↓
       Create Analysis Job
             ↓
         Queue Job
             ↓
          Return ID
```

Response:

```json
{
  "analysis_id": "analysis_123",
  "status": "QUEUED"
}
```

The client then checks:

```text
GET /api/v1/analysis/analysis_123
```

Example:

```json
{
  "analysis_id": "analysis_123",
  "status": "PROCESSING",
  "progress": 62
}
```

Final:

```json
{
  "analysis_id": "analysis_123",
  "status": "COMPLETED",
  "session_id": "session_456"
}
```

---

# 40. Failure Handling

Potential failures:

### Upload failure

- Retry upload.
- Preserve session state.

### Pose failure

- Mark analysis as failed.
- Provide actionable reason.

### Low-quality video

- Return quality warning.
- Ask for another recording if required.

### Model failure

- Retry worker.
- Log model error.
- Preserve original video.

### Partial processing

- Store stage status.
- Resume from safe checkpoint where practical.

---

# 41. Observability

The production system should monitor:

### Application

- API latency.
- Error rate.
- Request count.
- Authentication failures.

### AI

- Processing time.
- Frames processed.
- Pose confidence.
- Model failures.
- GPU/CPU utilization.

### Pipeline

- Queue length.
- Job duration.
- Failed jobs.
- Retry count.

### Product

- Videos uploaded.
- Sessions completed.
- Analysis completion rate.
- Reports generated.

---

# 42. Scalability Strategy

## Stage 1 — Hackathon

Single deployment:

```text
Frontend
+
FastAPI
+
PostgreSQL
+
Redis
+
Single AI Worker
```

## Stage 2 — Pilot

Separate:

- API.
- Database.
- Object storage.
- Queue.
- AI worker.

## Stage 3 — Multi-Academy

Use:

- Multiple API instances.
- Multiple AI workers.
- Managed database.
- Object storage.
- Monitoring.

## Stage 4 — Federation Scale

Introduce:

- Multi-tenant architecture.
- Regional deployments.
- Stronger access controls.
- Data partitioning.
- Advanced analytics.
- Federated reporting.

---

# 43. Multi-Tenant Architecture

For academy/federation deployment, data should be logically isolated.

```text
Federation
   │
   ├── Academy A
   │      ├── Coach 1
   │      └── Coach 2
   │
   ├── Academy B
   │      ├── Coach 3
   │      └── Coach 4
   │
   └── Academy C
          └── Coach 5
```

Every request should be authorized against the user's organization and role.

---

# 44. Future Integration Architecture

AthletiQ should eventually support additional data sources.

```text
                 ATHLETE
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
 Smartphone       Wearables    Sensors
   Video             │            │
       │             │            │
       └─────────────┼────────────┘
                     ▼
              Unified Athlete
               Data Platform
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Trends     Analysis    Reports
```

Possible integrations:

- Smartwatches.
- IMUs.
- Heart-rate sensors.
- GPS.
- Timing gates.
- Force plates.
- Professional biomechanics systems.

---

# 45. Architecture Decision Records

Important architecture decisions should be documented.

Example:

## ADR-001 — FastAPI

**Decision:** Use FastAPI for the backend.

**Reason:**

- Python ecosystem.
- Easy AI integration.
- Async support.
- Pydantic validation.
- OpenAPI generation.

## ADR-002 — PostgreSQL

**Decision:** Use PostgreSQL for structured data.

**Reason:**

- Mature relational database.
- Strong consistency.
- Complex querying.
- Suitable for multi-tenant relational data.

## ADR-003 — Object Storage

**Decision:** Store videos outside the relational database.

**Reason:**

- Large file sizes.
- Better scalability.
- Independent lifecycle management.

## ADR-004 — Asynchronous AI Processing

**Decision:** Process videos asynchronously.

**Reason:**

- AI inference can take significant time.
- Prevents HTTP request timeouts.
- Enables worker scaling.

---

# 46. Technical Constraints

The architecture must recognize that smartphone video is not equivalent to laboratory measurement.

### Important constraints

- 2D perspective distortion.
- Camera calibration uncertainty.
- Unknown camera height.
- Unknown camera distance.
- Lens distortion.
- Occlusion.
- Frame-rate variability.
- Compression artifacts.
- Lighting conditions.
- Athlete clothing.
- Multiple-person detection.

Therefore, the system should report **validated movement indicators**, not claim unrestricted laboratory-grade biomechanics.

---

# 47. Recommended MVP Architecture

For the hackathon, keep the implementation simple:

```text
              NEXT.JS
                 │
                 ▼
             FASTAPI
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
 PostgreSQL   Redis      MinIO
                 │
                 ▼
          Python AI Worker
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    OpenCV   Pose Model  Metrics
                 │
                 ▼
             Baseline
                 │
                 ▼
              Insights
                 │
                 ▼
             Dashboard
```

### Recommended MVP processing

```text
Video
 ↓
OpenCV
 ↓
Pose Estimation
 ↓
Landmarks
 ↓
Joint Angles / Selected Metrics
 ↓
Store Session
 ↓
Baseline
 ↓
Comparison
 ↓
Coach Dashboard
```

Avoid introducing microservices, Kubernetes, complex event buses, or multiple databases unless the MVP genuinely requires them.

---

# 48. End-to-End Example

A coach uploads a 20-second running video.

### Step 1

Frontend uploads video to object storage.

### Step 2

Backend creates a session.

### Step 3

Backend creates an analysis job.

### Step 4

Worker retrieves the video.

### Step 5

Video is validated and normalized.

### Step 6

Pose model extracts landmarks.

### Step 7

Movement engine identifies running cycles.

### Step 8

Biomechanics engine calculates:

- Knee angle.
- Hip angle.
- Stride timing.
- Cadence.
- Symmetry.

### Step 9

Results are stored.

### Step 10

Baseline engine retrieves the athlete's previous sessions.

### Step 11

Current metrics are compared with the baseline.

### Step 12

Deviation engine detects a meaningful change.

### Step 13

Insight engine generates a coach-review message.

### Step 14

Dashboard displays:

```text
Current Session
       │
       ├── Knee Angle: 94°
       ├── Cadence: 174
       ├── Symmetry: 89%
       └── Confidence: 93%

Baseline
       │
       ├── Knee Angle: 91°
       ├── Cadence: 176
       └── Symmetry: 96%

Flag
       ↓
"Review recommended:
symmetry is below recent baseline."
```

### Step 15

Coach reviews the actual video and records a note.

---

# 49. Technical Success Criteria

The architecture is considered successful when:

- Frontend and backend communicate through documented APIs.
- Videos can be securely uploaded.
- Analysis jobs run asynchronously.
- AI inference can be executed independently.
- Pose landmarks are stored in a structured format.
- Biomechanical metrics can be calculated independently of the pose model.
- Sessions are associated with athletes.
- Personal baselines can be generated.
- New sessions can be compared with baselines.
- Results can be visualized.
- Processing failures can be detected and handled.
- User permissions prevent unauthorized athlete-data access.
- The system can scale from a single coach to multiple academies with minimal architectural changes.

---

# 50. Conclusion

AthletiQ's technical architecture is designed around a simple principle:

> **Separate video processing, AI inference, biomechanics, athlete intelligence, and product workflows into modular layers.**

The most important architectural decision is to avoid coupling the application directly to one computer-vision model.

The architecture should instead follow:

```text
Video
  ↓
Pose Model
  ↓
Standardized Landmarks
  ↓
Biomechanics Engine
  ↓
Metrics
  ↓
Athlete Baseline
  ↓
Deviation / Trends
  ↓
Coach Decision Support
```

This allows the AI model, biomechanics algorithms, and product interface to evolve independently.

For the hackathon, the recommended implementation is a **modular monolith + asynchronous AI worker** rather than a complex microservice architecture. This provides enough structure for a production-oriented design while keeping development manageable.

The architecture can later evolve into a multi-tenant, multi-centre platform supporting academies, federations, additional sports, edge inference, wearables, and advanced 3D biomechanics.

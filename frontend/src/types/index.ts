export interface EventSummary {
  event_id: string;
  latitude: number;
  longitude: number;
  detection_count: number;
}

export interface PersistentEvent {
  event_id: string;
  persistence: string;
  persistence_score: number;
}

export interface ThermalData {
  frp_mean: number;
  frp_max: number;
  confidence: number | null;
}

export interface SpatialData {
  facility_distance: number | null;
  facility_count: number;
}

export interface LandCoverData {
  industrial_ratio: number | null;
  forest_ratio: number | null;
  agriculture_ratio: number | null;
  builtup_ratio: number | null;
}

export interface TemporalData {
  detection_count: number;
  event_duration_hours: number;
}

export interface EventDetail {
  event_id: string;
  thermal: ThermalData;
  spatial: SpatialData;
  land_cover: LandCoverData;
  temporal: TemporalData;
  classification?: 'INDUSTRIAL_FIRE' | 'WILDFIRE' | 'AGRICULTURAL_BURNING' | 'PERSISTENT_FLARE';
  persistence_score?: number;
}

export interface SystemStatistics {
  total_events: number;
  industrial_fires: number;
  wildfires: number;
  agricultural_burning: number;
  persistent_sources: number;
  recurring_events: number;
  high_risk_events: number;
}

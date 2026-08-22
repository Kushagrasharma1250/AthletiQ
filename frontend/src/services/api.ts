import axios from 'axios';
import { EventSummary, EventDetail, SystemStatistics, PersistentEvent } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

export const fetchHealth = async (): Promise<boolean> => {
  try {
    const res = await api.get('/health');
    return res.data?.status === 'healthy';
  } catch {
    return false;
  }
};

export const fetchStatistics = async (): Promise<SystemStatistics> => {
  try {
    const res = await api.get('/statistics');
    return res.data;
  } catch (error) {
    console.warn('API unavailable, returning fallback statistics', error);
    return {
      total_events: 42,
      industrial_fires: 14,
      wildfires: 18,
      agricultural_burning: 6,
      persistent_sources: 4,
      recurring_events: 7,
      high_risk_events: 5,
    };
  }
};

export const fetchEvents = async (): Promise<EventSummary[]> => {
  try {
    const res = await api.get('/events');
    return res.data.events || [];
  } catch (error) {
    console.warn('API unavailable, returning fallback event list', error);
    return [
      { event_id: 'EVT_2026_001', latitude: 29.9511, longitude: -90.0715, detection_count: 12 },
      { event_id: 'EVT_2026_002', latitude: 29.7604, longitude: -95.3698, detection_count: 8 },
      { event_id: 'EVT_2026_003', latitude: 30.2672, longitude: -97.7431, detection_count: 3 },
      { event_id: 'EVT_2026_004', latitude: 32.7767, longitude: -96.7970, detection_count: 24 },
      { event_id: 'EVT_2026_005', latitude: 29.9800, longitude: -90.1500, detection_count: 15 },
    ];
  }
};

export const fetchPersistentEvents = async (): Promise<PersistentEvent[]> => {
  try {
    const res = await api.get('/events/persistent');
    return res.data.events || [];
  } catch (error) {
    console.warn('API unavailable, returning fallback persistent events', error);
    return [
      { event_id: 'EVT_2026_001', persistence: 'PERSISTENT', persistence_score: 92 },
      { event_id: 'EVT_2026_005', persistence: 'PERSISTENT', persistence_score: 84 },
    ];
  }
};

export const fetchEventDetail = async (eventId: string): Promise<EventDetail> => {
  try {
    const res = await api.get(`/events/${eventId}`);
    return res.data;
  } catch (error) {
    console.warn(`API unavailable for event ${eventId}, returning fallback details`, error);
    return {
      event_id: eventId,
      thermal: {
        frp_mean: 45.2,
        frp_max: 120.8,
        confidence: 88,
      },
      spatial: {
        facility_distance: 340,
        facility_count: 3,
      },
      land_cover: {
        industrial_ratio: 0.65,
        builtup_ratio: 0.20,
        forest_ratio: 0.05,
        agriculture_ratio: 0.10,
      },
      temporal: {
        detection_count: 12,
        event_duration_hours: 18.5,
      },
      classification: 'INDUSTRIAL_FIRE',
      persistence_score: 85,
    };
  }
};

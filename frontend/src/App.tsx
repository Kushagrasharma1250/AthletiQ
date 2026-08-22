import React, { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { MetricCards } from './components/MetricCards';
import { ThermalMap } from './components/ThermalMap';
import { EventList } from './components/EventList';
import { EventInspector } from './components/EventInspector';
import {
  fetchHealth,
  fetchStatistics,
  fetchEvents,
  fetchPersistentEvents,
  fetchEventDetail,
} from './services/api';
import { SystemStatistics, EventSummary, PersistentEvent, EventDetail } from './types';

export const App: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean>(false);
  const [stats, setStats] = useState<SystemStatistics | null>(null);
  const [events, setEvents] = useState<EventSummary[]>([]);
  const [persistentEvents, setPersistentEvents] = useState<PersistentEvent[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [eventDetail, setEventDetail] = useState<EventDetail | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [healthRes, statsRes, eventsRes, persistentRes] = await Promise.all([
        fetchHealth(),
        fetchStatistics(),
        fetchEvents(),
        fetchPersistentEvents(),
      ]);

      setIsHealthy(healthRes);
      setStats(statsRes);
      setEvents(eventsRes);
      setPersistentEvents(persistentRes);

      // Auto-select first event if none selected
      if (eventsRes.length > 0 && !selectedEventId) {
        setSelectedEventId(eventsRes[0].event_id);
      }
    } catch (err) {
      console.error('Error loading dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Fetch specific event telemetry when selection changes
  useEffect(() => {
    if (!selectedEventId) return;

    const loadDetail = async () => {
      setDetailLoading(true);
      try {
        const detail = await fetchEventDetail(selectedEventId);
        setEventDetail(detail);
      } catch (err) {
        console.error('Error loading event detail', err);
      } finally {
        setDetailLoading(false);
      }
    };

    loadDetail();
  }, [selectedEventId]);

  return (
    <div className="h-screen w-screen flex flex-col bg-[#090d16] text-slate-100 overflow-hidden">
      {/* Top App Header */}
      <Header isHealthy={isHealthy} onRefresh={loadData} isLoading={loading} />

      {/* KPI Metrics Summary Bar */}
      <MetricCards stats={stats} loading={loading} />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Event Feed & Filter Sidebar */}
        <EventList
          events={events}
          persistentEvents={persistentEvents}
          selectedEventId={selectedEventId}
          onSelectEvent={setSelectedEventId}
        />

        {/* Center Interactive Map View */}
        <div className="flex-1 h-full p-2 relative bg-[#0b0f19]">
          <ThermalMap
            events={events}
            persistentEvents={persistentEvents}
            selectedEventId={selectedEventId}
            onSelectEvent={setSelectedEventId}
          />
        </div>

        {/* Right Event Inspector Analytical Drawer */}
        {selectedEventId && (
          <EventInspector
            event={eventDetail}
            loading={detailLoading}
            onClose={() => setSelectedEventId(null)}
          />
        )}
      </div>
    </div>
  );
};

export default App;

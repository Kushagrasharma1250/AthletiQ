import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { EventSummary, PersistentEvent } from '../types';
import { Flame, Factory, AlertCircle, Crosshair } from 'lucide-react';

interface ThermalMapProps {
  events: EventSummary[];
  persistentEvents: PersistentEvent[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

// Controller component to dynamically pan map when an event is selected
const MapController: React.FC<{ selectedEvent: EventSummary | null }> = ({ selectedEvent }) => {
  const map = useMap();
  useEffect(() => {
    if (selectedEvent) {
      map.flyTo([selectedEvent.latitude, selectedEvent.longitude], 12, {
        duration: 1.5,
      });
    }
  }, [selectedEvent, map]);
  return null;
};

// Helper function to generate custom colored SVGs for Leaflet icons
const createCustomIcon = (color: string, isSelected: boolean) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="${isSelected ? 36 : 28}" height="${isSelected ? 36 : 28}">
      <circle cx="12" cy="12" r="10" fill="${color}" fill-opacity="0.3" stroke="${color}" stroke-width="${isSelected ? 3 : 2}"/>
      <circle cx="12" cy="12" r="4" fill="${color}"/>
      ${isSelected ? `<circle cx="12" cy="12" r="11" fill="none" stroke="#ffffff" stroke-width="2" stroke-dasharray="2 2"/>` : ''}
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: 'custom-thermal-marker',
    iconSize: [isSelected ? 36 : 28, isSelected ? 36 : 28],
    iconAnchor: [isSelected ? 18 : 14, isSelected ? 18 : 14],
  });
};

export const ThermalMap: React.FC<ThermalMapProps> = ({
  events,
  persistentEvents,
  selectedEventId,
  onSelectEvent,
}) => {
  const defaultCenter: [number, number] = [29.9511, -90.0715]; // Gulf Coast Industrial Zone default
  const defaultZoom = 7;

  const persistentMap = new Map(persistentEvents.map((p) => [p.event_id, p]));
  const selectedEvent = events.find((e) => e.event_id === selectedEventId) || null;

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-[#0b0f19]">
      {/* Map Legend Overlay */}
      <div className="absolute top-4 right-4 z-[1000] bg-slate-900/90 backdrop-blur-md p-3 rounded-lg border border-slate-800 text-xs shadow-xl space-y-2">
        <div className="font-mono font-bold text-slate-300 flex items-center space-x-1.5 border-b border-slate-800 pb-1.5">
          <Crosshair className="w-3.5 h-3.5 text-orange-400" />
          <span>MAP CLASSIFICATION LEGEND</span>
        </div>
        <div className="space-y-1.5 font-medium">
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-red-500 shadow-sm shadow-red-500/50"></span>
            <span className="text-slate-300">Industrial Fire Hazard</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-purple-500 shadow-sm shadow-purple-500/50"></span>
            <span className="text-slate-300">Persistent Flare / Source</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="w-3 h-3 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50"></span>
            <span className="text-slate-300">Agricultural / Wildfire</span>
          </div>
        </div>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <MapController selectedEvent={selectedEvent} />

        {/* CartoDB Dark Matter Basemap */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/">OSM</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* Render Event Markers */}
        {events.map((event) => {
          const isPersistent = persistentMap.has(event.event_id);
          const isSelected = event.event_id === selectedEventId;

          // Color selection logic
          let markerColor = '#f59e0b'; // Amber default
          if (isPersistent) {
            markerColor = '#a855f7'; // Purple persistent
          } else if (event.detection_count > 10) {
            markerColor = '#ef4444'; // Red industrial/heavy fire
          }

          const icon = createCustomIcon(markerColor, isSelected);

          return (
            <React.Fragment key={event.event_id}>
              {/* Optional 5km proximity circle for selected event */}
              {isSelected && (
                <Circle
                  center={[event.latitude, event.longitude]}
                  radius={5000} // 5 km buffer radius
                  pathOptions={{
                    color: markerColor,
                    fillColor: markerColor,
                    fillOpacity: 0.1,
                    dashArray: '4 4',
                  }}
                />
              )}

              <Marker
                position={[event.latitude, event.longitude]}
                icon={icon}
                eventHandlers={{
                  click: () => onSelectEvent(event.event_id),
                }}
              >
                <Popup>
                  <div className="p-1 space-y-2">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-1">
                      <span className="font-mono font-bold text-xs text-orange-400">
                        {event.event_id}
                      </span>
                      {isPersistent && (
                        <span className="px-1.5 py-0.5 text-[9px] font-mono bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
                          PERSISTENT
                        </span>
                      )}
                    </div>
                    <div className="text-xs space-y-1 text-slate-300">
                      <div>
                        <span className="text-slate-400">Detections:</span>{' '}
                        <strong className="text-white">{event.detection_count}</strong>
                      </div>
                      <div>
                        <span className="text-slate-400">Coordinates:</span>{' '}
                        <span className="font-mono text-[11px]">
                          {event.latitude.toFixed(4)}, {event.longitude.toFixed(4)}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => onSelectEvent(event.event_id)}
                      className="w-full mt-2 py-1 bg-orange-600 hover:bg-orange-500 text-white font-semibold text-[11px] rounded transition"
                    >
                      Inspect Details
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};

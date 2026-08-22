import React, { useState } from 'react';
import { EventSummary, PersistentEvent } from '../types';
import { Search, Filter, Flame, Zap, CheckCircle2, SlidersHorizontal } from 'lucide-react';

interface EventListProps {
  events: EventSummary[];
  persistentEvents: PersistentEvent[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

export const EventList: React.FC<EventListProps> = ({
  events,
  persistentEvents,
  selectedEventId,
  onSelectEvent,
}) => {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<'ALL' | 'PERSISTENT' | 'HIGH_DETECTION'>('ALL');

  const persistentSet = new Set(persistentEvents.map((p) => p.event_id));

  const filteredEvents = events.filter((evt) => {
    const matchesSearch = evt.event_id.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;

    if (filterType === 'PERSISTENT') {
      return persistentSet.has(evt.event_id);
    }
    if (filterType === 'HIGH_DETECTION') {
      return evt.detection_count > 10;
    }
    return true;
  });

  return (
    <div className="w-full lg:w-80 bg-[#0f172a] border-r border-slate-800 h-full flex flex-col z-20">
      {/* Search & Filter Header */}
      <div className="p-3.5 border-b border-slate-800 bg-[#0b0f19] space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <SlidersHorizontal className="w-4 h-4 text-orange-400" />
            <h2 className="font-mono font-bold text-xs text-slate-200">EVENT FEED</h2>
          </div>
          <span className="px-2 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-400 rounded-full border border-slate-700">
            {filteredEvents.length} Active
          </span>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search Event ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-orange-500/50 font-mono transition"
          />
        </div>

        {/* Category Toggles */}
        <div className="flex space-x-1 font-mono text-[10px]">
          <button
            onClick={() => setFilterType('ALL')}
            className={`flex-1 py-1 rounded transition border ${
              filterType === 'ALL'
                ? 'bg-orange-500/20 text-orange-400 border-orange-500/40 font-bold'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
          >
            ALL ({events.length})
          </button>
          <button
            onClick={() => setFilterType('PERSISTENT')}
            className={`flex-1 py-1 rounded transition border ${
              filterType === 'PERSISTENT'
                ? 'bg-purple-500/20 text-purple-400 border-purple-500/40 font-bold'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
          >
            FLARES
          </button>
          <button
            onClick={() => setFilterType('HIGH_DETECTION')}
            className={`flex-1 py-1 rounded transition border ${
              filterType === 'HIGH_DETECTION'
                ? 'bg-red-500/20 text-red-400 border-red-500/40 font-bold'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
          >
            HEAVY
          </button>
        </div>
      </div>

      {/* Event Feed Scroll Container */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
        {filteredEvents.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs font-mono">
            No matching events found.
          </div>
        ) : (
          filteredEvents.map((evt) => {
            const isSelected = evt.event_id === selectedEventId;
            const isPersistent = persistentSet.has(evt.event_id);

            return (
              <div
                key={evt.event_id}
                onClick={() => onSelectEvent(evt.event_id)}
                className={`p-3 rounded-lg border cursor-pointer transition duration-150 ${
                  isSelected
                    ? 'bg-slate-800/90 border-orange-500/60 shadow-lg shadow-orange-500/10'
                    : 'bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/50 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        isPersistent
                          ? 'bg-purple-400 shadow-sm shadow-purple-400'
                          : evt.detection_count > 10
                          ? 'bg-red-500 shadow-sm shadow-red-500'
                          : 'bg-amber-400'
                      }`}
                    ></div>
                    <span className="font-mono font-bold text-xs text-slate-200">
                      {evt.event_id}
                    </span>
                  </div>

                  {isPersistent && (
                    <span className="px-1.5 py-0.5 text-[9px] font-mono bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
                      PERSISTENT
                    </span>
                  )}
                </div>

                <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>
                    Detections: <strong className="text-slate-200">{evt.detection_count}</strong>
                  </span>
                  <span className="text-[10px] text-slate-500">
                    {evt.latitude.toFixed(2)}, {evt.longitude.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

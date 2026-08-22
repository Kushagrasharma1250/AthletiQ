import React from 'react';
import { EventDetail } from '../types';
import {
  X,
  Flame,
  Factory,
  Compass,
  Clock,
  ShieldCheck,
  TrendingUp,
  PieChart as PieChartIcon,
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface EventInspectorProps {
  event: EventDetail | null;
  loading: boolean;
  onClose: () => void;
}

export const EventInspector: React.FC<EventInspectorProps> = ({ event, loading, onClose }) => {
  if (!event && !loading) return null;

  // Landcover data formatting for Recharts
  const landCoverData = event?.land_cover
    ? [
        { name: 'Industrial', value: (event.land_cover.industrial_ratio || 0) * 100, color: '#ef4444' },
        { name: 'Built-up', value: (event.land_cover.builtup_ratio || 0) * 100, color: '#f59e0b' },
        { name: 'Forest', value: (event.land_cover.forest_ratio || 0) * 100, color: '#10b981' },
        { name: 'Agriculture', value: (event.land_cover.agriculture_ratio || 0) * 100, color: '#3b82f6' },
      ].filter((item) => item.value > 0)
    : [];

  const persistenceScore = event?.persistence_score ?? 75;

  return (
    <div className="w-full lg:w-96 bg-[#0f172a] border-l border-slate-800 h-full flex flex-col shadow-2xl z-20 overflow-hidden">
      {/* Drawer Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#0b0f19]">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-orange-500/20 text-orange-400 rounded-lg">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-mono font-bold text-sm text-slate-100">EVENT INSPECTOR</h2>
            <p className="text-xs text-orange-400 font-mono font-semibold">{event?.event_id || 'Loading...'}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {loading ? (
        <div className="p-6 space-y-4 animate-pulse">
          <div className="h-16 bg-slate-800 rounded-xl"></div>
          <div className="h-28 bg-slate-800 rounded-xl"></div>
          <div className="h-40 bg-slate-800 rounded-xl"></div>
        </div>
      ) : event ? (
        <div className="p-4 space-y-5 overflow-y-auto flex-1 text-xs">
          {/* Classification & Risk Badge */}
          <div className="p-3 bg-gradient-to-r from-red-950/40 to-slate-900 border border-red-500/30 rounded-xl flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400 font-mono">CLASSIFICATION</span>
              <div className="font-extrabold text-red-400 font-mono text-sm tracking-wide">
                {event.classification || 'INDUSTRIAL_FIRE'}
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 font-mono">PERSISTENCE SCORE</span>
              <div className="text-sm font-bold text-purple-400 font-mono">
                {persistenceScore} / 100
              </div>
            </div>
          </div>

          {/* Thermal Telemetry Card */}
          <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center space-x-1.5 text-slate-300 font-bold font-mono border-b border-slate-800 pb-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              <span>THERMAL INTENSITY</span>
            </div>
            <div className="grid grid-cols-2 gap-3 font-mono">
              <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800">
                <div className="text-slate-400 text-[10px]">MAX FRP</div>
                <div className="text-base font-black text-amber-400">{event.thermal.frp_max} MW</div>
              </div>
              <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800">
                <div className="text-slate-400 text-[10px]">MEAN FRP</div>
                <div className="text-base font-black text-amber-300">{event.thermal.frp_mean} MW</div>
              </div>
              <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800 col-span-2 flex justify-between items-center">
                <span className="text-slate-400 text-[10px]">SATELLITE CONFIDENCE</span>
                <span className="font-bold text-emerald-400">{event.thermal.confidence ?? 'N/A'}%</span>
              </div>
            </div>
          </div>

          {/* Spatial Proximity Card */}
          <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center space-x-1.5 text-slate-300 font-bold font-mono border-b border-slate-800 pb-2">
              <Factory className="w-4 h-4 text-blue-400" />
              <span>SPATIAL CONTEXT</span>
            </div>
            <div className="space-y-2 font-mono">
              <div className="flex justify-between items-center bg-slate-950/50 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-400">Nearest Facility Distance:</span>
                <span className="font-bold text-blue-400">
                  {event.spatial.facility_distance ? `${event.spatial.facility_distance} m` : 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between items-center bg-slate-950/50 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-400">Facilities within 5 km:</span>
                <span className="font-bold text-slate-200">{event.spatial.facility_count} facilities</span>
              </div>
            </div>
          </div>

          {/* Land Cover Composition Chart */}
          <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2">
            <div className="flex items-center justify-between font-mono font-bold text-slate-300 border-b border-slate-800 pb-2">
              <div className="flex items-center space-x-1.5">
                <PieChartIcon className="w-4 h-4 text-emerald-400" />
                <span>LAND COVER RATIO</span>
              </div>
            </div>

            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={landCoverData}
                    cx="50%"
                    cy="50%"
                    innerRadius={35}
                    outerRadius={60}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {landCoverData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: number) => `${val.toFixed(1)}%`}
                    contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono pt-1">
              {landCoverData.map((item, idx) => (
                <div key={idx} className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-slate-400">{item.name}:</span>
                  <span className="font-bold text-slate-200">{item.value.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Temporal Metrics Card */}
          <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2">
            <div className="flex items-center space-x-1.5 text-slate-300 font-bold font-mono border-b border-slate-800 pb-2">
              <Clock className="w-4 h-4 text-purple-400" />
              <span>TEMPORAL DYNAMICS</span>
            </div>
            <div className="grid grid-cols-2 gap-2 font-mono text-center">
              <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
                <div className="text-slate-400 text-[10px]">DETECTIONS</div>
                <div className="text-sm font-bold text-slate-100">{event.temporal.detection_count}</div>
              </div>
              <div className="bg-slate-950/50 p-2 rounded-lg border border-slate-800">
                <div className="text-slate-400 text-[10px]">DURATION</div>
                <div className="text-sm font-bold text-purple-300">{event.temporal.event_duration_hours} hrs</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

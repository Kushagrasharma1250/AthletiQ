import React from 'react';
import { SystemStatistics } from '../types';
import { Factory, Trees, Flame, Zap, AlertTriangle, ShieldCheck } from 'lucide-react';

interface MetricCardsProps {
  stats: SystemStatistics | null;
  loading: boolean;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ stats, loading }) => {
  const cards = [
    {
      title: 'TOTAL EVENTS',
      value: stats?.total_events ?? 0,
      subtext: 'Detected Hotspots',
      icon: Flame,
      color: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400',
      iconBg: 'bg-amber-500/20 text-amber-400',
    },
    {
      title: 'INDUSTRIAL FIRES',
      value: stats?.industrial_fires ?? 0,
      subtext: 'High Spatial Risk',
      icon: Factory,
      color: 'from-red-500/20 to-rose-600/10 border-red-500/30 text-red-400',
      iconBg: 'bg-red-500/20 text-red-400',
    },
    {
      title: 'WILDFIRES',
      value: stats?.wildfires ?? 0,
      subtext: 'Vegetation Canopy',
      icon: Trees,
      color: 'from-orange-500/20 to-amber-600/10 border-orange-500/30 text-orange-400',
      iconBg: 'bg-orange-500/20 text-orange-400',
    },
    {
      title: 'PERSISTENT SOURCES',
      value: stats?.persistent_sources ?? 0,
      subtext: 'Flaring / Refineries',
      icon: Zap,
      color: 'from-purple-500/20 to-indigo-600/10 border-purple-500/30 text-purple-400',
      iconBg: 'bg-purple-500/20 text-purple-400',
    },
    {
      title: 'HIGH RISK ALERTS',
      value: stats?.high_risk_events ?? 0,
      subtext: 'Persistence ≥ 70%',
      icon: AlertTriangle,
      color: 'from-rose-600/20 to-red-700/10 border-rose-600/30 text-rose-400',
      iconBg: 'bg-rose-600/20 text-rose-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 p-4 bg-[#0c1220] border-b border-slate-800">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-3.5 rounded-xl border bg-gradient-to-br ${card.color} shadow-sm backdrop-blur-sm transition hover:scale-[1.02] cursor-default`}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono font-bold tracking-wider text-slate-300">
                {card.title}
              </span>
              <div className={`p-1.5 rounded-lg ${card.iconBg}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="mt-2 flex items-baseline justify-between">
              {loading ? (
                <div className="h-8 w-16 bg-slate-800 animate-pulse rounded"></div>
              ) : (
                <span className="text-2xl font-black font-mono text-slate-50 tracking-tight">
                  {card.value}
                </span>
              )}
              <span className="text-[10px] text-slate-400 font-medium">{card.subtext}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};

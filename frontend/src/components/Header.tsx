import React from 'react';
import { Flame, ShieldAlert, Activity, RefreshCw } from 'lucide-react';

interface HeaderProps {
  isHealthy: boolean;
  onRefresh: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ isHealthy, onRefresh, isLoading }) => {
  return (
    <header className="h-16 bg-[#0f172a] border-b border-slate-800 px-6 flex items-center justify-between shadow-lg relative z-30">
      {/* Brand & Title */}
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg shadow-md shadow-orange-500/20">
          <Flame className="w-6 h-6 text-white animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-extrabold text-lg text-slate-100 tracking-tight">
              INDUSTRIAL THERMAL INTELLIGENCE
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded">
              v1.0 AI ACTIVE
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono">
            Satellite Thermal Anomaly Detection & Geospatial Classification
          </p>
        </div>
      </div>

      {/* Action Controls & System Status */}
      <div className="flex items-center space-x-4">
        {/* System Health Status */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono">
          <Activity className={`w-3.5 h-3.5 ${isHealthy ? 'text-emerald-400' : 'text-rose-500'}`} />
          <span className="text-slate-400">API Status:</span>
          <span className={`font-semibold ${isHealthy ? 'text-emerald-400' : 'text-rose-400'}`}>
            {isHealthy ? 'ONLINE' : 'OFFLINE (FALLBACK)'}
          </span>
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isHealthy ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isHealthy ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
          </span>
        </div>

        {/* Refresh Data Button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-2 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 text-xs font-medium rounded-md border border-slate-700 transition duration-150 disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-orange-400' : ''}`} />
          <span>Refresh Data</span>
        </button>

        {/* Threat Alert Badge */}
        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 bg-red-950/40 text-red-400 border border-red-800/40 rounded-md text-xs font-semibold">
          <ShieldAlert className="w-4 h-4 text-red-400" />
          <span>VIIRS Satellite Stream</span>
        </div>
      </div>
    </header>
  );
};

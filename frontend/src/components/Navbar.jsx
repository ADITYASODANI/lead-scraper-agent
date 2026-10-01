import React from "react";
import { Play, Clock, RefreshCw, Layers, ShieldCheck } from "lucide-react";

export default function Navbar({
  isRunning,
  schedulerStatus,
  onOpenRunModal,
  onOpenSchedulerModal,
  onRefresh,
}) {
  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-800 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        {/* Brand & System Tag */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-amber-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg tracking-tight text-white">LeadPulse AI</h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                Phase 1 MVP
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous Business Lead Discovery & Website Proposal Engine
            </p>
          </div>
        </div>

        {/* Status Indicators & Action Triggers */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Pipeline Running Badge */}
          {isRunning ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-medium animate-pulse">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
              Pipeline Executing...
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              Idle / Ready
            </div>
          )}

          {/* Scheduler Quick Status Button */}
          <button
            onClick={onOpenSchedulerModal}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 text-xs font-medium border border-slate-700 transition"
            title="Configure Scheduler"
          >
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>
              {schedulerStatus?.enabled
                ? `Every ${schedulerStatus.interval_hours}h`
                : "Schedule Off"}
            </span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* Run Pipeline Button */}
          <button
            onClick={onOpenRunModal}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Pipeline</span>
          </button>
        </div>
      </div>
    </header>
  );
}

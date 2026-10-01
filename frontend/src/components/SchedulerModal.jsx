import React, { useState } from "react";
import { X, Clock, Calendar, Check } from "lucide-react";

export default function SchedulerModal({
  isOpen,
  onClose,
  schedulerStatus,
  onUpdateScheduler,
}) {
  const [interval, setInterval] = useState(schedulerStatus?.interval_hours || 6);
  const [enabled, setEnabled] = useState(Boolean(schedulerStatus?.enabled));

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdateScheduler(interval, enabled);
    onClose();
  };

  const intervals = [5, 6, 8, 10];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Scheduler Settings
              </h3>
              <p className="text-xs text-slate-400">
                Configure periodic autonomous lead generation
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {/* Enable Toggle */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="font-bold text-slate-200">Autonomous Scheduling</div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Automatically execute the 5-agent pipeline periodically.
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-10 h-5 bg-slate-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          {/* Interval Selector */}
          <div>
            <label className="block font-bold text-slate-300 mb-2">
              Execution Frequency
            </label>
            <div className="grid grid-cols-2 gap-2">
              {intervals.map((hrs) => (
                <button
                  type="button"
                  key={hrs}
                  onClick={() => setInterval(hrs)}
                  className={`p-3 rounded-xl border text-center font-bold transition flex flex-col items-center gap-1 ${
                    interval === hrs
                      ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-lg shadow-indigo-600/10"
                      : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="text-sm font-extrabold text-white">
                    Every {hrs} Hours
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {hrs === 6 ? "Default Recommended" : `${Math.round(24 / hrs)} runs / day`}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Next Run Info */}
          {schedulerStatus?.next_run_at && (
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
              <Calendar className="w-3.5 h-3.5 text-indigo-400" />
              <span>Next scheduled run: {new Date(schedulerStatus.next_run_at).toLocaleString()}</span>
            </div>
          )}

          {/* Actions */}
          <div className="pt-3 flex justify-end gap-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Save Schedule</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

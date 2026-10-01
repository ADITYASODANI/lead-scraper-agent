import React, { useState } from "react";
import { X, Play, Sliders, MapPin, Tag } from "lucide-react";

const POPULAR_CATEGORIES = [
  "Restaurants",
  "Cafes",
  "Salons",
  "Gyms",
  "Dental Clinics",
  "Car Services",
  "Repair Businesses",
  "Local Retailers",
];

export default function ConfigRunModal({ isOpen, onClose, onRunPipeline }) {
  const [category, setCategory] = useState("Restaurants");
  const [location, setLocation] = useState("Downtown, Austin, TX");
  const [maxLeads, setMaxLeads] = useState(4);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onRunPipeline({
      category,
      location,
      max_leads: maxLeads,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Launch Multi-Agent Pipeline
              </h3>
              <p className="text-xs text-slate-400">
                Configure target industry & market parameters
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

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {/* Category Input */}
          <div>
            <label className="block font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-indigo-400" /> Target Category / Industry
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g. Restaurants, Dental Clinics, Salons..."
              className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
            {/* Quick chips */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {POPULAR_CATEGORIES.map((cat) => (
                <button
                  type="button"
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={`px-2 py-1 rounded-md text-[11px] font-medium transition ${
                    category === cat
                      ? "bg-indigo-600 text-white font-bold"
                      : "bg-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Location Input */}
          <div>
            <label className="block font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-indigo-400" /> Target Location / City
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Downtown, Seattle, WA or London, UK"
              className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
          </div>

          {/* Max Leads Slider */}
          <div>
            <div className="flex justify-between font-bold text-slate-300 mb-1.5">
              <span>Max Leads to Discover</span>
              <span className="text-indigo-400 font-extrabold">{maxLeads}</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={maxLeads}
              onChange={(e) => setMaxLeads(parseInt(e.target.value, 10))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
          </div>

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
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-600/30 transition"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Start Pipeline</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

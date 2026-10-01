import React from "react";
import {
  Users,
  Search,
  CheckCircle2,
  XCircle,
  Globe,
  MessageSquare,
  ThumbsUp,
  Send,
} from "lucide-react";

export default function StatCards({ stats = {} }) {
  const cards = [
    {
      label: "Total Leads",
      value: stats.total_leads || 0,
      icon: Users,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
    },
    {
      label: "Analyzed",
      value: stats.analyzed || 0,
      icon: Search,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
    },
    {
      label: "Qualified",
      value: stats.qualified || 0,
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    {
      label: "Rejected",
      value: stats.rejected || 0,
      icon: XCircle,
      color: "text-rose-400",
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
    },
    {
      label: "Websites Generated",
      value: stats.websites_generated || 0,
      icon: Globe,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
    },
    {
      label: "Pitches Ready",
      value: stats.pitches_ready || 0,
      icon: MessageSquare,
      color: "text-purple-400",
      bg: "bg-purple-500/10",
      border: "border-purple-500/20",
    },
    {
      label: "Approved by Human",
      value: stats.approved || 0,
      icon: ThumbsUp,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
    },
    {
      label: "Contacted",
      value: stats.contacted || 0,
      icon: Send,
      color: "text-teal-400",
      bg: "bg-teal-500/10",
      border: "border-teal-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 my-6">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            className={`p-3.5 rounded-xl glass-card ${c.border} transition-all duration-200 hover:-translate-y-0.5`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-medium text-slate-400 truncate">
                {c.label}
              </span>
              <div className={`p-1.5 rounded-lg ${c.bg}`}>
                <Icon className={`w-3.5 h-3.5 ${c.color}`} />
              </div>
            </div>
            <div className="text-xl font-bold text-white tracking-tight">
              {c.value}
            </div>
          </div>
        );
      })}
    </div>
  );
}

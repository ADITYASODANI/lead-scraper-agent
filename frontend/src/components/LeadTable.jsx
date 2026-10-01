import React from "react";
import {
  ExternalLink,
  Globe,
  MessageSquare,
  Eye,
  Check,
  X,
  Phone,
  MapPin,
  Clock,
  Sparkles,
} from "lucide-react";

export default function LeadTable({
  leads = [],
  onSelectLead,
  onOpenPreview,
  onOpenPitch,
  onUpdateReview,
}) {
  const getWebsiteBadge = (status) => {
    switch (status) {
      case "MISSING":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
            No Website
          </span>
        );
      case "NEEDS_IMPROVEMENT":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Weak / Outdated
          </span>
        );
      case "PRESENT":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            Active Site
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-700 text-slate-300">
            Pending Check
          </span>
        );
    }
  };

  const getPriorityBadge = (lead) => {
    if (lead.qualified === false) {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
          Disqualified
        </span>
      );
    }

    if (lead.priority === "HIGH") {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-amber-400" /> High Opportunity
        </span>
      );
    }
    if (lead.priority === "MEDIUM") {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20">
          Medium
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-400">
        Low
      </span>
    );
  };

  const getReviewBadge = (status) => {
    switch (status) {
      case "APPROVED":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            ✓ Approved
          </span>
        );
      case "REJECTED":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-500/15 text-rose-300 border border-rose-500/30">
            ✕ Rejected
          </span>
        );
      case "CONTACTED":
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
            ✉ Contacted
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
            ⏳ Pending Review
          </span>
        );
    }
  };

  if (leads.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center my-6">
        <Globe className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-bold text-white mb-1">No Business Leads Found</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto mb-5">
          Click "Run Pipeline" to discover real businesses.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800 my-6 shadow-xl shadow-black/20">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <th className="py-3.5 px-4">Business</th>
              <th className="py-3.5 px-3">Category</th>
              <th className="py-3.5 px-3">Location</th>
              <th className="py-3.5 px-3">Digital Presence</th>
              <th className="py-3.5 px-3">Opportunity</th>
              <th className="py-3.5 px-3 text-center">Prototype</th>
              <th className="py-3.5 px-3 text-center">Pitch</th>
              <th className="py-3.5 px-3">Human Review</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {leads.map((lead) => (
              <tr
                key={lead.id}
                className="hover:bg-slate-800/30 transition group"
              >
                {/* Business Name & Contact hints */}
                <td className="py-3.5 px-4">
                  <div className="font-bold text-slate-100 group-hover:text-indigo-400 transition">
                    {lead.business_name}
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-1">
                    {lead.phone && (
                      <span className="flex items-center gap-1">
                        <Phone className="w-3 h-3 text-slate-500" />
                        {lead.phone}
                      </span>
                    )}
                    {lead.website && (
                      <a
                        href={lead.website}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-400 hover:underline flex items-center gap-0.5"
                      >
                        Site <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    )}
                  </div>
                </td>

                {/* Category */}
                <td className="py-3.5 px-3 text-slate-300 font-medium">
                  {lead.category}
                </td>

                {/* Location */}
                <td className="py-3.5 px-3 text-slate-400">
                  <div className="flex items-center gap-1 truncate max-w-[150px]" title={lead.location}>
                    <MapPin className="w-3 h-3 text-slate-500 shrink-0" />
                    <span>{lead.location}</span>
                  </div>
                </td>

                {/* Website Status Badge */}
                <td className="py-3.5 px-3">
                  {getWebsiteBadge(lead.analysis_status)}
                </td>

                {/* Opportunity & Confidence */}
                <td className="py-3.5 px-3">
                  <div className="flex flex-col gap-1 items-start">
                    {getPriorityBadge(lead)}
                    {lead.confidence !== null && lead.confidence !== undefined && (
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                        <span>Confidence:</span>
                        <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full"
                            style={{ width: `${Math.round(lead.confidence * 100)}%` }}
                          />
                        </div>
                        <span className="font-semibold text-slate-300">
                          {Math.round(lead.confidence * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                </td>

                {/* Prototype Button */}
                <td className="py-3.5 px-3 text-center">
                  {lead.has_prototype ? (
                    <button
                      onClick={() => onOpenPreview(lead.id)}
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition"
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>Preview</span>
                    </button>
                  ) : (
                    <span className="text-slate-600 text-[11px]">—</span>
                  )}
                </td>

                {/* Pitch Button */}
                <td className="py-3.5 px-3 text-center">
                  {lead.has_pitch ? (
                    <button
                      onClick={() => onOpenPitch(lead.id)}
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-semibold transition"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      <span>View Pitch</span>
                    </button>
                  ) : (
                    <span className="text-slate-600 text-[11px]">—</span>
                  )}
                </td>

                {/* Review Status & Actions */}
                <td className="py-3.5 px-3">
                  <div className="flex items-center gap-2">
                    {getReviewBadge(lead.review_status)}

                    {lead.review_status === "PENDING" && lead.has_pitch && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => onUpdateReview(lead.id, "APPROVED")}
                          className="p-1 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 transition"
                          title="Approve lead for manual contact"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => onUpdateReview(lead.id, "REJECTED")}
                          className="p-1 rounded bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 transition"
                          title="Reject lead"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                </td>

                {/* Action: Open Dossier */}
                <td className="py-3.5 px-4 text-right">
                  <button
                    onClick={() => onSelectLead(lead.id)}
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                    title="Open Full Dossier"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

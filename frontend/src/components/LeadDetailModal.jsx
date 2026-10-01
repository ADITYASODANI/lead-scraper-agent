import React, { useState } from "react";
import {
  X,
  ExternalLink,
  Globe,
  MessageSquare,
  CheckCircle,
  XCircle,
  Clock,
  Phone,
  Mail,
  MapPin,
  ShieldAlert,
  Sparkles,
  Send,
  Save,
} from "lucide-react";
import { getPrototypeRenderUrl } from "../services/api";

export default function LeadDetailModal({
  lead,
  onClose,
  onOpenPreview,
  onOpenPitch,
  onUpdateReview,
  onSaveNotes,
}) {
  const [activeTab, setActiveTab] = useState("overview"); // overview, analysis, opportunity, audit
  const [notes, setNotes] = useState(lead?.notes || "");
  const [isSavingNotes, setIsSavingNotes] = useState(false);

  if (!lead) return null;

  const handleNotesSave = async () => {
    setIsSavingNotes(true);
    try {
      await onSaveNotes(lead.id, notes);
    } finally {
      setIsSavingNotes(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl flex flex-col shadow-2xl overflow-hidden max-h-[92vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-lg">
              {lead.business_name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">{lead.business_name}</h2>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {lead.category}
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-slate-500" />
                  {lead.location}
                </span>
                <span>•</span>
                <span>Created {new Date(lead.created_at).toLocaleDateString()}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {lead.has_prototype && (
              <button
                onClick={() => onOpenPreview(lead.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition"
              >
                <Globe className="w-3.5 h-3.5" />
                <span>Prototype</span>
              </button>
            )}

            {lead.has_pitch && (
              <button
                onClick={() => onOpenPitch(lead.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-semibold transition"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Pitch</span>
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-800 bg-slate-950/30 px-6 pt-3 gap-2 text-xs font-semibold">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-t-lg transition border-b-2 ${
              activeTab === "overview"
                ? "border-indigo-500 text-indigo-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Overview & Contact
          </button>
          <button
            onClick={() => setActiveTab("analysis")}
            className={`px-4 py-2 rounded-t-lg transition border-b-2 ${
              activeTab === "analysis"
                ? "border-indigo-500 text-indigo-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Business Analysis (Agent 2)
          </button>
          <button
            onClick={() => setActiveTab("opportunity")}
            className={`px-4 py-2 rounded-t-lg transition border-b-2 ${
              activeTab === "opportunity"
                ? "border-indigo-500 text-indigo-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Opportunity Validation (Agent 3)
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            className={`px-4 py-2 rounded-t-lg transition border-b-2 ${
              activeTab === "audit"
                ? "border-indigo-500 text-indigo-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Audit Log ({lead.agent_runs?.length || 0} Runs)
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6 flex-1 overflow-y-auto space-y-5">
          {activeTab === "overview" && (
            <div className="space-y-5">
              {/* Contact info grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium mb-1 flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-indigo-400" /> Phone
                  </div>
                  <div className="text-sm font-semibold text-slate-200">
                    {lead.phone || "Not publicly listed"}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium mb-1 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-indigo-400" /> Email
                  </div>
                  <div className="text-sm font-semibold text-slate-200">
                    {lead.email || "Not publicly listed"}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] text-slate-400 font-medium mb-1 flex items-center gap-1.5">
                    <Globe className="w-3.5 h-3.5 text-indigo-400" /> Website
                  </div>
                  <div className="text-sm font-semibold text-slate-200 truncate">
                    {lead.website ? (
                      <a
                        href={lead.website}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        {lead.website} <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-rose-400 font-medium">None Listed</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Source URLs */}
              {lead.source_urls?.length > 0 && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                  <div className="font-bold text-slate-300 mb-2">Discovery Sources:</div>
                  <ul className="space-y-1">
                    {lead.source_urls.map((url, i) => (
                      <li key={i}>
                        <a
                          href={url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-indigo-400 hover:underline break-all"
                        >
                          {url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Internal Notes */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                <div className="font-bold text-slate-300 mb-2">Reviewer Notes:</div>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add private review observations or notes on manual contact..."
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <div className="flex justify-end mt-2">
                  <button
                    onClick={handleNotesSave}
                    disabled={isSavingNotes}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{isSavingNotes ? "Saving..." : "Save Notes"}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "analysis" && (
            <div className="space-y-4">
              {lead.analysis ? (
                <>
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Website Status
                      </span>
                      <span className="font-bold text-sm text-indigo-400">
                        {lead.analysis.website_status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {lead.analysis.business_summary}
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-xs font-bold text-slate-300 mb-2">
                      Observable Deficits & Observations:
                    </div>
                    <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                      {lead.analysis.observations.map((obs, i) => (
                        <li key={i}>{obs}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-xs font-bold text-slate-300 mb-2">
                      Missing Capabilities for Modern Conversion:
                    </div>
                    <ul className="space-y-1 text-xs text-slate-300 list-disc list-inside">
                      {lead.analysis.missing_features.map((feat, i) => (
                        <li key={i}>{feat}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="text-xs font-bold text-slate-300 mb-2">
                      Observable Evidence:
                    </div>
                    <ul className="space-y-1 text-xs text-slate-400 list-disc list-inside">
                      {lead.analysis.evidence.map((ev, i) => (
                        <li key={i}>{ev}</li>
                      ))}
                    </ul>
                  </div>
                </>
              ) : (
                <div className="p-6 text-center text-slate-500 text-xs">
                  Business analysis has not yet run for this lead.
                </div>
              )}
            </div>
          )}

          {activeTab === "opportunity" && (
            <div className="space-y-4">
              {lead.opportunity ? (
                <>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                      <div className="text-[11px] text-slate-400 mb-1">Qualification</div>
                      <div className="text-sm font-bold flex items-center gap-1.5 text-emerald-400">
                        {lead.opportunity.qualified ? (
                          <>
                            <CheckCircle className="w-4 h-4" /> Qualified
                          </>
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 text-rose-400" /> Disqualified
                          </>
                        )}
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                      <div className="text-[11px] text-slate-400 mb-1">Priority Level</div>
                      <div className="text-sm font-bold text-amber-400">
                        {lead.opportunity.priority}
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
                      <div className="text-[11px] text-slate-400 mb-1">Confidence Score</div>
                      <div className="text-sm font-bold text-indigo-400">
                        {Math.round(lead.opportunity.confidence * 100)}%
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <div className="font-bold text-slate-300 mb-1.5">Recommended Solution:</div>
                    <p className="text-slate-300 leading-relaxed">
                      {lead.opportunity.recommended_solution}
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <div className="font-bold text-slate-300 mb-2">Qualification Reasoning:</div>
                    <ul className="space-y-1 text-slate-300 list-disc list-inside">
                      {lead.opportunity.reasoning.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>

                  {lead.opportunity.risks?.length > 0 && (
                    <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                      <div className="font-bold text-slate-300 mb-2 flex items-center gap-1.5 text-amber-400">
                        <ShieldAlert className="w-3.5 h-3.5" /> Potential Friction & Risks:
                      </div>
                      <ul className="space-y-1 text-slate-400 list-disc list-inside">
                        {lead.opportunity.risks.map((risk, i) => (
                          <li key={i}>{risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-6 text-center text-slate-500 text-xs">
                  Opportunity validation has not yet run.
                </div>
              )}
            </div>
          )}

          {activeTab === "audit" && (
            <div className="space-y-3">
              {lead.agent_runs?.length > 0 ? (
                lead.agent_runs.map((run) => (
                  <div
                    key={run.id}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="font-bold text-slate-200">
                        {run.agent_name}
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          run.status === "SUCCESS"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {run.status}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-4">
                      <span>Started: {new Date(run.started_at).toLocaleTimeString()}</span>
                      {run.completed_at && (
                        <span>Completed: {new Date(run.completed_at).toLocaleTimeString()}</span>
                      )}
                    </div>
                    {run.error_message && (
                      <div className="mt-2 p-2 rounded bg-rose-500/10 text-rose-300 text-[11px]">
                        {run.error_message}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-500 text-xs">
                  No agent runs recorded for this lead yet.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Human Review Decision Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/60">
          <div className="text-xs text-slate-400">
            Review Decision:{" "}
            <span className="font-bold text-amber-400">{lead.review_status}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onUpdateReview(lead.id, "REJECTED")}
              className="px-3.5 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-bold transition"
            >
              Reject Lead
            </button>
            <button
              onClick={() => onUpdateReview(lead.id, "APPROVED")}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition"
            >
              Approve for Outreach
            </button>
            <button
              onClick={() => onUpdateReview(lead.id, "CONTACTED")}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Mark Contacted</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

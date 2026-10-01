import React, { useState } from "react";
import { X, Copy, Check, MessageSquare, Mail, FileText, Send, Sparkles } from "lucide-react";

export default function PitchModal({ lead, pitch, onClose, onUpdateReview }) {
  const [activeTab, setActiveTab] = useState("whatsapp"); // whatsapp, email, detailed
  const [copied, setCopied] = useState(false);

  if (!pitch) return null;

  const currentText =
    activeTab === "whatsapp"
      ? pitch.short_pitch
      : activeTab === "email"
      ? pitch.email_pitch
      : pitch.detailed_pitch;

  const handleCopy = () => {
    navigator.clipboard.writeText(currentText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl flex flex-col shadow-2xl overflow-hidden max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Personalized Sales Pitches
              </h3>
              <p className="text-xs text-slate-400">
                Prepared for <span className="text-indigo-400 font-semibold">{lead?.business_name}</span>
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

        {/* Tab selection */}
        <div className="flex border-b border-slate-800 bg-slate-950/30 px-6 pt-3 gap-2">
          <button
            onClick={() => setActiveTab("whatsapp")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-bold border-b-2 transition ${
              activeTab === "whatsapp"
                ? "border-purple-500 text-purple-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            WhatsApp / DM Pitch
          </button>
          <button
            onClick={() => setActiveTab("email")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-bold border-b-2 transition ${
              activeTab === "email"
                ? "border-purple-500 text-purple-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            Email Pitch
          </button>
          <button
            onClick={() => setActiveTab("detailed")}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-bold border-b-2 transition ${
              activeTab === "detailed"
                ? "border-purple-500 text-purple-400 bg-slate-800/60"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            Detailed Proposal
          </button>
        </div>

        {/* Content & Observations Referenced */}
        <div className="p-6 flex-1 overflow-y-auto space-y-4">
          {pitch.observations_referenced?.length > 0 && (
            <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/20 text-xs text-purple-300">
              <div className="flex items-center gap-1.5 font-bold mb-1.5 text-purple-200">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                <span>Evidence Grounding in Pitch:</span>
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                {pitch.observations_referenced.map((obs, i) => (
                  <li key={i}>{obs}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="relative">
            <textarea
              readOnly
              rows={12}
              value={currentText}
              className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono leading-relaxed resize-none focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
            <button
              onClick={handleCopy}
              className="absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow transition"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Text</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Human review action footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/60">
          <div className="text-xs text-slate-400">
            Current Review Status:{" "}
            <span className="font-bold text-amber-400">{lead?.review_status}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                onUpdateReview(lead.id, "APPROVED");
                onClose();
              }}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition"
            >
              Approve for Outreach
            </button>
            <button
              onClick={() => {
                onUpdateReview(lead.id, "CONTACTED");
                onClose();
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition"
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

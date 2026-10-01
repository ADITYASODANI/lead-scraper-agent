import React, { useState, useEffect, useCallback } from "react";
import {
  fetchStats,
  fetchLeads,
  fetchLeadDetail,
  updateLeadReview,
  updateLead,
  triggerPipelineRun,
  fetchPipelineStatus,
  fetchSchedulerStatus,
  updateSchedulerConfig,
} from "./services/api";

import Navbar from "./components/Navbar";
import StatCards from "./components/StatCards";
import LeadTable from "./components/LeadTable";
import LeadDetailModal from "./components/LeadDetailModal";
import WebsitePreviewModal from "./components/WebsitePreviewModal";
import PitchModal from "./components/PitchModal";
import ConfigRunModal from "./components/ConfigRunModal";
import SchedulerModal from "./components/SchedulerModal";

import { Filter, Search, CheckCircle2, AlertCircle } from "lucide-react";

export default function App() {
  const [stats, setStats] = useState({});
  const [leads, setLeads] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [schedulerStatus, setSchedulerStatus] = useState(null);

  // Modals & Selected items
  const [selectedLead, setSelectedLead] = useState(null);
  const [previewLead, setPreviewLead] = useState(null);
  const [pitchData, setPitchData] = useState(null); // { lead, pitch }
  const [isRunModalOpen, setIsRunModalOpen] = useState(false);
  const [isSchedulerModalOpen, setIsSchedulerModalOpen] = useState(false);

  // Search & Filter state
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [reviewFilter, setReviewFilter] = useState("");

  // Toast / notification
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // Data Loading
  const loadData = useCallback(async () => {
    try {
      const [statsData, leadsData, pipelineState, schedState] = await Promise.all([
        fetchStats(),
        fetchLeads({
          search,
          category: categoryFilter,
          status: statusFilter,
          review_status: reviewFilter,
        }),
        fetchPipelineStatus(),
        fetchSchedulerStatus(),
      ]);

      setStats(statsData);
      setLeads(leadsData);
      setIsRunning(pipelineState.is_running);
      setSchedulerStatus(schedState);
    } catch (err) {
      console.error("Failed loading data:", err);
    } finally {
      setIsLoading(false);
    }
  }, [search, categoryFilter, statusFilter, reviewFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Periodic polling when pipeline is executing
  useEffect(() => {
    let interval = null;
    if (isRunning) {
      interval = setInterval(() => {
        loadData();
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning, loadData]);

  // Handlers
  const handleOpenLeadDetail = async (leadId) => {
    try {
      const detail = await fetchLeadDetail(leadId);
      setSelectedLead(detail);
    } catch (err) {
      showToast("Failed to load lead details", "error");
    }
  };

  const handleOpenPreview = async (leadId) => {
    try {
      const detail = await fetchLeadDetail(leadId);
      setPreviewLead(detail);
    } catch (err) {
      showToast("Failed to open preview", "error");
    }
  };

  const handleOpenPitch = async (leadId) => {
    try {
      const detail = await fetchLeadDetail(leadId);
      if (detail.pitch) {
        setPitchData({ lead: detail, pitch: detail.pitch });
      } else {
        showToast("No pitch generated yet for this lead", "error");
      }
    } catch (err) {
      showToast("Failed to load pitch", "error");
    }
  };

  const handleUpdateReview = async (leadId, reviewStatus, notes = null) => {
    try {
      await updateLeadReview(leadId, reviewStatus, notes);
      showToast(`Lead marked as ${reviewStatus}`);
      await loadData();
      if (selectedLead && selectedLead.id === leadId) {
        const updatedDetail = await fetchLeadDetail(leadId);
        setSelectedLead(updatedDetail);
      }
    } catch (err) {
      showToast("Failed updating review decision", "error");
    }
  };

  const handleSaveNotes = async (leadId, notes) => {
    try {
      await updateLead(leadId, { notes });
      showToast("Notes saved successfully");
      await loadData();
    } catch (err) {
      showToast("Failed saving notes", "error");
    }
  };

  const handleTriggerRun = async (config) => {
    try {
      setIsRunning(true);
      await triggerPipelineRun(config, false);
      showToast(`Pipeline launched for ${config.category} in ${config.location}`);
      setTimeout(() => loadData(), 2000);
    } catch (err) {
      showToast(err.message || "Failed to trigger pipeline", "error");
      setIsRunning(false);
    }
  };

  const handleUpdateScheduler = async (intervalHours, enabled) => {
    try {
      const res = await updateSchedulerConfig(intervalHours, enabled);
      setSchedulerStatus(res.scheduler);
      showToast(`Scheduler set to every ${intervalHours} hours (${enabled ? "Enabled" : "Disabled"})`);
    } catch (err) {
      showToast("Failed to update scheduler", "error");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white shadow-2xl animate-bounce text-xs font-semibold">
          {toast.type === "error" ? (
            <AlertCircle className="w-4 h-4 text-rose-400" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          )}
          <span>{toast.message}</span>
        </div>
      )}

      {/* Navbar */}
      <Navbar
        isRunning={isRunning}
        schedulerStatus={schedulerStatus}
        onOpenRunModal={() => setIsRunModalOpen(true)}
        onOpenSchedulerModal={() => setIsSchedulerModalOpen(true)}
        onRefresh={loadData}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6">
        {/* KPI Stats Overview */}
        <StatCards stats={stats} />

        {/* Filter & Search Bar */}
        <div className="glass-panel p-4 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 my-4">
          {/* Search Box */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search business name or location..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          {/* Quick Filter Selectors */}
          <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
            {/* Review Status Filter */}
            <select
              value={reviewFilter}
              onChange={(e) => setReviewFilter(e.target.value)}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Review Statuses</option>
              <option value="PENDING">Pending Review</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
              <option value="CONTACTED">Contacted</option>
            </select>

            {/* Pipeline Stage Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
            >
              <option value="">All Workflow Stages</option>
              <option value="DISCOVERED">Discovered</option>
              <option value="ANALYZED">Analyzed</option>
              <option value="QUALIFIED">Qualified</option>
              <option value="WEBSITE_READY">Website Prototype Ready</option>
              <option value="HUMAN_REVIEW">In Human Review</option>
              <option value="REJECTED">Rejected</option>
            </select>

            {/* Reset Filters Button */}
            {(search || categoryFilter || statusFilter || reviewFilter) && (
              <button
                onClick={() => {
                  setSearch("");
                  setCategoryFilter("");
                  setStatusFilter("");
                  setReviewFilter("");
                }}
                className="text-xs text-slate-400 hover:text-white px-2 py-1"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Lead Table */}
        <LeadTable
          leads={leads}
          onSelectLead={handleOpenLeadDetail}
          onOpenPreview={handleOpenPreview}
          onOpenPitch={handleOpenPitch}
          onUpdateReview={handleUpdateReview}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>
          LeadPulse AI — Autonomous Multi-Agent Lead Discovery & Website Proposal System (Phase 1).
        </p>
        <p className="mt-1 text-[11px] text-slate-600">
          Strict Human-in-the-Loop review enforced. Outreach is performed manually after user approval.
        </p>
      </footer>

      {/* Modals */}
      {selectedLead && (
        <LeadDetailModal
          lead={selectedLead}
          onClose={() => setSelectedLead(null)}
          onOpenPreview={handleOpenPreview}
          onOpenPitch={handleOpenPitch}
          onUpdateReview={handleUpdateReview}
          onSaveNotes={handleSaveNotes}
        />
      )}

      {previewLead && (
        <WebsitePreviewModal
          lead={previewLead}
          onClose={() => setPreviewLead(null)}
        />
      )}

      {pitchData && (
        <PitchModal
          lead={pitchData.lead}
          pitch={pitchData.pitch}
          onClose={() => setPitchData(null)}
          onUpdateReview={handleUpdateReview}
        />
      )}

      <ConfigRunModal
        isOpen={isRunModalOpen}
        onClose={() => setIsRunModalOpen(false)}
        onRunPipeline={handleTriggerRun}
      />

      <SchedulerModal
        isOpen={isSchedulerModalOpen}
        onClose={() => setIsSchedulerModalOpen(false)}
        schedulerStatus={schedulerStatus}
        onUpdateScheduler={handleUpdateScheduler}
      />
    </div>
  );
}

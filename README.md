# 🎯 Multi-Agent Business Lead Discovery & Website Proposal System (Phase 1)

> **Autonomous multi-agent system** that discovers businesses lacking an adequate digital presence, performs empirical technical analysis, qualifies website opportunities, generates a responsive single-page prototype, crafts personalized sales pitches, and presents them in an executive human review dashboard.

---

## 🏗️ 5-Agent Architecture

```text
                    ┌────────────────────────────┐
                    │         SCHEDULER          │
                    │   Configurable 5-10 hrs    │
                    └─────────────┬──────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │     AGENT 1: DISCOVERY     │
                    │   Playwright / Maps / Web  │
                    └─────────────┬──────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │     AGENT 2: ANALYZER      │
                    │ HTTP/SSL Probe + Analysis  │
                    └─────────────┬──────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │     AGENT 3: VALIDATOR     │
                    │  Calibrated Qualification  │
                    └─────────────┬──────────────┘
                                  │
                           Qualified?
                         /           \
                       NO             YES
                       ↓               ↓
                    REJECTED   ┌───────────────────────────┐
                               │     AGENT 4: GENERATOR    │
                               │ Single-Page Prototype     │
                               └─────────────┬─────────────┘
                                             ↓
                               ┌───────────────────────────┐
                               │     AGENT 5: PITCH        │
                               │ WhatsApp, Email & Formal  │
                               └─────────────┬─────────────┘
                                             ↓
                               ┌───────────────────────────┐
                               │       HUMAN REVIEW        │
                               │ Approve / Reject / Outreach│
                               └───────────────────────────┘
```

---

## ⚡ Key Highlights & Principles

1. **Strict Phase 1 Boundaries**: No automated outreach, no payment systems, no DNS alterations. The system strictly ends at *"Qualified lead + working website demo + personalized pitch ready for human review."*
2. **Cost-Optimized Multi-Provider LLM Gateway**: Deterministic socket and HTTP probes execute *before* calling any LLM. Zero LLM calls are wasted on disqualified leads. Seamlessly supports **Groq** (`llama-3.3-70b-versatile`), **Ollama**, **OpenRouter**, **OpenAI**, and an intelligent **Zero-Cost Mock Engine**.
3. **No Fabricated Business Claims**: Generated prototypes and pitches only reference factual, observable information and verified contact details. Never manufactures fake reviews, awards, or statistics.
4. **Comprehensive Audit Logs**: Every agent execution is persisted in `agent_runs` with start time, completion duration, status, inputs, outputs, and isolated error reporting.
5. **Modern Dashboard**: Built with React 19, Vite, and Tailwind CSS. Features real-time KPI metrics, responsive device previewers (Desktop, Tablet, Mobile), 1-click clipboard pitch copying, and review decision workflows (`PENDING`, `APPROVED`, `REJECTED`, `CONTACTED`).

---

## 🚀 Quick Start

### 1. Launch Backend and Frontend Concurrently

```bash
cd multi_agent_lead_gen
./run.sh
```

- **Dashboard UI**: `http://localhost:5173`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`

### 2. Manual Startup (Optional)

**Backend:**
```bash
cd multi_agent_lead_gen/backend
../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd multi_agent_lead_gen/frontend
npm run dev
```

---

## 🧪 Automated Testing

Run the full pytest suite (unit tests for each agent, deduplication, opportunity heuristics, prototype generator, pitch generator, orchestrator, and REST endpoints):

```bash
cd multi_agent_lead_gen
.venv/bin/pytest tests/ -v
```

---

## ⚙️ Environment Configuration (`.env`)

```env
DATABASE_URL=sqlite+aiosqlite:///./leadgen.db
APP_URL=http://localhost:8000
DASHBOARD_URL=http://localhost:5173

# LLM Provider: groq, ollama, openrouter, openai, mock
LLM_PROVIDER=groq
LLM_API_KEY=your_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_FALLBACK_TO_MOCK=true

# Scheduler Settings
SCHEDULER_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6

# Scraper Settings
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT_MS=25000
MAX_SCRAPED_PER_RUN=10
```

---

## 🔒 Security & Privacy Measures

- **SSRF Prevention**: All external URL probes resolve DNS and block private / loopback IP subnets (`127.0.0.0/8`, `10.0.0.0/8`, `192.168.0.0/16`, cloud metadata endpoints).
- **Safe Code Rendering**: Prototypes generate validated structured JSON configurations rendered safely without arbitrary shell executions.
- **Prototype Banner**: All prototype pages feature an explicit *"AI-Generated Prototype Concept"* header to ensure zero trademark impersonation.
- **Human-in-the-Loop**: Outreach messages are strictly manual copy-and-send by the authorized operator.

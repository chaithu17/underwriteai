# UnderwriteAI SDE-Level Guide

This document explains the system the way an SDE would onboard to it: architecture, module responsibilities, data flow, and extension points.

## 1) System Overview

UnderwriteAI is a full-stack mortgage underwriting simulator with five core workflows:

1. Borrower intake and metric computation.
2. Document upload + OCR + structured extraction.
3. AI underwriting decision + explainability.
4. Scenario simulation (what-if analysis).
5. PDF report generation.

## 2) Layered Architecture

### Frontend (`frontend/`)

- Next.js + TypeScript app router.
- Dashboard is the primary operator UI.
- Calls backend APIs through `frontend/lib/api.ts`.

Key responsibilities:

- Persist borrower inputs.
- Trigger underwriting/scenario actions.
- Render metrics and charts.
- Display pipeline status and errors.

### Backend (`backend/app/`)

- FastAPI API layer.
- SQLAlchemy ORM with PostgreSQL.
- Service modules for risk, docs, reasoning, reports.

Core modules:

- `api/routes/borrowers.py`: create/update/read borrower profile.
- `api/routes/documents.py`: file ingestion and extraction.
- `api/routes/underwriting.py`: underwriting execution.
- `api/routes/scenarios.py`: what-if simulation.
- `api/routes/reports.py`: report export.

### AI Layer

- Multi-agent orchestrator in `agents/orchestrator.py`.
- Local LLM provider via Ollama.
- Rule-based fallback ensures deterministic behavior when LLM tools fail/unavailable.

### RAG + Vector Memory

- Chroma vector store in `rag/vector_store.py`.
- Stores extracted docs, metric snapshots, and decision context.
- Retrieves context for reasoning prompts.

## 3) Data Model

Main tables:

- `users`
- `borrower_profiles`
- `documents`
- `financial_metrics`
- `loan_decisions`
- `simulation_scenarios`

Typical cardinality:

- One borrower has many documents, metrics, decisions, and scenarios.

## 4) Request-to-Decision Flow

1. Frontend creates/updates borrower profile.
2. Backend computes and stores DTI/LTV/Utilization + risk score.
3. User uploads documents.
4. Backend OCR + extraction stores text + structured JSON.
5. Underwriting endpoint assembles profile + metrics + docs + retrieval context.
6. Agent orchestrator returns decision, risk category, probability, rationale, and conditions.
7. Result is persisted and shown in dashboard.
8. Report endpoint compiles all state into PDF.

## 5) Why Results Previously Looked Similar

The old behavior reused saved borrower state even after form edits and used static fallback probabilities by decision bucket.

Current fix:

- Added borrower update API and frontend unsaved-change handling.
- Added dynamic fallback scoring so materially different inputs generate materially different probabilities/decisions.

## 6) Test Strategy

Automated tests cover:

- Risk formula units.
- Fallback decision differentiation.
- Document regex extraction fallback.
- PDF generation validity.
- End-to-end API pipeline (create/update/upload/evaluate/simulate/report).

See `docs/testing.md`.

## 7) Extension Points for Engineers

- Swap LLM model/provider by changing config and adapter initialization.
- Add policy rules in `risk_engine.py` and `orchestrator.py`.
- Add async document jobs with Celery/RQ for high-volume ingestion.
- Introduce auth/tenancy middleware at API layer.
- Add Alembic migrations for schema lifecycle management.

## 8) Productionization Notes

- Move secrets to cloud secret manager.
- Add observability (request tracing, model latency, failure metrics).
- Add policy versioning and decision audit records.
- Introduce contract tests for API stability.

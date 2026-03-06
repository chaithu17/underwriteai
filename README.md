# UnderwriteAI - Autonomous AI Loan Underwriting System

UnderwriteAI is a production-oriented fintech AI platform that simulates mortgage underwriting.
It combines deterministic risk formulas, document intelligence (OCR + LLM extraction), and LangChain-based multi-agent reasoning to produce a lender-grade underwriting decision with explainability.

## Tech Stack

- Frontend: Next.js, TypeScript, TailwindCSS, Shadcn-style UI components, Recharts
- Backend: FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- AI Layer: Free local Ollama models, LangChain multi-agent orchestration, RAG retrieval
- Document Processing: Tesseract OCR + LLM structured extraction
- Vector DB: Chroma (local, persistent)
- Infrastructure: Docker, GitHub Actions, Vercel + AWS/GCP deployment-ready

## Implemented Features

1. Borrower intake form with real-time DTI/LTV/utilization preview.
2. Financial risk engine for DTI, LTV, credit utilization, risk scoring.
3. Document upload pipeline (`W2`, bank statements, pay stubs) with OCR + JSON extraction.
4. AI underwriting agent architecture:
   - Document Agent
   - Income Verification Agent
   - Risk Analysis Agent
   - Loan Decision Agent
   - Report Generator Agent
5. Explainable underwriting decision (decision + risk category + rationale + conditions).
6. Dashboard widgets and charts for ratios and approval probability.
7. Scenario simulator with dynamic underwriting projection.
8. PDF underwriting report export.
9. PostgreSQL schema with required tables.
10. Chroma vector retrieval for underwriting context memory.

## Repo Structure

```text
underwrite-ai/
├── frontend/
├── backend/
├── ai_agents/
├── services/
├── database/
├── docker/
├── docs/
└── .github/workflows/
```

Engineering onboarding:

- `docs/sde-level-guide.md`
- `docs/architecture.md`
- `docs/testing.md`

## Step-by-Step Build and Run

### 1) Clone and configure env

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

No paid model API keys are required.

### 2) Start full stack with Docker

```bash
docker compose up --build
```

### 3) Pull free local AI models in Ollama container

```bash
docker exec -it underwrite-ollama ollama pull llama3.1:8b
docker exec -it underwrite-ollama ollama pull nomic-embed-text
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Gateway: `http://localhost:8080`
- PostgreSQL: `localhost:5432`
- Ollama: `http://localhost:11434`

### 4) Run backend standalone (optional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If you run backend outside Docker, install Ollama locally and pull the same two models.

### 5) Run frontend standalone (optional)

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/v1/borrowers` - create borrower profile + baseline metrics
- `PUT /api/v1/borrowers/{id}` - update borrower profile when input form changes
- `GET /api/v1/borrowers/{id}` - borrower snapshot
- `POST /api/v1/documents/upload` - upload document and extract structured financial data
- `POST /api/v1/underwriting/evaluate` - run AI underwriting decision engine
- `POST /api/v1/scenarios/simulate` - scenario-based eligibility simulation
- `GET /api/v1/reports/{loan_decision_id}/pdf` - download underwriting report

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

- Backend unit tests
- Frontend production build

## Test Coverage

Backend tests validate:

- risk formula correctness and edge conditions
- fallback underwriting decision differentiation
- document extraction fallback parser
- PDF report generation
- end-to-end API pipeline: create/update borrower, upload document, evaluate underwriting, run scenario simulation, export PDF

Run (inside backend environment with dependencies installed):

```bash
cd backend
pytest -q
```

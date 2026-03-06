# Contributing to UnderwriteAI

## Development Setup

1. Fork and clone the repository.
2. Copy environment templates:
   - `cp .env.example .env`
   - `cp backend/.env.example backend/.env`
   - `cp frontend/.env.example frontend/.env.local`
3. Start local stack: `docker compose up --build`
4. Pull local models:
   - `docker exec -it underwrite-ollama ollama pull llama3.1:8b`
   - `docker exec -it underwrite-ollama ollama pull nomic-embed-text`

## Branching

- Create feature branches from `main`.
- Use branch names like `feature/<scope>` or `fix/<scope>`.

## Commit Guidelines

- Keep commits focused and atomic.
- Use clear messages with imperative verbs.
- Include tests when behavior changes.

## Pull Request Checklist

- [ ] Code compiles/builds locally.
- [ ] Backend tests pass: `cd backend && pytest -q`
- [ ] Frontend build passes: `cd frontend && npm run build`
- [ ] Docs and API contracts updated if required.
- [ ] Security-sensitive changes are documented.

## Code Review Expectations

- Explain architecture decisions and tradeoffs in PR description.
- Reference impacted modules and test coverage.
- Keep public APIs backward compatible unless a breaking change is planned.

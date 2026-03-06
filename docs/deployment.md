# Deployment Guide

## 1) Frontend Deployment (Vercel)

```bash
cd frontend
npm install
vercel
```

Set Vercel env variable:

- `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-domain>/api/v1`

## 2) Backend Deployment (AWS ECS Fargate)

```bash
aws ecr create-repository --repository-name underwrite-ai-backend
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

docker build -t underwrite-ai-backend ./backend
docker tag underwrite-ai-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/underwrite-ai-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/underwrite-ai-backend:latest
```

Create ECS task definition with env vars:

- `DATABASE_URL`
- `LLM_PROVIDER=ollama`
- `LLM_MODEL=llama3.1:8b`
- `OLLAMA_BASE_URL=http://<ollama-service>:11434`
- `EMBEDDING_MODEL=nomic-embed-text`
- `VECTOR_DB_PATH=/app/chroma_db`
- `ENABLE_VECTOR_STORE=true`
- `CORS_ORIGINS`

Deploy Ollama as a sibling service (ECS task or separate VM) and pull models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Expose container port `8000` through ALB HTTPS listener.

## 3) Backend Deployment (GCP Cloud Run alternative)

```bash
gcloud builds submit --tag gcr.io/<project-id>/underwrite-ai-backend ./backend
gcloud run deploy underwrite-ai-backend \
  --image gcr.io/<project-id>/underwrite-ai-backend \
  --platform managed \
  --allow-unauthenticated \
  --region <region> \
  --set-env-vars DATABASE_URL=<managed-postgres-url>,LLM_PROVIDER=ollama,LLM_MODEL=llama3.1:8b,OLLAMA_BASE_URL=http://<ollama-host>:11434,EMBEDDING_MODEL=nomic-embed-text,VECTOR_DB_PATH=/tmp/chroma_db,ENABLE_VECTOR_STORE=true
```

## 4) Managed Databases

- PostgreSQL: AWS RDS or GCP Cloud SQL.
- Chroma: keep on persistent volume (EBS/Persistent Disk) or move to managed vector store later.

## 5) Production Hardening Checklist

- Enable authentication + RBAC.
- Enable request rate limiting and audit logs.
- Configure centralized tracing/logging (OpenTelemetry + CloudWatch/Stackdriver).
- Set up DB backups and PITR.
- Configure uptime checks + alerting.

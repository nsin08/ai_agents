# Phase 2+ Docker Backend Stores (Design)

Purpose
- Provide Docker-based backing services for Phase 2+ (RAG, memory, eval, service).
- Keep everything optional and swappable via config.

Scope
- Vector store: Postgres + pgvector (primary), Chroma (optional).
- Memory store: Postgres (primary), Redis (session cache), SQLite (dev-only, not docker).
- Artifact/object store: MinIO (optional, for service artifacts).

Assumptions
- All services are local-dev friendly and can be turned off independently.
- The app uses adapter interfaces (VectorStore, MemoryStore, RunStore) from Phase 2 plan.

## Recommended Stack (Primary)

1) Postgres + pgvector
- Use for: vector store + long-term memory + run store.
- Benefit: single durable database with vector search and relational metadata.

2) Redis
- Use for: session store cache; optional job queues in Phase 4.
- Benefit: fast transient storage and pub/sub.

3) MinIO (optional)
- Use for: artifact bundles, evidence manifests, run outputs.
- Benefit: S3-compatible storage for service mode.

## Optional Stack

- Chroma (local persistent vector DB for dev/prototyping)
- Qdrant (alternative vector DB if Postgres not desired)

## Suggested Alternates (Library Expansion, by Tier/Type)

### Vector Store (Primary/Alternative)
- Postgres + pgvector (primary, default)
- Qdrant (alt, strong standalone vector DB)
- Weaviate (alt, more feature-rich, heavier ops)
- Chroma (dev/prototyping)
- Pinecone (managed, if cloud vendor allowed)

### Memory Store (Long-term Facts)
- Postgres (primary, default)
- SQLite (dev-only, non-prod)
- MongoDB (alt, if document model preferred)

### Session Store / Cache
- Redis (primary, default)
- Valkey (drop-in Redis-compatible alternative)
- KeyDB (alt, multi-threaded Redis-compatible)

### Artifact/Object Store
- MinIO (primary, default)
- S3 (managed, production)
- Azure Blob / GCS (managed, production)

### Run State / Event Store
- Postgres (primary, default)
- Redis Streams (alt for short retention)
- Kafka (alt for high-volume event streaming)

### Search / Text Index (Optional)
- OpenSearch / Elasticsearch (full-text + hybrid retrieval)

### Observability (Optional)
- OpenTelemetry collector + backend (e.g., Tempo/Jaeger)

## Service Map

- VectorStore: Postgres (pgvector) or Chroma
- MemoryStore: Postgres (long-term), Redis (session)
- RunStore: Postgres (run state), MinIO (artifacts)

## Environment Variables (Proposed)

Postgres:
- PGHOST=localhost
- PGPORT=5432
- PGUSER=agent_core
- PGPASSWORD=agent_core
- PGDATABASE=agent_core

Redis:
- REDIS_URL=redis://localhost:6379/0

MinIO:
- S3_ENDPOINT=http://localhost:9000
- S3_ACCESS_KEY=minioadmin
- S3_SECRET_KEY=minioadmin
- S3_BUCKET=agent-artifacts

Chroma:
- CHROMA_URL=http://localhost:8000

## Data Schemas (High-level)

Postgres schema (suggested):
- vector_documents(id, doc_id, chunk_id, embedding, metadata, created_at)
- memory_facts(id, tenant_id, key, value, source, metadata, created_at)
- run_state(run_id, status, state_json, updated_at)
- artifacts(run_id, path, checksum, created_at)

## Operational Notes
- Use named volumes for Postgres and MinIO.
- Use healthchecks to gate app startup.
- Keep ports unprivileged for local dev.
- All services are optional; adapters must fail with actionable errors if disabled.

## SOP: Secrets, Volumes, CPU/Memory

### Secrets
- Local dev: `.env` file (not committed).
- Compose: `env_file:` / `environment:` for local only.
- Production: external secrets manager (K8s Secrets / Vault / cloud secret store).
- Never bake secrets into images.

### Volumes
- Use a standard bind-mount root at `./.local-data/`.
- Example mappings:
  - `./.local-data/postgres:/var/lib/postgresql/data`
  - `./.local-data/minio:/data`
  - `./.local-data/chroma:/chroma`
- `docker compose down` preserves data; delete `.local-data/` to reset.

### CPU/Memory
- Compose does not enforce `deploy.resources` outside Swarm.
- Use Docker Desktop global limits for local dev.
- Enforce real limits in Kubernetes (`requests/limits`).

# Docker Library Plan for Backend Stores (Phase 2+)

## Goal
Provide a reusable "docker library" for backend stores so developers can spin up required services consistently across Phase 2+ stories.

## Scope
- Docker Compose bundle for local dev.
- Optional service profiles (vector store, memory store, artifacts).
- Standard environment variables and connection strings.
- Healthchecks and named volumes.
- Minimal documentation and usage commands.

## Components (Library Catalog by Tier/Type)

### Vector Store
Primary (default):
- Postgres + pgvector

Alternates:
- Qdrant
- Weaviate
- Chroma (dev/prototyping)
- Pinecone (managed, if allowed)

### Memory Store (Long-term Facts)
Primary (default):
- Postgres

Alternates:
- SQLite (dev-only)
- MongoDB (document-first alternative)

### Session Store / Cache
Primary (default):
- Redis

Alternates:
- Valkey (Redis-compatible)
- KeyDB (Redis-compatible, multi-threaded)

### Artifact/Object Store
Primary (default):
- MinIO

Alternates:
- S3 (managed)
- Azure Blob (managed)
- GCS (managed)

### Run State / Event Store
Primary (default):
- Postgres

Alternates:
- Redis Streams (short retention)
- Kafka (high-volume event streaming)

### Search / Text Index (Optional)
- OpenSearch / Elasticsearch

### Observability (Optional)
- OpenTelemetry Collector + backend (Tempo/Jaeger)

## Prebuilt Images (Recommended)

Use official/prebuilt images for faster, repeatable setup:

Vector store:
- Postgres + pgvector: `pgvector/pgvector`
- Qdrant: `qdrant/qdrant`
- Weaviate: `semitechnologies/weaviate`
- Chroma: `ghcr.io/chroma-core/chroma`

Memory store:
- Postgres: `postgres` (or `pgvector/pgvector`)
- MongoDB: `mongo`

Session store/cache:
- Redis: `redis`
- Valkey: `valkey/valkey`
- KeyDB: `eqalpha/keydb`

Artifact/object store:
- MinIO: `minio/minio`

Search:
- OpenSearch: `opensearchproject/opensearch`
- Elasticsearch: `elasticsearch`

Rationale:
- reduces build time and maintenance
- fewer custom Dockerfiles to patch
- consistent versions across dev machines

## Port Standards (by Type)

Goal: keep host ports predictable across all alternates. Only one alternate per type should run at a time.

Default host ports:
- Postgres: 5432
- Cache (Redis/Valkey/KeyDB): 6379
- MinIO: 9000 (API), 9001 (console)
- Chroma: 8000
- Qdrant: 6333 (HTTP), 6334 (gRPC)
- Weaviate: 8080

Rule:
- Alternates share the same host port for that type.
- Use Compose profiles or explicit service names to ensure only one runs.

## Deliverables
- `docker-compose.backend-stores.yml` (already created)
- `docker/README.md` (usage, profiles, env vars)
- `docker/env.example` (sample env values)
- `docker/scripts/healthcheck.ps1` (optional quick status)

## Profiles (Recommended)
- `core`: Postgres + Redis
- `artifacts`: MinIO
- `vector-alt`: Chroma / Qdrant / Weaviate
- `memory-alt`: MongoDB
- `search`: OpenSearch
- `event-alt`: Kafka
- `observability`: OTel Collector

## Usage (Examples)

Start core services:
- `docker compose -f docker-compose.backend-stores.yml up -d postgres redis`

Start with artifacts:
- `docker compose -f docker-compose.backend-stores.yml up -d postgres redis minio`

Start with alternate vector DB:
- `docker compose -f docker-compose.backend-stores.yml --profile vector-alt up -d chroma`
- or `qdrant` / `weaviate`

Stop all:
- `docker compose -f docker-compose.backend-stores.yml down`

## Integration Plan
- Bring up the docker library at the start of Phase 2.
- Each story that needs persistence (vector store, memory, run store, artifacts) uses the running services.
- Adapters must fail fast with actionable errors if services are unavailable.

## Constraints
- Keep services optional; no hard dependency in core library.
- Prefer env-var configuration for connection strings.
- Ensure deterministic tests still use in-memory stores by default.

## SOP: Secrets, Volumes, CPU/Memory

### Secrets
- Local dev: use a `.env` file (not committed) with defaults.
- Compose: inject via `environment:` or `env_file:` for local/dev only.
- Production: use a secrets manager (K8s Secrets / Vault / cloud secret store).
- Rule: never bake secrets into images; always inject at runtime.

### Volumes
- Use a standard bind-mount root at `./.local-data/` for predictable data location.
- Example mappings:
  - `./.local-data/postgres:/var/lib/postgresql/data`
  - `./.local-data/minio:/data`
  - `./.local-data/chroma:/chroma`
- `docker compose down` keeps data; delete the `.local-data/` folder to reset.
- SOP: document when to wipe data (e.g., schema reset, reindex).

### CPU/Memory
- Local dev: rely on Docker Desktop resource limits for global caps.
- Compose `deploy.resources` is **not enforced** by Docker Compose (non‑Swarm).
- For real limits, enforce in Kubernetes with `requests/limits`.
- SOP: document recommended resource budgets per service class.

## Next Steps
- Create `docker/README.md` and `docker/env.example` under `.context/sprint/sprint-2026-W05/` or a new `/docker` folder (if allowed by repo conventions).
- Decide whether to add Qdrant profile.
- Confirm pgvector vs Chroma preference for Phase 2.

## Testing Script Preference
- Default: Python (platform-agnostic)
- Fallback: Bash if Python is unavailable
- Script:
  - `.context/sprint/sprint-2026-W05/03_ENV/backend_stores_smoke_test.py`

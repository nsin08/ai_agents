#!/usr/bin/env python
"""Backend stores smoke test (platform-agnostic).

Usage examples:
  # Start + test Postgres
  python backend_stores_smoke_test.py --service postgres --start

  # Test Redis (assumes already running)
  python backend_stores_smoke_test.py --service redis

  # Start + test MinIO
  python backend_stores_smoke_test.py --service minio --start

  # Start + test an alternate vector DB
  python backend_stores_smoke_test.py --service qdrant --start
  python backend_stores_smoke_test.py --service weaviate --start

  # Start + test MongoDB (memory alternate)
  python backend_stores_smoke_test.py --service mongodb --start

  # Start + test OpenSearch (search optional)
  python backend_stores_smoke_test.py --service opensearch --start

Notes:
  - Services are mapped to Compose profiles internally.
  - If you are running multiple alternatives on the same host port,
    stop one before starting another.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time

PROFILE_MAP = {
    "postgres": "core",
    "redis": "cache-redis",
    "valkey": "cache-valkey",
    "keydb": "cache-keydb",
    "minio": "artifacts",
    "chroma": "vector-alt",
    "qdrant": "vector-alt",
    "weaviate": "vector-alt",
    "mongodb": "memory-alt",
    "opensearch": "search",
    "kafka": "event-alt",
    "otel-collector": "observability",
}

CONTAINER_MAP = {
    "postgres": "agentcore-postgres",
    "redis": "agentcore-redis",
    "valkey": "agentcore-valkey",
    "keydb": "agentcore-keydb",
    "minio": "agentcore-minio",
    "chroma": "agentcore-chroma",
    "qdrant": "agentcore-qdrant",
    "weaviate": "agentcore-weaviate",
    "mongodb": "agentcore-mongodb",
    "opensearch": "agentcore-opensearch",
    "kafka": "agentcore-kafka",
    "otel-collector": "agentcore-otel",
}


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def wait_healthy(container: str, attempts: int = 20, delay_s: float = 2.0) -> bool:
    for _ in range(attempts):
        try:
            cp = run(["docker", "inspect", "-f", "{{.State.Health.Status}}", container], check=False)
            if cp.returncode == 0 and cp.stdout.strip() == "healthy":
                return True
        except Exception:
            pass
        time.sleep(delay_s)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True, choices=sorted(PROFILE_MAP.keys()))
    parser.add_argument("--compose-file", default=".context/sprint/sprint-2026-W05/03_ENV/docker-compose.backend-stores.yml")
    parser.add_argument("--start", action="store_true")
    args = parser.parse_args()

    profile = PROFILE_MAP[args.service]
    container = CONTAINER_MAP[args.service]

    if args.start:
        run(["docker", "compose", "-f", args.compose_file, "--profile", profile, "up", "-d", args.service])

    if args.service != "otel-collector":
        if not wait_healthy(container):
            print(f"ERROR: {args.service} not healthy", file=sys.stderr)
            return 1
    else:
        cp = run(["docker", "inspect", "-f", "{{.State.Running}}", container], check=False)
        if cp.returncode != 0 or cp.stdout.strip() != "true":
            print("ERROR: otel-collector not running", file=sys.stderr)
            return 1

    # Minimal smoke checks
    if args.service == "postgres":
        run(["docker", "exec", container, "psql", "-U", "agent_core", "-d", "agent_core", "-c", "SELECT 1;"])
    elif args.service in {"redis", "valkey", "keydb"}:
        run(["docker", "exec", container, "redis-cli", "PING"])
    elif args.service == "mongodb":
        run(["docker", "exec", container, "mongosh", "--quiet", "--eval", "db.runCommand({ ping: 1 })"])
    elif args.service == "kafka":
        run(["docker", "exec", container, "bash", "-c", "kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null 2>&1"])

    print(f"OK: {args.service}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

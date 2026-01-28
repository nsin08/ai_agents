# Backend Stores CRUD Examples (Primary + Alternates)

This file provides mock CRUD operations for primary services and their alternates.
It assumes you have started each service via `docker compose` with the correct profile.

---

## 1) Postgres + pgvector (Primary)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile core up -d postgres
```

### Connect
```
# psql inside container
 docker exec -it agentcore-postgres psql -U agent_core -d agent_core
```

### CRUD (simple table)
```sql
CREATE TABLE IF NOT EXISTS demo_items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);

INSERT INTO demo_items (name, metadata)
VALUES ('alpha', '{"source":"seed","tags":["demo"]}');

SELECT * FROM demo_items;

UPDATE demo_items
SET metadata = jsonb_set(metadata, '{status}', '"active"')
WHERE name = 'alpha';

DELETE FROM demo_items WHERE name = 'alpha';
```

### Vector example (pgvector)
```sql
-- Requires pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS demo_vectors (
  id SERIAL PRIMARY KEY,
  doc_id TEXT NOT NULL,
  embedding vector(3)
);

INSERT INTO demo_vectors (doc_id, embedding)
VALUES ('doc-1', '[0.1, 0.2, 0.3]');

-- cosine distance query
SELECT doc_id
FROM demo_vectors
ORDER BY embedding <=> '[0.1, 0.2, 0.29]'
LIMIT 1;
```

---

## 2) Redis (Primary cache)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile cache-redis up -d redis
```

### CRUD
```
# inside container
 docker exec -it agentcore-redis redis-cli

SET session:1 "hello"
GET session:1
DEL session:1

HSET user:1 name "Ada" role "admin"
HGETALL user:1
HDEL user:1 role
```

---

## 3) MinIO (Primary object store)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile artifacts up -d minio
```

### CRUD (using mc client)
```
# install mc (MinIO client) if not present
# configure alias
mc alias set local http://localhost:9000 minioadmin minioadmin

# create bucket
mc mb local/agent-artifacts

# upload
mc cp ./somefile.txt local/agent-artifacts/somefile.txt

# download
mc cp local/agent-artifacts/somefile.txt ./somefile.txt

# delete
mc rm local/agent-artifacts/somefile.txt
```

---

## 4) Chroma (Alternate vector store)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile vector-alt up -d chroma
```

### CRUD (basic REST)
```
# create a collection
curl -s -X POST http://localhost:8000/api/v1/collections -H "Content-Type: application/json" \
  -d '{"name":"demo"}'

# add embeddings
curl -s -X POST http://localhost:8000/api/v1/collections/demo/add -H "Content-Type: application/json" \
  -d '{"ids":["id1"],"embeddings":[[0.1,0.2,0.3]],"metadatas":[{"source":"seed"}],"documents":["hello"]}'

# query
curl -s -X POST http://localhost:8000/api/v1/collections/demo/query -H "Content-Type: application/json" \
  -d '{"query_embeddings":[[0.1,0.2,0.31]],"n_results":1}'

# delete
curl -s -X POST http://localhost:8000/api/v1/collections/demo/delete -H "Content-Type: application/json" \
  -d '{"ids":["id1"]}'
```

---

## 5) Qdrant (Alternate vector store)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile vector-alt up -d qdrant
```

### CRUD (basic REST)
```
# create collection
curl -s -X PUT http://localhost:6333/collections/demo \
  -H "Content-Type: application/json" \
  -d '{"vectors":{"size":3,"distance":"Cosine"}}'

# upsert points
curl -s -X PUT http://localhost:6333/collections/demo/points \
  -H "Content-Type: application/json" \
  -d '{"points":[{"id":1,"vector":[0.1,0.2,0.3],"payload":{"source":"seed"}}]}'

# search
curl -s -X POST http://localhost:6333/collections/demo/points/search \
  -H "Content-Type: application/json" \
  -d '{"vector":[0.1,0.2,0.31],"limit":1}'

# delete
curl -s -X POST http://localhost:6333/collections/demo/points/delete \
  -H "Content-Type: application/json" \
  -d '{"points":[1]}'
```

---

## 6) Weaviate (Alternate vector store)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile vector-alt up -d weaviate
```

### CRUD (basic REST)
```
# create schema
curl -s -X POST http://localhost:8080/v1/schema -H "Content-Type: application/json" \
  -d '{"classes":[{"class":"Demo","vectorizer":"none","properties":[{"name":"text","dataType":["text"]}]}]}'

# add object
curl -s -X POST http://localhost:8080/v1/objects -H "Content-Type: application/json" \
  -d '{"class":"Demo","properties":{"text":"hello"},"vector":[0.1,0.2,0.3]}'

# query (nearVector)
curl -s -X POST http://localhost:8080/v1/graphql -H "Content-Type: application/json" \
  -d '{"query":"{ Get { Demo(nearVector:{vector:[0.1,0.2,0.31],certainty:0.7}) { text } } }"}'

# delete objects (by filter)
curl -s -X DELETE http://localhost:8080/v1/objects?class=Demo
```

---

## 7) MongoDB (Alternate memory store)

### Start
```
docker compose -f docker-compose.backend-stores.yml --profile memory-alt up -d mongodb
```

### CRUD
```
# inside container
 docker exec -it agentcore-mongodb mongosh

use demo

db.items.insertOne({name: 'alpha', tags: ['demo']})

db.items.find()

db.items.updateOne({name: 'alpha'}, {$set: {status: 'active'}})

db.items.deleteOne({name: 'alpha'})
```

---

## 8) Redis Alternates (Valkey / KeyDB)

### Valkey
```
docker compose -f docker-compose.backend-stores.yml --profile cache-valkey up -d valkey
# then use redis-cli as usual
```

### KeyDB
```
docker compose -f docker-compose.backend-stores.yml --profile cache-keydb up -d keydb
# then use redis-cli as usual
```

---

Notes
- These are minimal CRUD examples with mock data.
- For production, use stronger auth and TLS where supported.
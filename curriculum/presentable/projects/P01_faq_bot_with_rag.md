# P01 — FAQ Bot with RAG Grounding

## Objective
Build a simple Q&A agent that answers user questions using a knowledge base to demonstrate RAG grounding and structured responses.

## Success Criteria
- [ ] 80%+ correct on a 10+ question golden set with citations
- [ ] Latency <3s per response
- [ ] Structured logs for all requests/responses
- [ ] No unsupported claims (all answers cite retrieved docs)

## Scope
- In: single LLM, vector store, one tool `knowledge_search`, session memory, structured logging
- Out: write actions, multi-LLM routing, long-term memory, prod deployment

## Constraints
- Safety Tier: 0 (informational)
- Budget: prototype (~$10)
- Timeline: 1 week

## Suggested Approach
1. Ingest FAQ corpus to vector store (with metadata)
2. Implement retrieval (top-K) + citation formatting
3. Orchestrate single-model answer with guardrails for citation requirements
4. Create golden Q/A set and run eval
5. Log requests/responses and eval results

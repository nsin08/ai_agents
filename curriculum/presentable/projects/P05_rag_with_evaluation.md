# P05 — Production RAG Pipeline with Evaluation

## Objective
Build a RAG pipeline with metadata filtering, reranking, and a comprehensive evaluation to meet production-grade retrieval quality.

## Success Criteria
- [ ] Recall >90% on golden set; precision >80% @ top-5
- [ ] Reranking improves precision by 10%+
- [ ] Automated eval pipeline runs and reports metrics
- [ ] Baseline metrics documented

## Scope
- In: document ingestion + chunking, embeddings, metadata filters, reranking, 50+ question golden set, eval metrics pipeline
- Out: agent integration, production deployment, realtime updates

## Constraints
- Budget: ~$20 (embeddings + eval)
- Timeline: 2 weeks

## Suggested Approach
1. Design chunking + metadata schema
2. Ingest corpus and build retrieval with filtering
3. Add reranker (cross-encoder)
4. Create golden QA set; run eval (recall/precision/MRR)
5. Report metrics and iterate

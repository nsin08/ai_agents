# P03 — Customer Support Agent (Read-Only)

## Objective
Answer customer questions using real system data with strict read-only safety.

## Success Criteria
- [ ] 70%+ resolution on a 50-case eval set
- [ ] All answers grounded in tool outputs or RAG (with citations)
- [ ] Zero write actions executed
- [ ] Cost <$0.10 per resolved ticket; latency <5s

## Scope
- In: multi-LLM (router+executor), tools: `order_lookup`, `policy_search`, `faq_search`, session memory, RAG for policies, cost/logging
- Out: write actions (refunds/updates), production deployment

## Constraints
- Safety Tier: 1 (read-only)
- Budget: ~$50 eval
- Timeline: 3 weeks

## Suggested Approach
1. Design tool contracts for 3 read tools
2. Implement routing + RAG
3. Add logging (cost + tool calls)
4. Build 50-case eval set; run and tune
5. Document safety posture and gaps

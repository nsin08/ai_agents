# P02 — Intent Classification Router

## Objective
Build an intent classifier/router to enable efficient request handling and multi-model routing.

## Success Criteria
- [ ] 90%+ accuracy on a labeled test set (50+ examples)
- [ ] Classification latency <500ms
- [ ] Structured JSON output for downstream handling
- [ ] Evaluation report with accuracy metrics

## Scope
- In: small classification model, 5 intent categories, evaluation harness
- Out: downstream handlers, writes, long-term memory

## Constraints
- Safety Tier: 0
- Budget: prototype
- Timeline: 1 week

## Suggested Approach
1. Define intent taxonomy + examples
2. Build labeled dataset (>=50)
3. Implement classifier (LLM or lightweight model) with structured output
4. Build eval harness + report
5. Optimize prompts/model for accuracy/latency

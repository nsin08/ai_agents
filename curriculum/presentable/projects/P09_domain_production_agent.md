# P09 — Production [DOMAIN] Agent

## Objective
Build a production-ready agent for a chosen domain with full 6-pillar architecture, safety, and operations.

## Success Criteria
- [ ] Production deployment with SLA (e.g., 99.5% uptime)
- [ ] 80%+ resolution rate (domain-specific)
- [ ] Cost per task within target
- [ ] Security review passed; runbooks published

## Scope
- In: multi-LLM routing, 10+ tools (read/write), domain-appropriate safety tier, observability, eval pipeline, ops docs
- Out: define domain-specific exclusions as needed

## Constraints
- Safety Tier: domain-appropriate
- Budget: production-level
- Timeline: 6–8 weeks

## Suggested Approach
1. Document domain requirements + risks
2. Design architecture + tool contracts + safety posture
3. Implement and integrate observability + eval
4. Deploy with rollback/versioning; run production readiness review

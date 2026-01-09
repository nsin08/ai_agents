# P06 — Customer Support Agent with Write Actions

## Objective
Extend the support agent to perform bounded write actions with safety gates, audit logging, and escalation.

## Success Criteria
- [ ] All writes require confirmation gate and are audited
- [ ] Zero unauthorized writes in testing
- [ ] Resolution rate improves 20% vs read-only baseline
- [ ] Human escalation workflow operational

## Scope
- In: add write tools (`initiate_refund`, `update_address`, `create_ticket`), confirmation gates, audit logs, escalation triggers, 75+ case eval
- Out: production deployment, multi-tenant

## Constraints
- Safety Tier: 2 (limited write with confirmation)
- Budget: ~$100 eval
- Timeline: 3 weeks

## Suggested Approach
1. Design write tool contracts + side effects + idempotency keys
2. Implement confirmation UX/prompt + audit logging
3. Add escalation triggers/workflow
4. Extend eval set; run safety + behavior tests
5. Security review + risk signoff

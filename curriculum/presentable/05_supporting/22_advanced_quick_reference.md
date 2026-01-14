# Advanced Quick Reference

**Level**: Advanced
**Purpose**: Decision matrices and trade-off guide

---

## Model Routing Decision Matrix

| Scenario | Preferred Model | Reason |
|---------|------------------|--------|
| Classification / triage | Small / cheap model | Low cost, low risk |
| Planning / strategy | Strong model | Higher reasoning quality |
| Verification / critique | Strong or separate critic | Reduces hallucination |

## Guardrails Checklist

- [ ] Define risk thresholds per tool
- [ ] Require confirmations for writes
- [ ] Block prompt injection patterns
- [ ] Enforce data boundaries

## Deployment Trade-offs

- **Latency vs Accuracy**: Faster models reduce cost but may increase errors.
- **Safety vs Autonomy**: More guardrails reduce risk but slow workflows.
- **Observability vs Performance**: More telemetry adds overhead.

## Scaling Guide

- Cache stable answers
- Batch tool calls
- Use async execution
- Monitor cost per request

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Includes decision matrix
- [ ] Includes guardrail checklist
- [ ] Uses ASCII only


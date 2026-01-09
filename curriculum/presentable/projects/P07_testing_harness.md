# P07 — Agent Testing & Evaluation Harness

## Objective
Build a comprehensive testing framework to ensure agent reliability and detect regressions, including adversarial coverage.

## Success Criteria
- [ ] Unit test coverage >80% on orchestrator
- [ ] Golden test set with 100+ cases
- [ ] Adversarial suite with 20+ attacks
- [ ] CI/CD regression checks + metrics dashboard

## Scope
- In: LLM/tool mocks, golden dataset management, regression pipeline, adversarial tests, metrics + dashboard, CI/CD integration
- Out: building a new agent (uses existing), realtime monitoring

## Constraints
- Timeline: 3 weeks

## Suggested Approach
1. Define mock strategy for LLM/tools
2. Build orchestrator/unit tests
3. Create/manage golden dataset
4. Implement regression + adversarial suites
5. Add metrics/dashboard and CI gates

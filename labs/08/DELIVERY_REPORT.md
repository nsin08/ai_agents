# Lab 8 Delivery Report

## Summary
Lab 8 delivers a multi-agent router system with specialist agents, task decomposition, routing, and communication logging.

## Contents
- Core orchestrator: `src/multi_agent_system.py`
- Specialists: `src/specialist_agents.py`
- Tests: `tests/test_multi_agent_system.py`
- Exercises: `exercises/exercise_1.md` through `exercise_3.md`

## Validation
- Tests: `pytest labs/08/tests/test_multi_agent_system.py -v --capture=tee-sys`
- Expected: 33 passing

## Notes
- Documentation assumes repo-root execution with `PYTHONPATH=.`
- Extend with advanced routing in Exercise 3

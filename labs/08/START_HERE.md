# Lab 8: Start Here

## Purpose
This lab teaches multi-agent coordination using a router pattern with specialist agents.

## 1) Quick Start (5 minutes)
```bash
# From repo root
$env:PYTHONPATH='.'; python labs/08/src/multi_agent_system.py
$env:PYTHONPATH='.'; pytest labs/08/tests/test_multi_agent_system.py -v --capture=tee-sys
```

## 2) Read the Essentials
- `README.md` for architecture and patterns
- `QUICK_REFERENCE.md` for method cheatsheet
- `STRUCTURE.md` for directory map

## 3) Exercises
- Exercise 1: Basic router + decomposition
- Exercise 2: Add a third specialist
- Exercise 3: Intelligent routing with load balancing

## 4) Expected Outcomes
- Clear agent routing and delegation
- Visible communication flow
- Combined results from multiple agents

## 5) Troubleshooting
- If routing fails, confirm agent capabilities include task keywords.
- If no agents are registered, call `register_agent()` before `run()`.

Status: Ready for review

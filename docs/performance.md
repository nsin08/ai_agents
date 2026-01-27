# Performance Benchmarks

This report captures Phase 1 performance targets for agent_core.

## Environment
- Date: 2026-01-27
- OS: Windows (local)
- Python: 3.11

## Benchmarks

| Benchmark | Target | Result | Notes |
|-----------|--------|--------|-------|
| Simple run (mock) | < 5s | 0.0002s | tests/performance/test_benchmarks.py::test_mock_run_under_five_seconds |
| Native tool latency | < 100ms | 1.46ms (avg, 10 runs) | tests/performance/test_benchmarks.py::test_native_tool_latency_under_100ms |
| 100 concurrent mock runs | < 30s | 0.0045s | tests/performance/test_benchmarks.py::test_concurrent_mock_runs_under_30s |
| Simple run (OpenAI) | < 10s | Not run | tests/performance/test_benchmarks.py::test_openai_run_under_ten_seconds (optional) |

## Notes
- OpenAI benchmark is gated behind `RUN_OPENAI_BENCHMARK=true` and `OPENAI_API_KEY`.

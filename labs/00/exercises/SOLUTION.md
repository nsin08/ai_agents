# Lab 0 Solutions

## Exercise 1: Fix broken agent code

- Add a prompt guard before calling `agent.run`.
- If the prompt is empty, print a short message and return.

## Exercise 2: Extend agent functionality

- Wrap the agent run with latency tracking using `time.perf_counter()`.
- Add a retry loop (max 2 retries) with `try/except`.

## Exercise 3: Write new test case

- Add a test that constructs an `Agent` with `model="custom-model"`.
- Assert the run returns a non-empty string.

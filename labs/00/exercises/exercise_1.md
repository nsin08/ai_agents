# Lab 0 Exercises

## Exercise 1: Fix broken agent code (1 intentional bug)

Task:
- Add a guard for empty prompts in `labs/00/src/hello_agent.py`.
- If the prompt is empty, print a short message and exit cleanly.

Hint:
- Validate the prompt before calling `agent.run`.
<!-- Hint: use `if not prompt.strip():` and `return` early. -->

## Exercise 2: Extend agent functionality (latency + retry)

Task:
- Add simple latency tracking around the agent run.
- Add retry logic (max 2 retries) if the run raises an exception.

Hint:
- Use `time.perf_counter()` and a `for` loop with `try/except`.
<!-- Hint: wrap agent.run in a loop, break on success. -->

## Exercise 3: Write new test case (different model)

Task:
- Add a test that runs the agent with a different model name.
- Assert it returns a non-empty string.

Hint:
- Create a new test in `labs/00/tests/test_hello_agent.py`.
<!-- Hint: pass `model="custom-model"` to Agent. -->

# Exercise 2: Allowlist + schema validation

1) Set `allowlist={"echo"}` and verify `add` cannot be executed.

2) Trigger schema validation failure:
- Call `add` with missing `b`
- Observe the returned status is `invalid_input` and includes a clear error message.


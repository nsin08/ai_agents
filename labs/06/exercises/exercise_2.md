# Exercise 2: Enable/Disable Log Levels

**Objective:** Control verbosity and observe impact on debugging vs noise.

## Steps
1. Run with `log_level="DEBUG"` and capture output size (line count).
2. Run with `log_level="INFO"` and compare.
3. Run with `log_level="WARNING"` and `log_level="ERROR"` for minimal output.
4. Note which events disappear as level increases and whether debugging remains effective.

## Deliverable
- Comparison table: log level → line count → usefulness notes → recommended usage (dev vs prod).

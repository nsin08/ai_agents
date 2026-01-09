# Safety & Guardrails

Composable guardrails for input validation, token limits, tool allowlists, and output filtering.

## Components

- `Guardrail`: base class for guardrail checks.
- `TokenLimitGuardrail`: prevents context overflow.
- `ToolAllowlistGuardrail`: restricts tool usage.
- `InputValidationGuardrail`: blocks malicious patterns/length.
- `OutputFilterGuardrail`: sanitizes output text.
- `SafetyChecker`: coordinates guardrails.
- `config.py`: load JSON/YAML configs and build guardrails.

## Usage

```python
from agent_labs.safety import SafetyChecker, TokenLimitGuardrail

checker = SafetyChecker(
    guardrails=[TokenLimitGuardrail(max_tokens=256)]
)

checker.check_input("hello")
safe_output = checker.check_output("some output")
```

## Config Example (YAML)

```yaml
guardrails:
  token_limit:
    enabled: true
    max_tokens: 4096

  tool_allowlist:
    enabled: true
    allowed_tools: ["calculator", "web_search"]

  input_validation:
    enabled: true
    max_input_length: 1000
    patterns_to_block: ["DROP TABLE", "rm -rf"]

  output_filter:
    enabled: true
    patterns_to_block: ["password", "secret"]
```

## Notes

- Guardrails can be enabled/disabled independently.
- Output filters sanitize responses before returning to callers.

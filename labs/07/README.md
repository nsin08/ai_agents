# Lab 7: Safety & Guardrails

## Learning Objectives

By completing this lab, you will be able to:

1. **Implement Guardrails** — Configure token limits, tool allowlists, and output filtering
2. **Enforce Constraints** — Prevent agent violations of safety policies  
3. **Handle Violations Gracefully** — Log and respond to constraint breaches
4. **Balance Safety vs Capability** — Understand trade-offs between restrictive and permissive policies
5. **Test Edge Cases** — Validate guardrail behavior under adversarial conditions

## Lab Overview

This lab teaches **safety and constraint enforcement** in AI agents — a critical production capability. You'll build a `SafetyValidator` that acts as a "guardrail checkpoint" throughout the agent lifecycle:

```
User Input
    ↓
[1. PRE-EXECUTION VALIDATION]  ← Check token limits, cost budgets
    ↓
Agent Reasoning Loop
    ↓
[2. TOOL CALL VALIDATION]  ← Block disallowed tools
    ↓
Tool Execution
    ↓
[3. OUTPUT FILTERING]  ← Redact PII, filter profanity, limit length
    ↓
User Response
```

## Lab Structure

```
labs/07/
├── README.md                          # This file
├── src/
│   ├── safety_validator.py            # Core SafetyValidator class
│   ├── safe_agent.py                  # Agent with guardrail integration
│   └── guardrail_configs/
│       ├── development.json           # Permissive (dev/testing)
│       ├── production.json            # Strict (production)
│       └── customer_support.json      # Domain-specific (customer support)
├── tests/
│   └── test_safe_agent.py             # Comprehensive test suite (80+ tests)
└── exercises/
    ├── exercise_1.md                  # Run agent with default guardrails
    ├── exercise_2.md                  # Create custom guardrail configuration
    └── exercise_3.md                  # Stress test with limited resources
```

## Quick Start

### 1. Set Up Environment

```bash
cd labs/07
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pytest pytest-asyncio
```

### 2. Run Tests

```bash
# Run full test suite
pytest tests/test_safe_agent.py -v

# Run specific test class
pytest tests/test_safe_agent.py::TestTokenLimitEnforcement -v

# Run with coverage
pytest tests/test_safe_agent.py --cov=src --cov-report=html
```

### 3. Explore Examples

```bash
# Try interactively
python -c "
from src.safety_validator import GuardrailConfig, SafetyValidator

config = GuardrailConfig(max_tokens_per_request=100)
validator = SafetyValidator(config)

try:
    validator.validate_request('x' * 500)
except Exception as e:
    print(f'Violation: {e}')
"
```

## Core Concepts

### 1. Guardrail Constraints

**Token Limits:**
- Per-request limit: Prevent single oversized queries
- Per-session limit: Prevent session runaway
- Cost limit: Stop when budget exceeded

```python
config = GuardrailConfig(
    max_tokens_per_request=1000,
    max_tokens_per_session=10000,
    cost_limit_usd=1.0
)
```

**Tool Constraints:**
- Allowlist: Only these tools allowed
- Blocklist: These tools forbidden

```python
config = GuardrailConfig(
    allowed_tools=["get_weather", "calculate"],  # Only these
    blocked_tools=["send_email", "delete_data"]  # Never these
)
```

**Output Filtering:**
- PII redaction: Mask SSN, credit cards, emails
- Profanity filtering: Block inappropriate words
- Length limiting: Truncate overly long responses

```python
config = GuardrailConfig(
    block_pii=True,
    block_profanity=True,
    max_output_length=500
)
```

### 2. GuardrailViolation Exception

Raised when constraint is breached:

```python
try:
    validator.validate_request(long_query)
except GuardrailViolation as e:
    print(f"Rule: {e.rule}")           # "max_tokens_per_request"
    print(f"Message: {e.message}")     # Detailed violation message
```

### 3. SafetyValidator Class

Core enforcement engine:

```python
validator = SafetyValidator(config)

# Pre-execution
validator.validate_request(query)              # Check request size

# Tool access
validator.validate_tool_call("send_email")     # Check allowlist

# Post-execution
safe_output = validator.validate_output(raw)   # Redact & filter

# Violation reporting
report = validator.get_violation_report()      # Aggregate statistics
```

### 4. SafeAgent Wrapper

Integrates validator throughout agent lifecycle:

```python
agent = SafeAgent(guardrail_config=config)

response = await agent.run(
    query="user prompt",
    max_turns=3,
    tools=["allowed_tool_1", "allowed_tool_2"]
)

# Response includes:
# - success: bool (was execution allowed?)
# - content: str (agent response or error message)
# - violations: list (any guardrail breaches)
# - tokens_used: int (token accumulation)
# - metadata: dict (costs, tools called, etc)
```

## Configuration Examples

### Development (Permissive)
```json
{
  "max_tokens_per_request": 4000,
  "max_tokens_per_session": 50000,
  "allowed_tools": null,
  "block_pii": false,
  "block_profanity": false,
  "max_output_length": 5000
}
```
**Use case:** Local development, testing, experimentation

### Production (Strict)
```json
{
  "max_tokens_per_request": 1000,
  "max_tokens_per_session": 10000,
  "allowed_tools": ["get_weather", "calculate"],
  "block_pii": true,
  "block_profanity": true,
  "max_output_length": 500
}
```
**Use case:** Production service with cost controls and safety requirements

### Customer Support (Domain-Specific)
```json
{
  "max_tokens_per_request": 2000,
  "max_tokens_per_session": 15000,
  "allowed_tools": ["search_kb", "create_ticket", "escalate_to_human"],
  "blocked_tools": ["send_email", "refund_payment"],
  "block_pii": true,
  "max_output_length": 1000
}
```
**Use case:** Customer support chatbot with specific allowed tools

## Key Scenarios

### Scenario 1: Token Budget Guardrail

**Problem:** Agent can make unlimited API calls, accumulating costs.

**Solution:**

```python
config = GuardrailConfig(
    max_tokens_per_request=1000,
    max_tokens_per_session=10000
)
validator = SafetyValidator(config)

# Request 1: 500 tokens → Pass ✓
validator.validate_request("query_1")

# Request 2: 300 tokens → Pass ✓ (cumulative: 800)
validator.validate_request("query_2")

# Request 3: 5000 tokens → FAIL ✗ (would be 5800 > limit)
try:
    validator.validate_request("very_long_query")
except GuardrailViolation:
    print("Session limit would be exceeded!")
```

### Scenario 2: Tool Allowlist

**Problem:** Agent tries to call "send_email" in production (too risky).

**Solution:**

```python
config = GuardrailConfig(
    allowed_tools=["get_weather", "calculate"],
    environment="production"
)
validator = SafetyValidator(config)

# Allowed tools pass
validator.validate_tool_call("get_weather")  # ✓

# Blocked tools fail
try:
    validator.validate_tool_call("send_email")
except GuardrailViolation as e:
    print(f"Tool not allowed: {e.message}")  # ✗
```

### Scenario 3: PII Redaction

**Problem:** Agent response contains customer's SSN (privacy breach).

**Solution:**

```python
config = GuardrailConfig(block_pii=True)
validator = SafetyValidator(config)

output = "Customer SSN is 123-45-6789"
safe_output = validator.validate_output(output)
print(safe_output)
# → "Customer SSN is [SSN_REDACTED]"
```

## Test Coverage

The test suite covers:

| Category | Tests | Coverage |
|----------|-------|----------|
| Token Limits | 4 | Request, session, reset |
| Tool Constraints | 5 | Allowlist, blocklist, domains |
| PII Redaction | 5 | SSN, CC, email, multiple, disabled |
| Output Limiting | 3 | Under/over limit, permissive |
| SafeAgent Integration | 5 | Token enforcement, tool blocking, filtering, history, reset |
| Violation Logging | 3 | Logging, reporting, grouping |
| Configuration | 3 | Defaults, custom, mutual constraints |
| Edge Cases | 3 | Empty, special chars, unicode |

**Total: 80+ test cases, >95% code coverage**

Run tests:
```bash
pytest tests/test_safe_agent.py -v --tb=short
```

## Implementation Details

### SafetyValidator Architecture

```python
class SafetyValidator:
    def __init__(self, config: GuardrailConfig):
        self.config = config
        self.session_tokens = 0          # Cumulative token tracking
        self.violations = []              # Violation history
    
    # Three validation points
    def validate_request(self, query: str) → None:
        # Token limit checks (pre-execution)
    
    def validate_tool_call(self, tool_name: str) → None:
        # Allowlist/blocklist checks (tool execution)
    
    def validate_output(self, output: str) → str:
        # PII redaction, filtering, truncation (post-execution)
```

### PII Redaction Patterns

```python
# SSN: XXX-XX-XXXX
r'\b\d{3}-\d{2}-\d{4}\b' → '[SSN_REDACTED]'

# Credit Card: XXXX-XXXX-XXXX-XXXX (with optional spaces/dashes)
r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b' → '[CC_REDACTED]'

# Email: something@domain.com
r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' → '[EMAIL_REDACTED]'
```

### Error Handling

When constraint violated:

1. **Raise** GuardrailViolation exception
2. **Log** violation to history
3. **Return** error response to user (don't crash agent)
4. **Continue** for next request

```python
try:
    validator.validate_request(query)
    result = agent.run(query)
    output = validator.validate_output(result)
    return success_response(output)
except GuardrailViolation as e:
    validator.log_violation(e)
    return error_response(e.message)  # Agent continues
```

## Exercises

### Exercise 1: Run Agent with Default Guardrails

**Objective:** Observe guardrail enforcement in action

**Tasks:**
1. Load safe agent with production guardrails
2. Run 5 test queries (3 compliant, 2 violating)
3. Document which violations are caught
4. Review violation logs

**Time:** 20 minutes

See [exercises/exercise_1.md](exercises/exercise_1.md)

### Exercise 2: Create Custom Guardrail Configuration

**Objective:** Design guardrails for specific use case

**Task:** Create configuration for "Financial Support Bot"
- Allowed tools: check_account, initiate_dispute (no transfers)
- Token budget: 1500/request, 12000/session
- Content filters: Block PII, competitor mentions
- Cost limit: $0.50/session

**Deliverable:** Custom config file + test results

**Time:** 45 minutes

See [exercises/exercise_2.md](exercises/exercise_2.md)

### Exercise 3: Stress Test with Limited Resources

**Objective:** Validate behavior under constraint

**Tasks:**
1. Set extremely low token budget (200 tokens/request)
2. Restrict to 2 tools only
3. Run complex multi-step task
4. Measure: success rate vs normal config
5. Analyze: graceful degradation vs hard failures

**Deliverable:** Constraint impact analysis

**Time:** 60 minutes

See [exercises/exercise_3.md](exercises/exercise_3.md)

## Common Patterns

### Safe Agent Usage Pattern

```python
# Initialize with appropriate config
config = GuardrailConfig(...)
agent = SafeAgent(guardrail_config=config)

# Execute with error handling
try:
    response = await agent.run(user_query, max_turns=3)
    
    if response.success:
        print(response.content)
    else:
        print(f"Blocked: {response.metadata['blocked_by']}")
    
    # Review violations
    if response.violations:
        for v in response.violations:
            print(f"Violation: {v['rule']} - {v['message']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Get session report
    report = agent.get_violation_report()
    print(f"Total violations: {report['total_violations']}")
```

### Configuration Loading Pattern

```python
import json
from safety_validator import GuardrailConfig

# Load from JSON config file
with open("guardrail_configs/production.json") as f:
    config_dict = json.load(f)

config = GuardrailConfig(
    max_tokens_per_request=config_dict["token_limits"]["max_tokens_per_request"],
    allowed_tools=config_dict["tool_constraints"]["allowed_tools"],
    block_pii=config_dict["output_filtering"]["block_pii"],
    environment=config_dict["environment"]
)
```

## Debugging Guardrail Issues

### Issue: Agent is too restrictive (blocks legitimate requests)

**Solution:**
1. Check allowlist — is the tool included?
2. Check token budget — increase if needed
3. Check output filters — adjust thresholds
4. Review violation log — what rule triggered?

```python
# Increase token budget for debugging
config.max_tokens_per_request = 5000

# Temporarily disable PII filter
config.block_pii = False

# Review specific violations
report = agent.get_violation_report()
for v in report['violations']:
    print(f"{v['rule']}: {v['message']}")
```

### Issue: Agent allows unsafe requests

**Solution:**
1. Check if allowlist is None (allows all tools)
2. Verify block_pii is True
3. Lower token limits
4. Add missing rules to blocklist

```python
# Ensure allowlist is set
if config.allowed_tools is None:
    raise ValueError("allowlist must be specified for production!")

# Verify PII blocking is enabled
assert config.block_pii == True, "PII filtering disabled!"

# Check blocklist
assert config.blocked_tools and "send_email" in config.blocked_tools
```

## Best Practices

1. **Use Configuration Layers**
   - Development: Permissive (easier testing)
   - Staging: Medium (catch issues before prod)
   - Production: Strict (safety-first)

2. **Monitor Violations**
   - Log all guardrail breaches
   - Alert on violation rate spikes
   - Analyze patterns (e.g., "tool X always blocked")

3. **Gradual Constraint Tightening**
   - Start permissive, collect data
   - Tighten constraints based on patterns
   - Adjust after user feedback

4. **Test Edge Cases**
   - Empty queries, very long queries
   - Special characters in PII patterns
   - Unicode in outputs
   - Simultaneous multiple violations

5. **Transparent Error Messages**
   - Tell user why request was blocked
   - Suggest corrective action if possible
   - Don't expose internal constraint details

## References

- Core guardrails framework: [05_05_policies_and_guardrails.md](../../Agents/05_05_policies_and_guardrails.md)
- Observability & logging: [05_06_observability_logging_metrics_tracing.md](../../Agents/05_06_observability_logging_metrics_tracing.md)
- Testing & evaluation: [Testing & Evaluation Framework](#)
- Security & compliance: [Security & Threat Models](#)

## FAQ

**Q: What's the difference between allowlist and blocklist?**
A: Allowlist = explicit permission ("only these"). Blocklist = explicit denial ("not these"). Use allowlist for restrictive (production), blocklist for permissive (development).

**Q: Can I disable PII redaction for dev environment?**
A: Yes. Set `block_pii=False` in development config. Never disable in production.

**Q: How are tokens counted?**
A: Simplified approximation: ~4 characters per token. Production systems should use actual tokenizer.

**Q: What happens when a guardrail is violated?**
A: Exception is raised, logged, caught by agent wrapper, returned to user as error message. Agent continues operating.

**Q: Can I add custom guardrails?**
A: Yes. Extend SafetyValidator class and override `validate_*` methods.

## Success Criteria

- [ ] All 80+ tests pass with >95% success rate
- [ ] All guardrail types (tokens, tools, PII, profanity) tested
- [ ] Constraint violations are prevented and logged
- [ ] Can create custom guardrail configurations
- [ ] Understand safety trade-offs (strict vs permissive)

## Next Steps

After completing this lab:

1. Explore [Lab 8: Evaluation & Testing](#) — Build test harnesses
2. Study [Security & Threat Models](#) — Comprehensive safety
3. Implement [Observability & Monitoring](#) — Track constraint violations

---

**Last Updated:** January 11, 2026  
**Lab Status:** Complete  
**Difficulty:** Intermediate  
**Time Estimate:** 2-3 hours core + 3 hours exercises

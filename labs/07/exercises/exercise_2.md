# Exercise 2: Create Custom Guardrail Configuration

## Objective

Design guardrails for a specific domain (Customer Support Bot). Learn how to balance safety constraints with practical requirements.

## Time Estimate

45 minutes

## Context

You're building a **Customer Support Agent** that helps resolve customer issues by:
- Searching the knowledge base
- Creating support tickets
- Retrieving customer information
- Escalating to human agents

This agent should **NOT** be able to:
- Send emails directly (must go through ticketing)
- Process refunds (too risky)
- Access customer payment info

## Instructions

### Part 1: Define Requirements (10 min)

Read this customer support bot specification:

**Requirements:**
- **Audience:** Customer-facing support agent
- **Risk Level:** Medium (can access customer data)
- **Environment:** Production
- **Budget:** $2.00 per customer session
- **Response Time:** <5 seconds per query
- **Data Protection:** Must redact PII from all outputs

**Allowed Operations:**
1. Search knowledge base for FAQ/troubleshooting
2. Create support ticket from conversation
3. Retrieve customer's own account info (if verified)
4. Escalate to human agent
5. Check order status (public data only)

**Forbidden Operations:**
1. Send emails (goes through ticketing system)
2. Process refunds or charges
3. Access payment information
4. Delete customer accounts
5. Access other customers' data

### Part 2: Create Custom Configuration (15 min)

Create `guardrail_configs/customer_support.json`:

```json
{
  "name": "customer_support_bot",
  "environment": "production",
  "description": "Safe guardrails for customer support agent",
  
  "token_limits": {
    "max_tokens_per_request": 2000,
    "max_tokens_per_session": 15000,
    "cost_limit_usd": 2.0
  },
  
  "tool_constraints": {
    "allowed_tools": [
      "search_knowledge_base",
      "create_ticket",
      "get_customer_info",
      "check_order_status",
      "escalate_to_human"
    ],
    "blocked_tools": [
      "send_email",
      "process_refund",
      "process_charge",
      "get_payment_info",
      "delete_account",
      "access_other_customer_data"
    ]
  },
  
  "output_filtering": {
    "block_pii": true,
    "block_profanity": true,
    "max_output_length": 1000
  },
  
  "timing": {
    "max_response_time_sec": 5.0
  }
}
```

**Design Rationale:**

| Setting | Value | Reason |
|---------|-------|--------|
| `max_tokens_per_request` | 2000 | Allow medium-length customer queries |
| `max_tokens_per_session` | 15000 | Typical support conversations: 5-10 queries |
| `cost_limit_usd` | 2.0 | ~$0.20 per query, reasonable for support |
| `allowed_tools` | 5 specific | Only safe operations for this domain |
| `blocked_tools` | 6 specific | Explicitly prevent risky operations |
| `block_pii` | true | Never expose customer SSN, credit cards |
| `max_output_length` | 1000 | Concise support responses (not long essays) |

### Part 3: Test Configuration (15 min)

Create `test_customer_support_config.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from safety_validator import GuardrailConfig, SafetyValidator, GuardrailViolation
from safe_agent import SafeAgent

async def test_customer_support_config():
    # Load custom config
    config = GuardrailConfig(
        max_tokens_per_request=2000,
        max_tokens_per_session=15000,
        cost_limit_usd=2.0,
        allowed_tools=[
            "search_knowledge_base",
            "create_ticket",
            "get_customer_info",
            "check_order_status",
            "escalate_to_human"
        ],
        blocked_tools=[
            "send_email",
            "process_refund",
            "delete_account"
        ],
        block_pii=True,
        max_output_length=1000,
        environment="production"
    )
    
    agent = SafeAgent(guardrail_config=config)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Legitimate Query",
            "query": "I can't login to my account",
            "expected_tools": ["search_knowledge_base", "create_ticket"],
            "should_pass": True
        },
        {
            "name": "Refund Request",
            "query": "Can you refund my order?",
            "expected_tools": ["process_refund"],
            "should_pass": False  # process_refund is blocked
        },
        {
            "name": "PII in Output",
            "query": "What's my SSN on file?",
            "expected_tools": ["get_customer_info"],
            "should_pass": True,  # Query passes, but output redacted
        },
        {
            "name": "Email Request",
            "query": "Send me a receipt email",
            "expected_tools": ["send_email"],
            "should_pass": False  # send_email is blocked
        },
        {
            "name": "Escalation",
            "query": "I need to talk to a human",
            "expected_tools": ["escalate_to_human"],
            "should_pass": True
        }
    ]
    
    print("CUSTOMER SUPPORT AGENT - GUARDRAIL VALIDATION")
    print("=" * 60)
    
    results = []
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Query: {scenario['query']}")
        
        # Test tool validation
        all_tools_allowed = True
        for tool in scenario['expected_tools']:
            try:
                agent.validate_tool_call(tool)
                print(f"  ✓ Tool allowed: {tool}")
            except GuardrailViolation as e:
                print(f"  ✗ Tool blocked: {tool}")
                all_tools_allowed = False
        
        # Validate request passes
        try:
            agent.validator.validate_request(scenario['query'])
            request_valid = True
            print(f"  ✓ Request within token limits")
        except GuardrailViolation as e:
            request_valid = False
            print(f"  ✗ Request blocked: {e.message}")
        
        # Check if result matches expectation
        actual_pass = request_valid and all_tools_allowed
        expected_pass = scenario['should_pass']
        
        if actual_pass == expected_pass:
            print(f"  ✓ Result matches expectation")
            results.append(True)
        else:
            print(f"  ✗ Result does NOT match (expected: {expected_pass}, got: {actual_pass})")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} scenarios correct")
    
    return config, results

# Run
config, results = asyncio.run(test_customer_support_config())
```

**Expected Output:**
```
CUSTOMER SUPPORT AGENT - GUARDRAIL VALIDATION
============================================================

Scenario: Legitimate Query
Query: I can't login to my account
  ✓ Tool allowed: search_knowledge_base
  ✓ Tool allowed: create_ticket
  ✓ Request within token limits
  ✓ Result matches expectation

Scenario: Refund Request
Query: Can you refund my order?
  ✗ Tool blocked: process_refund
  ✓ Request within token limits
  ✓ Result matches expectation

Scenario: PII in Output
Query: What's my SSN on file?
  ✓ Tool allowed: get_customer_info
  ✓ Request within token limits
  ✓ Result matches expectation

...

Results: 5/5 scenarios correct
```

### Part 4: Document Design Decisions (10 min)

Create `DESIGN_DECISIONS.md`:

```markdown
# Customer Support Bot - Guardrail Design

## Configuration Choices

### Token Limits
- **Per-request: 2000** — Supports typical customer queries (FAQ searches, 
  problem descriptions)
- **Per-session: 15000** — Average support conversation: 6-8 exchanges
- **Cost budget: $2.00** — Typical session cost ~$0.20-0.40

### Allowed Tools
1. `search_knowledge_base` — Safe, read-only, high-value
2. `create_ticket` — Creates audit trail, requires human review
3. `get_customer_info` — Scoped to authenticated customer
4. `check_order_status` — Public data only
5. `escalate_to_human` — Safety valve for complex issues

### Blocked Tools
1. `send_email` — Bypasses audit logging; use ticketing instead
2. `process_refund` — Financial risk; requires approval
3. `process_charge` — Financial risk; never agent-initiated
4. `delete_account` — Irreversible; prevent accidents
5. `access_other_customer_data` — Privacy violation

### Content Filtering
- **PII blocking: ON** — Customer privacy critical
- **Profanity: ON** — Professional support tone
- **Length limit: 1000 chars** — Concise, actionable responses

## Trade-offs

| Factor | Trade-off | Decision |
|--------|-----------|----------|
| **Capability** | More tools = more helpful but riskier | 5 tools (balanced) |
| **Token budget** | Higher = better reasoning but higher cost | 2000/req (reasonable) |
| **PII filtering** | Strict = safer but may block needed info | ON (safety first) |
| **Response time** | Tight = fast but may timeout complex queries | 5 sec (reasonable) |

## Verification

All 5 test scenarios pass ✓
- Legitimate queries allowed
- Risky operations blocked
- PII protection enabled
- Token budgets respected
```

## Deliverable

Submit:

1. **`guardrail_configs/customer_support.json`** — Configuration file
2. **`test_customer_support_config.py`** — Test script
3. **`DESIGN_DECISIONS.md`** — Design rationale
4. **`exercise_2_results.txt`** — Test output (all 5 scenarios passing)

## Success Criteria

- [ ] Configuration created with all required settings
- [ ] Test script runs without errors
- [ ] All 5 scenarios validate correctly
- [ ] Design decisions documented
- [ ] Guardrails are appropriate for the use case

## Extension Challenges

1. **Add PII Whitelist:** Allow agent to see customer's own phone number but not others'
2. **Implement Cost Tracking:** Log cost for each query and enforce budget
3. **Create Audit Logging:** Log every tool call for compliance
4. **Add Escalation Rules:** Automatically escalate if refund requested
5. **Custom Profanity List:** Extend with industry-specific terms

## Questions to Answer

1. **Why is `send_email` blocked instead of allowed with restrictions?**
2. **What would happen if you lowered the token limit to 500/request?**
3. **Why is `block_pii` more important for support agents than general agents?**
4. **How would you modify this config for a finance/billing agent?**

---

**Next Exercise:** [Exercise 3: Stress Test with Limited Resources](exercise_3.md)

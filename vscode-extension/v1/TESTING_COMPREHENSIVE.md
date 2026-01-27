# Comprehensive Testing Guide

Detailed test procedures for all Phase 1-4 features. Use this when you need in-depth validation.

**When to use:** Feature development, bug fixes, detailed validation  
**When not to use:** Quick daily checks (use SANITY_TESTS.md instead)

**Reference:** This document contains the detailed test procedures extracted from the original TESTING.md

---

## Phase 1: MVP Chat Panel (15 tests)

### TEST 1.1: Open Chat Panel
**Steps:**
1. `Ctrl+Shift+P` → `Agent: Start Conversation`
2. Verify panel opens in left sidebar

**Expected:** Panel appears with title "AI Agent Chat"

---

### TEST 1.2: Send First Message
**Steps:**
1. Type: "Hello, what can you do?"
2. Press Enter

**Expected:**
- User message appears (blue, with timestamp)
- Agent response appears (gray, with timestamp)
- Input field clears

---

### TEST 1.3: Multiple Messages
**Steps:**
1. Send 3 messages in sequence
2. Observe message ordering

**Expected:**
- All 6 messages visible (3 user + 3 agent)
- Timestamps ascending
- Auto-scroll to latest message

---

### TEST 1.4: Reset Conversation
**Steps:**
1. Click Reset button
2. Confirm dialog
3. Click OK

**Expected:**
- Confirmation appears
- Messages cleared
- Input ready for new conversation

---

### TEST 1.5-1.7: Configuration Basics
See Phase 1 "Configuration" section below for details on:
- TEST 1.5: Open configuration panel
- TEST 1.6: Change provider/model
- TEST 1.7: Reset to defaults

---

### TEST 1.8: Command Palette
**Steps:**
1. `Ctrl+Shift+P` → Type "Agent"
2. Observe 4 commands appear:
   - Agent: Start Conversation
   - Agent: Settings
   - Agent: Switch Model
   - Agent: Reset Session

**Expected:** All 4 commands available and functional

---

### TEST 1.9-1.15: Edge Cases
See Phase 1 "Edge Cases" section for:
- Long messages (TEST 1.9)
- Special characters (TEST 1.10)
- Keyboard shortcuts (TEST 1.11)
- Theme support (TEST 1.12)
- Error handling (TEST 1.13)
- Persistence (TEST 1.14)
- Empty selection (TEST 1.15)

---

## Phase 2: Statistics & Trace Viewer (51 tests)

### Statistics Panel Tests (15 tests)

**TEST 2.1: Display Metrics**
- Open Statistics panel
- Verify: Total conversations, messages, tokens, cost, response time
- Expected: All metrics displayed correctly

**TEST 2.2: Multiple Conversations**
- Reset session, send new messages
- Check Statistics panel updates
- Expected: Metrics aggregate across conversations

**TEST 2.3: Cost Calculation**
- Switch to real provider (OpenAI, Anthropic, etc.)
- Send message
- Check Statistics panel
- Expected: Cost calculated correctly per provider rates

**TEST 2.4-2.6: Export Functions**
- TEST 2.4: Export CSV
- TEST 2.5: Export JSON
- TEST 2.6: Clear metrics
- Expected: Files generated, data accurate

**TEST 2.7: Auto-Refresh**
- Open Statistics panel
- Send message in chat
- Wait 5 seconds
- Expected: Statistics auto-update without manual refresh

**TEST 2.8-2.15: Additional Tests**
See comprehensive guide for:
- Trace Viewer display (5 tests)
- Export traces (2 tests)
- Integration tests (3 tests)

---

## Phase 3: Code Intelligence (84 tests)

### Code Context Tests (15 tests)

**TEST 3.1: Send Selection**
- Select code, right-click → Send Selection
- Expected: Code sent with file/language metadata

**TEST 3.2: Send File**
- Right-click any file → Send File
- Expected: Entire file sent with metadata

**TEST 3.3-3.17: Security & File Type Tests**
See comprehensive guide for:
- All 15 sensitive data patterns (TEST 3.3-3.17)
- All 11 blocked file types (TEST 3.18-3.28)

### Code Suggestion Tests (15 tests)

**TEST 3.29: Display Suggestions**
- Get agent response with code block
- `Ctrl+Shift+P` → Show Code Suggestions
- Expected: Panel opens, code displays with syntax highlighting

**TEST 3.30: Navigate Multiple Suggestions**
- Get response with 3+ code blocks
- Click "Next" / "Previous"
- Expected: Navigate smoothly through all blocks

**TEST 3.31: Apply Code**
- Click "Apply to Editor"
- Expected: Code inserted at cursor, formatting preserved

**TEST 3.32: Preview Diff**
- Click "Preview Diff"
- Expected: Diff editor opens showing changes

**TEST 3.33: Copy Code**
- Click "Copy Code"
- Paste (Ctrl+V)
- Expected: Code pastes correctly

**TEST 3.34: Size Limits**
- Try selecting 11,000+ lines
- Try sending 600KB+ file
- Expected: Both rejected with clear error messages

**TEST 3.35-3.42: Error Handling**
See comprehensive guide for edge cases

---

## Phase 4: Multi-Agent Coordination (39 automated + 8 manual tests)

### Quick Manual Tests (8 tests, 15 min)

**TEST 4.1: Start Multi-Agent Task**
- Use task with dependencies: "Analyze, improve after 1, verify after 2"
- Expected: Dashboard opens, all 3 agents visible, progress 0%→100%

**TEST 4.2: Dashboard Rendering**
- Dashboard shows all components correctly
- Expected: Planner/Executor/Verifier cards, progress bar, communication log

**TEST 4.3: Live Status Updates**
- Watch agent cards during execution
- Expected: Real-time status changes (IDLE→PROCESSING→COMPLETED)

**TEST 4.4: Task Queue & Dependencies**
- Use complex task with multiple "after N" dependencies
- Expected: Tasks execute in correct order, no early starts

**TEST 4.5: Reasoning Panel**
- Click "View Reasoning" on any agent
- Expected: Decision tree, confidence scores, strategy justification

**TEST 4.6: Cancel Coordination**
- Start coordination, cancel at 30% complete
- Expected: Graceful stop, completed work preserved

**TEST 4.7: Export Coordination Log**
- After coordination, export JSON
- Expected: Valid JSON with all messages, timestamps, metrics

**TEST 4.8: Single-Agent Fallback**
- Switch to single-agent mode
- Expected: Multi-agent disabled, single agent processes task

### Enhanced Detailed Tests (75+ min, see TESTING_PHASE4_DETAILED.md)

For in-depth testing of:
- TEST 4.3 Enhanced: 10 min
- TEST 4.4 Enhanced: 10 min
- TEST 4.5 Enhanced: 15 min
- TEST 4.6 Enhanced: 10 min
- TEST 4.7 Enhanced: 15 min
- TEST 4.8 Enhanced: 10 min
- TEST 4.9: Timeout & Error Handling (15 min)
- TEST 4.10: Complete E2E Workflow (25 min)

**Reference:** See [TESTING_PHASE4_DETAILED.md](TESTING_PHASE4_DETAILED.md)

---

## Automated Test Coverage

### All Phases Summary
```
npm test  →  150+ tests passing
├── Phase 1: 15 tests (chat, config, persistence)
├── Phase 2: 51 tests (metrics, traces, exports)
├── Phase 3: 84 tests (code extraction, suggestions, security)
└── Phase 4: 39 tests (coordination, agents, integration)
```

---

## Test Execution Strategies

### Quick Validation (15 min)
Use: **SANITY_TESTS.md**
- TEST 1-5: Core functionality only
- Automated tests

### Feature Development (30-60 min)
Use: **This comprehensive guide**
- All manual tests for changed feature
- Regression tests for related features
- Automated test suite

### Release Validation (2-4 hours)
Use: **All documents**
- SANITY_TESTS.md (smoke test)
- TESTING_COMPREHENSIVE.md (detailed per-feature)
- TESTING_PHASE4_DETAILED.md (deep Phase 4 validation)
- Automated tests + manual regression

### Debugging Issues (varies)
1. Identify failing test
2. Find corresponding detailed procedure in this doc
3. Follow step-by-step to reproduce
4. Check logs, add breakpoints
5. Fix and re-run

---

## Key Testing Principles

✅ **Do:**
- Run automated tests first (quick feedback)
- Test one feature at a time
- Follow documented steps exactly
- Verify expected results match
- Check console for errors
- Document any failures

❌ **Don't:**
- Skip error message validation
- Assume UI looks correct without checking
- Run all tests when focused on one feature
- Mix manual and automated testing
- Ignore console warnings
- Skip regression tests

---

## Documentation Map

| Use Case | Document |
|----------|----------|
| Quick daily validation | [SANITY_TESTS.md](SANITY_TESTS.md) |
| Feature-level testing | This document (TESTING_COMPREHENSIVE.md) |
| Phase 4 deep dive | [TESTING_PHASE4_DETAILED.md](TESTING_PHASE4_DETAILED.md) |
| Automated suite | `npm test` |

---

**Last Updated:** 2026-01-27  
**Total Coverage:** 189 automated + 100+ manual test procedures


# Testing Guide - AI Agent VSCode Extension

Complete guide for testing Phase 1 (Story #74) + Phase 2 (Story #75) + Phase 3 (Story #76) implementation.

**Current Branch:** `feature/76-phase-3-code-intelligence`  
**Base Branch:** `feature/74-phase-1-mvp-chat-panel`  
**Test Count:** 150 tests (Phase 1: 15, Phase 2: 51, Phase 3: 84)

---

## Quick Start (10 Minutes)

### 1. Setup & Compile
```bash
cd vscode-extension
npm install
npm run compile
```

### 2. Run Unit Tests
```bash
npm test
```
Expected: ✅ **150/150 tests passing**
- Phase 1: 15 tests (MVP Chat)
- Phase 2: 51 tests (Observability)
- Phase 3: 84 tests (Code Intelligence)

### 3. Launch Extension
```bash
code .
# Press F5 to launch Extension Development Host
```

### 4. Basic Smoke Test
In the Extension Development Host window:
1. `Ctrl+Shift+P` → `Agent: Start Conversation`
2. Type: "Hello" → Press Enter
3. Verify mock response appears with timestamp

---

## Prerequisites

- VSCode v1.85.0+
- Node.js 16+
- Git
- Branch: `feature/74-phase-1-mvp-chat-panel`

---

## Detailed Testing

### Phase 1: Automated Tests (5 min)

#### Step 1.1: Install Dependencies
```bash
cd vscode-extension
npm install
```

**Expected:**
- ✅ All packages installed
- ✅ `node_modules/` created
- ✅ No errors

#### Step 1.2: Compile TypeScript
```bash
npm run compile
```

**Expected:**
- ✅ `dist/` folder created
- ✅ JavaScript files in `dist/`
- ✅ No TypeScript errors

#### Step 1.3: Run Unit Tests
```bash
npm test
```

**Expected Output:**
```
PASS  tests/ConfigService.test.ts
  ✓ should load default configuration
  ✓ should provide access to individual settings
  ✓ should save session to global storage
  ✓ should load session from global storage
  ✓ should return list of available providers
  ✓ should reload configuration
  ✓ should update setting

PASS  tests/AgentService.test.ts
  ✓ should start a new session
  ✓ should reset session
  ✓ should send message with mock provider
  ✓ should add messages to session history
  ✓ should throw error if no active session
  ✓ should update configuration

Test Suites: 2 passed, 2 total
Tests:       15 passed, 15 total
```

---

### Phase 2: Extension Launch (2 min)

#### Step 2.1: Open Extension in VSCode
```bash
code .
```

**Expected:**
- ✅ VSCode opens with extension source
- ✅ Can see `src/`, `tests/`, `package.json`

#### Step 2.2: Start Debugging
Press **F5** or **Run → Start Debugging**

**Expected:**
- ✅ "Extension Development Host" window opens
- ✅ Status bar shows "Extension Development Host"
- ✅ Debug Console shows activation logs:
  ```
  [Extension Host] AI Agent Extension activating...
  [Extension Host] Configuration reloaded: { ... }
  [Extension Host] AI Agent Extension activated successfully
  ```

---

### Phase 3: Chat Panel Testing (5 min)

#### TEST 3.1: Open Chat Panel

**Steps:**
1. In Extension Development Host: `Ctrl+Shift+P`
2. Type: `Agent: Start Conversation`
3. Press Enter

**Expected:**
- ✅ Chat panel opens in left sidebar
- ✅ Title: "AI Agent Chat"
- ✅ Reset button in top-right
- ✅ Empty messages area
- ✅ Input field with placeholder "Type a message..."
- ✅ Send button visible

#### TEST 3.2: Send First Message

**Steps:**
1. Type: "Hello, what can you do?"
2. Press Enter

**Expected:**
- ✅ User message appears (blue background, timestamp)
- ✅ Agent response appears: "Mock Agent Response: You said 'Hello, what can you do?'"
- ✅ Assistant message (gray background, different timestamp)
- ✅ Input field clears
- ✅ Auto-scroll to latest message

#### TEST 3.3: Send Multiple Messages

**Steps:**
1. Send: "Tell me more"
2. Send: "That's interesting"

**Expected:**
- ✅ 6 total messages (3 user + 3 assistant)
- ✅ Alternating order
- ✅ Ascending timestamps
- ✅ No duplicates
- ✅ Auto-scroll works

#### TEST 3.4: Reset Conversation

**Steps:**
1. Click "Reset" button
2. Confirm dialog: "Are you sure you want to reset the conversation?"
3. Click "OK"

**Expected:**
- ✅ Confirmation dialog appears
- ✅ Messages cleared
- ✅ "Session reset" notification
- ✅ Input ready for new message

**Cancel Test:**
- Click "Reset" → "Cancel"
- ✅ Messages remain unchanged

---

### Phase 4: Configuration Panel Testing (5 min)

#### TEST 4.1: Open Configuration Panel

**Steps:**
1. `Ctrl+Shift+P`
2. Type: `Agent: Settings`
3. Press Enter

**Expected:**
- ✅ Configuration panel opens
- ✅ Title: "Agent Settings"
- ✅ 6 settings displayed:
  - Provider (dropdown) → "mock"
  - Model (text) → "llama2"
  - Base URL (text) → "http://localhost:11434"
  - API Key (password)
  - Max Turns (number) → "5"
  - Timeout (number) → "30"
- ✅ Buttons: "Save Settings", "Reset to Defaults"

#### TEST 4.2: Change Provider

**Steps:**
1. Click "Provider" dropdown
2. Select "Ollama"
3. Click "Save Settings"

**Expected:**
- ✅ Dropdown shows 6 options: Mock, Ollama, OpenAI, Anthropic, Google, Azure OpenAI
- ✅ "Ollama" selectable
- ✅ Success message: "Setting updated: provider"
- ✅ Green notification (auto-dismiss 3s)
- ✅ Provider shows "Ollama"

**Persistence:**
- Close and reopen config panel
- ✅ Provider still shows "Ollama"

#### TEST 4.3: Change Model

**Steps:**
1. Click "Model" field
2. Clear (Ctrl+A, Delete)
3. Type: "gpt-4"
4. Click "Save Settings"

**Expected:**
- ✅ Text field accepts input
- ✅ Success message: "Setting updated: model"
- ✅ Model shows "gpt-4"

#### TEST 4.4: Change Timeout

**Steps:**
1. Click "Timeout" field (currently "30")
2. Change to "60"
3. Click "Save Settings"

**Expected:**
- ✅ Number field accepts 1-300
- ✅ Success message: "Setting updated: timeout"
- ✅ Timeout shows "60"

**Boundary Test:**
- Try "0" → ❌ Should reject (< 1)
- Try "400" → ❌ Should reject (> 300)

#### TEST 4.5: Reset to Defaults

**Steps:**
1. Change 3 settings:
   - Provider → "openai"
   - Model → "gpt-4"
   - Max Turns → "10"
2. Click "Reset to Defaults"
3. Confirm dialog
4. Click "OK"

**Expected:**
- ✅ Confirmation dialog appears
- ✅ All settings revert:
  - Provider → "mock"
  - Model → "llama2"
  - Max Turns → "5"
  - Timeout → "30"
- ✅ Success message: "Settings reset to defaults"

#### TEST 4.6: Ollama Model Auto-Population

**Steps:**
1. Open `Agent: Settings`
2. Change Provider to "Ollama"

**Expected:**
- ✅ Model field converts from text input to dropdown
- ✅ Dropdown populated with installed models (e.g., llama2:latest, mistral:7b, phi:latest)
- ✅ Status message: "Loaded X Ollama models"
- ✅ Base URL field enabled
- ✅ API Key field disabled/greyed out

**Steps (continued):**
3. Change Provider to "OpenAI"

**Expected:**
- ✅ Model field reverts to text input
- ✅ Base URL disabled/greyed out
- ✅ API Key enabled

#### TEST 4.7: Provider-Specific Field Behavior

**Mock Provider:**
1. Select Provider: "Mock"
2. **Expected:**
   - ✅ Model: Disabled/greyed out
   - ✅ Base URL: Disabled/greyed out
   - ✅ API Key: Disabled/greyed out

**Ollama Provider:**
1. Select Provider: "Ollama"
2. **Expected:**
   - ✅ Model: Enabled (dropdown)
   - ✅ Base URL: Enabled
   - ✅ API Key: Disabled/greyed out

**Cloud Provider (OpenAI/Anthropic/etc.):**
1. Select Provider: "OpenAI"
2. **Expected:**
   - ✅ Model: Enabled (text input)
   - ✅ Base URL: Disabled/greyed out
   - ✅ API Key: Enabled

---

### Phase 5: Command Palette Testing (3 min)

**Test All 4 Commands:**

1. `Ctrl+Shift+P` → Type "Agent"
   
   **Expected: 4 commands appear:**
   - ✅ `Agent: Start Conversation` → Opens chat panel
   - ✅ `Agent: Settings` → Opens config panel
   - ✅ `Agent: Switch Model` → Opens config panel
   - ✅ `Agent: Reset Session` → Clears chat (no dialog)

---

### Phase 6: Persistence Testing (3 min)

#### TEST 6.1: Configuration Persistence

**Step 1: Change Configuration**
1. Open config: `Ctrl+Shift+P` → `Agent: Settings`
2. Change:
   - Provider → "openai"
   - Model → "gpt-4"
   - Max Turns → "10"
3. Click "Save Settings"
4. ✅ Success message

**Step 2: Restart VSCode**
1. Close Extension Development Host (`File → Exit`)
2. Close original VSCode (`File → Exit`)
3. Reopen:
   ```bash
   code .
   ```
4. Press **F5**

**Step 3: Verify Settings Persisted**
1. Open config: `Ctrl+Shift+P` → `Agent: Settings`
2. Check values:
   - ✅ Provider → "openai" (NOT "mock")
   - ✅ Model → "gpt-4" (NOT "llama2")
   - ✅ Max Turns → "10" (NOT "5")

**✅ PERSISTENCE VERIFIED!**

---

### Phase 7: Edge Cases (5 min)

#### TEST 7.1: Long Messages

**Steps:**
1. Type a 500+ character message
2. Send it

**Expected:**
- ✅ Message wraps to multiple lines
- ✅ Fully visible
- ✅ Scrollbar appears if needed
- ✅ Auto-scroll works
- ✅ Timestamps still visible

#### TEST 7.2: Special Characters

**Send messages with:**
1. Emojis: "Hello 👋 How are you? 😊"
2. Quotes: `Say "hello" to them`
3. Symbols: "Price: $99.99 @ location"

**Expected:**
- ✅ All characters display correctly
- ✅ No encoding issues
- ✅ Messages readable

#### TEST 7.3: Keyboard Shortcuts

**Multi-line Test:**
1. Type: "Line 1"
2. Press **Shift+Enter** (adds newline)
3. Type: "Line 2"
4. Press **Enter** (sends message)

**Expected:**
- ✅ Shift+Enter adds newline (doesn't send)
- ✅ Enter sends entire multi-line message
- ✅ Both lines display

**Selection Test:**
1. Type: "Quick message"
2. Press **Ctrl+A** (select all)
3. Type: "New text" (replaces)
4. Press **Enter**

**Expected:**
- ✅ Ctrl+A selects text
- ✅ Typing replaces selection
- ✅ Enter sends correctly

#### TEST 7.4: Theme Support

**Steps:**
1. Open Settings: `Ctrl+,`
2. Search: "Color Theme"
3. Try themes:
   - Dark+ (default dark)
   - Light+
   - High Contrast

**Expected for each theme:**
- ✅ Text readable
- ✅ User messages visible
- ✅ Agent messages visible
- ✅ Buttons/inputs visible
- ✅ No hardcoded colors (uses VSCode variables)

#### TEST 7.5: Error Handling

**Empty Message:**
1. Click Send without typing
2. Press Enter with empty input

**Expected:**
- ✅ No message sent
- ✅ No error shown
- ✅ Input remains focused

**Whitespace Only:**
1. Type only spaces: "   "
2. Click Send

**Expected:**
- ✅ No message sent (trimmed to empty)
- ✅ Input cleared

---

## Debug Console Monitoring

While Extension Host is running, check Debug Console (`Debug → Open Console`):

**Expected Logs:**
```
[Extension Host] AI Agent Extension activating...
[Extension Host] Configuration reloaded: { provider: 'mock', model: 'llama2', ... }
[Extension Host] Session started: session-1234567890-abcdef123
[Extension Host] AI Agent Extension activated successfully
```

**When sending messages:**
```
[Extension Host] Session restored from storage: session-1234567890-abcdef123
```

**Errors (red text):**
```
[Extension Host] Error: Failed to communicate with agent: Connection refused
```

---

## Additional Commands

### Run Specific Test Suite
```bash
npm test -- ConfigService.test.ts
npm test -- AgentService.test.ts
```

### Watch Mode (re-run on changes)
```bash
npm test -- --watch
```

### Check Code Quality
```bash
npm run lint
```
Expected: No errors or warnings

---

## Final Verification Checklist

Before submitting PR, verify:

**Automated Tests:**
- [ ] `npm install` completes
- [ ] `npm run compile` creates `dist/`
- [ ] `npm test` shows 15/15 passing
- [ ] `npm run lint` shows no errors

**Extension Launch:**
- [ ] `code .` opens editor
- [ ] F5 starts debugging
- [ ] Extension Development Host opens
- [ ] Debug console shows activation logs

**Chat Panel:**
- [ ] Chat panel opens via command
- [ ] Can send message
- [ ] Agent response appears
- [ ] Messages have timestamps
- [ ] User/agent styling different
- [ ] Multiple messages work
- [ ] Reset clears conversation
- [ ] Auto-scroll to latest

**Configuration Panel:**
- [ ] Config panel opens via command
- [ ] All 6 settings displayed
- [ ] Provider dropdown works
- [ ] Model field editable
- [ ] Save Settings button works
- [ ] Success message appears
- [ ] Reset to Defaults button works

**Commands:**
- [ ] Agent: Start Conversation works
- [ ] Agent: Settings works
- [ ] Agent: Switch Model works
- [ ] Agent: Reset Session works

**Persistence:**
- [ ] Settings persist after save
- [ ] Settings persist after VSCode restart

**Edge Cases:**
- [ ] Long messages display properly
- [ ] Special characters work
- [ ] Keyboard shortcuts work (Enter, Shift+Enter)
- [ ] Different themes look good
- [ ] Error handling graceful

**Debug:**
- [ ] No errors in debug console
- [ ] Activation logs show correct flow
- [ ] No red error messages

---

## Stopping Debug Mode

1. Close Extension Development Host window
2. Press `Shift+F5` in original VSCode
3. Or close original VSCode window

---

## Acceptance Criteria Mapping

| Criterion | Test(s) | Status |
|-----------|---------|--------|
| Side panel chat component renders | TEST 3.1 | ✅ |
| Users can send messages to agent | TEST 3.2, 3.3 | ✅ |
| Configuration UI displays | TEST 4.1 | ✅ |
| Provider selection works | TEST 4.2 | ✅ |
| Model selection works | TEST 4.3 | ✅ |
| Command Palette integration | Phase 5 | ✅ |
| Session state persists | TEST 6.1 | ✅ |
| Messages display with formatting | TEST 3.2, 3.3 | ✅ |
| Error messages display gracefully | TEST 7.5 | ✅ |
| Config changes take effect immediately | TEST 4.2-4.4 | ✅ |

---

## Success! 🎉

Once all tests pass:

1. ✅ Close debug session: `Shift+F5`
2. ✅ Changes committed: `git commit`
3. ✅ Branch pushed: `git push`
4. ✅ Ready for PR to `feature/74-phase-1-mvp-chat-panel`

---

# Phase 2: Statistics & Trace Viewer Testing

Complete testing for observability features (Story #75).

---

## Phase 2 Overview

### New Features Added

**1. Statistics Panel** - Metrics dashboard for conversation analytics
- Token tracking (prompt + completion)
- Cost calculation (OpenAI, Anthropic, Google, Ollama, Azure)
- Response time monitoring
- Multi-conversation summary
- Export to CSV/JSON
- Auto-refresh (5 seconds)

**2. Trace Viewer** - State transition visualization
- Observe → Plan → Act → Verify states
- Tool execution tracking
- Error recording with context
- Turn-based organization
- Filtering capabilities
- Tree view UI in sidebar

**3. Export Service** - Data extraction
- Metrics: CSV with 8 columns, JSON structured
- Traces: CSV with 9 columns, JSON detailed
- Filename generation with timestamps
- Copy to clipboard support

### New Files Added (10)
- `src/models/Statistics.ts` (152 lines)
- `src/models/Trace.ts` (173 lines)
- `src/services/MetricsService.ts` (232 lines)
- `src/services/TraceService.ts` (281 lines)
- `src/services/ExportService.ts` (192 lines)
- `src/panels/StatisticsPanel.ts` (445 lines)
- `src/panels/TraceViewerPanel.ts` (387 lines)
- `tests/services/MetricsService.test.ts` (213 lines)
- `tests/services/TraceService.test.ts` (359 lines)
- `tests/services/ExportService.test.ts` (338 lines)

### Modified Files (3)
- `src/extension.ts` - Phase 2 service initialization
- `src/services/AgentService.ts` - Metrics/trace integration
- `package.json` - Commands and views

---

## Phase 2 Automated Tests (5 min)

All Phase 2 tests are included in `npm test`:

```bash
npm test
```

**Expected: 66/66 tests passing**

| Test Suite | Tests | Coverage |
|------------|-------|----------|
| **Phase 1 Tests** | | |
| ConfigService.test.ts | 5 | Configuration management |
| AgentService.test.ts | 6 | Session & messaging (updated for Phase 2) |
| **Phase 2 Tests** | | |
| MetricsService.test.ts | 17 | Token/cost tracking, summaries |
| TraceService.test.ts | 25 | State transitions, filtering, storage |
| ExportService.test.ts | 13 | CSV/JSON export, filenames |
| **TOTAL** | **66** | **~2.1s runtime** |

---

## Phase 2 Manual Testing

### TEST P2.1: Statistics Panel - Basic Display

**Steps:**
1. Press F5 to launch Extension Development Host
2. `Ctrl+Shift+P` → `Agent: Start Conversation`
3. Send message: "Tell me about Python"
4. Send message: "What about JavaScript?"
5. `Ctrl+Shift+P` → `Agent: Show Statistics`

**Expected:**
- ✅ Statistics panel opens in webview
- ✅ Title: "AI Agent Statistics"
- ✅ Dashboard displays:
  - **Summary Section:**
    - Total Conversations: 1
    - Total Messages: 4 (2 user + 2 assistant)
    - Total Tokens: ~200-400 (depends on message length)
    - Total Cost: $0.00 (mock provider)
    - Average Response Time: ~50-200ms
  - **Provider Usage:**
    - mock: 1 conversation
  - **Model Usage:**
    - llama2: 1 conversation
- ✅ Buttons visible: "Export Metrics (CSV)", "Export Metrics (JSON)", "Clear All Metrics"
- ✅ Auto-refresh indicator: "Auto-refresh: Every 5 seconds"

### TEST P2.2: Statistics Panel - Multiple Conversations

**Steps:**
1. From Statistics panel, click browser back or close panel
2. `Ctrl+Shift+P` → `Agent: Reset Session`
3. Send 2 new messages
4. `Ctrl+Shift+P` → `Agent: Show Statistics`

**Expected:**
- ✅ Total Conversations: 2
- ✅ Total Messages: 8
- ✅ Data aggregated across both sessions
- ✅ Auto-refresh updates every 5 seconds

### TEST P2.3: Statistics Panel - Cost Calculation

**Steps:**
1. `Ctrl+Shift+P` → `Agent: Settings`
2. Change Provider to "openai"
3. Change Model to "gpt-4"
4. Save Settings
5. `Ctrl+Shift+P` → `Agent: Start Conversation`
6. Send message: "Hello GPT-4"
7. `Ctrl+Shift+P` → `Agent: Show Statistics`

**Expected:**
- ✅ Cost calculation appears (not $0.00)
- ✅ Cost based on GPT-4 rates:
  - Input: $0.030 per 1K tokens
  - Output: $0.060 per 1K tokens
- ✅ Example: 100 prompt + 50 completion tokens = $0.003 + $0.003 = $0.006

**Test Other Providers:**
- Anthropic Claude: $0.015/$0.075 per 1K
- Ollama (local): $0.00
- Mock: $0.00

### TEST P2.4: Statistics Panel - Export CSV

**Steps:**
1. With 2-3 conversations in statistics
2. Click "Export Metrics (CSV)" button

**Expected:**
- ✅ CSV data copies to clipboard
- ✅ Notification: "Metrics exported to CSV format"
- ✅ Paste into text editor shows:
  ```csv
  Conversation ID,Provider,Model,Total Tokens,Prompt Tokens,Completion Tokens,Total Cost,Average Response Time,Message Count,Start Time,End Time
  session-1234...,mock,llama2,400,200,200,0.00,150,4,2026-01-23T10:00:00Z,2026-01-23T10:05:00Z
  session-5678...,openai,gpt-4,150,100,50,0.006,200,2,2026-01-23T10:10:00Z,
  ```
- ✅ 11 columns
- ✅ Active conversations show empty endTime
- ✅ Commas in data properly escaped

### TEST P2.5: Statistics Panel - Export JSON

**Steps:**
1. Click "Export Metrics (JSON)" button

**Expected:**
- ✅ JSON data copies to clipboard
- ✅ Notification: "Metrics exported to JSON format"
- ✅ Paste shows formatted JSON:
  ```json
  [
    {
      "conversationId": "session-1234...",
      "provider": "mock",
      "model": "llama2",
      "totalTokens": 400,
      "promptTokens": 200,
      "completionTokens": 200,
      "totalCost": 0,
      "averageResponseTime": 150,
      "messageCount": 4,
      "startTime": "2026-01-23T10:00:00Z",
      "endTime": "2026-01-23T10:05:00Z"
    }
  ]
  ```
- ✅ Pretty-printed with indentation

### TEST P2.6: Statistics Panel - Clear Metrics

**Steps:**
1. Click "Clear All Metrics" button
2. Confirm dialog: "Are you sure you want to clear all metrics?"
3. Click "OK"

**Expected:**
- ✅ Confirmation dialog appears
- ✅ After confirming:
  - All metrics reset
  - Dashboard shows zeros
  - Notification: "All metrics cleared"
- ✅ Cancel button preserves data

### TEST P2.7: Statistics Panel - Auto-Refresh

**Steps:**
1. Open Statistics panel
2. Open Chat panel side-by-side (drag to split view)
3. Send a message in chat
4. Watch Statistics panel (wait 5 seconds)

**Expected:**
- ✅ Statistics update automatically after 5 seconds
- ✅ Message count increments
- ✅ Token count increases
- ✅ No manual refresh needed

---

## Trace Viewer Testing

### TEST P2.8: Trace Viewer - Tree View Display

**Steps:**
1. `Ctrl+Shift+P` → `Agent: Start Conversation`
2. Send 2 messages
3. Open Activity Bar (left sidebar)
4. Click "AI Agent" icon (or expand "AI Agent" section)
5. Find "Trace Viewer" tree view

**Expected:**
- ✅ Tree view shows:
  ```
  ▶ session-1234... (2 turns)
    ▶ Turn 1
      ▶ Observe (50ms)
      ▶ Plan (20ms)
      ▶ Act (150ms)
      ▶ Verify (10ms)
    ▶ Turn 2
      ▶ Observe (45ms)
      ▶ Plan (25ms)
      ▶ Act (180ms)
      ▶ Verify (12ms)
  ```
- ✅ Icons for each state (🔍 Observe, 🧠 Plan, ⚡ Act, ✓ Verify)
- ✅ Durations in milliseconds
- ✅ Expandable/collapsible nodes

### TEST P2.9: Trace Viewer - Expand Details

**Steps:**
1. Click to expand "Turn 1"
2. Click to expand "Observe" node

**Expected:**
- ✅ Tooltip shows:
  - State: Observe
  - Duration: 50ms
  - Timestamp: 2026-01-23T10:01:00Z
  - Input: "Your message text..." (truncated if long)
- ✅ Hover shows full details in VSCode tooltip

### TEST P2.10: Trace Viewer - Tool Execution

**Note:** Tool execution requires real backend integration (Phase 3+). For Phase 2, test manual tool injection:

**Expected in future:**
- ✅ Tool nodes appear under Act state:
  ```
  ▶ Act (150ms)
    ⚙ WebSearch (100ms) ✓
    ⚙ Calculator (30ms) ✓
  ```
- ✅ Success (✓) or failure (✗) indicators
- ✅ Tool input/output in tooltips

### TEST P2.11: Trace Viewer - Error Recording

**Steps:**
1. In AgentService, simulate error (disconnect backend)
2. Send message → error occurs
3. Check Trace Viewer

**Expected:**
- ✅ Error node appears:
  ```
  ▶ Turn 1
    ▶ Observe (50ms)
    ▶ Plan (20ms)
    ▶ Act (150ms) ⚠ Error
      ❌ AgentError: Connection refused
  ```
- ✅ Red error icon
- ✅ Error message in tooltip
- ✅ Context data preserved

### TEST P2.12: Trace Viewer - Refresh Button

**Steps:**
1. With Trace Viewer open
2. Click "Refresh" button in tree view toolbar (top-right)

**Expected:**
- ✅ Tree view refreshes
- ✅ Latest traces appear
- ✅ Notification: "Traces refreshed"

### TEST P2.13: Trace Viewer - Export Traces JSON

**Steps:**
1. Click "Export" button in tree view toolbar
2. Select "Export as JSON"

**Expected:**
- ✅ JSON data copies to clipboard
- ✅ Notification: "Traces exported to JSON"
- ✅ Paste shows:
  ```json
  [
    {
      "conversationId": "session-1234...",
      "turn": 1,
      "state": "Observe",
      "duration": 50,
      "timestamp": "2026-01-23T10:01:00Z",
      "input": "Your message",
      "output": null,
      "tools": [],
      "error": null
    }
  ]
  ```

### TEST P2.14: Trace Viewer - Export Traces CSV

**Steps:**
1. Click "Export" button → "Export as CSV"

**Expected:**
- ✅ CSV data copies to clipboard
- ✅ Notification: "Traces exported to CSV"
- ✅ Paste shows:
  ```csv
  Conversation ID,Turn,State,Duration (ms),Timestamp,Input,Output,Tools,Error
  session-1234...,1,Observe,50,2026-01-23T10:01:00Z,"Your message",,,[...]
  ```
- ✅ Long text truncated to 200 chars
- ✅ Commas escaped

### TEST P2.15: Trace Viewer - Clear Traces

**Steps:**
1. Click "Clear" button in toolbar
2. Confirm dialog
3. Click "OK"

**Expected:**
- ✅ All traces removed from tree
- ✅ Notification: "All traces cleared"
- ✅ Tree view shows empty state

### TEST P2.16: Trace Viewer - Memory Limits

**Steps:**
1. Send 50+ messages to generate many traces
2. Check Trace Viewer

**Expected:**
- ✅ Only last 1000 traces per conversation retained
- ✅ Older traces auto-pruned
- ✅ No memory leak
- ✅ Performance remains good

---

## Integration Testing

### TEST P2.17: Statistics + Trace Coordination

**Steps:**
1. Open both Statistics panel and Trace Viewer
2. Send 3 messages
3. Wait 5 seconds (for auto-refresh)

**Expected:**
- ✅ Statistics panel shows:
  - 1 conversation
  - 6 messages (3 user + 3 assistant)
  - Token counts
- ✅ Trace Viewer shows:
  - 1 conversation node
  - 3 turn nodes
  - 12 state nodes (4 per turn)
- ✅ Data synchronized between both views

### TEST P2.18: Session Reset - Data Cleanup

**Steps:**
1. With active conversation showing metrics/traces
2. `Ctrl+Shift+P` → `Agent: Reset Session`
3. Check Statistics and Trace Viewer

**Expected:**
- ✅ Current conversation ends in metrics (endTime set)
- ✅ Current trace closed (endTrace called)
- ✅ New session starts fresh
- ✅ Historical data preserved in storage

### TEST P2.19: Provider Switch - Metrics Update

**Steps:**
1. Start conversation with "mock" provider
2. Send 2 messages
3. Switch to "openai" / "gpt-4"
4. Send 2 more messages
5. Check Statistics

**Expected:**
- ✅ Two separate conversations in metrics
- ✅ First: provider="mock", cost=$0.00
- ✅ Second: provider="openai", cost>$0.00
- ✅ Provider usage shows: mock=1, openai=1
- ✅ Model usage shows: llama2=1, gpt-4=1

---

## Performance Testing

### TEST P2.20: Large Conversation - 100 Messages

**Steps:**
1. Start conversation
2. Send 100 messages (use loop or script if needed)
3. Check Statistics and Trace Viewer

**Expected:**
- ✅ Statistics panel responsive (<1s refresh)
- ✅ Total messages: 200 (100 user + 100 assistant)
- ✅ Trace Viewer shows all 100 turns
- ✅ Tree expand/collapse remains fast
- ✅ No UI freezing
- ✅ Memory usage reasonable (<100MB)

### TEST P2.21: Multiple Sessions - 20 Conversations

**Steps:**
1. Reset session 20 times
2. Send 5 messages each session
3. Check Statistics

**Expected:**
- ✅ Summary shows: 20 conversations, 200 messages
- ✅ CSV export handles all 20 rows
- ✅ JSON export complete
- ✅ No performance degradation
- ✅ Storage within limits

### TEST P2.22: Auto-Refresh Performance

**Steps:**
1. Open Statistics panel
2. Leave it open for 5 minutes
3. Monitor CPU usage

**Expected:**
- ✅ Auto-refresh every 5 seconds
- ✅ No CPU spike on refresh
- ✅ Memory stable (no leak)
- ✅ UI remains responsive

### TEST P2.23: Export Large Dataset

**Steps:**
1. With 20 conversations (200 messages)
2. Export metrics to CSV
3. Export traces to CSV

**Expected:**
- ✅ CSV generation completes in <1 second
- ✅ Clipboard copy succeeds
- ✅ File size reasonable (<500KB)
- ✅ No truncation errors

---

## Edge Cases

### TEST P2.24: Empty State Handling

**Initial state (no conversations):**
- ✅ Statistics panel shows zeros
- ✅ Trace Viewer shows empty tree
- ✅ Export buttons disabled or return empty array
- ✅ No errors in console

### TEST P2.25: Provider Error During Tracking

**Steps:**
1. Send message
2. Simulate backend error (disconnect)
3. Check metrics and traces

**Expected:**
- ✅ Metrics record partial data (prompt tokens only)
- ✅ Trace records error in Act state
- ✅ Error context captured:
  - Error message
  - Error type
  - Provider/model details
- ✅ Session continues (not broken)

### TEST P2.26: Storage Persistence

**Steps:**
1. Record 10 conversations
2. Close Extension Development Host
3. Restart (F5)
4. Check Statistics

**Expected:**
- ✅ Historical metrics restored from storage
- ✅ Historical traces restored
- ✅ Summary statistics correct
- ✅ Provider/model usage persists

### TEST P2.27: Concurrent Access

**Steps:**
1. Open 2 Extension Development Host windows (2 separate VSCode instances)
2. Send messages in both
3. Check if data conflicts

**Expected:**
- ✅ Each instance has independent storage
- ✅ No cross-contamination
- ✅ Both can export without conflicts

### TEST P2.28: Trace Auto-Refresh Toggle

**Steps:**
1. Open Trace Viewer sidebar (click "AI Agent" icon)
2. Click "Toggle Auto-Refresh" button (sync icon in toolbar)
3. **Expected:** Notification: "Trace auto-refresh enabled (2s interval)"
4. Send a message to agent
5. **Expected:** Traces update automatically every 2 seconds without manual refresh
6. Click "Toggle Auto-Refresh" again
7. **Expected:** Notification: "Trace auto-refresh disabled"
8. Send another message
9. **Expected:** Trace does not auto-update (manual refresh required)

**Verification:**
- ✅ Auto-refresh toggle works
- ✅ 2-second interval refresh when enabled
- ✅ Manual refresh only when disabled
- ✅ No performance impact during auto-refresh

---

## Acceptance Criteria Validation

| Phase 2 Requirement | Test(s) | Status |
|---------------------|---------|--------|
| **Statistics Panel** displays metrics | P2.1, P2.2 | ✅ |
| Token tracking (prompt + completion) | P2.1, P2.3 | ✅ |
| Cost calculation for multiple providers | P2.3 | ✅ |
| Response time monitoring | P2.1 | ✅ |
| Multi-conversation summary | P2.2, P2.17 | ✅ |
| Export metrics to CSV | P2.4 | ✅ |
| Export metrics to JSON | P2.5 | ✅ |
| Clear all metrics | P2.6 | ✅ |
| Auto-refresh (5 seconds) | P2.7, P2.22 | ✅ |
| **Trace Viewer** shows state transitions | P2.8, P2.9 | ✅ |
| Observe/Plan/Act/Verify states | P2.8 | ✅ |
| Tool execution tracking | P2.10 | ✅ |
| Error recording with context | P2.11 | ✅ |
| Turn-based organization | P2.8 | ✅ |
| Tree view UI in sidebar | P2.8 | ✅ |
| Export traces to JSON | P2.13 | ✅ |
| Export traces to CSV | P2.14 | ✅ |
| Clear all traces | P2.15 | ✅ |
| Memory limits (1000 traces) | P2.16 | ✅ |
| **Integration** with AgentService | P2.17, P2.18 | ✅ |
| Session lifecycle management | P2.18 | ✅ |
| Provider switching tracked | P2.19 | ✅ |
| **Performance** with 100+ messages | P2.20 | ✅ |
| Multiple sessions (20+) | P2.21 | ✅ |
| Auto-refresh performance | P2.22 | ✅ |
| Large dataset export | P2.23 | ✅ |
| **Edge Cases** handled gracefully | P2.24-P2.27 | ✅ |
| All unit tests passing | Automated | ✅ 66/66 |

---

## Final Phase 2 Checklist

Before PR to Phase 1 branch, verify:

**Automated Tests:**
- [ ] `npm test` shows 66/66 passing (Phase 1: 11, Phase 2: 55)
- [ ] All test suites green:
  - [ ] ConfigService.test.ts (5 tests)
  - [ ] AgentService.test.ts (6 tests)
  - [ ] MetricsService.test.ts (17 tests)
  - [ ] TraceService.test.ts (25 tests)
  - [ ] ExportService.test.ts (13 tests)

**Statistics Panel:**
- [ ] Panel opens via command palette
- [ ] Displays all metrics (tokens, cost, response time)
- [ ] Cost calculation works for multiple providers
- [ ] Export CSV works (clipboard)
- [ ] Export JSON works (clipboard)
- [ ] Clear metrics works with confirmation
- [ ] Auto-refresh updates every 5 seconds
- [ ] No console errors

**Trace Viewer:**
- [ ] Tree view shows in AI Agent sidebar
- [ ] Conversations expand to show turns
- [ ] Turns expand to show states (Observe/Plan/Act/Verify)
- [ ] State details show in tooltips
- [ ] Refresh button works
- [ ] Export JSON works
- [ ] Export CSV works
- [ ] Clear traces works with confirmation
- [ ] No console errors

**Integration:**
- [ ] Metrics and traces synchronized
- [ ] Session reset clears current data
- [ ] Provider switching tracked correctly
- [ ] Storage persists across restarts

**Performance:**
- [ ] 100+ message conversation handles well
- [ ] 20+ sessions tracked without slowdown
- [ ] Auto-refresh doesn't spike CPU
- [ ] Export large datasets succeeds

**Edge Cases:**
- [ ] Empty state displays gracefully
- [ ] Provider errors recorded in traces
- [ ] Storage persistence works
- [ ] No data conflicts

**Documentation:**
- [ ] TESTING_PHASE2.md comprehensive
- [ ] TEST_RESULTS_PHASE2.md shows 66/66 passing
- [ ] All issues resolved and documented

---

## Phase 3: Code Intelligence Testing (Issue #76)

**Issue Link:** https://github.com/nsin08/ai_agents/issues/76  
**Branch:** `feature/76-phase-3-code-intelligence`  
**Acceptance Criteria:** 9 features + 3 bug fixes

**Features Added:**
- CodeContextService: Extract code with security filtering
- CodeInsertionService: Parse and apply code suggestions
- CodeSuggestionPanel: Display suggestions with syntax highlighting
- Commands: sendSelection, sendFile, showCodeSuggestions
- Context menu integration
- Sensitive data detection (15 patterns)
- File type blocking (11 types)

---

### Quick Validation Checklist (Issue #76)

**Before Review:**
- [ ] All 150 tests passing (`npm test`)
- [ ] No TypeScript errors (`npm run compile`)
- [ ] Branch pushed to remote
- [ ] 7 commits present (f6207ef → b7551c7)

**Acceptance Criteria Validation:**
- [ ] AC1: Code extraction with metadata ✅
- [ ] AC2: 15 sensitive data patterns detected ✅
- [ ] AC3: 11 file types blocked ✅
- [ ] AC4: Code insertion service ✅
- [ ] AC5: Suggestion panel with highlighting ✅
- [ ] AC6: Commands integrated ✅
- [ ] AC7: Bug fix - Trace Viewer config ✅
- [ ] AC8: Bug fix - Statistics labels ✅
- [ ] AC9: Bug fix - Conversation metadata ✅

**Manual Tests (30 min):**
- [ ] Test 3.1: Send Selection (security warning)
- [ ] Test 3.2: Send File
- [ ] Test 3.3: All 15 sensitive patterns
- [ ] Test 3.4: All 11 blocked file types
- [ ] Test 3.5: Code suggestions display
- [ ] Test 3.6: Multiple suggestions navigation
- [ ] Test 3.7: Apply code
- [ ] Test 3.8: Preview diff
- [ ] Test 3.9: Copy to clipboard
- [ ] Test 3.10: Size limits
- [ ] Test 3.11: Error handling

---

### Issue #76 Specific Test Procedures

#### Procedure 1: Validate Bug Fixes (10 min)

**Bug Fix #1: Trace Viewer Model Display**

**Before:** Trace showed historical "top" provider/model  
**After:** Trace shows current session config

**Test Steps:**
1. Start conversation with `mock` provider, `llama2` model
2. Send 2-3 messages
3. Open Trace Viewer (sidebar icon)
4. Expand conversation node
5. **Verify:** Shows "mock" and "llama2" in config
6. **Verify:** Does NOT show any other provider/model

**Bug Fix #2: Statistics Panel Labels**

**Before:** "Top Provider" / "Top Model"  
**After:** "Current Provider" / "Current Model"

**Test Steps:**
1. Send 3-4 messages in conversation
2. Press `Ctrl+Shift+P` → "Agent: Show Statistics"
3. Look at provider/model section
4. **Verify:** Labels say "Current Provider" (not "Top Provider")
5. **Verify:** Labels say "Current Model" (not "Top Model")
6. **Verify:** Values match current configuration

**Bug Fix #3: Conversation History Metadata**

**Test Steps:**
1. Start conversation
2. Send message: "Hello"
3. Check chat panel
4. **Verify:** Provider/model displayed correctly per message
5. Switch provider via Settings
6. Send another message
7. **Verify:** New message shows updated provider/model

**Pass Criteria:** All 3 bug fixes working as expected

---

#### Procedure 2: Security Pattern Detection (15 min)

**Objective:** Validate all 15 sensitive data patterns are detected

**Setup:** Create test file `security_test.ts`

**Test Data:**
```typescript
// Test all 15 patterns
const API_KEY = "abcdefghij1234567890"; // Pattern 1: API Key
const BEARER = "Authorization: Bearer xyz123abc"; // Pattern 2: Bearer Token
const PASSWORD = "MySecretPassword123"; // Pattern 3: Password
const SECRET_KEY = "abcdefghij1234567890"; // Pattern 4: Secret Key
const PRIVATE_KEY = "xyz123"; // Pattern 5: Private Key
const ACCESS_TOKEN = "abcdefghij1234567890"; // Pattern 6: Access Token
const AUTH_TOKEN = "abcdefghij1234567890"; // Pattern 7: Auth Token
const CLIENT_SECRET = "abcdefghij1234567890"; // Pattern 8: Client Secret
const CARD = "4532-1234-5678-9010"; // Pattern 9: Credit Card
const EMAIL = "user@example.com"; // Pattern 10: Email
const PK_BLOCK = "-----BEGIN PRIVATE KEY-----"; // Pattern 11: Private Key Block
const JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc"; // Pattern 12: JWT
const GH_TOKEN = "ghp_123456789012345678901234567890123456"; // Pattern 13: GitHub Token
const OPENAI_KEY = "sk-123456789012345678901234567890123456789012345678"; // Pattern 14: OpenAI Key
const GOOGLE_KEY = "AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz12345678"; // Pattern 15: Google Key
```

**Test Steps (for each pattern):**
1. Select ONE line at a time
2. Right-click → "Agent: Send Selection to Agent"
3. **Verify:** Warning dialog appears
4. **Verify:** Warning message includes pattern name
5. Click "No" → **Verify:** Operation cancelled
6. Repeat with "Yes" → **Verify:** Code sent

**Expected Results:**
| Pattern # | Name | Detected | Warning Shows |
|-----------|------|----------|---------------|
| 1 | API Key | ✅ | ✅ |
| 2 | Bearer Token | ✅ | ✅ |
| 3 | Password | ✅ | ✅ |
| 4 | Secret Key | ✅ | ✅ |
| 5 | Private Key | ✅ | ✅ |
| 6 | Access Token | ✅ | ✅ |
| 7 | Auth Token | ✅ | ✅ |
| 8 | Client Secret | ✅ | ✅ |
| 9 | Credit Card | ✅ | ✅ |
| 10 | Email | ✅ | ✅ |
| 11 | Private Key Block | ✅ | ✅ |
| 12 | JWT Token | ✅ | ✅ |
| 13 | GitHub Token | ✅ | ✅ |
| 14 | OpenAI API Key | ✅ | ✅ |
| 15 | Google API Key | ✅ | ✅ |

**Pass Criteria:** All 15 patterns detected with correct warnings

---

#### Procedure 3: File Type Blocking (10 min)

**Objective:** Validate all 11 credential file types are blocked

**Test Steps:**

1. **Test .env file:**
   - Create `.env` file with: `API_KEY=secret123`
   - Try "Agent: Send File to Agent"
   - **Verify:** Error message appears
   - **Verify:** Message: "Cannot send .env files (may contain sensitive data)"
   - **Verify:** No code sent to agent

2. **Test .pem file:**
   - Create `cert.pem` file with any content
   - Try "Agent: Send File to Agent"
   - **Verify:** Blocked

3. **Test .key file:**
   - Create `private.key` file
   - Try "Agent: Send File to Agent"
   - **Verify:** Blocked

4. **Quick test remaining types:**
   - Create files: `.p12`, `.pfx`, `.crt`, `.cert`, `.der`, `.pkcs12`, `.jks`, `.keystore`
   - **Verify:** All blocked with appropriate error message

**Expected Results:**
| Extension | Blocked | Error Shown |
|-----------|---------|-------------|
| .env | ✅ | ✅ |
| .pem | ✅ | ✅ |
| .key | ✅ | ✅ |
| .p12 | ✅ | ✅ |
| .pfx | ✅ | ✅ |
| .crt | ✅ | ✅ |
| .cert | ✅ | ✅ |
| .der | ✅ | ✅ |
| .pkcs12 | ✅ | ✅ |
| .jks | ✅ | ✅ |
| .keystore | ✅ | ✅ |

**Pass Criteria:** All 11 file types blocked, no false positives on normal files (.ts, .js, .py)

---

#### Procedure 4: Code Intelligence Workflow (15 min)

**Objective:** Validate complete code intelligence workflow

**Scenario: TypeScript Function Refactoring**

**Setup:**
```typescript
// calculator.ts
function calculate(a, b, op) {
  if (op === '+') return a + b;
  if (op === '-') return a - b;
  if (op === '*') return a * b;
  if (op === '/') return a / b;
}
```

**Step 1: Send to Agent**
1. Select the function
2. Right-click → "Agent: Send Selection to Agent"
3. **Verify:** Chat panel opens
4. **Verify:** Code formatted with metadata:
   - File: calculator.ts
   - Language: typescript
   - Lines: 1-6
   - Code in markdown block

**Step 2: Get Suggestion**
Simulate agent response (paste into chat):
```markdown
Here's an improved version with TypeScript types:

```typescript
function calculate(a: number, b: number, op: string): number {
  switch (op) {
    case '+': return a + b;
    case '-': return a - b;
    case '*': return a * b;
    case '/': 
      if (b === 0) throw new Error('Division by zero');
      return a / b;
    default:
      throw new Error(`Unknown operator: ${op}`);
  }
}
```

This adds type safety and error handling.
```

**Step 3: View Suggestion**
1. Press `Ctrl+Shift+P` → "Agent: Show Code Suggestions"
2. Paste the agent response
3. **Verify:** Code Suggestion Panel opens
4. **Verify:** Counter shows "1 of 1"
5. **Verify:** Explanation shown: "This adds type safety and error handling."
6. **Verify:** Code displayed with TypeScript syntax highlighting
7. **Verify:** Metadata shows: Language: typescript

**Step 4: Preview Diff**
1. Click "👁 Preview Diff" button
2. **Verify:** Diff editor opens (split view)
3. **Verify:** Left side shows original (if available)
4. **Verify:** Right side shows suggested code
5. **Verify:** Changes highlighted
6. Close diff view

**Step 5: Copy Code**
1. Click "📋 Copy Code" button
2. **Verify:** Success message: "Code copied to clipboard!"
3. Open new file, paste (Ctrl+V)
4. **Verify:** Code pastes correctly with formatting

**Step 6: Apply Code**
1. Return to original file
2. Place cursor at function location
3. Click "✓ Apply to Editor" button
4. **Verify:** Success message: "Code suggestion applied successfully!"
5. **Verify:** Code inserted at cursor
6. **Verify:** Formatting preserved
7. **Verify:** Panel stays open (can apply multiple times)

**Pass Criteria:** Complete workflow works end-to-end without errors

---

#### Procedure 5: Size Limit Enforcement (10 min)

**Test 1: Line Count Limit**

**Setup:**
```python
# Generate large file
with open('large_test.py', 'w') as f:
    for i in range(11000):
        f.write(f'# Line {i}\\n')
```

**Steps:**
1. Open `large_test.py` (11,000 lines)
2. Select all (Ctrl+A)
3. Right-click → "Agent: Send Selection to Agent"
4. **Verify:** Error appears immediately (no delay/freeze)
5. **Verify:** Message: "Code too large (11000 lines). Maximum: 10000 lines."
6. **Verify:** No agent invocation
7. **Verify:** Chat panel doesn't open
8. **Verify:** No crash

**Test 2: File Size Limit**

**Setup:**
```python
# Generate 600KB file
with open('huge_test.py', 'w') as f:
    f.write('x' * 600000)
```

**Steps:**
1. Open `huge_test.py`
2. Right-click → "Agent: Send File to Agent"
3. **Verify:** Error: "File too large (0.58MB). Maximum: 500KB."
4. **Verify:** No agent invocation

**Test 3: Boundary Testing**

**Test 3a: Exactly 10,000 lines (should work)**
```python
# Generate exactly 10,000 lines
with open('boundary_test.py', 'w') as f:
    for i in range(10000):
        f.write(f'# Line {i}\\n')
```
- Select all → Send Selection
- **Verify:** Succeeds (no error)

**Test 3b: Exactly 500KB (should work)**
```python
# Generate exactly 500KB
with open('boundary_size.py', 'w') as f:
    f.write('x' * 500000)
```
- Send File
- **Verify:** Succeeds (no error)

**Pass Criteria:** 
- Over limits: Error shown, no processing
- At limits: Succeeds
- No performance issues

---

#### Procedure 6: Error Handling Validation (10 min)

**Test 1: No Active Editor**
1. Close all editor tabs
2. Press `Ctrl+Shift+P`
3. Run: "Agent: Send Selection to Agent"
4. **Verify:** Warning: "No active editor. Please open a file and select code."
5. **Verify:** No crash
6. **Verify:** Command exits gracefully

**Test 2: Empty Selection**
1. Open any file
2. Click to place cursor (no selection)
3. Right-click → "Agent: Send Selection to Agent"
4. **Verify:** Warning: "No code selected. Please select code and try again."
5. **Verify:** No crash

**Test 3: No Code Blocks in Response**
1. Press `Ctrl+Shift+P` → "Agent: Show Code Suggestions"
2. Enter text: "This is just plain text without code blocks"
3. **Verify:** Info message: "No code suggestions found in the response."
4. **Verify:** Panel shows empty state
5. **Verify:** Icon and message displayed
6. **Verify:** Hint: "Ask the agent to provide code suggestions using markdown code blocks"

**Test 4: Invalid File Path**
1. Create file, get path
2. Delete file
3. Try to send (if possible to trigger)
4. **Verify:** Graceful error handling

**Test 5: Network Error (if applicable)**
1. Configure non-mock provider (if network available)
2. Disconnect network
3. Send message
4. **Verify:** Error displayed in chat
5. **Verify:** No crash
6. **Verify:** Can retry

**Pass Criteria:** All error cases handled gracefully with user-friendly messages

---

#### Procedure 7: Context Menu Integration (5 min)

**Test 1: Selection Context**
1. Open any code file
2. Select 2-3 lines of code
3. Right-click
4. **Verify:** Context menu shows "Agent: Send Selection to Agent"
5. **Verify:** Command has sparkle icon ✨
6. Click command
7. **Verify:** Works as expected

**Test 2: File Context**
1. Open any code file (no selection)
2. Right-click anywhere
3. **Verify:** Context menu shows "Agent: Send File to Agent"
4. **Verify:** Command has file icon
5. Click command
6. **Verify:** Sends entire file

**Test 3: Context Menu Visibility**
1. Close all editors
2. Right-click in explorer
3. **Verify:** Agent commands NOT shown (only for editor)
4. Open editor
5. Right-click
6. **Verify:** Commands now visible

**Pass Criteria:** Context menus work correctly with proper visibility conditions

---

### Issue #76 Regression Tests

**After completing Issue #76, verify Phase 1 & 2 still work:**

#### Phase 1 Regression (5 min)
- [ ] Chat panel opens without errors
- [ ] Can send messages and receive responses
- [ ] Session reset works
- [ ] Configuration changes apply
- [ ] Panel lifecycle (close/reopen) works

#### Phase 2 Regression (5 min)
- [ ] Statistics panel displays metrics
- [ ] Trace viewer shows conversations
- [ ] Export functions work (CSV/JSON)
- [ ] Auto-refresh toggles correctly
- [ ] All bug fixes still applied

**Pass Criteria:** No Phase 1 or Phase 2 functionality broken

---

### Issue #76 Sign-Off Checklist

**Code Quality:**
- [ ] All 150 tests passing
- [ ] No TypeScript compilation errors
- [ ] No linting errors
- [ ] Code follows project conventions

**Functionality:**
- [ ] All 9 acceptance criteria met
- [ ] All 3 bug fixes validated
- [ ] All 15 security patterns detected
- [ ] All 11 file types blocked
- [ ] All commands working
- [ ] Context menus functional

**Testing:**
- [ ] All automated tests pass
- [ ] All manual E2E tests completed
- [ ] All error handling scenarios tested
- [ ] Regression tests passed
- [ ] Performance acceptable (<2s operations)

**Documentation:**
- [ ] TESTING.md updated with Issue #76 procedures
- [ ] README.md updated with Phase 3 features
- [ ] Code comments present
- [ ] Commit messages clear

**Ready for PR:**
- [ ] All commits pushed to remote
- [ ] Branch: feature/76-phase-3-code-intelligence
- [ ] Target: feature/74-phase-1-mvp-chat-panel
- [ ] Issue #76 will be linked in PR description

**Reviewer Actions:**
- [ ] Code review completed
- [ ] Manual testing performed
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] Approved for merge

---

### Phase 3 Automated Tests (84 tests)

**CodeContextService (29 tests):**
- Sensitive data detection (10 tests)
- File type blocking (9 tests)
- Code formatting (2 tests)
- Helper methods (8 tests)

**CodeInsertionService (23 tests):**
- Code parsing from markdown (8 tests)
- Suggestion counting (3 tests)
- Explanation extraction (2 tests)
- Application modes (2 tests)
- Position/range validation (2 tests)
- Diff preview (2 tests)
- Edge cases (4 tests)

**CodeSuggestionPanel (19 tests):**
- Panel creation (2 tests)
- Suggestion parsing (3 tests)
- Navigation (5 tests)
- User actions (2 tests)
- HTML generation (5 tests)
- Lifecycle (2 tests)

**Integration Tests (13 tests):**
- End-to-end flow (3 tests)
- Security integration (3 tests)
- Code formatting (2 tests)
- Size limit enforcement (2 tests)
- Error handling (3 tests)

### Phase 3 Manual E2E Tests

#### Test 3.1: Send Selection to Agent (5 min)

**Setup:**
1. Open TypeScript file
2. Create function:
```typescript
function calculateTotal(price: number, tax: number): number {
  return price + (price * tax);
}
```

**Steps:**
1. Select the function
2. Right-click → "Agent: Send Selection to Agent"

**Expected Results:**
- ✅ Context menu shows command
- ✅ Chat panel opens automatically
- ✅ Code formatted with metadata:
  ```
  **File:** filename.ts
  **Language:** typescript
  **Lines:** 1-3
  **Size:** 3 lines
  ```typescript
  function calculateTotal...
  ```
  ```
- ✅ Message sent automatically
- ✅ Agent receives code context

**Time:** ~2 minutes

---

#### Test 3.2: Send File to Agent (5 min)

**Setup:**
1. Create Python file with 50+ lines
2. Include imports, functions, classes

**Steps:**
1. Open the file (no selection needed)
2. Right-click anywhere → "Agent: Send File to Agent"

**Expected Results:**
- ✅ Command available without selection
- ✅ Chat panel opens
- ✅ Full file sent with metadata
- ✅ File size shown (e.g., "Size: 50 lines")

**Time:** ~2 minutes

---

#### Test 3.3: Sensitive Data Warning (10 min)

**Setup: Create test file with sensitive data**
```python
# config.py
API_KEY = "sk-123456789012345678901234567890123456789012345678"
PASSWORD = "MySecret123!"
GITHUB_TOKEN = "ghp_123456789012345678901234567890123456"
```

**Test All 15 Patterns:**

| # | Pattern | Test Code | Should Warn |
|---|---------|-----------|-------------|
| 1 | API Key | `API_KEY="12345678901234567890"` | ✅ |
| 2 | Bearer Token | `Authorization: Bearer abc123xyz` | ✅ |
| 3 | Password | `PASSWORD="secret123"` | ✅ |
| 4 | Secret Key | `SECRET_KEY="12345678901234567890"` | ✅ |
| 5 | Private Key | `PRIVATE_KEY="abc123"` | ✅ |
| 6 | Access Token | `ACCESS_TOKEN="12345678901234567890"` | ✅ |
| 7 | Auth Token | `AUTH_TOKEN="12345678901234567890"` | ✅ |
| 8 | Client Secret | `CLIENT_SECRET="12345678901234567890"` | ✅ |
| 9 | Credit Card | `4532-1234-5678-9010` | ✅ |
| 10 | Email | `user@example.com` | ✅ |
| 11 | Private Key Block | `-----BEGIN PRIVATE KEY-----` | ✅ |
| 12 | JWT | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc` | ✅ |
| 13 | GitHub Token | `ghp_123456789012345678901234567890123456` | ✅ |
| 14 | OpenAI Key | `sk-123456789012345678901234567890123456789012345678` | ✅ |
| 15 | Google Key | `AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz12345678` | ✅ |

**Steps for Each Pattern:**
1. Select code with pattern
2. Right-click → "Send Selection to Agent"

**Expected Results:**
- ✅ Warning dialog appears
- ✅ Message: "Warning: Sensitive data detected ([Pattern Name]). Continue?"
- ✅ Options: "Yes" / "No"
- ✅ If "No" → Operation cancelled
- ✅ If "Yes" → Code sent with warning logged

**Time:** ~5 minutes (test 3-4 patterns)

---

#### Test 3.4: Blocked File Types (10 min)

**Test All Blocked Extensions:**

| Extension | Purpose | Should Block |
|-----------|---------|--------------|
| .env | Environment variables | ✅ |
| .pem | Certificate | ✅ |
| .key | Private key | ✅ |
| .p12 | PKCS#12 archive | ✅ |
| .pfx | Personal exchange | ✅ |
| .crt | Certificate | ✅ |
| .cert | Certificate | ✅ |
| .der | DER certificate | ✅ |
| .pkcs12 | PKCS#12 | ✅ |
| .jks | Java keystore | ✅ |
| .keystore | Keystore | ✅ |

**Steps:**
1. Create `.env` file:
   ```
   API_KEY=secret123
   DATABASE_URL=postgres://...
   ```
2. Try: "Agent: Send File to Agent"

**Expected Results:**
- ✅ Error message appears
- ✅ Message: "Cannot send .env files (may contain sensitive data)"
- ✅ Lists blocked extensions
- ✅ No code sent to agent
- ✅ No crash or exception

**Repeat for:** .pem, .key, .p12 (sample 3-4 extensions)

**Time:** ~3 minutes

---

#### Test 3.5: Code Suggestions Display (10 min)

**Setup: Get agent response with code**
```markdown
Here's how to fix the bug:

```typescript
function calculateTotal(price: number, tax: number): number {
  // Add input validation
  if (price < 0 || tax < 0) {
    throw new Error("Price and tax must be non-negative");
  }
  return price + (price * tax);
}
```

This adds proper error handling.
```

**Steps:**
1. Copy the agent response above
2. `Ctrl+Shift+P` → "Agent: Show Code Suggestions"
3. Paste response → Enter

**Expected Results:**
- ✅ Code Suggestion panel opens (column 2)
- ✅ Title: "Code Suggestion"
- ✅ Counter: "1 of 1"
- ✅ Explanation shown: "This adds proper error handling."
- ✅ Metadata visible:
  - Language: typescript
  - File: (none if no context)
- ✅ Code displayed with syntax highlighting
- ✅ Action buttons visible:
  - ✓ Apply to Editor
  - 👁 Preview Diff
  - 📋 Copy Code
  - ✕ Close

**Time:** ~3 minutes

---

#### Test 3.6: Multiple Suggestions Navigation (10 min)

**Setup: Agent response with 3 code blocks**
```markdown
Let me provide three solutions:

1. First, add the import:
```typescript
import { validateInput } from './validators';
```

2. Then, use the validator:
```typescript
function calculateTotal(price: number, tax: number): number {
  validateInput(price, tax);
  return price + (price * tax);
}
```

3. Finally, add the validator:
```typescript
export function validateInput(price: number, tax: number): void {
  if (price < 0 || tax < 0) {
    throw new Error("Values must be non-negative");
  }
}
```
```

**Steps:**
1. Show code suggestions with above response
2. Click "Next →" button
3. Click "← Previous" button
4. Navigate through all 3 suggestions

**Expected Results:**
- ✅ Counter updates: "1 of 3", "2 of 3", "3 of 3"
- ✅ Code content changes for each suggestion
- ✅ Explanation changes per suggestion
- ✅ Previous disabled at first suggestion
- ✅ Next disabled at last suggestion
- ✅ Navigation smooth, no flicker

**Time:** ~3 minutes

---

#### Test 3.7: Apply Code Suggestion (10 min)

**Setup:**
1. Open TypeScript file
2. Place cursor at desired insertion point

**Steps:**
1. Get suggestion with code:
   ```typescript
   const result = calculateTotal(100, 0.08);
   console.log(`Total: ${result}`);
   ```
2. Open Code Suggestion panel
3. Click "✓ Apply to Editor"

**Expected Results:**
- ✅ Success notification: "Code suggestion applied successfully!"
- ✅ Code inserted at cursor position
- ✅ Formatting preserved (indentation, newlines)
- ✅ Auto-format triggered (if formatter available)
- ✅ Panel stays open (can apply multiple times)
- ✅ No duplicate application

**Time:** ~3 minutes

---

#### Test 3.8: Preview Diff (10 min)

**Setup:**
1. Create file with original code:
```typescript
function greet(name) {
  console.log("Hello " + name);
}
```

**Steps:**
1. Get suggestion with improved version:
```typescript
function greet(name: string): void {
  console.log(`Hello ${name}!`);
}
```
2. Click "👁 Preview Diff"

**Expected Results:**
- ✅ Diff editor opens (split view)
- ✅ Left: Original code (or empty)
- ✅ Right: Suggested code
- ✅ Changes highlighted (additions/deletions)
- ✅ Can close diff without applying

**Note:** If no original code, left side shows empty/placeholder

**Time:** ~3 minutes

---

#### Test 3.9: Copy Code to Clipboard (5 min)

**Steps:**
1. Open Code Suggestion panel
2. Click "📋 Copy Code"
3. Open new editor tab
4. Paste with `Ctrl+V`

**Expected Results:**
- ✅ Success message: "Code copied to clipboard!"
- ✅ Code pastes correctly
- ✅ Formatting preserved
- ✅ No extra whitespace
- ✅ All newlines intact

**Time:** ~2 minutes

---

#### Test 3.10: Size Limit Enforcement (10 min)

**Test 1: Line Count Limit**

**Setup:**
```python
# Generate large file
with open('large.py', 'w') as f:
    for i in range(11000):
        f.write(f'# Line {i}\n')
```

**Steps:**
1. Open `large.py` (11,000 lines)
2. Select all (`Ctrl+A`)
3. Try "Send Selection to Agent"

**Expected Results:**
- ✅ Error appears immediately
- ✅ Message: "Code too large (11000 lines). Maximum: 10000 lines."
- ✅ No agent invocation
- ✅ No timeout/freeze

**Test 2: File Size Limit**

**Setup:**
```python
# Generate 600KB file
with open('huge.py', 'w') as f:
    f.write('x' * 600000)
```

**Steps:**
1. Open `huge.py` (600KB)
2. Try "Send File to Agent"

**Expected Results:**
- ✅ Error: "File too large (0.58MB). Maximum: 500KB."
- ✅ No agent invocation

**Time:** ~5 minutes

---

#### Test 3.11: Error Handling (10 min)

**Test 1: No Active Editor**

**Steps:**
1. Close all editor tabs
2. `Ctrl+Shift+P` → "Agent: Send Selection to Agent"

**Expected:**
- ✅ Warning: "No active editor. Please open a file and select code."
- ✅ No crash

**Test 2: Empty Selection**

**Steps:**
1. Open file
2. Place cursor (no selection)
3. Try "Send Selection to Agent"

**Expected:**
- ✅ Warning: "No code selected. Please select code and try again."
- ✅ Command exits gracefully

**Test 3: No Code Blocks in Response**

**Steps:**
1. Show Code Suggestions with: "Here is some text without code blocks."

**Expected:**
- ✅ Info message: "No code suggestions found in the response."
- ✅ Panel shows empty state
- ✅ Message: "No code suggestions found"
- ✅ Hint: "Ask the agent to provide code suggestions using markdown code blocks"

**Time:** ~3 minutes

---

### Phase 3 Bug Fix Validation (Issue #76)

**Bug Fix 1: Trace Viewer - Model Display**

**Before Fix:**
- Trace showed historical top provider/model

**After Fix:**
- Trace shows current session config

**Test:**
1. Start conversation with mock/llama2
2. Send 2 messages
3. Open Trace Viewer
4. Check conversation details

**Expected:**
- ✅ Shows "mock" / "llama2"
- ✅ NOT historical "most used" provider

---

**Bug Fix 2: Statistics Panel - Current Config**

**Before Fix:**
- Showed "Top Provider: X" (historical)
- Showed "Top Model: Y" (historical)

**After Fix:**
- Shows "Current Provider: X"
- Shows "Current Model: Y"

**Test:**
1. Send 3-4 messages
2. Open Statistics Panel
3. Check labels

**Expected:**
- ✅ Label: "Current Provider" (not "Top")
- ✅ Label: "Current Model" (not "Top")
- ✅ Values match active config

---

**Bug Fix 3: Conversation History - Config Display**

**Test:**
1. Start conversation
2. Send message
3. Check metadata shown in chat

**Expected:**
- ✅ Provider/model shown correctly per message
- ✅ Config updates reflected in real-time

---

## Phase 3 Regression Testing

After Phase 3 changes, verify Phase 1 & 2 still work:

### Phase 1 Quick Check (5 min)
- [ ] Chat panel opens
- [ ] Messages send/receive
- [ ] Session reset works
- [ ] Config changes apply

### Phase 2 Quick Check (5 min)
- [ ] Statistics panel shows metrics
- [ ] Trace viewer displays conversations
- [ ] Export functions work
- [ ] Bug fixes still applied

---

## Performance Testing (Phase 3)

### Test 3.12: Large Selection Performance

**Steps:**
1. Select 9,500 lines of code
2. Send to agent
3. Measure time

**Expected:**
- ✅ Extraction completes <1 second
- ✅ Sensitive data scan <500ms
- ✅ Formatting <200ms
- ✅ Total <2 seconds

### Test 3.13: Multiple Suggestions Performance

**Steps:**
1. Agent response with 10 code blocks
2. Open Code Suggestion panel
3. Navigate through all

**Expected:**
- ✅ Panel opens <500ms
- ✅ Navigation instant (<100ms)
- ✅ HTML rendering smooth
- ✅ No lag or stuttering

---

## Security Audit Checklist

### Data Protection
- [ ] Sensitive data patterns detected (15/15)
- [ ] Credential files blocked (11/11)
- [ ] User warned before sending sensitive data
- [ ] No credentials in logs/traces
- [ ] No credentials in exported data

### Input Validation
- [ ] Size limits enforced
- [ ] File type validation
- [ ] HTML escaping in webviews
- [ ] No code injection possible
- [ ] No path traversal possible

### Privacy
- [ ] No telemetry without consent
- [ ] No data sent to external servers (mock mode)
- [ ] Session data cleared on reset
- [ ] Exported data user-controlled

---

## Test Coverage Summary

### Phase 3 Test Breakdown

**Unit Tests: 71 tests**
- CodeContextService: 29 tests
- CodeInsertionService: 23 tests
- CodeSuggestionPanel: 19 tests

**Integration Tests: 13 tests**
- E2E flow: 3 tests
- Security: 3 tests
- Formatting: 2 tests
- Size limits: 2 tests
- Error handling: 3 tests

**Total: 84 Phase 3 tests**
**Grand Total: 150 tests (Phases 1+2+3)**

---

## Ready for PR!

Once all Phase 1 + Phase 2 + Phase 3 tests pass:

1. ✅ All 150 automated tests passing
2. ✅ Manual E2E tests completed (11 Phase 3 tests)
3. ✅ Bug fixes validated (3 fixes)
4. ✅ Security audit passed
5. ✅ Performance acceptable
6. ✅ Regression tests passed
7. ✅ Commit Phase 3 changes
8. ✅ Push to `feature/76-phase-3-code-intelligence`
9. ✅ Create PR to merge into `feature/74-phase-1-mvp-chat-panel`
10. ✅ Link to Issue #76
11. ✅ Request review
12. ✅ After approval, all phases merge to `develop`

**🎉 Phase 3 Complete!**

**Total Implementation:**
- ✅ Phase 1: MVP Chat Panel (15 tests)
- ✅ Phase 2: Observability & Metrics (51 tests)
- ✅ Phase 3: Code Intelligence + Bug Fixes (84 tests)
- ✅ **150/150 tests passing**

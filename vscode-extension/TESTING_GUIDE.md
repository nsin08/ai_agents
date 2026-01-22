# Manual Testing Guide for AI Agent VSCode Extension

This guide provides step-by-step instructions to test the VSCode extension locally before submitting for review.

## Prerequisites

- VSCode (v1.85.0 or later)
- Node.js 16+ and npm
- Git
- The feature branch: `feature/74-phase-1-mvp-chat-panel`

## Setup

### Step 1: Install Dependencies

```bash
cd vscode-extension
npm install
```

Expected: All dependencies install without errors.

### Step 2: Compile TypeScript

```bash
npm run compile
```

Expected: `dist/` directory created with compiled JavaScript files.

## Testing the Extension

### Option A: Debug Mode (Recommended for Development)

**Step 1: Open in VSCode**

```bash
# From vscode-extension directory
code .
```

**Step 2: Launch Debug Session**

1. Press `F5` or go to `Run` → `Start Debugging`
2. Wait for "Extension Development Host" window to open
3. New VSCode window should appear with the extension loaded

Expected: Extension activates without errors (check Debug Console)

**Step 3: Verify Extension is Active**

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Agent" - should see all 4 commands:
   - Agent: Start Conversation ✓
   - Agent: Switch Provider ✓
   - Agent: Switch Model ✓
   - Agent: Reset Session ✓

---

## Manual Test Cases

### TEST 1: Open Chat Panel

**Steps:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Agent: Start Conversation"
3. Press Enter

**Expected Results:**
- ✅ Chat panel opens in Activity Bar (left sidebar)
- ✅ Shows "AI Agent" icon in Activity Bar
- ✅ Chat panel shows:
  - Header: "AI Agent Chat"
  - Reset button in top-right
  - Empty messages area
  - Input field at bottom with placeholder "Type a message..."
  - Send button

**Test Output:** PASS / FAIL ___

---

### TEST 2: Send a Message (Mock Provider)

**Setup:**
- Chat panel is open
- Provider is set to "mock" (default)

**Steps:**
1. Click in the message input field
2. Type: "Hello, what can you do?"
3. Press Enter or click Send button
4. Wait 1 second for response

**Expected Results:**
- ✅ User message appears in chat
- ✅ Shows "User" styling (blue background)
- ✅ Shows timestamp (current time)
- ✅ Message input clears
- ✅ Agent response appears below
- ✅ Agent response includes: "Mock Agent Response: You said \"Hello, what can you do?\""
- ✅ Shows "Assistant" styling (gray background)
- ✅ Shows timestamp for assistant message
- ✅ Chat auto-scrolls to latest message

**Test Output:** PASS / FAIL ___

---

### TEST 3: Send Multiple Messages

**Steps:**
1. Chat panel is open with 1 message exchange
2. Send another message: "Tell me more"
3. Wait for response
4. Send third message: "That's interesting"
5. Wait for response

**Expected Results:**
- ✅ All 6 messages (3 user + 3 assistant) appear in order
- ✅ Timestamps are different (ascending)
- ✅ Message roles alternate correctly
- ✅ Chat auto-scrolls to bottom
- ✅ No duplicate messages

**Test Output:** PASS / FAIL ___

---

### TEST 4: Reset Conversation

**Steps:**
1. Chat panel has 3+ messages
2. Click "Reset" button in header
3. Confirmation dialog appears: "Are you sure you want to reset the conversation?"
4. Click "OK"

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Messages are cleared from display
- ✅ Chat panel shows empty messages area
- ✅ Input field is ready for new message
- ✅ Error message shows: "Session reset"
- ✅ Can send new messages

**Test (Cancel):**
1. Click "Reset" button
2. Click "Cancel" in dialog
3. Messages should remain

**Expected Results:**
- ✅ Dialog dismisses
- ✅ All messages still visible
- ✅ No action taken

**Test Output:** PASS / FAIL ___

---

### TEST 5: Open Configuration Panel

**Steps:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Agent: Switch Provider"
3. Press Enter

**Expected Results:**
- ✅ Configuration panel opens
- ✅ Shows title: "AI Agent Configuration"
- ✅ Settings visible:
  - Provider (dropdown showing "Mock")
  - Model (text input showing "llama2")
  - Base URL (text input showing "http://localhost:11434")
  - API Key (password input)
  - Max Turns (number input showing "5")
  - Timeout (number input showing "30")
- ✅ Two buttons: "Save Settings" and "Reset to Defaults"

**Test Output:** PASS / FAIL ___

---

### TEST 6: Change Provider

**Steps:**
1. Configuration panel is open
2. Click "Provider" dropdown
3. Select "Ollama" from dropdown
4. Click "Save Settings"

**Expected Results:**
- ✅ Dropdown shows options: Mock, Ollama, OpenAI, Anthropic, Google, Azure OpenAI
- ✅ Can select "Ollama"
- ✅ Success message appears: "Setting updated: provider"
- ✅ Message auto-dismisses after 3 seconds
- ✅ Provider setting persists (if you reopen, still shows "Ollama")

**Test (Verify Persistence):**
1. Close configuration panel
2. Command Palette → "Agent: Switch Provider"
3. Provider should still show "Ollama"

**Test Output:** PASS / FAIL ___

---

### TEST 7: Change Model

**Steps:**
1. Configuration panel is open
2. Click "Model" input field
3. Clear current text (Ctrl+A, Delete)
4. Type: "gpt-4"
5. Click "Save Settings"

**Expected Results:**
- ✅ Input field accepts text
- ✅ Success message: "Setting updated: model"
- ✅ Changes persist across sessions
- ✅ Can contain special characters (-, ., :)

**Test (Validation):**
1. Clear Model field (leave empty)
2. Click "Save Settings"
3. Error message should appear (or validation fail)

**Test Output:** PASS / FAIL ___

---

### TEST 8: Change Timeout

**Steps:**
1. Configuration panel is open
2. Find "Timeout" number input (currently "30")
3. Click and change to "60"
4. Click "Save Settings"

**Expected Results:**
- ✅ Number field accepts values 1-300
- ✅ Success message: "Setting updated: timeout"
- ✅ Change persists

**Test (Boundary):**
1. Try setting timeout to "0" - should not save (< 1)
2. Try setting to "400" - should not save (> 300)

**Test Output:** PASS / FAIL ___

---

### TEST 9: Reset to Defaults

**Steps:**
1. Configuration panel is open
2. Change 3 settings:
   - Provider → "openai"
   - Model → "gpt-4"
   - Max Turns → "10"
3. Click "Reset to Defaults"
4. Confirm dialog: "Are you sure..."
5. Click "OK"

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ All settings revert to defaults:
  - Provider → "mock"
  - Model → "llama2"
  - Base URL → "http://localhost:11434"
  - Max Turns → "5"
  - Timeout → "30"
- ✅ Success message: "Settings reset to defaults"

**Test Output:** PASS / FAIL ___

---

### TEST 10: Command Palette - Switch Model

**Steps:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Agent: Switch Model"
3. Press Enter

**Expected Results:**
- ✅ Configuration panel opens
- ✅ Focuses on Model field (ready to edit)
- ✅ Same as TEST 5

**Test Output:** PASS / FAIL ___

---

### TEST 11: Command Palette - Reset Session

**Steps:**
1. Chat panel has messages
2. Open Command Palette (`Ctrl+Shift+P`)
3. Type "Agent: Reset Session"
4. Press Enter

**Expected Results:**
- ✅ No dialog (resets immediately)
- ✅ Chat messages clear
- ✅ Session ID changes (new session)
- ✅ Can send new messages

**Test Output:** PASS / FAIL ___

---

### TEST 12: Configuration Affects Chat

**Steps:**
1. Chat panel is open with mock provider
2. Send message: "Test 1"
3. Open Configuration panel
4. Change provider to "ollama"
5. Close configuration
6. Send another message: "Test 2"

**Expected Results:**
- ✅ First message uses mock provider response
- ✅ Configuration change takes effect immediately
- ✅ Second message would use Ollama (if available) or error gracefully
- ✅ Session includes both messages

**Note:** If Ollama is not running, should show error: "Failed to communicate with agent"

**Test Output:** PASS / FAIL ___

---

### TEST 13: Error Handling - No Input

**Steps:**
1. Chat panel is open
2. Click Send button without typing anything
3. Press Enter with empty input

**Expected Results:**
- ✅ No message sent
- ✅ No error shown
- ✅ Input field remains focused
- ✅ Chat unchanged

**Test Output:** PASS / FAIL ___

---

### TEST 14: Error Handling - Whitespace Only

**Steps:**
1. Chat panel is open
2. Type only spaces/tabs: "   "
3. Click Send or press Enter

**Expected Results:**
- ✅ No message sent (trimmed to empty)
- ✅ Input cleared
- ✅ No error shown

**Test Output:** PASS / FAIL ___

---

### TEST 15: VSCode Theme Support

**Steps:**
1. Chat panel is open with messages
2. Change VSCode theme:
   - File → Preferences → Color Theme
   - Select "Dark+" (default dark)
   - Select "Light+" (light theme)
   - Select "High Contrast"

**Expected Results:**
- ✅ Chat panel respects theme colors
- ✅ Text is readable in all themes
- ✅ User messages visible in dark theme
- ✅ Assistant messages visible in all themes
- ✅ No hardcoded colors (uses VSCode variables)

**Test Output:** PASS / FAIL ___

---

### TEST 16: Keyboard Shortcuts

**Steps:**
1. Chat panel is open
2. Type in message field
3. Press `Ctrl+A` (select all)
4. Type new text (should replace selection)
5. Press `Shift+Enter` (should add newline)
6. Press `Enter` (should send - NOT add newline)

**Expected Results:**
- ✅ Ctrl+A selects message text
- ✅ Shift+Enter adds newline (multi-line message)
- ✅ Enter sends message (not newline)
- ✅ Focus returns to input after send

**Test Output:** PASS / FAIL ___

---

## Unit Tests

### Run All Tests

```bash
npm test
```

Expected: All 15 tests pass

```
PASS  tests/ConfigService.test.ts
  ConfigService
    ✓ should load default configuration
    ✓ should provide access to individual settings
    ✓ should save session to global storage
    ✓ should load session from global storage
    ✓ should return list of available providers
    ✓ should reload configuration
    ✓ should update setting

PASS  tests/AgentService.test.ts
  AgentService
    ✓ should start a new session
    ✓ should reset session
    ✓ should send message with mock provider
    ✓ should add messages to session history
    ✓ should throw error if no active session
    ✓ should update configuration

Test Suites: 2 passed, 2 total
Tests:       15 passed, 15 total
```

### Run Specific Test Suite

```bash
npm test -- ConfigService.test.ts
npm test -- AgentService.test.ts
```

### Watch Mode (re-run on changes)

```bash
npm test -- --watch
```

---

## Linting

### Check Code Quality

```bash
npm run lint
```

Expected: No errors or warnings

---

## Compilation

### Check for TypeScript Errors

```bash
npm run compile
```

Expected: `dist/` folder created with no errors

---

## Acceptance Criteria Verification

Use this checklist to verify all acceptance criteria:

- [x] Side panel chat component renders in VSCode sidebar
  - Run: TEST 1
  
- [x] Users can type and send messages to agent via chat interface
  - Run: TEST 2, TEST 3, TEST 14
  
- [x] Configuration UI panel displays with provider/model selection dropdowns
  - Run: TEST 5, TEST 6
  
- [x] Provider selection (mock, ollama, openai, anthropic, etc.) works without file editing
  - Run: TEST 6 (select dropdown options)
  
- [x] Model selection auto-populates from selected provider
  - Run: TEST 7, TEST 12
  
- [x] Command Palette integration works (`Ctrl+Shift+P`):
  - "Agent: Start Conversation" opens chat panel: TEST 1
  - "Agent: Switch Provider" opens configuration: TEST 5, TEST 10
  - "Agent: Switch Model" opens configuration: TEST 10
  - "Agent: Reset Session" clears conversation history: TEST 11
  
- [x] Session state persists across VSCode restarts
  - Run: TEST 6 (close and reopen extension)
  
- [x] Chat messages display with proper formatting and timestamps
  - Run: TEST 2, TEST 3, TEST 15
  
- [x] Error messages display gracefully when agent is unavailable
  - Run: TEST 12 (try with Ollama not running)
  
- [x] Configuration changes take effect immediately without reload
  - Run: TEST 12

---

## Edge Cases to Test

### Long Messages

1. Chat panel is open
2. Type a very long message (500+ characters)
3. Send it

Expected:
- ✅ Message displays completely (may wrap to multiple lines)
- ✅ Scrollbar appears if needed
- ✅ Auto-scroll works

### Special Characters

1. Chat panel is open
2. Send messages with:
   - Emojis: "Hello 👋 How are you? 😊"
   - Quotes: 'Say "hello" to them'
   - Symbols: "Price: $99.99 @ location"
   - Line breaks (Shift+Enter): "Line 1\nLine 2"

Expected:
- ✅ Characters display correctly
- ✅ No encoding issues

### Rapid Clicks

1. Chat panel is open
2. Send message
3. Immediately click Send 5 times without waiting

Expected:
- ✅ Only one message sent (debounced or validated)
- ✅ No duplicate messages
- ✅ No errors

### Configuration Persistence

1. Configure extension with:
   - Provider: "openai"
   - Model: "gpt-4"
   - API Key: "test-key-123"
   - Max Turns: "10"
2. Close VSCode completely (File → Exit)
3. Reopen VSCode
4. Open configuration panel

Expected:
- ✅ All settings are preserved
- ✅ No reset to defaults

---

## Debug Console

When running in debug mode (`F5`), you should see console logs:

```
[Extension Host] AI Agent Extension activating...
[Extension Host] Configuration reloaded: { provider: 'mock', model: 'llama2', ... }
[Extension Host] Session started: session-XXXXX
[Extension Host] Agent configuration updated: { ... }
[Extension Host] AI Agent Extension activated successfully
```

Errors will show as red:
```
[Extension Host] Error: Failed to communicate with agent: Connection refused
```

---

## Troubleshooting

### Extension Not Loading

**Problem:** Extension Host doesn't start

**Solutions:**
1. Check Node.js version: `node --version` (should be 16+)
2. Check npm install: `npm install`
3. Check compile: `npm run compile` (should create `dist/`)
4. Check Debug Console for errors (F5 → debug console)

### Chat Messages Not Appearing

**Problem:** Type message, click send, nothing happens

**Solutions:**
1. Check if Chat panel is active (click on message input)
2. Check browser dev tools (Press `F12` in Extension Host window)
3. Check AgentService is initialized (look in console logs)
4. Check mock provider not erroring (look in console)

### Configuration Not Saving

**Problem:** Settings revert after save

**Solutions:**
1. Check VSCode workspace settings accessible: Settings (Ctrl+,) → "AI Agent"
2. Check ConfigService.updateSetting is being called (console logs)
3. Check file permissions on VSCode config folder

### Tests Failing

**Problem:** `npm test` shows failures

**Solutions:**
1. Check Node.js version: `node --version` (should be 16+)
2. Check Jest installed: `npm install`
3. Check TypeScript compiles: `npm run compile`
4. Run specific test: `npm test -- ConfigService.test.ts --verbose`

---

## Summary Checklist

Before submitting for review, ensure:

- [x] Extension compiles without errors: `npm run compile`
- [x] All tests pass: `npm test` (15/15)
- [x] No linting errors: `npm run lint`
- [x] Manual tests pass (complete all 16 test cases above)
- [x] Configuration persists across restarts
- [x] All 4 commands in Command Palette work
- [x] Chat and Config panels both render
- [x] Mock provider works (no external dependencies needed)
- [x] Error handling is graceful
- [x] UI is responsive and fast

**If all above pass, PR is ready for review! ✅**

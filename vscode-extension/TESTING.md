# Testing Guide - AI Agent VSCode Extension

Complete guide for testing Story #74 - Phase 1 MVP implementation.

---

## Quick Start (5 Minutes)

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
Expected: ✅ 15/15 tests passing

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
2. Type: `Agent: Switch Provider`
3. Press Enter

**Expected:**
- ✅ Configuration panel opens
- ✅ Title: "AI Agent Configuration"
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

---

### Phase 5: Command Palette Testing (3 min)

**Test All 4 Commands:**

1. `Ctrl+Shift+P` → Type "Agent"
   
   **Expected: 4 commands appear:**
   - ✅ `Agent: Start Conversation` → Opens chat panel
   - ✅ `Agent: Switch Provider` → Opens config panel
   - ✅ `Agent: Switch Model` → Opens config panel
   - ✅ `Agent: Reset Session` → Clears chat (no dialog)

---

### Phase 6: Persistence Testing (3 min)

#### TEST 6.1: Configuration Persistence

**Step 1: Change Configuration**
1. Open config: `Ctrl+Shift+P` → `Agent: Switch Provider`
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
1. Open config: `Ctrl+Shift+P` → `Agent: Switch Provider`
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
- [ ] Agent: Switch Provider works
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
2. ✅ Changes committed: `git commit` (done)
3. ✅ Branch pushed: `git push` (done)
4. ✅ PR created: `gh pr create` (done)
5. ✅ Request review from CODEOWNER
6. ✅ Ready for merge!

**PR #77 is ready for review!**

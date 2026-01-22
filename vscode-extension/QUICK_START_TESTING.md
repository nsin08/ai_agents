# Quick Start Testing (5 Minutes)

## TL;DR - Fast Testing Path

### 1. Setup (2 min)
```bash
cd vscode-extension
npm install
npm run compile
```

### 2. Run Tests (1 min)
```bash
npm test
```
Should see: ✅ 15 passed

### 3. Run Extension (2 min)
```bash
code .
# Then press F5 to launch in debug mode
```

In the new VSCode window:
1. `Ctrl+Shift+P` → Type "Agent: Start Conversation" → Enter
2. Type message "Hello" → Press Enter
3. See mock response appear with timestamp

## Manual Testing Steps (Step by Step)

### Step 1: Install & Compile

```bash
cd /mnt/d/Study/AI/ai_agents/vscode-extension
npm install
npm run compile
```

✅ Expected: Both commands complete without errors

### Step 2: Run Unit Tests

```bash
npm test
```

✅ Expected Output:
```
PASS  tests/ConfigService.test.ts
PASS  tests/AgentService.test.ts
Tests: 15 passed, 15 total
```

### Step 3: Launch Debug Extension

```bash
code .
```

Press `F5` (or Run → Start Debugging)

✅ Expected: New VSCode window opens titled "Extension Development Host"

### Step 4: Test Chat Panel

In the Extension Development Host window:

**Open Chat Panel:**
1. Press `Ctrl+Shift+P`
2. Type: `Agent: Start Conversation`
3. Press Enter

✅ Expected:
- Chat panel opens in left sidebar
- Shows "AI Agent Chat" with Reset button
- Empty message area
- Input field with "Type a message..." placeholder

**Send a Message:**
1. Click in the message input field
2. Type: `Hello, what can you do?`
3. Press Enter (or click Send)

✅ Expected:
- Your message appears with blue styling and timestamp
- Agent response appears below: "Mock Agent Response: You said \"Hello, what can you do?\""
- Gray styling for agent message
- Both have timestamps

**Send Multiple Messages:**
1. Type: `Tell me more`
2. Press Enter
3. Type: `That's interesting`
4. Press Enter

✅ Expected:
- All 6 messages visible (3 user + 3 assistant)
- Proper alternating order
- Different timestamps for each

**Reset Conversation:**
1. Click "Reset" button (top right of chat panel)
2. Confirmation dialog appears: "Are you sure you want to reset the conversation?"
3. Click "OK"

✅ Expected:
- Messages disappear
- Chat cleared
- Can type new message

### Step 5: Test Configuration Panel

In the Extension Development Host window:

**Open Config Panel:**
1. Press `Ctrl+Shift+P`
2. Type: `Agent: Switch Provider`
3. Press Enter

✅ Expected:
- Configuration panel opens
- Shows all 6 settings:
  - Provider (dropdown) → "mock"
  - Model (text) → "llama2"
  - Base URL (text) → "http://localhost:11434"
  - API Key (password)
  - Max Turns (number) → "5"
  - Timeout (number) → "30"

**Change Provider:**
1. Click "Provider" dropdown
2. Select "Ollama"
3. Click "Save Settings"

✅ Expected:
- Green success message: "Setting updated: provider"
- Message disappears after 3 seconds
- Provider dropdown shows "Ollama"

**Change Model:**
1. Click "Model" field
2. Clear it (Ctrl+A, Delete)
3. Type: `gpt-4`
4. Click "Save Settings"

✅ Expected:
- Success message: "Setting updated: model"
- Model field shows "gpt-4"

**Reset to Defaults:**
1. Click "Reset to Defaults"
2. Confirmation dialog appears
3. Click "OK"

✅ Expected:
- All fields revert to defaults:
  - Provider → "mock"
  - Model → "llama2"
  - Max Turns → "5"
  - Timeout → "30"
- Success message: "Settings reset to defaults"

### Step 6: Test Command Palette Commands

In the Extension Development Host window:

**Test All Commands:**
```
Ctrl+Shift+P → "Agent: Start Conversation"      ✅ Opens chat panel
Ctrl+Shift+P → "Agent: Switch Provider"          ✅ Opens config panel
Ctrl+Shift+P → "Agent: Switch Model"             ✅ Opens config panel
Ctrl+Shift+P → "Agent: Reset Session"            ✅ Clears chat (no dialog)
```

### Step 7: Test Configuration Persistence

1. In Config panel, change:
   - Provider → "openai"
   - Model → "gpt-4"
   - Max Turns → "10"

2. Close Extension Development Host window (File → Exit)

3. Close original VSCode window (File → Exit)

4. Reopen VSCode:
   ```bash
   code .
   ```

5. Press F5 again

6. Open Config panel → `Ctrl+Shift+P` → "Agent: Switch Provider"

✅ Expected:
- All settings are still there:
  - Provider shows "openai" (NOT reverted to "mock")
  - Model shows "gpt-4"
  - Max Turns shows "10"

This proves **session persistence works!**

### Step 8: Test Keyboard Shortcuts

In Chat panel:

**Multi-line Message:**
1. Type: `Line 1`
2. Press `Shift+Enter` (adds newline)
3. Type: `Line 2`
4. Press `Enter` (sends entire message)

✅ Expected:
- Message displays on two lines
- Both lines appear in sent message

**Send with Enter:**
1. Type: `Quick message`
2. Press `Enter`

✅ Expected:
- Message sent immediately
- Input clears

### Step 9: Test Long Messages

In Chat panel:

1. Type a long message (500+ characters):
   ```
   This is a long message to test how the extension handles lengthy user input. 
   It should wrap to multiple lines without any issues and display properly in the chat interface. 
   The message should appear with proper formatting and timestamps. 
   Let's see if everything works as expected!
   ```

2. Press Enter

✅ Expected:
- Message wraps across multiple lines
- Fully visible in chat panel
- Scrollbar appears if needed
- Auto-scroll works

### Step 10: Test VSCode Theme Support

1. Open Settings: `Ctrl+,`
2. Search: "Color Theme"
3. Click "Color Theme"
4. Try different themes:
   - Dark+ (default dark)
   - Light+ (light)
   - High Contrast

✅ Expected for each theme:
- Chat panel adjusts colors
- Text is readable
- User messages visible
- Agent messages visible
- No hardcoded colors

---

## What to Look For ✅

**Success Indicators:**
- ✅ Extension loads without errors (check Debug Console)
- ✅ Chat panel renders with proper styling
- ✅ Messages display with user/assistant distinction
- ✅ Timestamps are different for each message
- ✅ Configuration panel has all 6 settings
- ✅ Dropdown works for provider selection
- ✅ All 4 commands appear in Command Palette
- ✅ Settings persist across VSCode restarts
- ✅ Error messages show gracefully
- ✅ Keyboard shortcuts work (Enter sends, Shift+Enter adds newline)

**Red Flags (Stop & Debug):**
- ❌ Extension Host fails to start
- ❌ Messages don't appear when sending
- ❌ Configuration doesn't save
- ❌ Commands not in Command Palette
- ❌ Chat panel styling broken
- ❌ Crashes on theme change

---

## Debug Console

While Extension Host is running, open Debug Console (Debug → Open Console):

Should see logs like:
```
[Extension Host] AI Agent Extension activating...
[Extension Host] Configuration reloaded: { provider: 'mock', model: 'llama2', ... }
[Extension Host] Session started: session-1234567890-abcdef123
[Extension Host] AI Agent Extension activated successfully
```

When you send a message:
```
[Extension Host] Session restored from storage: session-1234567890-abcdef123
```

**Errors will show in red:**
```
[Extension Host] Error: Failed to communicate with agent: Connection refused
```

---

## Stopping Debug Mode

1. Close Extension Development Host window
2. Press `Shift+F5` in original VSCode to stop debugging
3. Or close original VSCode window

---

## Final Checklist Before Review

- [ ] `npm install` runs successfully
- [ ] `npm run compile` creates `dist/` folder
- [ ] `npm test` shows 15/15 passing
- [ ] `npm run lint` shows no errors
- [ ] Extension loads in debug mode (F5)
- [ ] Chat panel opens and displays correctly
- [ ] Can send message and receive mock response
- [ ] Configuration panel opens with all 6 settings
- [ ] Can change provider and see success message
- [ ] Can change model and see success message
- [ ] All 4 commands appear in Command Palette
- [ ] Reset session clears conversation
- [ ] Settings persist after VSCode restart
- [ ] No errors in Debug Console
- [ ] Chat works with different themes
- [ ] Keyboard shortcuts work (Enter, Shift+Enter)

**Once all above pass ✅, PR is ready for review!**

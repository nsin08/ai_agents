# Sanity Tests - AI Agent VSCode Extension

Quick verification that the plugin works correctly. Run daily before commits.

**Time:** 15 minutes | **Coverage:** All core functionality

---

## Setup (1 min)

```bash
cd vscode-extension/v1
npm install
npm run compile
code .
# Press F5 to launch Extension Development Host
```

---

## TEST 1: Chat Panel Works (3 min)

1. `Ctrl+Shift+P` ? `Agent: Start Conversation`
2. Type: `Hello`
3. Press Enter

**Expected:**
- ? Chat panel opens
- ? Message appears (blue)
- ? Response appears (gray)
- ? No errors in console

---

## TEST 2: Configuration Saves (3 min)

1. `Ctrl+Shift+P` ? `Agent: Settings`
2. Change Provider to "Ollama"
3. Click "Save Configuration"
4. Close and reopen config
5. Verify "Ollama" is still selected

**Expected:**
- ? Settings persist after save
- ? No errors

---

## TEST 3: Debug Mode Toggle (1 min)

1. `Ctrl+Shift+P` ? `Agent: Settings`
2. Toggle **Debug Mode** on
3. Run a multi-agent task
4. Toggle **Debug Mode** off

**Expected:**
- ? Verbose logs appear only when enabled
- ? Toggle state persists in the workspace

---

## TEST 4: Code Intelligence Works (3 min)

1. Create file: `test.js` with any code
2. Select 2-3 lines
3. Right-click ? `Agent: Send Selection to Agent`
4. Click "Yes" if warning appears

**Expected:**
- ? Chat opens automatically
- ? Code sent with metadata (file, language)
- ? Agent responds
- ? No crashes

---

## TEST 5: Multi-Agent Coordination Starts (3 min)

1. `Ctrl+Shift+P` ? `Agent: Start Multi-Agent Task`
2. Type: `analyze code, implement improvements after 1, verify quality after 2`
3. Press Enter

**Expected:**
- ? Dashboard opens
- ? 3 agent cards visible
- ? Progress: 0% ? 100%
- ? Completes in 10-30 seconds

---

## TEST 6: Dashboard Displays Correctly (3 min)

1. Dashboard should be open from TEST 5
2. Or: `Ctrl+Shift+P` ? `Agent: Show Multi-Agent Dashboard`

**Expected:**
- ? All 3 agents visible (Planner, Executor, Verifier)
- ? Status, task, duration shown per agent
- ? Progress bar visible
- ? Communication log visible
- ? Clean UI layout

---

## TEST 7: History & Export (2 min)

1. `Ctrl+Shift+P` ? `Agent: Start Conversation`
2. Send two short messages
3. `Ctrl+Shift+P` ? `Agent: Show History`
4. Open the latest conversation
5. Click Export Markdown, then Export HTML

**Expected:**
- ? History list shows latest conversation
- ? Read-only replay view renders messages
- ? Markdown + HTML files save successfully

---

## Run Automated Tests (2 min)

```bash
npm test
```

**Expected:**
- ? 150+ tests pass
- ? 0 failures
- ? Completes in <5 seconds

---

## Results

| Test | Status |
|------|--------|
| TEST 1: Chat | ? |
| TEST 2: Config | ? |
| TEST 3: Debug Toggle | ? |
| TEST 4: Code Intelligence | ? |
| TEST 5: Multi-Agent | ? |
| TEST 6: Dashboard | ? |
| TEST 7: History | ? |
| Automated Suite | ? |
| **TOTAL** | **? PASS** |

---

## If Any Test Fails

1. Check console (View ? Output ? Extension Host)
2. Review [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md) for detailed steps
3. Run specific test: `npm test -- {feature}.test.ts`
4. Fix and retry

---

**That's it!** All core functionality validated in 15 minutes.

For detailed testing, see [TESTING_COMPREHENSIVE.md](TESTING_COMPREHENSIVE.md).

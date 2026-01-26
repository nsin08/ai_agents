# Testing Settings Persistence

## Test Plan

### Issue Description
User reports: "Agent settings are still not persistent, now even the dropdown value is gone when provider value is changed to ollama."

### Root Cause Analysis
1. **Race condition in batch update**: Multiple async updates with immediate reload
2. **Saved model not preserved**: When Ollama dropdown loads, saved model value was lost
3. **VSCode config timing**: Settings may not be immediately readable after update

### Fixes Applied

#### Fix 1: Store and Use Saved Model
- Added `savedModel` variable to preserve model from config
- When Ollama models are fetched, use `savedModel` to select correct option
- Falls back to first model if no saved model

#### Fix 2: Add Delays for Persistence
- Added 50ms delay in `ConfigService.updateSettings()` after Promise.all()
- Added 100ms delay in `ConfigPanel` before reloading panel after save
- Ensures VSCode has time to persist to disk

#### Fix 3: Enhanced Logging
- Added console.log statements to trace save flow
- Log settings being saved
- Log settings after reload
- Log config when panel loads

### Manual Testing Steps

**Test 1: Save Ollama Settings**
1. Open Extension Development Host (F5)
2. Open Output panel → "Extension Host"
3. Open Agent Settings panel
4. Change provider to "ollama"
5. Select model "phi:latest" from dropdown
6. Click "Save Settings"
7. Check logs for: `[ConfigService] Updating settings: {...}`
8. Check logs for: `[ConfigService] Settings updated and reloaded: {...}`
9. Verify notification: "Settings saved: ollama / phi:latest"
10. Close Settings panel

**Test 2: Verify Persistence**
1. Reopen Agent Settings panel
2. Check logs for: `[ConfigPanel] Loading configuration: {...}`
3. Verify dropdown shows "ollama"
4. Wait for "Loaded X Ollama models" status
5. **VERIFY**: Dropdown shows "phi:latest" selected
6. Close panel

**Test 3: Settings File Check**
1. Open `%APPDATA%\Code\User\settings.json`
2. **VERIFY**: Contains `"aiAgent.provider": "ollama"`
3. **VERIFY**: Contains `"aiAgent.model": "phi:latest"`

**Test 4: Change to Different Model**
1. Open Settings panel
2. Select different model (e.g., "llama2")
3. Save
4. Close panel
5. Reopen panel
6. **VERIFY**: Shows "llama2" selected

**Test 5: Switch Provider**
1. Open Settings panel (shows ollama/llama2)
2. Change provider to "openai"
3. Enter model "gpt-4"
4. Save
5. Close panel
6. Reopen panel
7. **VERIFY**: Shows provider="openai", model="gpt-4"
8. Change back to "ollama"
9. **VERIFY**: Dropdown reappears with previously saved model

### Expected Console Output

```
[ConfigPanel] Saving settings: {provider: "ollama", model: "phi:latest", ...}
[ConfigService] Updating settings: {provider: "ollama", model: "phi:latest", ...}
[ConfigService] Settings updated and reloaded: {provider: "ollama", model: "phi:latest", ...}
[ConfigPanel] Settings saved, reloading panel...
[ConfigPanel] Loading configuration: {provider: "ollama", model: "phi:latest", ...}
```

### Success Criteria
- [ ] Settings save without errors
- [ ] Settings file updated correctly
- [ ] Reopening panel shows saved values
- [ ] Ollama dropdown shows correct model selected
- [ ] No race conditions in logs
- [ ] Works across VSCode restarts

### Known Issues (If Any)
- If Ollama is not running, dropdown will fall back to text input but saved model will still be shown
- First time using Ollama, dropdown might be empty until models are pulled


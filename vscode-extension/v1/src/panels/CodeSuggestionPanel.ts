import * as vscode from 'vscode';
import { CodeInsertionService, CodeSuggestion } from '../services/CodeInsertionService';
import { CodeContextService } from '../services/CodeContextService';

/**
 * Panel for displaying and managing code suggestions from the AI agent
 */
export class CodeSuggestionPanel {
  public static currentPanel: CodeSuggestionPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];
  private _suggestions: CodeSuggestion[] = [];
  private _currentIndex: number = 0;
  private readonly _codeInsertionService: CodeInsertionService;
  private readonly _codeContextService: CodeContextService;

  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    codeInsertionService: CodeInsertionService,
    codeContextService: CodeContextService
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._codeInsertionService = codeInsertionService;
    this._codeContextService = codeContextService;

    // Set up event handlers
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    this._panel.webview.onDidReceiveMessage(
      this._handleMessage.bind(this),
      null,
      this._disposables
    );
  }

  /**
   * Create or show the code suggestion panel
   */
  public static createOrShow(
    extensionUri: vscode.Uri,
    codeInsertionService: CodeInsertionService,
    codeContextService: CodeContextService,
    agentResponse: string
  ) {
    const column = vscode.ViewColumn.Two;

    // If panel exists, show it
    if (CodeSuggestionPanel.currentPanel) {
      CodeSuggestionPanel.currentPanel._panel.reveal(column);
      CodeSuggestionPanel.currentPanel.updateSuggestions(agentResponse);
      return;
    }

    // Create new panel
    const panel = vscode.window.createWebviewPanel(
      'codeSuggestions',
      'Code Suggestions',
      column,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
      }
    );

    CodeSuggestionPanel.currentPanel = new CodeSuggestionPanel(
      panel,
      extensionUri,
      codeInsertionService,
      codeContextService
    );

    CodeSuggestionPanel.currentPanel.updateSuggestions(agentResponse);
  }

  /**
   * Update suggestions from agent response
   */
  public updateSuggestions(agentResponse: string) {
    this._suggestions = this._codeInsertionService.parseCodeSuggestions(agentResponse);
    this._currentIndex = 0;

    if (this._suggestions.length === 0) {
      vscode.window.showInformationMessage('No code suggestions found in the response.');
      this._panel.webview.html = this._getNoSuggestionsHtml();
      return;
    }

    this._updateWebview();
  }

  /**
   * Handle messages from webview
   */
  private async _handleMessage(message: any) {
    switch (message.command) {
      case 'apply':
        await this._applySuggestion();
        break;
      case 'copy':
        this._copySuggestion();
        break;
      case 'preview':
        await this._previewSuggestion();
        break;
      case 'next':
        this._navigateNext();
        break;
      case 'previous':
        this._navigatePrevious();
        break;
      case 'close':
        this._panel.dispose();
        break;
    }
  }

  /**
   * Apply current suggestion to editor
   */
  private async _applySuggestion() {
    const suggestion = this._suggestions[this._currentIndex];
    if (!suggestion) {
      return;
    }

    try {
      const applied = await this._codeInsertionService.applySuggestion(suggestion);
      if (applied) {
        vscode.window.showInformationMessage('Code suggestion applied successfully!');
        // Keep panel open for multiple applications
      }
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to apply suggestion: ${error}`);
    }
  }

  /**
   * Copy current suggestion to clipboard
   */
  private _copySuggestion() {
    const suggestion = this._suggestions[this._currentIndex];
    if (suggestion) {
      vscode.env.clipboard.writeText(suggestion.suggestedCode);
      vscode.window.showInformationMessage('Code copied to clipboard!');
    }
  }

  /**
   * Show diff preview for current suggestion
   */
  private async _previewSuggestion() {
    const suggestion = this._suggestions[this._currentIndex];
    if (suggestion) {
      await this._codeInsertionService.showDiffPreview(
        suggestion.originalCode || '',
        suggestion.suggestedCode,
        suggestion.filePath || 'untitled'
      );
    }
  }

  /**
   * Navigate to next suggestion
   */
  private _navigateNext() {
    if (this._currentIndex < this._suggestions.length - 1) {
      this._currentIndex++;
      this._updateWebview();
    }
  }

  /**
   * Navigate to previous suggestion
   */
  private _navigatePrevious() {
    if (this._currentIndex > 0) {
      this._currentIndex--;
      this._updateWebview();
    }
  }

  /**
   * Update webview content
   */
  private _updateWebview() {
    this._panel.webview.html = this._getHtmlForWebview();
  }

  /**
   * Generate HTML for webview
   */
  private _getHtmlForWebview(): string {
    const suggestion = this._suggestions[this._currentIndex];
    const totalSuggestions = this._suggestions.length;
    const currentNumber = this._currentIndex + 1;

    // Escape HTML in code
    const escapedCode = this._escapeHtml(suggestion.suggestedCode);
    const languageClass = suggestion.language || 'plaintext';

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code Suggestions</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      margin: 0;
    }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    
    .title {
      font-size: 18px;
      font-weight: bold;
      color: var(--vscode-foreground);
    }
    
    .counter {
      font-size: 14px;
      color: var(--vscode-descriptionForeground);
    }
    
    .explanation {
      background-color: var(--vscode-textBlockQuote-background);
      border-left: 4px solid var(--vscode-textBlockQuote-border);
      padding: 12px;
      margin-bottom: 20px;
      font-size: 14px;
      line-height: 1.6;
    }
    
    .code-container {
      background-color: var(--vscode-textCodeBlock-background);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 4px;
      margin-bottom: 20px;
      overflow: hidden;
    }
    
    .code-header {
      background-color: var(--vscode-editorGroupHeader-tabsBackground);
      padding: 8px 12px;
      font-size: 12px;
      color: var(--vscode-descriptionForeground);
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    
    .code-content {
      padding: 0;
      overflow-x: auto;
    }
    
    pre {
      margin: 0;
      padding: 16px;
      font-family: var(--vscode-editor-font-family);
      font-size: var(--vscode-editor-font-size);
      line-height: 1.5;
      color: var(--vscode-editor-foreground);
    }
    
    code {
      font-family: var(--vscode-editor-font-family);
      white-space: pre;
    }
    
    .button-container {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 20px;
    }
    
    button {
      background-color: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 8px 16px;
      font-size: 14px;
      cursor: pointer;
      border-radius: 2px;
      font-family: var(--vscode-font-family);
    }
    
    button:hover {
      background-color: var(--vscode-button-hoverBackground);
    }
    
    button:active {
      transform: translateY(1px);
    }
    
    button.secondary {
      background-color: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }
    
    button.secondary:hover {
      background-color: var(--vscode-button-secondaryHoverBackground);
    }
    
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .navigation {
      display: flex;
      gap: 10px;
      justify-content: center;
      margin-bottom: 20px;
    }
    
    .nav-button {
      min-width: 80px;
    }
    
    .metadata {
      font-size: 12px;
      color: var(--vscode-descriptionForeground);
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="title">Code Suggestion</div>
    <div class="counter">${currentNumber} of ${totalSuggestions}</div>
  </div>
  
  ${totalSuggestions > 1 ? `
  <div class="navigation">
    <button class="nav-button" onclick="navigate('previous')" ${this._currentIndex === 0 ? 'disabled' : ''}>
      ← Previous
    </button>
    <button class="nav-button" onclick="navigate('next')" ${this._currentIndex === totalSuggestions - 1 ? 'disabled' : ''}>
      Next →
    </button>
  </div>
  ` : ''}
  
  ${suggestion.explanation ? `
  <div class="explanation">
    ${this._escapeHtml(suggestion.explanation)}
  </div>
  ` : ''}
  
  <div class="metadata">
    <strong>Language:</strong> ${languageClass}
    ${suggestion.filePath ? ` | <strong>File:</strong> ${suggestion.filePath}` : ''}
    ${suggestion.startLine !== undefined ? ` | <strong>Lines:</strong> ${suggestion.startLine}-${suggestion.endLine}` : ''}
  </div>
  
  <div class="code-container">
    <div class="code-header">Code Suggestion</div>
    <div class="code-content">
      <pre><code class="language-${languageClass}">${escapedCode}</code></pre>
    </div>
  </div>
  
  <div class="button-container">
    <button onclick="apply()">✓ Apply to Editor</button>
    <button class="secondary" onclick="preview()">👁 Preview Diff</button>
    <button class="secondary" onclick="copy()">📋 Copy Code</button>
    <button class="secondary" onclick="close()">✕ Close</button>
  </div>
  
  <script>
    const vscode = acquireVsCodeApi();
    
    function apply() {
      vscode.postMessage({ command: 'apply' });
    }
    
    function copy() {
      vscode.postMessage({ command: 'copy' });
    }
    
    function preview() {
      vscode.postMessage({ command: 'preview' });
    }
    
    function navigate(direction) {
      vscode.postMessage({ command: direction });
    }
    
    function close() {
      vscode.postMessage({ command: 'close' });
    }
  </script>
</body>
</html>`;
  }

  /**
   * Generate HTML for no suggestions state
   */
  private _getNoSuggestionsHtml(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Code Suggestions</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      margin: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    
    .empty-state {
      text-align: center;
      color: var(--vscode-descriptionForeground);
    }
    
    .icon {
      font-size: 48px;
      margin-bottom: 20px;
    }
    
    .message {
      font-size: 16px;
      margin-bottom: 10px;
    }
    
    .hint {
      font-size: 14px;
      color: var(--vscode-descriptionForeground);
    }
  </style>
</head>
<body>
  <div class="empty-state">
    <div class="icon">💡</div>
    <div class="message">No code suggestions found</div>
    <div class="hint">Ask the agent to provide code suggestions using markdown code blocks</div>
  </div>
</body>
</html>`;
  }

  /**
   * Escape HTML special characters
   */
  private _escapeHtml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Get current suggestions
   */
  public getSuggestions(): CodeSuggestion[] {
    return this._suggestions;
  }

  /**
   * Get current suggestion index
   */
  public getCurrentIndex(): number {
    return this._currentIndex;
  }

  /**
   * Dispose panel and clean up resources
   */
  public dispose() {
    CodeSuggestionPanel.currentPanel = undefined;

    this._panel.dispose();

    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }
}

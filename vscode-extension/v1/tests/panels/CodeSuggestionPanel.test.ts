import * as vscode from 'vscode';
import { CodeSuggestionPanel } from '../../src/panels/CodeSuggestionPanel';
import { CodeInsertionService, CodeSuggestion } from '../../src/services/CodeInsertionService';
import { CodeContextService } from '../../src/services/CodeContextService';

// Mock VSCode API
jest.mock('vscode', () => ({
  window: {
    createWebviewPanel: jest.fn(),
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn()
  },
  ViewColumn: {
    Two: 2
  },
  Uri: {
    joinPath: jest.fn((uri, ...paths) => ({ path: `${uri}/${paths.join('/')}` }))
  },
  env: {
    clipboard: {
      writeText: jest.fn()
    }
  }
}));

describe('CodeSuggestionPanel', () => {
  let mockPanel: any;
  let mockExtensionUri: vscode.Uri;
  let codeInsertionService: CodeInsertionService;
  let codeContextService: CodeContextService;
  let messageHandler: Function;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Create mock webview panel
    mockPanel = {
      webview: {
        html: '',
        onDidReceiveMessage: jest.fn((handler) => {
          messageHandler = handler;
          return { dispose: jest.fn() };
        })
      },
      reveal: jest.fn(),
      dispose: jest.fn(),
      onDidDispose: jest.fn((handler) => {
        return { dispose: jest.fn() };
      })
    };

    (vscode.window.createWebviewPanel as jest.Mock).mockReturnValue(mockPanel);

    mockExtensionUri = { path: '/mock/extension/uri' } as vscode.Uri;
    codeInsertionService = new CodeInsertionService();
    codeContextService = new CodeContextService();

    // Clear current panel
    (CodeSuggestionPanel as any).currentPanel = undefined;
  });

  afterEach(() => {
    // Clean up
    (CodeSuggestionPanel as any).currentPanel = undefined;
  });

  describe('Panel Creation', () => {
    it('should create new panel', () => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      expect(vscode.window.createWebviewPanel).toHaveBeenCalledWith(
        'codeSuggestions',
        'Code Suggestions',
        vscode.ViewColumn.Two,
        expect.objectContaining({
          enableScripts: true,
          retainContextWhenHidden: true
        })
      );
    });

    it('should reuse existing panel', () => {
      const response1 = '```typescript\nconst x = 1;\n```';
      const response2 = '```typescript\nconst y = 2;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response1
      );

      const firstCallCount = (vscode.window.createWebviewPanel as jest.Mock).mock.calls.length;

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response2
      );

      // Should not create new panel
      expect((vscode.window.createWebviewPanel as jest.Mock).mock.calls.length).toBe(firstCallCount);
      expect(mockPanel.reveal).toHaveBeenCalled();
    });
  });

  describe('Suggestion Parsing', () => {
    it('should parse single suggestion from response', () => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const panel = (CodeSuggestionPanel as any).currentPanel;
      const suggestions = panel.getSuggestions();

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].suggestedCode).toBe('const x = 1;');
      expect(suggestions[0].language).toBe('typescript');
    });

    it('should parse multiple suggestions from response', () => {
      const response = `
        \`\`\`typescript
        const x = 1;
        \`\`\`
        \`\`\`javascript
        const y = 2;
        \`\`\`
      `;

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const panel = (CodeSuggestionPanel as any).currentPanel;
      const suggestions = panel.getSuggestions();

      expect(suggestions).toHaveLength(2);
      expect(suggestions[0].language).toBe('typescript');
      expect(suggestions[1].language).toBe('javascript');
    });

    it('should handle response with no code blocks', () => {
      const response = 'Just plain text without code';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
        'No code suggestions found in the response.'
      );
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      const response = `
        \`\`\`typescript
        const x = 1;
        \`\`\`
        \`\`\`javascript
        const y = 2;
        \`\`\`
        \`\`\`python
        z = 3
        \`\`\`
      `;

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );
    });

    it('should start at first suggestion', () => {
      const panel = (CodeSuggestionPanel as any).currentPanel;
      expect(panel.getCurrentIndex()).toBe(0);
    });

    it('should navigate to next suggestion', () => {
      const panel = (CodeSuggestionPanel as any).currentPanel;

      messageHandler({ command: 'next' });

      expect(panel.getCurrentIndex()).toBe(1);
    });

    it('should navigate to previous suggestion', () => {
      const panel = (CodeSuggestionPanel as any).currentPanel;

      messageHandler({ command: 'next' });
      messageHandler({ command: 'previous' });

      expect(panel.getCurrentIndex()).toBe(0);
    });

    it('should not navigate beyond last suggestion', () => {
      const panel = (CodeSuggestionPanel as any).currentPanel;
      const totalSuggestions = panel.getSuggestions().length;

      for (let i = 0; i < totalSuggestions + 5; i++) {
        messageHandler({ command: 'next' });
      }

      expect(panel.getCurrentIndex()).toBe(totalSuggestions - 1);
    });

    it('should not navigate before first suggestion', () => {
      const panel = (CodeSuggestionPanel as any).currentPanel;

      messageHandler({ command: 'previous' });
      messageHandler({ command: 'previous' });

      expect(panel.getCurrentIndex()).toBe(0);
    });
  });

  describe('User Actions', () => {
    beforeEach(() => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );
    });

    it('should copy code to clipboard', () => {
      messageHandler({ command: 'copy' });

      expect(vscode.env.clipboard.writeText).toHaveBeenCalledWith('const x = 1;');
      expect(vscode.window.showInformationMessage).toHaveBeenCalledWith(
        'Code copied to clipboard!'
      );
    });

    it('should close panel', () => {
      messageHandler({ command: 'close' });

      expect(mockPanel.dispose).toHaveBeenCalled();
    });
  });

  describe('HTML Generation', () => {
    it('should generate HTML with code content', () => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const html = mockPanel.webview.html;

      expect(html).toContain('const x = 1;');
      expect(html).toContain('typescript');
      expect(html).toContain('Code Suggestion');
    });

    it('should escape HTML in code', () => {
      const response = '```typescript\nconst html = "<div>";\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const html = mockPanel.webview.html;

      expect(html).toContain('&lt;div&gt;');
      expect(html).not.toContain('<div>');
    });

    it('should include navigation buttons for multiple suggestions', () => {
      const response = `
        \`\`\`typescript
        const x = 1;
        \`\`\`
        \`\`\`javascript
        const y = 2;
        \`\`\`
      `;

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const html = mockPanel.webview.html;

      expect(html).toContain('Previous');
      expect(html).toContain('Next');
      expect(html).toContain('1 of 2');
    });

    it('should not show navigation for single suggestion', () => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const html = mockPanel.webview.html;

      expect(html).toContain('1 of 1');
      expect(html).not.toContain('class="navigation"');
    });

    it('should display explanation when available', () => {
      // Create response with explanation
      const response = 'This is the explanation.\n```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const panel = (CodeSuggestionPanel as any).currentPanel;
      const suggestions = panel.getSuggestions();

      // Manually add explanation to test display
      if (suggestions[0]) {
        suggestions[0].explanation = 'This is the explanation.';
        panel._updateWebview();
      }

      const html = mockPanel.webview.html;
      expect(html).toContain('explanation');
    });
  });

  describe('Panel Lifecycle', () => {
    it('should dispose panel and clean up resources', () => {
      const response = '```typescript\nconst x = 1;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response
      );

      const panel = (CodeSuggestionPanel as any).currentPanel;
      panel.dispose();

      expect((CodeSuggestionPanel as any).currentPanel).toBeUndefined();
    });

    it('should update suggestions when panel already exists', () => {
      const response1 = '```typescript\nconst x = 1;\n```';
      const response2 = '```typescript\nconst y = 2;\n```';

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response1
      );

      const panel = (CodeSuggestionPanel as any).currentPanel;
      const firstSuggestion = panel.getSuggestions()[0].suggestedCode;

      CodeSuggestionPanel.createOrShow(
        mockExtensionUri,
        codeInsertionService,
        codeContextService,
        response2
      );

      const secondSuggestion = panel.getSuggestions()[0].suggestedCode;

      expect(firstSuggestion).toBe('const x = 1;');
      expect(secondSuggestion).toBe('const y = 2;');
    });
  });
});

import * as vscode from 'vscode';
import { CodeContextService } from '../../src/services/CodeContextService';
import { CodeInsertionService } from '../../src/services/CodeInsertionService';

// Mock VSCode API
jest.mock('vscode', () => ({
  window: {
    activeTextEditor: undefined,
    showWarningMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showInformationMessage: jest.fn(),
    createWebviewPanel: jest.fn()
  },
  ViewColumn: {
    Two: 2
  },
  Uri: {
    joinPath: jest.fn()
  },
  workspace: {
    applyEdit: jest.fn()
  },
  WorkspaceEdit: jest.fn(() => ({
    replace: jest.fn()
  })),
  Position: jest.fn((line, char) => ({ line, character: char })),
  Range: jest.fn((start, end) => ({ start, end })),
  env: {
    clipboard: {
      writeText: jest.fn()
    }
  }
}));

describe('Code Intelligence Integration', () => {
  let codeContextService: CodeContextService;
  let codeInsertionService: CodeInsertionService;

  beforeEach(() => {
    jest.clearAllMocks();
    codeContextService = new CodeContextService();
    codeInsertionService = new CodeInsertionService();
  });

  describe('End-to-End Code Intelligence Flow', () => {
    it('should extract code, detect patterns, and prepare for agent', async () => {
      // Mock active editor with selected code
      const mockDocument = {
        getText: jest.fn((range?: any) => 'const API_KEY = "test12345678901234567890";'),
        fileName: '/path/to/file.ts',
        languageId: 'typescript',
        lineCount: 10
      };

      const mockSelection = {
        isEmpty: false,
        start: { line: 0, character: 0 },
        end: { line: 0, character: 26 }
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: mockSelection
      };

      // Extract code
      const context = await codeContextService.extractSelectedCode();

      expect(context).not.toBeNull();
      if (context) {
        expect(context.selectedCode).toContain('API_KEY');
        expect(context.language).toBe('typescript');
        expect(context.fileName).toBe('file.ts');
        
        // Check for sensitive data detection
        const { hasSensitiveData, warnings } = (codeContextService as any).detectSensitiveData(context.selectedCode);
        expect(hasSensitiveData).toBe(true);
        expect(warnings).toContain('API Key');
      }
    });

    it('should parse agent response and prepare suggestions', () => {
      const agentResponse = `
        Here's a safer approach:
        \`\`\`typescript
        const API_KEY = process.env.API_KEY;
        \`\`\`
        This reads from environment variables instead.
      `;

      const suggestions = codeInsertionService.parseCodeSuggestions(agentResponse);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].suggestedCode).toContain('process.env.API_KEY');
      expect(suggestions[0].language).toBe('typescript');
      expect(suggestions[0].explanation).toBeTruthy();
    });

    it('should handle multiple code blocks in single response', () => {
      const agentResponse = `
        First, add the import:
        \`\`\`typescript
        import * as dotenv from 'dotenv';
        \`\`\`
        
        Then configure it:
        \`\`\`typescript
        dotenv.config();
        \`\`\`
        
        Finally, use it safely:
        \`\`\`typescript
        const API_KEY = process.env.API_KEY;
        \`\`\`
      `;

      const suggestions = codeInsertionService.parseCodeSuggestions(agentResponse);

      expect(suggestions).toHaveLength(3);
      expect(suggestions[0].suggestedCode).toContain('dotenv');
      expect(suggestions[1].suggestedCode).toContain('config()');
      expect(suggestions[2].suggestedCode).toContain('process.env');
    });
  });

  describe('Security Integration', () => {
    it('should block credential files', async () => {
      const mockDocument = {
        getText: jest.fn(() => 'API_KEY=secret123'),
        fileName: '/path/to/.env',
        languageId: 'plaintext',
        lineCount: 1
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: { isEmpty: false, start: { line: 0, character: 0 }, end: { line: 0, character: 10 } }
      };

      const context = await codeContextService.extractFileContent();

      expect(context).toBeNull();
      expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
        expect.stringContaining('.env')
      );
    });

    it('should warn on sensitive data patterns', async () => {
      const mockDocument = {
        getText: jest.fn((range?: any) => 'const token = "sk-123456789012345678901234567890123456789012345678";'),
        fileName: '/path/to/file.ts',
        languageId: 'typescript',
        lineCount: 1
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: {
          isEmpty: false,
          start: { line: 0, character: 0 },
          end: { line: 0, character: 70 }
        }
      };

      const context = await codeContextService.extractSelectedCode();

      expect(context).not.toBeNull();
      if (context) {
        expect(context.containsSensitiveData).toBe(true);
        expect(context.sensitiveDataWarnings).toEqual(
          expect.arrayContaining([expect.stringMatching(/API Key/i)])
        );
      }
    });

    it('should detect multiple sensitive patterns', async () => {
      const codeWithSecrets = `
        const API_KEY = "sk-123456789012345678901234567890123456789012345678";
        const PASSWORD = "secret123";
        const token = "ghp_123456789012345678901234567890123456";
      `;

      const mockDocument = {
        getText: jest.fn(() => codeWithSecrets),
        fileName: '/path/to/file.ts',
        languageId: 'typescript',
        lineCount: 4
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: {
          isEmpty: false,
          start: { line: 0, character: 0 },
          end: { line: 3, character: 50 }
        }
      };

      const context = await codeContextService.extractSelectedCode();

      expect(context).not.toBeNull();
      if (context) {
        expect(context.containsSensitiveData).toBe(true);
        expect(context.sensitiveDataWarnings!.length).toBeGreaterThan(1);
      }
    });
  });

  describe('Code Formatting Integration', () => {
    it('should format context with metadata', () => {
      const context = {
        selectedCode: 'const x = 1;',
        filePath: '/path/to/file.ts',
        fileName: 'file.ts',
        language: 'typescript',
        lineRange: { start: 10, end: 12 },
        fileSize: 100,
        timestamp: Date.now()
      };

      const formatted = codeContextService.formatContextForAgent(context);

      expect(formatted).toContain('file.ts');
      expect(formatted).toContain('typescript');
      expect(formatted).toContain('Lines:** 10-12');
      expect(formatted).toContain('```typescript');
      expect(formatted).toContain('const x = 1;');
    });

    it('should preserve code structure in formatting', () => {
      const context = {
        selectedCode: `function test() {
  console.log("hello");
  return true;
}`,
        filePath: '/path/to/file.js',
        fileName: 'file.js',
        language: 'javascript',
        lineRange: { start: 1, end: 4 },
        fileSize: 200,
        timestamp: Date.now()
      };

      const formatted = codeContextService.formatContextForAgent(context);

      expect(formatted).toContain('function test()');
      expect(formatted).toContain('console.log');
      expect(formatted).toContain('return true');
    });
  });

  describe('Size Limit Enforcement', () => {
    it('should enforce line count limit', async () => {
      const largeCode = Array(11000).fill('const x = 1;').join('\n');

      const mockDocument = {
        getText: jest.fn(() => largeCode),
        fileName: '/path/to/large.ts',
        languageId: 'typescript',
        lineCount: 11000
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: {
          isEmpty: false,
          start: { line: 0, character: 0 },
          end: { line: 10999, character: 10 }
        }
      };

      const context = await codeContextService.extractSelectedCode();

      expect(context).toBeNull();
      expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
        expect.stringContaining('10000 lines')
      );
    });

    it('should enforce file size limit', async () => {
      const largeFile = 'x'.repeat(600000); // 600KB

      const mockDocument = {
        getText: jest.fn(() => largeFile),
        fileName: '/path/to/large.ts',
        languageId: 'typescript',
        lineCount: 100
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: {
          isEmpty: false,
          start: { line: 0, character: 0 },
          end: { line: 99, character: 10 }
        }
      };

      const context = await codeContextService.extractFileContent();

      expect(context).toBeNull();
      expect(vscode.window.showErrorMessage).toHaveBeenCalledWith(
        expect.stringContaining('500KB')
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle no active editor', async () => {
      (vscode.window as any).activeTextEditor = undefined;

      const context = await codeContextService.extractSelectedCode();

      expect(context).toBeNull();
      expect(vscode.window.showWarningMessage).toHaveBeenCalledWith(
        'No active editor. Please open a file and select code.'
      );
    });

    it('should handle empty selection', async () => {
      const mockDocument = {
        getText: jest.fn(() => ''),
        fileName: '/path/to/file.ts',
        languageId: 'typescript',
        lineCount: 10
      };

      (vscode.window as any).activeTextEditor = {
        document: mockDocument,
        selection: {
          isEmpty: true,
          start: { line: 0, character: 0 },
          end: { line: 0, character: 0 }
        }
      };

      const context = await codeContextService.extractSelectedCode();

      expect(context).toBeNull();
      expect(vscode.window.showWarningMessage).toHaveBeenCalledWith(
        'No code selected. Please select code and try again.'
      );
    });

    it('should handle agent response with no code blocks', () => {
      const response = 'This is just text without any code blocks.';

      const suggestions = codeInsertionService.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(0);
    });
  });
});

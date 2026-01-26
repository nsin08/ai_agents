/**
 * CodeContextService - Extracts code context from active editor for agent consumption.
 * Handles security filtering, sensitive data detection, and file type validation.
 */

import * as vscode from 'vscode';

export interface CodeContext {
  /** Selected code content */
  selectedCode: string;
  
  /** Full file path */
  filePath: string;
  
  /** File name only */
  fileName: string;
  
  /** Language ID (typescript, python, etc.) */
  language: string;
  
  /** Line range of selection */
  lineRange: {
    start: number;
    end: number;
  };
  
  /** Total file size in lines */
  fileSize: number;
  
  /** Timestamp of extraction */
  timestamp: number;
  
  /** True if sensitive data detected */
  containsSensitiveData?: boolean;
  
  /** List of sensitive data types found */
  sensitiveDataWarnings?: string[];
}

export class CodeContextService {
  private static readonly MAX_CONTEXT_SIZE = 10000; // lines
  private static readonly MAX_FILE_SIZE_BYTES = 500000; // ~500KB

  /**
   * Extract selected code from active editor
   */
  public async extractSelectedCode(): Promise<CodeContext | null> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage('No active editor. Please open a file and select code.');
      return null;
    }

    const document = editor.document;
    const selection = editor.selection;
    const selectedCode = document.getText(selection);

    if (!selectedCode || selectedCode.trim().length === 0) {
      vscode.window.showWarningMessage('No code selected. Please select code and try again.');
      return null;
    }

    // Check line count limit
    const lineCount = selectedCode.split('\n').length;
    if (lineCount > CodeContextService.MAX_CONTEXT_SIZE) {
      vscode.window.showErrorMessage(
        `Selection too large (${lineCount} lines). Maximum: ${CodeContextService.MAX_CONTEXT_SIZE} lines.`
      );
      return null;
    }

    const context: CodeContext = {
      selectedCode,
      filePath: document.fileName,
      fileName: this.getFileName(document.fileName),
      language: document.languageId,
      lineRange: {
        start: selection.start.line + 1,
        end: selection.end.line + 1
      },
      fileSize: document.lineCount,
      timestamp: Date.now()
    };

    // Check for sensitive data
    const { hasSensitiveData, warnings } = this.detectSensitiveData(selectedCode);
    if (hasSensitiveData) {
      context.containsSensitiveData = true;
      context.sensitiveDataWarnings = warnings;
    }

    return context;
  }

  /**
   * Extract entire file content from active editor
   */
  public async extractFileContent(): Promise<CodeContext | null> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage('No active editor. Please open a file.');
      return null;
    }

    const document = editor.document;
    const content = document.getText();
    const fileExt = this.getFileExtension(document.fileName);

    // Block sensitive file types
    if (this.isBlockedFileType(fileExt)) {
      vscode.window.showErrorMessage(
        `Cannot send .${fileExt} files (may contain sensitive data). Blocked extensions: .env, .pem, .key, .p12, .pfx, .crt`
      );
      return null;
    }

    // Check file size
    if (content.length > CodeContextService.MAX_FILE_SIZE_BYTES) {
      const sizeMB = (content.length / 1024 / 1024).toFixed(2);
      vscode.window.showErrorMessage(
        `File too large (${sizeMB}MB). Maximum: 500KB.`
      );
      return null;
    }

    // Check line count
    if (document.lineCount > CodeContextService.MAX_CONTEXT_SIZE) {
      vscode.window.showErrorMessage(
        `File too large (${document.lineCount} lines). Maximum: ${CodeContextService.MAX_CONTEXT_SIZE} lines.`
      );
      return null;
    }

    const context: CodeContext = {
      selectedCode: content,
      filePath: document.fileName,
      fileName: this.getFileName(document.fileName),
      language: document.languageId,
      lineRange: { start: 1, end: document.lineCount },
      fileSize: document.lineCount,
      timestamp: Date.now()
    };

    // Check for sensitive data
    const { hasSensitiveData, warnings } = this.detectSensitiveData(content);
    if (hasSensitiveData) {
      context.containsSensitiveData = true;
      context.sensitiveDataWarnings = warnings;
    }

    return context;
  }

  /**
   * Detect sensitive data patterns in code (API keys, tokens, passwords, etc.)
   */
  private detectSensitiveData(code: string): { hasSensitiveData: boolean; warnings: string[] } {
    const warnings: string[] = [];
    
    const patterns = [
      { regex: /API[_-]?KEY\s*[=:]\s*['"]?[\w\-]{20,}/gi, name: 'API Key' },
      { regex: /BEARER\s+[\w\-\.]+/gi, name: 'Bearer Token' },
      { regex: /PASSWORD\s*[=:]\s*['"]?[\w!@#$%^&*]+/gi, name: 'Password' },
      { regex: /SECRET[_-]?KEY\s*[=:]\s*['"]?[\w\-]{20,}/gi, name: 'Secret Key' },
      { regex: /PRIVATE[_-]?KEY\s*[=:]/gi, name: 'Private Key' },
      { regex: /ACCESS[_-]?TOKEN\s*[=:]\s*['"]?[\w\-]{20,}/gi, name: 'Access Token' },
      { regex: /AUTH[_-]?TOKEN\s*[=:]\s*['"]?[\w\-]{20,}/gi, name: 'Auth Token' },
      { regex: /CLIENT[_-]?SECRET\s*[=:]\s*['"]?[\w\-]{20,}/gi, name: 'Client Secret' },
      { regex: /\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}/g, name: 'Credit Card Number' },
      { regex: /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, name: 'Email Address' },
      { regex: /-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----/gi, name: 'Private Key Block' },
      { regex: /eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g, name: 'JWT Token' },
      { regex: /ghp_[a-zA-Z0-9]{36}/g, name: 'GitHub Token' },
      { regex: /sk-[a-zA-Z0-9]{48}/g, name: 'OpenAI API Key' },
      { regex: /AIza[a-zA-Z0-9_-]{35}/g, name: 'Google API Key' }
    ];

    patterns.forEach(({ regex, name }) => {
      if (regex.test(code)) {
        warnings.push(name);
      }
    });

    return {
      hasSensitiveData: warnings.length > 0,
      warnings
    };
  }

  /**
   * Check if file type should be blocked from sending
   */
  private isBlockedFileType(ext: string): boolean {
    const blockedExtensions = [
      'env', 'pem', 'key', 'p12', 'pfx', 'crt',
      'cert', 'der', 'pkcs12', 'jks', 'keystore'
    ];
    
    const blockedNames = ['credentials', 'secrets', 'password', 'config'];
    
    const lowerExt = ext.toLowerCase();
    
    return blockedExtensions.includes(lowerExt) ||
           blockedNames.some(name => lowerExt.includes(name));
  }

  /**
   * Format code context for agent consumption
   */
  public formatContextForAgent(context: CodeContext): string {
    return `
📎 **Code Context**

**File:** \`${context.fileName}\`  
**Language:** ${context.language}  
**Lines:** ${context.lineRange.start}-${context.lineRange.end}  
**Full Path:** \`${context.filePath}\`

\`\`\`${context.language}
${context.selectedCode}
\`\`\`

Please analyze this code and provide suggestions.
`;
  }

  /**
   * Extract file name from full path
   */
  private getFileName(path: string): string {
    return path.split(/[\\/]/).pop() || 'unknown';
  }

  /**
   * Extract file extension from path
   */
  private getFileExtension(path: string): string {
    const parts = path.split('.');
    return parts.length > 1 ? parts[parts.length - 1] : '';
  }
}

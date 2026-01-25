/**
 * CodeInsertionService - Handles parsing agent responses for code suggestions
 * and applying them to the editor.
 */

import * as vscode from 'vscode';

export interface CodeSuggestion {
  /** Original code (if replacement) */
  originalCode?: string;
  
  /** Suggested code to insert/replace */
  suggestedCode: string;
  
  /** Explanation from agent */
  explanation?: string;
  
  /** Target file path (optional) */
  filePath?: string;
  
  /** Start line for replacement (optional) */
  startLine?: number;
  
  /** End line for replacement (optional) */
  endLine?: number;
  
  /** Language ID for syntax highlighting */
  language?: string;
}

export class CodeInsertionService {
  /**
   * Parse agent response for code suggestions (markdown code blocks)
   */
  public parseCodeSuggestions(agentResponse: string): CodeSuggestion[] {
    const suggestions: CodeSuggestion[] = [];
    
    // Match markdown code blocks with optional language identifier
    const codeBlockRegex = /```([\w\-]*)\n([\s\S]*?)```/g;
    let match;

    while ((match = codeBlockRegex.exec(agentResponse)) !== null) {
      const language = match[1] || 'plaintext';
      const code = match[2].trim();
      
      suggestions.push({
        suggestedCode: code,
        explanation: this.extractExplanation(agentResponse, match.index),
        language
      });
    }

    // If no markdown blocks found, look for indented code blocks
    if (suggestions.length === 0) {
      const indentedCodeRegex = /\n(    .+\n)+/g;
      let indentedMatch;
      
      while ((indentedMatch = indentedCodeRegex.exec(agentResponse)) !== null) {
        const code = indentedMatch[0]
          .split('\n')
          .map(line => line.substring(4)) // Remove 4-space indent
          .join('\n')
          .trim();
        
        if (code.length > 0) {
          suggestions.push({
            suggestedCode: code,
            explanation: this.extractExplanation(agentResponse, indentedMatch.index)
          });
        }
      }
    }

    return suggestions;
  }

  /**
   * Apply code suggestion to active editor
   */
  public async applySuggestion(suggestion: CodeSuggestion): Promise<boolean> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showErrorMessage('No active editor. Please open a file to apply the suggestion.');
      return false;
    }

    try {
      const edit = new vscode.WorkspaceEdit();
      const document = editor.document;

      if (suggestion.startLine !== undefined && suggestion.endLine !== undefined) {
        // Replace specific range
        const startPos = new vscode.Position(suggestion.startLine - 1, 0);
        const endPos = new vscode.Position(suggestion.endLine, 0);
        const range = new vscode.Range(startPos, endPos);
        
        edit.replace(document.uri, range, suggestion.suggestedCode);
      } else if (!editor.selection.isEmpty) {
        // Replace current selection
        edit.replace(document.uri, editor.selection, suggestion.suggestedCode);
      } else {
        // Insert at cursor position
        edit.insert(document.uri, editor.selection.start, suggestion.suggestedCode);
      }

      const applied = await vscode.workspace.applyEdit(edit);
      
      if (applied) {
        vscode.window.showInformationMessage('✅ Code suggestion applied!');
        
        // Format the inserted code
        try {
          await vscode.commands.executeCommand('editor.action.formatDocument');
        } catch (formatError) {
          // Formatting may fail if no formatter available, continue anyway
          console.log('Format failed:', formatError);
        }
      } else {
        vscode.window.showErrorMessage('Failed to apply suggestion. Please try again.');
      }
      
      return applied;
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to apply suggestion: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
      return false;
    }
  }

  /**
   * Insert code at specific position
   */
  public async insertCodeAtPosition(
    code: string,
    line: number,
    character: number = 0
  ): Promise<boolean> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return false;
    }

    const position = new vscode.Position(line - 1, character);
    const edit = new vscode.WorkspaceEdit();
    edit.insert(editor.document.uri, position, code);

    return await vscode.workspace.applyEdit(edit);
  }

  /**
   * Replace code at specific range
   */
  public async replaceCodeInRange(
    code: string,
    startLine: number,
    endLine: number
  ): Promise<boolean> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return false;
    }

    const startPos = new vscode.Position(startLine - 1, 0);
    const endPos = new vscode.Position(endLine, 0);
    const range = new vscode.Range(startPos, endPos);

    const edit = new vscode.WorkspaceEdit();
    edit.replace(editor.document.uri, range, code);

    return await vscode.workspace.applyEdit(edit);
  }

  /**
   * Show diff preview before applying (opens side-by-side comparison)
   */
  public async showDiffPreview(
    originalCode: string,
    suggestedCode: string,
    title: string = 'Code Suggestion'
  ): Promise<void> {
    // Create temporary documents for diff view
    const originalDoc = await vscode.workspace.openTextDocument({
      content: originalCode,
      language: 'typescript'
    });

    const suggestedDoc = await vscode.workspace.openTextDocument({
      content: suggestedCode,
      language: 'typescript'
    });

    // Open diff view
    await vscode.commands.executeCommand(
      'vscode.diff',
      originalDoc.uri,
      suggestedDoc.uri,
      `${title} (Original ↔ Suggested)`
    );
  }

  /**
   * Extract explanation text before code block
   */
  private extractExplanation(response: string, codeBlockIndex: number): string | undefined {
    const textBefore = response.substring(0, codeBlockIndex);
    const lines = textBefore.split('\n');
    
    // Get last few non-empty lines before code block
    const explanationLines = lines
      .reverse()
      .filter(line => line.trim().length > 0)
      .slice(0, 3)
      .reverse();

    const explanation = explanationLines.join(' ').trim();
    
    // Only return if it looks like an explanation (not just code or single word)
    return explanation.length > 10 ? explanation : undefined;
  }

  /**
   * Count number of code suggestions in agent response
   */
  public countSuggestions(agentResponse: string): number {
    const codeBlockRegex = /```[\w\-]*\n[\s\S]*?```/g;
    const matches = agentResponse.match(codeBlockRegex);
    return matches ? matches.length : 0;
  }
}

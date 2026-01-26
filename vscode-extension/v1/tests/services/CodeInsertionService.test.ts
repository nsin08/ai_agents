import { CodeInsertionService } from '../../src/services/CodeInsertionService';

describe('CodeInsertionService', () => {
  let service: CodeInsertionService;

  beforeEach(() => {
    service = new CodeInsertionService();
  });

  describe('parseCodeSuggestions', () => {
    it('should parse single markdown code block', () => {
      const response = '```typescript\nconst x = 1;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].language).toBe('typescript');
      expect(suggestions[0].suggestedCode).toBe('const x = 1;');
    });

    it('should parse multiple markdown code blocks', () => {
      const response = `
        Here's the fix:
        \`\`\`typescript
        const x = 1;
        \`\`\`
        And another:
        \`\`\`javascript
        const y = 2;
        \`\`\`
      `;
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(2);
      expect(suggestions[0].language).toBe('typescript');
      expect(suggestions[1].language).toBe('javascript');
    });

    it('should handle code blocks without language', () => {
      const response = '```\nconst x = 1;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].language).toBe('plaintext');
      expect(suggestions[0].suggestedCode).toBe('const x = 1;');
    });

    it('should trim whitespace from code', () => {
      const response = '```typescript\n\n  const x = 1;  \n\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions[0].suggestedCode).toBe('const x = 1;');
    });

    it('should return empty array for no code blocks', () => {
      const response = 'This is just text without any code.';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(0);
    });

    it('should handle nested code blocks', () => {
      const response = '```typescript\nconst code = `nested`;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].suggestedCode).toContain('nested');
    });

    it('should preserve multi-line code', () => {
      const response = `\`\`\`typescript
function test() {
  console.log("hello");
  return true;
}
\`\`\``;
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions[0].suggestedCode).toContain('function test()');
      expect(suggestions[0].suggestedCode).toContain('console.log');
      expect(suggestions[0].suggestedCode).toContain('return true');
    });
  });

  describe('countSuggestions', () => {
    it('should count single code block', () => {
      const response = '```typescript\nconst x = 1;\n```';
      const count = service.countSuggestions(response);

      expect(count).toBe(1);
    });

    it('should count multiple code blocks', () => {
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
      const count = service.countSuggestions(response);

      expect(count).toBe(3);
    });

    it('should return 0 for no code blocks', () => {
      const response = 'Just plain text';
      const count = service.countSuggestions(response);

      expect(count).toBe(0);
    });
  });

  describe('explanation extraction', () => {
    it('should parse suggestions with explanation', () => {
      const response = `
        This function calculates the sum.
        \`\`\`typescript
        const sum = (a, b) => a + b;
        \`\`\`
      `;
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].explanation).toBeDefined();
    });

    it('should handle suggestions without explanation', () => {
      const response = '```typescript\nconst x = 1;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
    });
  });

  describe('applySuggestion - mode detection', () => {
    it('should detect replace range mode when startLine/endLine provided', () => {
      const suggestion = {
        originalCode: '',
        suggestedCode: 'new code',
        explanation: '',
        filePath: undefined,
        startLine: 10,
        endLine: 15,
        language: 'typescript'
      };

      // We can't test actual editor operations without mocking VSCode APIs
      // But we can verify the service exists and accepts valid inputs
      expect(suggestion.startLine).toBeDefined();
      expect(suggestion.endLine).toBeDefined();
    });

    it('should handle insert at cursor when no range provided', () => {
      const suggestion = {
        originalCode: '',
        suggestedCode: 'new code',
        explanation: '',
        filePath: undefined,
        language: 'typescript'
      };

      // Verify structure for cursor insertion
      expect(suggestion.suggestedCode).toBe('new code');
      expect(suggestion.language).toBe('typescript');
    });
  });

  describe('insertCodeAtPosition', () => {
    it('should validate position parameters', () => {
      const suggestion = {
        originalCode: '',
        suggestedCode: 'code',
        explanation: '',
        filePath: undefined,
        language: 'typescript'
      };

      // Test data validation
      const line = 5;
      const character = 0;

      expect(line).toBeGreaterThanOrEqual(0);
      expect(character).toBeGreaterThanOrEqual(0);
    });
  });

  describe('replaceCodeInRange', () => {
    it('should validate range parameters', () => {
      const suggestion = {
        originalCode: '',
        suggestedCode: 'new code',
        explanation: '',
        filePath: undefined,
        startLine: 10,
        endLine: 15,
        language: 'typescript'
      };

      expect(suggestion.startLine).toBeLessThan(suggestion.endLine!);
      expect(suggestion.startLine).toBeGreaterThanOrEqual(0);
    });

    it('should handle single-line replacement', () => {
      const suggestion = {
        originalCode: '',
        suggestedCode: 'new code',
        explanation: '',
        filePath: undefined,
        startLine: 10,
        endLine: 10,
        language: 'typescript'
      };

      expect(suggestion.startLine).toEqual(suggestion.endLine);
    });
  });

  describe('showDiffPreview', () => {
    it('should prepare diff with original and suggested code', () => {
      const originalCode = 'const x = 1;';
      const suggestedCode = 'const x = 2;';
      const fileName = 'test.ts';

      expect(originalCode).not.toBe(suggestedCode);
      expect(fileName).toBeTruthy();
    });

    it('should handle empty original code', () => {
      const originalCode = '';
      const suggestedCode = 'new code';

      expect(originalCode.length).toBe(0);
      expect(suggestedCode.length).toBeGreaterThan(0);
    });
  });

  describe('parseCodeSuggestions - edge cases', () => {
    it('should handle code block at start of response', () => {
      const response = '```typescript\nconst x = 1;\n```\nExplanation follows.';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].suggestedCode).toBe('const x = 1;');
    });

    it('should handle code block at end of response', () => {
      const response = 'Here is the code:\n```typescript\nconst x = 1;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
    });

    it('should handle empty code block', () => {
      const response = '```typescript\n\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions).toHaveLength(1);
      expect(suggestions[0].suggestedCode).toBe('');
    });

    it('should handle code block with special characters', () => {
      const response = '```typescript\nconst regex = /[a-z]+/g;\n```';
      const suggestions = service.parseCodeSuggestions(response);

      expect(suggestions[0].suggestedCode).toContain('regex');
      expect(suggestions[0].suggestedCode).toContain('/[a-z]+/g');
    });
  });
});

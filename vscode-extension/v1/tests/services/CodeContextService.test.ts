import { CodeContextService } from '../../src/services/CodeContextService';

describe('CodeContextService', () => {
  let service: CodeContextService;

  beforeEach(() => {
    service = new CodeContextService();
  });

  describe('detectSensitiveData', () => {
    it('should detect API keys', () => {
      const code = 'const API_KEY = "sk-abc123def456ghi789012345678901234567890"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('API Key');
    });

    it('should detect Bearer tokens', () => {
      const code = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('Bearer Token');
    });

    it('should detect passwords', () => {
      const code = 'PASSWORD="MySecretPass123!"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('Password');
    });

    it('should detect private keys', () => {
      const code = 'PRIVATE_KEY="abc123def456"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('Private Key');
    });

    it('should detect OpenAI API keys', () => {
      const code = 'const key = "sk-123456789012345678901234567890123456789012345678"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('OpenAI API Key');
    });

    it('should detect JWT tokens', () => {
      const code = 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('JWT Token');
    });

    it('should detect GitHub tokens', () => {
      const code = 'GH_TOKEN=ghp_123456789012345678901234567890123456';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('GitHub Token');
    });

    it('should detect credit card numbers', () => {
      const code = 'card = "4532-1234-5678-9010"';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings).toContain('Credit Card Number');
    });

    it('should not detect sensitive data in clean code', () => {
      const code = 'function hello() { return "world"; }';
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(false);
      expect(result.warnings).toHaveLength(0);
    });

    it('should detect multiple types of sensitive data', () => {
      const code = `
        const API_KEY = "sk-abc123def456ghi789012345678901234567890";
        const PASSWORD = "secret123";
      `;
      const result = (service as any).detectSensitiveData(code);
      
      expect(result.hasSensitiveData).toBe(true);
      expect(result.warnings.length).toBeGreaterThan(1);
    });
  });

  describe('isBlockedFileType', () => {
    it('should block .env files', () => {
      const result = (service as any).isBlockedFileType('env');
      expect(result).toBe(true);
    });

    it('should block .pem files', () => {
      const result = (service as any).isBlockedFileType('pem');
      expect(result).toBe(true);
    });

    it('should block .key files', () => {
      const result = (service as any).isBlockedFileType('key');
      expect(result).toBe(true);
    });

    it('should block .p12 files', () => {
      const result = (service as any).isBlockedFileType('p12');
      expect(result).toBe(true);
    });

    it('should block .crt files', () => {
      const result = (service as any).isBlockedFileType('crt');
      expect(result).toBe(true);
    });

    it('should allow .ts files', () => {
      const result = (service as any).isBlockedFileType('ts');
      expect(result).toBe(false);
    });

    it('should allow .js files', () => {
      const result = (service as any).isBlockedFileType('js');
      expect(result).toBe(false);
    });

    it('should allow .py files', () => {
      const result = (service as any).isBlockedFileType('py');
      expect(result).toBe(false);
    });

    it('should be case-insensitive', () => {
      const result = (service as any).isBlockedFileType('ENV');
      expect(result).toBe(true);
    });
  });

  describe('formatContextForAgent', () => {
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

      const formatted = service.formatContextForAgent(context);

      expect(formatted).toContain('file.ts');
      expect(formatted).toContain('typescript');
      expect(formatted).toContain('Lines:** 10-12');
      expect(formatted).toContain('```typescript');
      expect(formatted).toContain('const x = 1;');
    });

    it('should include file path in formatted output', () => {
      const context = {
        selectedCode: 'print("hello")',
        filePath: '/home/user/project/main.py',
        fileName: 'main.py',
        language: 'python',
        lineRange: { start: 1, end: 1 },
        fileSize: 50,
        timestamp: Date.now()
      };

      const formatted = service.formatContextForAgent(context);

      expect(formatted).toContain('main.py');
      expect(formatted).toContain('python');
      expect(formatted).toContain('/home/user/project/main.py');
    });
  });

  describe('getFileName', () => {
    it('should extract filename from Windows path', () => {
      const result = (service as any).getFileName('C:\\Users\\test\\file.ts');
      expect(result).toBe('file.ts');
    });

    it('should extract filename from Unix path', () => {
      const result = (service as any).getFileName('/home/user/file.ts');
      expect(result).toBe('file.ts');
    });

    it('should handle filename without path', () => {
      const result = (service as any).getFileName('file.ts');
      expect(result).toBe('file.ts');
    });

    it('should return unknown for empty path', () => {
      const result = (service as any).getFileName('');
      expect(result).toBe('unknown');
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extension', () => {
      const result = (service as any).getFileExtension('file.ts');
      expect(result).toBe('ts');
    });

    it('should handle multiple dots', () => {
      const result = (service as any).getFileExtension('file.test.ts');
      expect(result).toBe('ts');
    });

    it('should return empty string for no extension', () => {
      const result = (service as any).getFileExtension('file');
      expect(result).toBe('');
    });

    it('should handle full path', () => {
      const result = (service as any).getFileExtension('/path/to/file.py');
      expect(result).toBe('py');
    });
  });
});

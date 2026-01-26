import { ConfigService } from '../src/services/ConfigService';
import * as vscode from 'vscode';

// Mock VSCode
jest.mock('vscode');

describe('ConfigService', () => {
  let configService: ConfigService;
  let mockContext: any;

  beforeEach(() => {
    mockContext = {
      globalState: {
        update: jest.fn(),
        get: jest.fn(),
      },
    };

    // Mock VSCode workspace
    (vscode.workspace.getConfiguration as jest.Mock).mockReturnValue({
      get: jest.fn((key: string, defaultValue: unknown) => {
        const defaults: Record<string, unknown> = {
          provider: 'mock',
          model: 'llama2',
          baseUrl: 'http://localhost:11434',
          apiKey: '',
          maxTurns: 5,
          timeout: 30,
        };
        return defaults[key] || defaultValue;
      }),
      update: jest.fn(),
    });

    configService = new ConfigService(mockContext);
  });

  describe('Configuration Loading', () => {
    it('should load default configuration', () => {
      const config = configService.getConfig();

      expect(config.provider).toBe('mock');
      expect(config.model).toBe('llama2');
      expect(config.maxTurns).toBe(5);
      expect(config.timeout).toBe(30);
    });

    it('should provide access to individual settings', () => {
      expect(configService.getProvider()).toBe('mock');
      expect(configService.getModel()).toBe('llama2');
      expect(configService.getMaxTurns()).toBe(5);
      expect(configService.getTimeout()).toBe(30);
    });
  });

  describe('Session Management', () => {
    it('should save session to global storage', async () => {
      const sessionData = { id: 'test', messages: [] };
      await configService.saveSession('test-session', sessionData);

      expect(mockContext.globalState.update).toHaveBeenCalledWith(
        'session-test-session',
        sessionData
      );
    });

    it('should load session from global storage', async () => {
      const sessionData = { id: 'test', messages: [] };
      (mockContext.globalState.get as jest.Mock).mockResolvedValue(sessionData);

      const loaded = await configService.loadSession('test-session');

      expect(loaded).toEqual(sessionData);
      expect(mockContext.globalState.get).toHaveBeenCalledWith('session-test-session');
    });
  });

  describe('Provider List', () => {
    it('should return list of available providers', () => {
      const providers = configService.getAvailableProviders();

      expect(providers).toContain('mock');
      expect(providers).toContain('ollama');
      expect(providers).toContain('openai');
      expect(providers).toContain('anthropic');
    });
  });
});

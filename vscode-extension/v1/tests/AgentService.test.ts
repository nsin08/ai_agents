import { AgentService } from '../src/services/AgentService';
import { ConfigService } from '../src/services/ConfigService';

// Mock ConfigService
jest.mock('../src/services/ConfigService');

describe('AgentService', () => {
  let agentService: AgentService;
  let mockConfigService: jest.Mocked<ConfigService>;

  beforeEach(() => {
    mockConfigService = {
      getConfig: jest.fn(() => ({
        provider: 'mock',
        model: 'llama2',
        baseUrl: 'http://localhost:11434',
        apiKey: '',
        maxTurns: 5,
        timeout: 30,
      })),
      getProvider: jest.fn(() => 'mock'),
      getModel: jest.fn(() => 'llama2'),
      getBaseUrl: jest.fn(),
      getApiKey: jest.fn(),
      getMaxTurns: jest.fn(() => 5),
      getTimeout: jest.fn(() => 30),
      saveSession: jest.fn(),
      loadSession: jest.fn(),
      updateSetting: jest.fn(),
      reload: jest.fn(),
      getAvailableProviders: jest.fn(),
    } as any;

    agentService = new AgentService(mockConfigService);
  });

  describe('Session Management', () => {
    it('should start a new session', async () => {
      const session = await agentService.startSession();

      expect(session).toBeDefined();
      expect(session.id).toBeDefined();
      expect(session.messages).toEqual([]);
      expect(session.config).toBeDefined();
    });

    it('should reset session', async () => {
      await agentService.startSession();
      await agentService.resetSession();

      expect(agentService.getCurrentSession()).toBeUndefined();
    });
  });

  describe('Message Handling', () => {
    it('should send message with mock provider', async () => {
      await agentService.startSession();
      const response = await agentService.sendMessage('Hello');

      expect(response).toContain('Mock Agent Response');
      expect(response).toContain('Hello');
    });

    it('should add messages to session history', async () => {
      await agentService.startSession();
      await agentService.sendMessage('Test message');

      const messages = agentService.getMessages();
      expect(messages.length).toBeGreaterThan(0);
      expect(messages[0].role).toBe('user');
      expect(messages[0].content).toBe('Test message');
    });

    it('should auto-create session if none exists', async () => {
      // sendMessage now automatically creates a session if needed
      const response = await agentService.sendMessage('Hello');
      expect(response).toContain('Mock Agent Response');
      
      const session = agentService.getCurrentSession();
      expect(session).toBeDefined();
      expect(session?.messages.length).toBe(2); // user + assistant
    });
  });

  describe('Configuration Updates', () => {
    it('should update configuration', async () => {
      await agentService.startSession();
      agentService.updateConfiguration();

      const session = agentService.getCurrentSession();
      expect(session?.config).toBeDefined();
    });
  });
});

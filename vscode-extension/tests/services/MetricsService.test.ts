/**
 * Unit tests for MetricsService
 */

import { MetricsService } from '../../src/services/MetricsService';

// Mock vscode module
const mockGlobalState = {
  data: new Map<string, any>(),
  get: jest.fn((key: string, defaultValue?: any) => {
    return mockGlobalState.data.get(key) || defaultValue;
  }),
  update: jest.fn((key: string, value: any) => {
    mockGlobalState.data.set(key, value);
    return Promise.resolve();
  }),
};

const mockContext = {
  globalState: mockGlobalState,
} as any;

describe('MetricsService', () => {
  let metricsService: MetricsService;

  beforeEach(() => {
    mockGlobalState.data.clear();
    metricsService = new MetricsService(mockContext);
  });

  describe('Conversation Tracking', () => {
    test('should start a new conversation', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      const metrics = metricsService.getConversationMetrics('conv-1');

      expect(metrics).toBeDefined();
      expect(metrics?.conversationId).toBe('conv-1');
      expect(metrics?.provider).toBe('openai');
      expect(metrics?.model).toBe('gpt-4');
      expect(metrics?.totalTokens).toBe(0);
      expect(metrics?.messageCount).toBe(0);
    });

    test('should end a conversation', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.endConversation('conv-1');

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics).toBeUndefined(); // Moved to storage
    });
  });

  describe('Message Recording', () => {
    beforeEach(() => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
    });

    test('should record message metrics', () => {
      metricsService.recordMessage('conv-1', 100, 200, 1500);

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics?.promptTokens).toBe(100);
      expect(metrics?.completionTokens).toBe(200);
      expect(metrics?.totalTokens).toBe(300);
      expect(metrics?.messageCount).toBe(1);
      expect(metrics?.averageResponseTime).toBe(1500);
    });

    test('should accumulate metrics across multiple messages', () => {
      metricsService.recordMessage('conv-1', 100, 200, 1000);
      metricsService.recordMessage('conv-1', 150, 250, 2000);

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics?.promptTokens).toBe(250);
      expect(metrics?.completionTokens).toBe(450);
      expect(metrics?.totalTokens).toBe(700);
      expect(metrics?.messageCount).toBe(2);
      expect(metrics?.averageResponseTime).toBe(1500); // (1000 + 2000) / 2
    });

    test('should calculate average response time correctly', () => {
      metricsService.recordMessage('conv-1', 100, 100, 1000);
      metricsService.recordMessage('conv-1', 100, 100, 2000);
      metricsService.recordMessage('conv-1', 100, 100, 3000);

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics?.averageResponseTime).toBe(2000); // (1000 + 2000 + 3000) / 3
    });
  });

  describe('Cost Calculation', () => {
    test('should calculate cost for OpenAI GPT-4', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.recordMessage('conv-1', 1000, 2000, 1500);

      const metrics = metricsService.getConversationMetrics('conv-1');
      // GPT-4: $0.03/1K prompt, $0.06/1K completion
      // (1000/1000 * 0.03) + (2000/1000 * 0.06) = 0.03 + 0.12 = 0.15
      expect(metrics?.totalCost).toBeCloseTo(0.15, 4);
    });

    test('should calculate cost for Anthropic Claude', () => {
      metricsService.startConversation('conv-1', 'anthropic', 'claude-3-sonnet');
      metricsService.recordMessage('conv-1', 1000, 2000, 1500);

      const metrics = metricsService.getConversationMetrics('conv-1');
      // Claude Sonnet: $0.003/1K prompt, $0.015/1K completion
      // (1000/1000 * 0.003) + (2000/1000 * 0.015) = 0.003 + 0.03 = 0.033
      expect(metrics?.totalCost).toBeCloseTo(0.033, 4);
    });

    test('should return zero cost for Ollama (local)', () => {
      metricsService.startConversation('conv-1', 'ollama', 'llama2');
      metricsService.recordMessage('conv-1', 1000, 2000, 1500);

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics?.totalCost).toBe(0);
    });

    test('should return zero cost for mock provider', () => {
      metricsService.startConversation('conv-1', 'mock', 'mock-model');
      metricsService.recordMessage('conv-1', 1000, 2000, 1500);

      const metrics = metricsService.getConversationMetrics('conv-1');
      expect(metrics?.totalCost).toBe(0);
    });
  });

  describe('Summary Statistics', () => {
    test('should return empty summary when no conversations', () => {
      const summary = metricsService.getSummary();

      expect(summary.totalConversations).toBe(0);
      expect(summary.totalMessages).toBe(0);
      expect(summary.totalTokens).toBe(0);
      expect(summary.totalCost).toBe(0);
      expect(summary.topProvider).toBe('N/A');
    });

    test('should generate summary across multiple conversations', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.recordMessage('conv-1', 100, 200, 1000);
      metricsService.recordMessage('conv-1', 100, 200, 2000);

      metricsService.startConversation('conv-2', 'anthropic', 'claude-3-sonnet');
      metricsService.recordMessage('conv-2', 150, 250, 1500);

      const summary = metricsService.getSummary();

      expect(summary.totalConversations).toBe(2);
      expect(summary.totalMessages).toBe(3);
      expect(summary.totalTokens).toBe(1000); // (100+200)*2 + (150+250)
      expect(summary.averageResponseTime).toBeCloseTo(1500, 0); // (1500 + 1500) / 2
    });

    test('should identify most used provider', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.startConversation('conv-2', 'openai', 'gpt-3.5-turbo');
      metricsService.startConversation('conv-3', 'anthropic', 'claude-3-sonnet');

      const summary = metricsService.getSummary();
      expect(summary.topProvider).toBe('openai');
    });

    test('should identify most used model', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.startConversation('conv-2', 'openai', 'gpt-4');
      metricsService.startConversation('conv-3', 'anthropic', 'claude-3-sonnet');

      const summary = metricsService.getSummary();
      expect(summary.topModel).toBe('gpt-4');
    });
  });

  describe('Storage', () => {
    test('should retrieve all metrics including stored', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.recordMessage('conv-1', 100, 200, 1000);

      const allMetrics = metricsService.getAllMetrics();
      expect(allMetrics.length).toBeGreaterThan(0);
    });

    test('should clear all metrics', () => {
      metricsService.startConversation('conv-1', 'openai', 'gpt-4');
      metricsService.recordMessage('conv-1', 100, 200, 1000);

      metricsService.clearAllMetrics();

      const summary = metricsService.getSummary();
      expect(summary.totalConversations).toBe(0);
      expect(summary.totalMessages).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle recording to non-existent conversation', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      metricsService.recordMessage('non-existent', 100, 200, 1000);

      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('No active conversation'));
      consoleSpy.mockRestore();
    });

    test('should handle ending non-existent conversation', () => {
      // Should not throw
      expect(() => {
        metricsService.endConversation('non-existent');
      }).not.toThrow();
    });
  });
});

/**
 * Unit tests for TraceService
 */

import { TraceService } from '../../src/services/TraceService';
import { AgentState } from '../../src/models/Trace';

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

describe('TraceService', () => {
  let traceService: TraceService;

  beforeEach(() => {
    mockGlobalState.data.clear();
    traceService = new TraceService(mockContext);
  });

  describe('Trace Lifecycle', () => {
    test('should start a new trace', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      const trace = traceService.getTrace('conv-1');

      expect(trace).toBeDefined();
      expect(trace?.conversationId).toBe('conv-1');
      expect(trace?.provider).toBe('openai');
      expect(trace?.model).toBe('gpt-4');
      expect(trace?.entries).toEqual([]);
      expect(trace?.totalTurns).toBe(0);
    });

    test('should end a trace', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.endTrace('conv-1');

      const trace = traceService.getTrace('conv-1');
      expect(trace).toBeUndefined(); // Moved to storage
    });
  });

  describe('State Transition Recording', () => {
    beforeEach(() => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
    });

    test('should record Observe state', () => {
      traceService.recordStateTransition(
        'conv-1',
        'Observe',
        1,
        50,
        'User message',
        undefined
      );

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries.length).toBe(1);
      expect(trace?.entries[0].state).toBe('Observe');
      expect(trace?.entries[0].turn).toBe(1);
      expect(trace?.entries[0].input).toBe('User message');
    });

    test('should record Plan state', () => {
      traceService.recordStateTransition(
        'conv-1',
        'Plan',
        1,
        100,
        'User input',
        'Plan: Generate response'
      );

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries[0].state).toBe('Plan');
      expect(trace?.entries[0].output).toBe('Plan: Generate response');
    });

    test('should record Act state', () => {
      traceService.recordStateTransition(
        'conv-1',
        'Act',
        1,
        200,
        undefined,
        'Tool execution result'
      );

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries[0].state).toBe('Act');
      expect(trace?.entries[0].duration).toBe(200);
    });

    test('should record Verify state', () => {
      traceService.recordStateTransition(
        'conv-1',
        'Verify',
        1,
        50,
        'Response text',
        'Verification passed'
      );

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries[0].state).toBe('Verify');
    });

    test('should record multiple states in sequence', () => {
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);
      traceService.recordStateTransition('conv-1', 'Plan', 1, 100);
      traceService.recordStateTransition('conv-1', 'Act', 1, 200);
      traceService.recordStateTransition('conv-1', 'Verify', 1, 50);

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries.length).toBe(4);
      expect(trace?.totalTurns).toBe(1);
    });

    test('should update totalTurns correctly', () => {
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);
      traceService.recordStateTransition('conv-1', 'Observe', 2, 50);
      traceService.recordStateTransition('conv-1', 'Observe', 3, 50);

      const trace = traceService.getTrace('conv-1');
      expect(trace?.totalTurns).toBe(3);
    });
  });

  describe('Tool Execution Recording', () => {
    beforeEach(() => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.recordStateTransition('conv-1', 'Act', 1, 200);
    });

    test('should record successful tool execution', () => {
      traceService.recordToolExecution(
        'conv-1',
        'calculator',
        { operation: 'add', a: 5, b: 3 },
        8,
        50,
        'success'
      );

      const trace = traceService.getTrace('conv-1');
      const actEntry = trace?.entries[0];
      expect(actEntry?.toolsUsed).toHaveLength(1);
      expect(actEntry?.toolsUsed?.[0].name).toBe('calculator');
      expect(actEntry?.toolsUsed?.[0].status).toBe('success');
      expect(actEntry?.toolsUsed?.[0].output).toBe(8);
    });

    test('should record failed tool execution', () => {
      traceService.recordToolExecution(
        'conv-1',
        'web_search',
        { query: 'test' },
        undefined,
        100,
        'failure',
        'Network timeout'
      );

      const trace = traceService.getTrace('conv-1');
      const actEntry = trace?.entries[0];
      expect(actEntry?.toolsUsed?.[0].status).toBe('failure');
      expect(actEntry?.toolsUsed?.[0].error).toBe('Network timeout');
    });

    test('should record multiple tool executions', () => {
      traceService.recordToolExecution('conv-1', 'tool1', {}, 'result1', 50, 'success');
      traceService.recordToolExecution('conv-1', 'tool2', {}, 'result2', 75, 'success');

      const trace = traceService.getTrace('conv-1');
      const actEntry = trace?.entries[0];
      expect(actEntry?.toolsUsed).toHaveLength(2);
    });
  });

  describe('Error Recording', () => {
    beforeEach(() => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
    });

    test('should record error in state transition', () => {
      traceService.recordStateTransition(
        'conv-1',
        'Act',
        1,
        100,
        'input',
        undefined,
        undefined,
        {
          message: 'API timeout',
          type: 'TimeoutError',
          stackTrace: 'Error: API timeout\n  at ...',
        }
      );

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries[0].error).toBeDefined();
      expect(trace?.entries[0].error?.message).toBe('API timeout');
      expect(trace?.entries[0].error?.type).toBe('TimeoutError');
    });
  });

  describe('Trace Filtering', () => {
    beforeEach(() => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);
      traceService.recordStateTransition('conv-1', 'Plan', 1, 100);
      traceService.recordStateTransition('conv-1', 'Act', 1, 200);
      traceService.recordStateTransition('conv-1', 'Observe', 2, 50);
      traceService.recordStateTransition('conv-1', 'Plan', 2, 100, undefined, undefined, undefined, {
        message: 'Error',
        type: 'TestError'
      });
    });

    test('should filter by state', () => {
      const filtered = traceService.filterTraces({ state: 'Act' });
      expect(filtered.length).toBe(1);
      expect(filtered[0].state).toBe('Act');
    });

    test('should filter by conversation ID', () => {
      traceService.startTrace('conv-2', 'anthropic', 'claude');
      traceService.recordStateTransition('conv-2', 'Observe', 1, 50);

      const filtered = traceService.filterTraces({ conversationId: 'conv-1' });
      expect(filtered.every(e => e.conversationId === 'conv-1')).toBe(true);
    });

    test('should filter by turn range', () => {
      const filtered = traceService.filterTraces({
        turnRange: { from: 1, to: 1 }
      });
      expect(filtered.every(e => e.turn === 1)).toBe(true);
      expect(filtered.length).toBe(3); // Observe, Plan, Act for turn 1
    });

    test('should filter errors only', () => {
      const filtered = traceService.filterTraces({ errorsOnly: true });
      expect(filtered.length).toBe(1);
      expect(filtered[0].error).toBeDefined();
    });

    test('should filter by tools used', () => {
      traceService.recordToolExecution('conv-1', 'calculator', {}, 8, 50, 'success');

      const filtered = traceService.filterTraces({ toolsOnly: true });
      expect(filtered.length).toBe(1);
      expect(filtered[0].state).toBe('Act');
    });
  });

  describe('Summary Statistics', () => {
    test('should return empty summary when no traces', () => {
      const summary = traceService.getSummary();

      expect(summary.totalTraces).toBe(0);
      expect(summary.totalTurns).toBe(0);
      expect(summary.totalErrors).toBe(0);
      expect(summary.successRate).toBe(100);
    });

    test('should generate summary with traces', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);
      traceService.recordStateTransition('conv-1', 'Plan', 1, 100);
      traceService.recordStateTransition('conv-1', 'Act', 1, 200);
      traceService.recordStateTransition('conv-1', 'Verify', 1, 50);

      const summary = traceService.getSummary();

      expect(summary.totalTraces).toBe(1);
      expect(summary.totalTurns).toBe(1);
      expect(summary.averageTurnDuration).toBe(100); // (50+100+200+50)/4
      expect(summary.mostCommonState).toBe('Plan'); // Excluding Observe
    });

    test('should calculate success rate with errors', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);
      traceService.recordStateTransition('conv-1', 'Plan', 1, 100);
      traceService.recordStateTransition('conv-1', 'Act', 1, 200, undefined, undefined, undefined, {
        message: 'Error',
        type: 'TestError'
      });

      const summary = traceService.getSummary();

      expect(summary.totalErrors).toBe(1);
      expect(summary.successRate).toBeCloseTo(66.67, 1); // 2 success out of 3
    });
  });

  describe('Storage Management', () => {
    test('should limit memory usage per conversation', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');

      // Record more than MAX_TRACES_PER_CONVERSATION (1000)
      for (let i = 0; i < 1100; i++) {
        traceService.recordStateTransition('conv-1', 'Observe', i + 1, 50);
      }

      const trace = traceService.getTrace('conv-1');
      expect(trace?.entries.length).toBeLessThanOrEqual(1000);
    });

    test('should clear all traces', () => {
      traceService.startTrace('conv-1', 'openai', 'gpt-4');
      traceService.recordStateTransition('conv-1', 'Observe', 1, 50);

      traceService.clearAllTraces();

      const summary = traceService.getSummary();
      expect(summary.totalTraces).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle recording to non-existent conversation', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      traceService.recordStateTransition('non-existent', 'Observe', 1, 50);

      expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('No active trace'));
      consoleSpy.mockRestore();
    });

    test('should handle tool recording to non-existent conversation', () => {
      // Should not throw
      expect(() => {
        traceService.recordToolExecution('non-existent', 'tool', {}, 'result', 50, 'success');
      }).not.toThrow();
    });

    test('should handle ending non-existent trace', () => {
      // Should not throw
      expect(() => {
        traceService.endTrace('non-existent');
      }).not.toThrow();
    });
  });
});

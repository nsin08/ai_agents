/**
 * Unit tests for ExportService
 */

import { ExportService } from '../../src/services/ExportService';
import { ConversationMetrics } from '../../src/models/Statistics';
import { ConversationTrace, TraceEntry } from '../../src/models/Trace';

describe('ExportService', () => {
  let exportService: ExportService;

  beforeEach(() => {
    exportService = new ExportService();
  });

  describe('Metrics CSV Export', () => {
    test('should export metrics to CSV format', () => {
      const metrics: ConversationMetrics[] = [
        {
          conversationId: 'conv-1',
          provider: 'openai',
          model: 'gpt-4',
          totalTokens: 1000,
          promptTokens: 400,
          completionTokens: 600,
          totalCost: 0.05,
          messageCount: 5,
          averageResponseTime: 1500,
          startTime: new Date('2026-01-23T10:00:00Z'),
          endTime: new Date('2026-01-23T10:05:00Z'),
        },
      ];

      const result = exportService.exportMetricsToCSV(metrics);

      expect(result.format).toBe('csv');
      expect(result.mimeType).toBe('text/csv');
      expect(result.filename).toContain('agent-metrics-');
      expect(result.filename).toMatch(/\.csv$/);

      // Check CSV content
      const lines = result.data.split('\n');
      expect(lines[0]).toContain('Conversation ID');
      expect(lines[0]).toContain('Provider');
      expect(lines[0]).toContain('Total Tokens');
      expect(lines[1]).toContain('conv-1');
      expect(lines[1]).toContain('openai');
      expect(lines[1]).toContain('gpt-4');
    });

    test('should handle CSV escaping for commas', () => {
      const metrics: ConversationMetrics[] = [
        {
          conversationId: 'conv,with,commas',
          provider: 'openai',
          model: 'gpt-4',
          totalTokens: 100,
          promptTokens: 50,
          completionTokens: 50,
          totalCost: 0.01,
          messageCount: 1,
          averageResponseTime: 1000,
          startTime: new Date('2026-01-23T10:00:00Z'),
        },
      ];

      const result = exportService.exportMetricsToCSV(metrics);

      expect(result.data).toContain('"conv,with,commas"');
    });

    test('should handle active conversations (no endTime)', () => {
      const metrics: ConversationMetrics[] = [
        {
          conversationId: 'conv-1',
          provider: 'openai',
          model: 'gpt-4',
          totalTokens: 100,
          promptTokens: 50,
          completionTokens: 50,
          totalCost: 0.01,
          messageCount: 1,
          averageResponseTime: 1000,
          startTime: new Date('2026-01-23T10:00:00Z'),
          // No endTime
        },
      ];

      const result = exportService.exportMetricsToCSV(metrics);

      expect(result.data).toContain('Active');
    });
  });

  describe('Metrics JSON Export', () => {
    test('should export metrics to JSON format', () => {
      const metrics: ConversationMetrics[] = [
        {
          conversationId: 'conv-1',
          provider: 'openai',
          model: 'gpt-4',
          totalTokens: 1000,
          promptTokens: 400,
          completionTokens: 600,
          totalCost: 0.05,
          messageCount: 5,
          averageResponseTime: 1500,
          startTime: new Date('2026-01-23T10:00:00Z'),
          endTime: new Date('2026-01-23T10:05:00Z'),
        },
      ];

      const result = exportService.exportMetricsToJSON(metrics);

      expect(result.format).toBe('json');
      expect(result.mimeType).toBe('application/json');
      expect(result.filename).toContain('agent-metrics-');
      expect(result.filename).toMatch(/\.json$/);

      // Check JSON parsing
      const parsed = JSON.parse(result.data);
      expect(parsed).toHaveLength(1);
      expect(parsed[0].conversationId).toBe('conv-1');
      expect(parsed[0].provider).toBe('openai');
    });

    test('should format JSON with indentation', () => {
      const metrics: ConversationMetrics[] = [
        {
          conversationId: 'conv-1',
          provider: 'openai',
          model: 'gpt-4',
          totalTokens: 100,
          promptTokens: 50,
          completionTokens: 50,
          totalCost: 0.01,
          messageCount: 1,
          averageResponseTime: 1000,
          startTime: new Date('2026-01-23T10:00:00Z'),
        },
      ];

      const result = exportService.exportMetricsToJSON(metrics);

      // Check for indentation (2 spaces)
      expect(result.data).toContain('  "conversationId"');
    });
  });

  describe('Traces JSON Export', () => {
    test('should export traces to JSON format', () => {
      const traces: ConversationTrace[] = [
        {
          conversationId: 'conv-1',
          provider: 'openai',
          model: 'gpt-4',
          startTime: new Date('2026-01-23T10:00:00Z'),
          endTime: new Date('2026-01-23T10:05:00Z'),
          totalTurns: 1,
          entries: [
            {
              id: 'trace-1',
              timestamp: new Date('2026-01-23T10:00:01Z'),
              state: 'Observe',
              turn: 1,
              conversationId: 'conv-1',
              input: 'User message',
              duration: 50,
            },
          ],
        },
      ];

      const result = exportService.exportTracesToJSON(traces);

      expect(result.format).toBe('json');
      expect(result.mimeType).toBe('application/json');
      expect(result.filename).toContain('agent-traces-');
      expect(result.filename).toMatch(/\.json$/);

      const parsed = JSON.parse(result.data);
      expect(parsed).toHaveLength(1);
      expect(parsed[0].conversationId).toBe('conv-1');
      expect(parsed[0].entries).toHaveLength(1);
    });
  });

  describe('Traces CSV Export', () => {
    test('should export trace entries to CSV format', () => {
      const entries: TraceEntry[] = [
        {
          id: 'trace-1',
          timestamp: new Date('2026-01-23T10:00:01Z'),
          state: 'Observe',
          turn: 1,
          conversationId: 'conv-1',
          input: 'User message',
          output: 'Observed',
          duration: 50,
        },
        {
          id: 'trace-2',
          timestamp: new Date('2026-01-23T10:00:02Z'),
          state: 'Plan',
          turn: 1,
          conversationId: 'conv-1',
          input: 'Context',
          output: 'Planning...',
          duration: 100,
        },
      ];

      const result = exportService.exportTracesToCSV(entries);

      expect(result.format).toBe('csv');
      expect(result.mimeType).toBe('text/csv');
      expect(result.filename).toContain('agent-traces-');
      expect(result.filename).toMatch(/\.csv$/);

      const lines = result.data.split('\n');
      expect(lines[0]).toContain('Trace ID');
      expect(lines[0]).toContain('State');
      expect(lines[0]).toContain('Duration');
      expect(lines[1]).toContain('trace-1');
      expect(lines[1]).toContain('Observe');
      expect(lines[2]).toContain('trace-2');
      expect(lines[2]).toContain('Plan');
    });

    test('should truncate long input/output in CSV', () => {
      const longText = 'a'.repeat(200);
      const entries: TraceEntry[] = [
        {
          id: 'trace-1',
          timestamp: new Date('2026-01-23T10:00:01Z'),
          state: 'Observe',
          turn: 1,
          conversationId: 'conv-1',
          input: longText,
          duration: 50,
        },
      ];

      const result = exportService.exportTracesToCSV(entries);

      // Should be truncated to ~100 chars + "..."
      const lines = result.data.split('\n');
      expect(lines[1]).toContain('...');
      expect(lines[1].length).toBeLessThan(longText.length);
    });

    test('should handle tools in CSV export', () => {
      const entries: TraceEntry[] = [
        {
          id: 'trace-1',
          timestamp: new Date('2026-01-23T10:00:01Z'),
          state: 'Act',
          turn: 1,
          conversationId: 'conv-1',
          duration: 200,
          toolsUsed: [
            {
              name: 'calculator',
              input: { a: 1, b: 2 },
              output: 3,
              duration: 50,
              status: 'success',
            },
            {
              name: 'web_search',
              input: { query: 'test' },
              output: { results: [] },
              duration: 150,
              status: 'success',
            },
          ],
        },
      ];

      const result = exportService.exportTracesToCSV(entries);

      expect(result.data).toContain('calculator; web_search');
    });

    test('should handle errors in CSV export', () => {
      const entries: TraceEntry[] = [
        {
          id: 'trace-1',
          timestamp: new Date('2026-01-23T10:00:01Z'),
          state: 'Act',
          turn: 1,
          conversationId: 'conv-1',
          duration: 100,
          error: {
            message: 'Network timeout',
            type: 'TimeoutError',
          },
        },
      ];

      const result = exportService.exportTracesToCSV(entries);

      expect(result.data).toContain('Network timeout');
    });
  });

  describe('Filename Generation', () => {
    test('should generate unique filenames with timestamps', () => {
      const metrics: ConversationMetrics[] = [];

      const result1 = exportService.exportMetricsToCSV(metrics);
      const result2 = exportService.exportMetricsToCSV(metrics);

      // Filenames should contain timestamps (may be same if called quickly)
      expect(result1.filename).toMatch(/agent-metrics-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.csv/);
      expect(result2.filename).toMatch(/agent-metrics-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.csv/);
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty metrics array', () => {
      const result = exportService.exportMetricsToCSV([]);

      // Should still have headers
      const lines = result.data.split('\n');
      expect(lines[0]).toContain('Conversation ID');
      expect(lines.length).toBe(1); // Only header row
    });

    test('should handle empty trace entries array', () => {
      const result = exportService.exportTracesToCSV([]);

      // Should still have headers
      const lines = result.data.split('\n');
      expect(lines[0]).toContain('Trace ID');
      expect(lines.length).toBe(1); // Only header row
    });
  });
});

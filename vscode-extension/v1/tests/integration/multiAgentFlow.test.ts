import { MultiAgentCoordinator } from '../../src/services/MultiAgentCoordinator';
import { AgentRole, AgentStatus, SpecialistAgent, TaskResult } from '../../src/models/AgentRole';
import { ConfigService } from '../../src/services/ConfigService';
import { MetricsService } from '../../src/services/MetricsService';
import { TraceService } from '../../src/services/TraceService';
import axios from 'axios';

jest.mock('../../src/services/ConfigService');
jest.mock('axios', () => ({
  create: jest.fn()
}));

describe('Multi-Agent Integration Flow', () => {
  let coordinator: MultiAgentCoordinator;
  let mockConfigService: jest.Mocked<ConfigService>;
  let mockMetricsService: jest.Mocked<MetricsService>;
  let mockTraceService: jest.Mocked<TraceService>;
  let mockPost: jest.Mock;

  beforeEach(() => {
    mockPost = jest.fn();
    (axios.create as jest.Mock).mockReturnValue({ post: mockPost });

    mockConfigService = {
      getConfig: jest.fn(() => ({
        provider: 'mock',
        model: 'llama2',
        baseUrl: '',
        apiKey: '',
        maxTurns: 5,
        timeout: 30
      }))
    } as any;

    mockMetricsService = {
      startConversation: jest.fn(),
      endConversation: jest.fn(),
      recordAgentExecution: jest.fn(),
      recordCoordinatorOverhead: jest.fn(),
      getAgentMetrics: jest.fn(),
      getCoordinatorOverhead: jest.fn(() => 0)
    } as any;

    mockTraceService = {
      startTrace: jest.fn(),
      endTrace: jest.fn(),
      recordCoordinatorState: jest.fn(),
      recordInterAgentMessage: jest.fn(),
      recordAgentReasoning: jest.fn()
    } as any;

    const mockAgentService = {
      sendMessage: jest.fn(async (message: string) => `mock:${message}`)
    } as any;

    coordinator = new MultiAgentCoordinator(
      mockAgentService,
      mockMetricsService,
      mockTraceService,
      mockConfigService
    );
    (coordinator as any).agentConfig = {
      mode: 'multi',
      plan: { provider: 'mock', model: 'llama2', maxTurns: 3, timeout: 30, temperature: 0.5, baseUrl: '', apiKey: '' },
      act: { provider: 'mock', model: 'llama2', maxTurns: 5, timeout: 30, temperature: 0.7, baseUrl: '', apiKey: '' }
    };
  });

  const buildAgent = (role: AgentRole): SpecialistAgent => ({
    id: `${role}-1`,
    role,
    status: AgentStatus.IDLE,
    config: mockConfigService.getConfig(),
    capabilities: [{ name: 'implementation', proficiency: 90, domains: ['general'] }],
    execute: jest.fn(async (task: string): Promise<TaskResult> => ({
      id: `result-${role}`,
      subtaskId: 'subtask',
      content: `${role}:${task}`,
      success: true,
      duration: 5,
      tokensUsed: { input: 5, output: 5 }
    }))
  });

  it('runs orchestration and emits state callbacks', async () => {
    const states: string[] = [];
    const progress: number[] = [];

    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    coordinator.setCallbacks({
      onStateChange: (state) => states.push(state),
      onProgressUpdate: (value) => progress.push(value)
    });

    mockPost
      .mockResolvedValueOnce({ data: { response: 'plan-output' } })
      .mockResolvedValueOnce({ data: { response: 'act-output' } });

    const result = await coordinator.orchestrate('Do A\nDo B');

    expect(result.decomposition.subtasks.length).toBe(2);
    expect(states).toContain('decomposing');
    expect(states).toContain('complete');
    expect(progress[progress.length - 1]).toBe(100);
    expect(mockTraceService.recordInterAgentMessage).not.toHaveBeenCalled();
  });
});

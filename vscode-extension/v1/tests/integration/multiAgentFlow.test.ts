import { MultiAgentCoordinator } from '../../src/services/MultiAgentCoordinator';
import { AgentRole, AgentStatus, SpecialistAgent, TaskResult } from '../../src/models/AgentRole';
import { ConfigService } from '../../src/services/ConfigService';
import { MetricsService } from '../../src/services/MetricsService';
import { TraceService } from '../../src/services/TraceService';

jest.mock('../../src/services/ConfigService');

describe('Multi-Agent Integration Flow', () => {
  let coordinator: MultiAgentCoordinator;
  let mockConfigService: jest.Mocked<ConfigService>;
  let mockMetricsService: jest.Mocked<MetricsService>;
  let mockTraceService: jest.Mocked<TraceService>;

  beforeEach(() => {
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

    const result = await coordinator.orchestrate('Do A\nDo B');

    expect(result.subtaskResults.length).toBe(2);
    expect(states).toContain('decomposing');
    expect(states).toContain('complete');
    expect(progress[progress.length - 1]).toBe(100);
    expect(mockTraceService.recordInterAgentMessage).toHaveBeenCalled();
  });
});

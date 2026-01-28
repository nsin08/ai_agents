import { MultiAgentCoordinator } from '../../src/services/MultiAgentCoordinator';
import { AgentService } from '../../src/services/AgentService';
import { AgentRole, AgentStatus, SpecialistAgent, TaskResult } from '../../src/models/AgentRole';
import { ConfigService } from '../../src/services/ConfigService';
import { MetricsService } from '../../src/services/MetricsService';
import { TraceService } from '../../src/services/TraceService';

jest.mock('../../src/services/ConfigService');

describe('MultiAgentCoordinator', () => {
  let coordinator: MultiAgentCoordinator;
  let mockAgentService: jest.Mocked<AgentService>;
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

    mockAgentService = {
      sendMessage: jest.fn(async (message: string) => `mock: ${message}`)
    } as any;

    mockMetricsService = {
      startConversation: jest.fn(),
      endConversation: jest.fn(),
      recordAgentExecution: jest.fn(),
      recordCoordinatorOverhead: jest.fn()
    } as any;

    mockTraceService = {
      startTrace: jest.fn(),
      endTrace: jest.fn(),
      recordCoordinatorState: jest.fn(),
      recordInterAgentMessage: jest.fn(),
      recordAgentReasoning: jest.fn()
    } as any;

    coordinator = new MultiAgentCoordinator(
      mockAgentService,
      mockMetricsService,
      mockTraceService,
      mockConfigService
    );
  });

  const buildAgent = (role: AgentRole, capabilities: any[] = []): SpecialistAgent => ({
    id: `${role}-1`,
    role,
    status: AgentStatus.IDLE,
    config: mockConfigService.getConfig(),
    capabilities,
    execute: jest.fn(async (task: string): Promise<TaskResult> => ({
      id: `result-${role}`,
      subtaskId: 'subtask-1',
      content: `${role}:${task}`,
      success: true,
      duration: 10,
      tokensUsed: { input: 10, output: 10 }
    }))
  });

  it('orchestrates subtasks and returns combined output', async () => {
    coordinator.registerAgent(AgentRole.PLANNER, buildAgent(AgentRole.PLANNER));
    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    const result = await coordinator.orchestrate('Do A\nDo B');

    expect(result.subtaskResults.length).toBe(2);
    expect(result.finalOutput).toContain('executor:');
    expect(mockMetricsService.startConversation).toHaveBeenCalled();
    expect(mockTraceService.startTrace).toHaveBeenCalled();
  });

  it('routes to verifier when enabled and task mentions verify', async () => {
    coordinator = new MultiAgentCoordinator(
      mockAgentService,
      mockMetricsService,
      mockTraceService,
      mockConfigService,
      { enableVerifier: true }
    );

    const verifier = buildAgent(AgentRole.VERIFIER, [
      { name: 'validation', proficiency: 90, domains: ['general'] }
    ]);
    coordinator.registerAgent(AgentRole.VERIFIER, verifier);
    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    const result = await coordinator.orchestrate('Verify the output');
    expect(result.subtaskResults[0].content).toContain('verifier');
  });

  it('executes dependent subtasks in order', async () => {
    const callOrder: string[] = [];
    const execAgent = buildAgent(AgentRole.EXECUTOR, [
      { name: 'implementation', proficiency: 90, domains: ['general'] }
    ]);
    execAgent.execute = jest.fn(async (task: string): Promise<TaskResult> => {
      callOrder.push(task);
      return {
        id: 'result-order',
        subtaskId: 'subtask',
        content: `done:${task}`,
        success: true,
        duration: 5,
        tokensUsed: { input: 5, output: 5 }
      };
    });

    coordinator.registerAgent(AgentRole.EXECUTOR, execAgent);

    await coordinator.orchestrate('1. First task\n2. Second task after 1');

    expect(callOrder[0]).toContain('First task');
    expect(callOrder[1]).toContain('Second task');
  });

  it('falls back to single-agent when disabled', async () => {
    coordinator.setMultiAgentEnabled(false);

    const result = await coordinator.orchestrate('Simple task');

    expect(result.finalOutput).toContain('mock: Simple task');
    expect(result.subtaskResults).toHaveLength(0);
  });

  it('records agent response messages', async () => {
    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    await coordinator.orchestrate('Do the task');

    const log = coordinator.getMessageLog();
    expect(log.some(entry => entry.type === 'task-response')).toBe(true);
  });
});

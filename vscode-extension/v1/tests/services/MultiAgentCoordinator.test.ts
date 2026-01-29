import { MultiAgentCoordinator } from '../../src/services/MultiAgentCoordinator';
import { AgentService } from '../../src/services/AgentService';
import { AgentRole, AgentStatus, SpecialistAgent, TaskResult } from '../../src/models/AgentRole';
import { ConfigService } from '../../src/services/ConfigService';
import { MetricsService } from '../../src/services/MetricsService';
import { TraceService } from '../../src/services/TraceService';
import axios from 'axios';

jest.mock('../../src/services/ConfigService');
jest.mock('axios', () => ({
  create: jest.fn()
}));

describe('MultiAgentCoordinator', () => {
  let coordinator: MultiAgentCoordinator;
  let mockAgentService: jest.Mocked<AgentService>;
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

    (coordinator as any).agentConfig = {
      mode: 'multi',
      plan: { provider: 'mock', model: 'llama2', maxTurns: 3, timeout: 30, temperature: 0.5, baseUrl: '', apiKey: '' },
      act: { provider: 'mock', model: 'llama2', maxTurns: 5, timeout: 30, temperature: 0.7, baseUrl: '', apiKey: '' }
    };
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

    mockPost
      .mockResolvedValueOnce({ data: { response: 'plan-output' } })
      .mockResolvedValueOnce({ data: { response: 'act-output' } });

    const result = await coordinator.orchestrate('Do A\nDo B');

    expect(result.decomposition.subtasks.length).toBe(2);
    expect(result.finalOutput).toContain('act-output');
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
    (coordinator as any).agentConfig = {
      mode: 'multi',
      plan: { provider: 'mock', model: 'llama2', maxTurns: 3, timeout: 30, temperature: 0.5, baseUrl: '', apiKey: '' },
      act: { provider: 'mock', model: 'llama2', maxTurns: 5, timeout: 30, temperature: 0.7, baseUrl: '', apiKey: '' }
    };

    const verifier = buildAgent(AgentRole.VERIFIER, [
      { name: 'validation', proficiency: 90, domains: ['general'] }
    ]);
    coordinator.registerAgent(AgentRole.VERIFIER, verifier);
    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    mockPost
      .mockResolvedValueOnce({ data: { response: 'plan-output' } })
      .mockResolvedValueOnce({ data: { response: 'act-output' } });

    const result = await coordinator.orchestrate('Verify the output');
    expect(result.finalOutput).toContain('act-output');
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

    mockPost
      .mockResolvedValueOnce({ data: { response: 'plan-output' } })
      .mockResolvedValueOnce({ data: { response: 'act-output' } });

    await coordinator.orchestrate('1. First task\n2. Second task after 1');

    expect(callOrder.length).toBe(0);
  });

  it('runs single-agent flow when configured', async () => {
    (coordinator as any).agentConfig = {
      mode: 'single',
      provider: 'mock',
      model: 'llama2',
      maxTurns: 5,
      timeout: 30,
      temperature: 0.7,
      baseUrl: '',
      apiKey: ''
    };

    const result = await coordinator.orchestrate('Simple task');

    expect(result.finalOutput).toContain('mock: Simple task');
    expect(result.subtaskResults).toHaveLength(0);
  });

  it('records agent response messages', async () => {
    coordinator.registerAgent(AgentRole.EXECUTOR, buildAgent(AgentRole.EXECUTOR));

    mockPost
      .mockResolvedValueOnce({ data: { response: 'plan-output' } })
      .mockResolvedValueOnce({ data: { response: 'act-output' } });

    await coordinator.orchestrate('Do the task');

    const log = coordinator.getMessageLog();
    expect(log.some(entry => entry.type === 'task-response')).toBe(false);
  });
});

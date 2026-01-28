import { AgentService } from '../AgentService';
import { ConfigService } from '../ConfigService';
import {
  AgentCapability,
  AgentStatus,
  TaskResult
} from '../../models/AgentRole';

export class ExecutorAgent {
  private agentService: AgentService;
  private configService: ConfigService;
  private status: AgentStatus = AgentStatus.IDLE;

  constructor(agentService: AgentService, configService: ConfigService) {
    this.agentService = agentService;
    this.configService = configService;
  }

  public async execute(_task: string): Promise<TaskResult> {
    this.status = AgentStatus.PROCESSING;
    const start = Date.now();
    try {
      const response = await this.agentService.sendMessage(`[Executor] ${_task}`);
      const duration = Date.now() - start;
      this.status = AgentStatus.COMPLETED;
      return this.buildResult(response, duration);
    } catch (error) {
      this.status = AgentStatus.ERROR;
      throw error;
    }
  }

  public getCapabilities(): AgentCapability[] {
    return [
      { name: 'implementation', proficiency: 90, domains: ['backend', 'frontend'] },
      { name: 'coding', proficiency: 85, domains: ['general'] },
      { name: 'design', proficiency: 75, domains: ['general'] }
    ];
  }

  public getStatus(): AgentStatus {
    return this.status;
  }

  private buildResult(content: string, duration: number): TaskResult {
    const estimatedTokens = Math.ceil(content.length / 4);
    return {
      id: `executor-result-${Date.now()}`,
      subtaskId: 'executor',
      content,
      success: true,
      duration,
      tokensUsed: {
        input: estimatedTokens,
        output: estimatedTokens
      },
      confidence: 0.85
    };
  }
}

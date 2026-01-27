import { AgentService } from '../AgentService';
import { ConfigService } from '../ConfigService';
import {
  AgentCapability,
  AgentStatus,
  TaskResult
} from '../../models/AgentRole';

export class PlannerAgent {
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
      const response = await this.agentService.sendMessage(`[Planner] ${_task}`);
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
      { name: 'task-decomposition', proficiency: 90, domains: ['planning'] },
      { name: 'planning', proficiency: 85, domains: ['general'] },
      { name: 'analysis', proficiency: 80, domains: ['general'] }
    ];
  }

  public getStatus(): AgentStatus {
    return this.status;
  }

  private buildResult(content: string, duration: number): TaskResult {
    const estimatedTokens = Math.ceil(content.length / 4);
    return {
      id: `planner-result-${Date.now()}`,
      subtaskId: 'planner',
      content,
      success: true,
      duration,
      tokensUsed: {
        input: estimatedTokens,
        output: estimatedTokens
      },
      confidence: 0.8
    };
  }
}

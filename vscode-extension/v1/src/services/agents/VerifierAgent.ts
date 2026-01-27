import { AgentService } from '../AgentService';
import { ConfigService } from '../ConfigService';
import {
  AgentCapability,
  AgentStatus,
  TaskResult
} from '../../models/AgentRole';

export class VerifierAgent {
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
      const response = await this.agentService.sendMessage(`[Verifier] ${_task}`);
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
      { name: 'quality-assurance', proficiency: 85, domains: ['general'] },
      { name: 'validation', proficiency: 80, domains: ['general'] },
      { name: 'security-audit', proficiency: 75, domains: ['backend'] }
    ];
  }

  public getStatus(): AgentStatus {
    return this.status;
  }

  private buildResult(content: string, duration: number): TaskResult {
    const estimatedTokens = Math.ceil(content.length / 4);
    return {
      id: `verifier-result-${Date.now()}`,
      subtaskId: 'verifier',
      content,
      success: true,
      duration,
      tokensUsed: {
        input: estimatedTokens,
        output: estimatedTokens
      },
      confidence: 0.75
    };
  }
}

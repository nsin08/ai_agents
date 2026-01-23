/**
 * Trace data models for agent state visualization.
 * Captures orchestrator state transitions, tool executions, and debugging context.
 */

export type AgentState = 'Observe' | 'Plan' | 'Act' | 'Verify';

export interface TraceEntry {
  /** Unique trace entry ID */
  id: string;
  
  /** Timestamp of state transition */
  timestamp: Date;
  
  /** Agent orchestrator state */
  state: AgentState;
  
  /** Turn number (1-indexed) */
  turn: number;
  
  /** Conversation ID this trace belongs to */
  conversationId: string;
  
  /** Input to this state (e.g., user message for Observe) */
  input?: string;
  
  /** Output from this state (e.g., plan description for Plan) */
  output?: string;
  
  /** Tools invoked during this state (mainly for Act) */
  toolsUsed?: ToolExecution[];
  
  /** Duration of this state in milliseconds */
  duration: number;
  
  /** Error if state transition failed */
  error?: TraceError;
  
  /** Additional metadata for debugging */
  metadata?: Record<string, any>;
}

export interface ToolExecution {
  /** Tool name */
  name: string;
  
  /** Tool input parameters */
  input: Record<string, any>;
  
  /** Tool output/result */
  output?: any;
  
  /** Execution duration (ms) */
  duration: number;
  
  /** Success/failure status */
  status: 'success' | 'failure';
  
  /** Error if tool execution failed */
  error?: string;
}

export interface TraceError {
  /** Error message */
  message: string;
  
  /** Error type/code */
  type: string;
  
  /** Full stack trace (if available) */
  stackTrace?: string;
  
  /** Context at time of error */
  context?: Record<string, any>;
}

export interface ConversationTrace {
  /** Conversation ID */
  conversationId: string;
  
  /** All trace entries for this conversation */
  entries: TraceEntry[];
  
  /** Conversation start time */
  startTime: Date;
  
  /** Conversation end time (if ended) */
  endTime?: Date;
  
  /** Total turns in conversation */
  totalTurns: number;
  
  /** Provider used */
  provider: string;
  
  /** Model used */
  model: string;
}

export interface TraceTreeNode {
  /** Node ID (for tree rendering) */
  id: string;
  
  /** Display label */
  label: string;
  
  /** Node type for icon selection */
  type: 'conversation' | 'turn' | 'state' | 'tool' | 'error';
  
  /** Child nodes */
  children?: TraceTreeNode[];
  
  /** Underlying trace data */
  data?: TraceEntry | ToolExecution | TraceError;
  
  /** Collapsible state */
  collapsibleState?: 'collapsed' | 'expanded' | 'none';
  
  /** Tooltip text */
  tooltip?: string;
  
  /** Icon name from VSCode icons */
  iconPath?: string;
}

export interface TraceFilter {
  /** Filter by conversation ID */
  conversationId?: string;
  
  /** Filter by state */
  state?: AgentState;
  
  /** Filter by turn range */
  turnRange?: {
    from: number;
    to: number;
  };
  
  /** Filter by time range */
  timeRange?: {
    from: Date;
    to: Date;
  };
  
  /** Show only entries with errors */
  errorsOnly?: boolean;
  
  /** Show only entries with tools */
  toolsOnly?: boolean;
}

export interface TraceSummary {
  /** Total traces captured */
  totalTraces: number;
  
  /** Total turns across all conversations */
  totalTurns: number;
  
  /** Average turn duration (ms) */
  averageTurnDuration: number;
  
  /** Most common state (excluding Observe) */
  mostCommonState: AgentState;
  
  /** Total errors encountered */
  totalErrors: number;
  
  /** Total tool executions */
  totalToolExecutions: number;
  
  /** Success rate (%) */
  successRate: number;
}

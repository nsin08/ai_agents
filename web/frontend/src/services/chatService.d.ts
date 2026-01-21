// Type declarations for Chat API Service

interface MessageData {
  message: string;
  sessionId?: string;
}

interface ChatResponse {
  success: boolean;
  response: string;
  metadata: Record<string, any>;
}

interface SessionData {
  session_id: string;
  messages: Array<{
    role: string;
    content: string;
  }>;
}

declare const chatService: {
  createSession(): Promise<string>;
  sendMessage(data: MessageData): Promise<ChatResponse>;
  getSession(sessionId: string): Promise<SessionData>;
};

export default chatService;


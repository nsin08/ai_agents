import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";
import chatService from "../services/chatService";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string | Date;
  metadata?: Record<string, unknown>;
}

interface ProviderConfig {
  provider: string;
  model: string;
  maxTurns: number;
  timeout: number;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [config, setConfig] = useState<ProviderConfig>({
    provider: "mock",
    model: "mock-model",
    maxTurns: 3,
    timeout: 30,
  });
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session on mount
  useEffect(() => {
    initializeSession();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const initializeSession = async () => {
    try {
      const newSessionId = await chatService.createSession();
      setSessionId(newSessionId);
    } catch (error) {
      console.error("Failed to initialize session:", error);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) {
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Send to API
      const response = await chatService.sendMessage({
        message: inputValue,
        sessionId: sessionId || undefined,
      });

      // Add assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to send message"}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    initializeSession();
  };

  const handleConfigChange = (
    key: keyof ProviderConfig,
    value: string | number
  ) => {
    setConfig((prev) => ({
      ...prev,
      [key]: typeof prev[key] === "number" ? Number(value) : value,
    }));
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Agent Chat</h1>
        <div className="header-actions">
          <button
            className="settings-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            ⚙️
          </button>
          <button
            className="clear-btn"
            onClick={handleClearChat}
            title="Clear chat"
          >
            🗑️
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="settings-panel">
          <h3>Settings</h3>
          <div className="settings-grid">
            <div className="setting-item">
              <label>Provider</label>
              <select
                value={config.provider}
                onChange={(e) => handleConfigChange("provider", e.target.value)}
              >
                <option value="mock">Mock</option>
                <option value="ollama">Ollama</option>
              </select>
            </div>
            <div className="setting-item">
              <label>Model</label>
              <input
                type="text"
                value={config.model}
                onChange={(e) => handleConfigChange("model", e.target.value)}
              />
            </div>
            <div className="setting-item">
              <label>Max Turns</label>
              <input
                type="number"
                min="1"
                max="10"
                value={config.maxTurns}
                onChange={(e) => handleConfigChange("maxTurns", e.target.value)}
              />
            </div>
            <div className="setting-item">
              <label>Timeout (s)</label>
              <input
                type="number"
                min="5"
                max="300"
                value={config.timeout}
                onChange={(e) => handleConfigChange("timeout", e.target.value)}
              />
            </div>
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Welcome to Agent Chat</h2>
            <p>Start a conversation with the AI agent</p>
            {sessionId && (
              <p className="session-id">Session: {sessionId.slice(0, 8)}...</p>
            )}
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`message message-${msg.role}`}>
              <div className="message-content">
                <p>{msg.content}</p>
                {msg.metadata && (
                  <details className="message-metadata">
                    <summary>Metadata</summary>
                    <pre>{JSON.stringify(msg.metadata, null, 2)}</pre>
                  </details>
                )}
              </div>
              <span className="message-time">
                {typeof msg.timestamp === 'string' 
                  ? new Date(msg.timestamp).toLocaleTimeString()
                  : msg.timestamp.toLocaleTimeString()}
              </span>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message message-assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default Chat;

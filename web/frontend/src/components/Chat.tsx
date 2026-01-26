import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";
import chatService from "../services/chatService";
import SettingsDrawer from "./SettingsDrawer";
import type { ProviderType, ProviderInfo } from "../types/providers";
import providerService from "../services/providerService";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string | Date;
  metadata?: Record<string, unknown>;
}

interface ProviderConfig {
  provider: ProviderType;
  model: string;
  maxTurns: number;
  timeout: number;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [config, setConfig] = useState<ProviderConfig>({
    provider: "mock" as ProviderType,
    model: "mock-model",
    maxTurns: 3,
    timeout: 30,
  });
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session and load providers on mount
  useEffect(() => {
    initializeSession();
    loadProviders();
  }, []);

  // Load models when provider changes
  useEffect(() => {
    if (config.provider) {
      (async () => {
        setIsLoadingModels(true);
        try {
          const providerInfo = providers.find((p) => p.id === config.provider);
          if (providerInfo && providerInfo.supported_models) {
            setAvailableModels(providerInfo.supported_models);
            // Set first model as default if current model not in list
            if (!providerInfo.supported_models.includes(config.model)) {
              setConfig((prev) => ({
                ...prev,
                model: providerInfo.supported_models![0],
              }));
            }
          } else {
            setAvailableModels([]);
          }
        } catch (error) {
          console.error("Failed to load models:", error);
          setAvailableModels([]);
        } finally {
          setIsLoadingModels(false);
        }
      })();
    }
  }, [config.provider, providers, config.model]);

  const loadProviders = async () => {
    try {
      console.log("Loading providers...");
      const data = await providerService.listProviders(true);
      console.log("Providers loaded:", data);
      setProviders(data);
    } catch (error) {
      console.error("Failed to load providers:", error);
    }
  };

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

    // Store message before clearing input
    const messageContent = inputValue;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Send to API with provider config (NO API KEY - loaded from backend env)
      const response = await chatService.sendMessage({
        message: messageContent,
        provider: config.provider,
        model: config.model,
        config: {
          max_turns: config.maxTurns,
          timeout: config.timeout,
        },
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

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-left">
          <h1>Agent Chat</h1>
          <div className="provider-badge">
            {config.provider} {config.model && `→ ${config.model}`}
          </div>
        </div>
        <div className="header-actions">
          <button
            className="settings-btn"
            onClick={() => setShowSettings(true)}
            title="Configuration Settings"
            aria-label="Open settings"
          >
            ⚙️ Settings
          </button>
          <button
            className="clear-btn"
            onClick={handleClearChat}
            title="Clear chat"
            aria-label="Clear chat"
          >
            🗑️
          </button>
        </div>
      </div>

      <SettingsDrawer
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        selectedProvider={config.provider}
        onProviderChange={(provider) => {
          setConfig((prev) => ({ ...prev, provider: provider as ProviderType }));
        }}
        selectedModel={config.model}
        onModelChange={(model) => {
          setConfig((prev) => ({ ...prev, model }));
        }}
        availableProviders={providers}
        availableModels={availableModels}
        isLoadingModels={isLoadingModels}
      />

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>Welcome to Agent Chat</h2>
            <p>Configure your provider using the Settings button →</p>
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
          disabled={isLoading || !config.model}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isLoading || !inputValue.trim() || !config.model}
          title={!config.model ? "Select a model in settings first" : ""}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default Chat;

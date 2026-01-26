import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";
import chatService from "../services/chatService";
import SettingsDrawer from "./SettingsDrawer";
import DebugPanel from "./DebugPanel";
import ConfigPanel from "./ConfigPanel";
import ConversationExport from "./ConversationExport";
import ThemeToggle from "./ThemeToggle";
import type { ProviderType, ProviderInfo } from "../types/providers";
import type { AgentConfig, DebugMetadata } from "../types/config";
import providerService from "../services/providerService";
import configService from "../services/configService";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string | Date;
  metadata?: Record<string, unknown>;
}

interface ChatResponse {
  response: string;
  metadata?: Record<string, unknown>;
  debug_metadata?: DebugMetadata;
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
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [showConfigPanel, setShowConfigPanel] = useState(false);
  const [debugMetadata, setDebugMetadata] = useState<DebugMetadata | null>(null);
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    max_turns: 3,
    temperature: 0.7,
    timeout_seconds: 30,
    system_prompt: null,
    enable_debug: false,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session and load providers and config on mount
  useEffect(() => {
    initializeSession();
    loadProviders();
    loadAgentConfig();
  }, []);

  const loadAgentConfig = async () => {
    try {
      const config = await configService.getDefaultConfig();
      setAgentConfig(config.config);
    } catch (error) {
      console.error("Failed to load agent config:", error);
    }
  };

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
      // Send to API with provider config and agent config
      const response: ChatResponse = await chatService.sendMessage({
        message: messageContent,
        provider: config.provider,
        model: config.model,
        config: {
          max_turns: agentConfig.max_turns,
          temperature: agentConfig.temperature,
          timeout: agentConfig.timeout_seconds,
          system_prompt: agentConfig.system_prompt,
          enable_debug: agentConfig.enable_debug,
        },
        sessionId: sessionId || undefined,
      });

      // Store debug metadata if available
      if (response.debug_metadata) {
        setDebugMetadata(response.debug_metadata);
      }

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
    setDebugMetadata(null);
    initializeSession();
  };

  const handleConfigChange = async (newConfig: AgentConfig) => {
    setAgentConfig(newConfig);
    // Sync max_turns and timeout with provider config for backwards compatibility
    setConfig((prev) => ({
      ...prev,
      maxTurns: newConfig.max_turns,
      timeout: newConfig.timeout_seconds,
    }));
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape to close modals
      if (e.key === "Escape") {
        setShowDebugPanel(false);
        setShowConfigPanel(false);
        setShowSettings(false);
      }
      // Ctrl+D to toggle debug panel (if debug metadata available)
      if (e.ctrlKey && e.key === "d" && debugMetadata) {
        e.preventDefault();
        setShowDebugPanel((prev) => !prev);
      }
      // Ctrl+K to open config panel
      if (e.ctrlKey && e.key === "k") {
        e.preventDefault();
        setShowConfigPanel(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [debugMetadata]);

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
          <ThemeToggle />
          <button
            className="config-btn"
            onClick={() => setShowConfigPanel(true)}
            title="Agent Configuration (Ctrl+K)"
            aria-label="Open agent configuration"
          >
            🎛️ Config
          </button>
          {debugMetadata && agentConfig.enable_debug && (
            <button
              className="debug-btn"
              onClick={() => setShowDebugPanel(true)}
              title="Debug Info (Ctrl+D)"
              aria-label="Open debug panel"
            >
              🐛 Debug
            </button>
          )}
          <button
            className="settings-btn"
            onClick={() => setShowSettings(true)}
            title="Provider Settings"
            aria-label="Open provider settings"
          >
            ⚙️ Settings
          </button>
          <ConversationExport messages={messages} />
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

      <DebugPanel
        metadata={debugMetadata}
        isOpen={showDebugPanel}
        onClose={() => setShowDebugPanel(false)}
      />

      <ConfigPanel
        isOpen={showConfigPanel}
        onClose={() => setShowConfigPanel(false)}
        onConfigChange={handleConfigChange}
        currentConfig={agentConfig}
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
        <textarea
          className="chat-input"
          placeholder="Type your message... (Shift+Enter for newline, Enter to send)"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage(e);
            }
          }}
          disabled={isLoading || !config.model}
          rows={1}
        />
        <button
          type="submit"
          className="send-btn"
          disabled={isLoading || !inputValue.trim() || !config.model}
          title={!config.model ? "Select a model in settings first" : "Send message (Enter)"}
          aria-label="Send message"
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default Chat;

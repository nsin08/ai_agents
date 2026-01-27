import React from "react";
import "./DebugPanel.css";
import type { DebugMetadata } from "../types/config";

interface DebugPanelProps {
  metadata: DebugMetadata | null;
  isOpen: boolean;
  onClose: () => void;
}

const DebugPanel: React.FC<DebugPanelProps> = ({ metadata, isOpen, onClose }) => {
  if (!isOpen || !metadata) {
    return null;
  }

  const copyToClipboard = () => {
    const debugInfo = JSON.stringify(metadata, null, 2);
    navigator.clipboard.writeText(debugInfo).then(
      () => {
        alert("Debug info copied to clipboard!");
      },
      (err) => {
        console.error("Failed to copy: ", err);
        alert("Failed to copy debug info");
      }
    );
  };

  return (
    <div className="debug-panel-overlay" onClick={onClose}>
      <div className="debug-panel" onClick={(e) => e.stopPropagation()}>
        <div className="debug-panel-header">
          <h3>🔧 Debug Panel</h3>
          <button className="close-button" onClick={onClose} aria-label="Close debug panel">
            ✕
          </button>
        </div>

        <div className="debug-panel-content">
          {/* Performance Metrics */}
          <section className="debug-section">
            <h4>⚡ Performance</h4>
            <div className="debug-grid">
              <div className="debug-item">
                <span className="debug-label">Latency:</span>
                <span className="debug-value">{metadata.latency_ms.toFixed(2)} ms</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Tokens Used:</span>
                <span className="debug-value">{metadata.tokens_used ?? "N/A"}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Input Tokens:</span>
                <span className="debug-value">{metadata.tokens_input ?? "N/A"}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Output Tokens:</span>
                <span className="debug-value">{metadata.tokens_output ?? "N/A"}</span>
              </div>
            </div>
          </section>

          {/* Configuration */}
          <section className="debug-section">
            <h4>⚙️ Configuration</h4>
            <div className="debug-grid">
              <div className="debug-item">
                <span className="debug-label">Provider:</span>
                <span className="debug-value">{metadata.provider}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Model:</span>
                <span className="debug-value">{metadata.model}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Temperature:</span>
                <span className="debug-value">{metadata.temperature}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Max Turns:</span>
                <span className="debug-value">{metadata.max_turns}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Current Turn:</span>
                <span className="debug-value">{metadata.current_turn}</span>
              </div>
              <div className="debug-item">
                <span className="debug-label">Backend:</span>
                <span className="debug-value">{metadata.backend}</span>
              </div>
            </div>
          </section>

          {/* Agent State */}
          {metadata.agent_state && (
            <section className="debug-section">
              <h4>🤖 Agent State</h4>
              <div className="debug-item">
                <span className="debug-label">Current State:</span>
                <span className="debug-value state-badge">{metadata.agent_state}</span>
              </div>
            </section>
          )}

          {/* Reasoning */}
          {metadata.reasoning && (
            <section className="debug-section">
              <h4>💭 Reasoning Chain</h4>
              <pre className="debug-code">{metadata.reasoning}</pre>
            </section>
          )}

          {/* Tool Calls */}
          {metadata.tool_calls && metadata.tool_calls.length > 0 && (
            <section className="debug-section">
              <h4>🔧 Tool Calls</h4>
              <ul className="tool-list">
                {metadata.tool_calls.map((tool, index) => (
                  <li key={index} className="tool-item">
                    {tool}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Errors */}
          {metadata.errors && metadata.errors.length > 0 && (
            <section className="debug-section error-section">
              <h4>❌ Errors</h4>
              <ul className="error-list">
                {metadata.errors.map((error, index) => (
                  <li key={index} className="error-item">
                    {error}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Raw JSON */}
          <section className="debug-section">
            <h4>📄 Raw JSON</h4>
            <pre className="debug-code">{JSON.stringify(metadata, null, 2)}</pre>
          </section>
        </div>

        <div className="debug-panel-footer">
          <button className="copy-button" onClick={copyToClipboard}>
            📋 Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;

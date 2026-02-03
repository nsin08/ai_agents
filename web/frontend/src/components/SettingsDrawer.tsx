import React from 'react';
import './SettingsDrawer.css';

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedProvider: string;
  onProviderChange: (provider: string) => void;
  selectedModel: string;
  onModelChange: (model: string) => void;
  availableProviders: any[];
  availableModels: string[];
  isLoadingModels: boolean;
}

const SettingsDrawer: React.FC<SettingsDrawerProps> = ({
  isOpen,
  onClose,
  selectedProvider,
  onProviderChange,
  selectedModel,
  onModelChange,
  availableProviders,
  availableModels,
  isLoadingModels
}) => {
  console.log("SettingsDrawer rendered:", { isOpen, availableProvidersCount: availableProviders.length, availableProviders });
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="settings-backdrop" onClick={onClose} />
      
      {/* Drawer */}
      <div className="settings-drawer">
        <div className="settings-header">
          <h2>Configuration</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="settings-content">
          {/* Provider Selection */}
          <div className="setting-group">
            <label htmlFor="provider-select" className="setting-label">
              LLM Provider
            </label>
            <select
              id="provider-select"
              value={selectedProvider}
              onChange={(e) => onProviderChange(e.target.value)}
              className="setting-select"
            >
              <option value="">Select a provider...</option>
              {availableProviders.map((provider) => (
                <option
                  key={provider.id}
                  value={provider.id}
                  disabled={provider.status === 'coming_soon'}
                >
                  {provider.name}
                  {provider.status === 'coming_soon' ? ' (Coming Soon)' : ''}
                </option>
              ))}
            </select>
            {selectedProvider && (
              <div className="provider-info">
                <p>
                  {availableProviders.find(p => p.id === selectedProvider)?.requires_api_key
                    ? '🔐 Requires API key from .env file'
                    : '✓ No authentication required'}
                </p>
              </div>
            )}
          </div>

          {/* Model Selection */}
          {selectedProvider && (
            <div className="setting-group">
              <label htmlFor="model-select" className="setting-label">
                Model
              </label>
              {isLoadingModels ? (
                <div className="loading-spinner">Loading models...</div>
              ) : availableModels.length > 0 ? (
                <select
                  id="model-select"
                  value={selectedModel}
                  onChange={(e) => onModelChange(e.target.value)}
                  className="setting-select"
                >
                  <option value="">Select a model...</option>
                  {availableModels.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="no-models">No models available</div>
              )}
            </div>
          )}

          {/* Configuration Info */}
          <div className="settings-info">
            <h3>Configuration</h3>
            <ul className="info-list">
              <li>
                <strong>API Credentials:</strong> Loaded from environment configuration
              </li>
              <li>
                <strong>Models:</strong> Fetched dynamically from provider APIs
              </li>
              <li>
                <strong>No Storage:</strong> Credentials never stored locally
              </li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
};

export default SettingsDrawer;

// ProviderSelector Component
import React, { useEffect, useState } from "react";
import providerService from "../services/providerService";
import type { ProviderInfo, ProviderType } from "../types/providers";
import "./ProviderSelector.css";

interface ProviderSelectorProps {
  selectedProvider: ProviderType;
  selectedModel: string;
  onProviderChange: (provider: ProviderType, model: string) => void;
  disabled?: boolean;
}

const ProviderSelector: React.FC<ProviderSelectorProps> = ({
  selectedProvider,
  selectedModel,
  onProviderChange,
  disabled = false,
}) => {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await providerService.listProviders(true);
      setProviders(data);
      setError(null);
    } catch (err) {
      setError("Failed to load providers");
      console.error("Provider load error:", err);
    } finally {
      setLoading(false);
    }
  };

  const currentProvider = providers.find((p) => p.id === selectedProvider);
  const availableModels = currentProvider?.supported_models || [];
  const isProviderAvailable = currentProvider?.status === "available";

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newProvider = e.target.value as ProviderType;
    const provider = providers.find((p) => p.id === newProvider);
    const defaultModel = provider?.supported_models[0] || "mock-model";
    onProviderChange(newProvider, defaultModel);
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onProviderChange(selectedProvider, e.target.value);
  };

  if (loading) {
    return <div className="provider-selector loading">Loading providers...</div>;
  }

  if (error) {
    return (
      <div className="provider-selector error">
        {error}{" "}
        <button onClick={loadProviders} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="provider-selector">
      <div className="selector-group">
        <label htmlFor="provider-select">Provider:</label>
        <select
          id="provider-select"
          value={selectedProvider}
          onChange={handleProviderChange}
          disabled={disabled}
          className="provider-dropdown"
        >
          {providers.map((provider) => (
            <option
              key={provider.id}
              value={provider.id}
              disabled={provider.status !== "available"}
            >
              {provider.name}
              {provider.status === "coming_soon" && " (Coming Soon)"}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label htmlFor="model-select">Model:</label>
        <select
          id="model-select"
          value={selectedModel}
          onChange={handleModelChange}
          disabled={disabled || !isProviderAvailable}
          className="model-dropdown"
        >
          {availableModels.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {currentProvider && (
        <div className="provider-info">
          {currentProvider.status !== "available" && (
            <span className="status-badge coming-soon">Coming Soon</span>
          )}
          {currentProvider.requires_api_key && (
            <span className="info-text">⚠️ Requires API key</span>
          )}
        </div>
      )}
    </div>
  );
};

export default ProviderSelector;

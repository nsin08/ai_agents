// APIKeyInput Component
import React, { useState } from "react";
import providerService from "../services/providerService";
import type { ProviderType } from "../types/providers";
import "./APIKeyInput.css";

interface APIKeyInputProps {
  provider: ProviderType;
  model: string;
  requiresKey: boolean;
  onKeyChange: (apiKey: string) => void;
  disabled?: boolean;
}

const APIKeyInput: React.FC<APIKeyInputProps> = ({
  provider,
  model,
  requiresKey,
  onKeyChange,
  disabled = false,
}) => {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    message: string;
  } | null>(null);

  if (!requiresKey) {
    return null;
  }

  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newKey = e.target.value;
    setApiKey(newKey);
    onKeyChange(newKey);
    setValidationResult(null); // Clear validation when key changes
  };

  const handleValidate = async () => {
    if (!apiKey) {
      setValidationResult({
        valid: false,
        message: "Please enter an API key",
      });
      return;
    }

    setValidating(true);
    try {
      const result = await providerService.validateApiKey({
        provider,
        api_key: apiKey,
        model,
      });
      setValidationResult(result);
    } catch (error) {
      setValidationResult({
        valid: false,
        message: "Validation failed: " + (error as Error).message,
      });
    } finally {
      setValidating(false);
    }
  };

  const handleClear = () => {
    setApiKey("");
    onKeyChange("");
    setValidationResult(null);
  };

  return (
    <div className="api-key-input">
      <label htmlFor="api-key-field" className="key-label">
        API Key <span className="required">*</span>
      </label>

      <div className="key-input-group">
        <input
          id="api-key-field"
          type={showKey ? "text" : "password"}
          value={apiKey}
          onChange={handleKeyChange}
          placeholder={`Enter ${provider} API key...`}
          disabled={disabled}
          className="key-field"
        />

        <button
          type="button"
          onClick={() => setShowKey(!showKey)}
          className="toggle-btn"
          disabled={disabled}
          title={showKey ? "Hide key" : "Show key"}
        >
          {showKey ? "👁️" : "🔒"}
        </button>

        <button
          type="button"
          onClick={handleValidate}
          disabled={disabled || validating || !apiKey}
          className="validate-btn"
        >
          {validating ? "Validating..." : "Validate"}
        </button>

        {apiKey && (
          <button
            type="button"
            onClick={handleClear}
            className="clear-btn"
            disabled={disabled}
            title="Clear key"
          >
            ✕
          </button>
        )}
      </div>

      {validationResult && (
        <div
          className={`validation-result ${
            validationResult.valid ? "valid" : "invalid"
          }`}
        >
          <span className="result-icon">
            {validationResult.valid ? "✓" : "✗"}
          </span>
          <span className="result-message">{validationResult.message}</span>
        </div>
      )}

      <div className="key-help-text">
        API key is required for {provider}. It will not be stored permanently.
      </div>
    </div>
  );
};

export default APIKeyInput;

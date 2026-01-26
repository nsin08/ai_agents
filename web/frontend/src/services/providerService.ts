// Provider API Service
import type {
  ProviderInfo,
  ValidateKeyRequest,
  ValidateKeyResponse,
} from "../types/providers";

const API_BASE_URL = "http://localhost:8000";

class ProviderService {
  /**
   * Get list of available LLM providers
   * @param includeModels - Whether to include model lists
   * @returns Promise resolving to array of ProviderInfo
   */
  async listProviders(includeModels: boolean = false): Promise<ProviderInfo[]> {
    const response = await fetch(
      `${API_BASE_URL}/providers?include_models=${includeModels}`
    );

    if (!response.ok) {
      throw new Error(`Failed to list providers: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get available providers (status === "available" only)
   * @param includeModels - Whether to include model lists
   * @returns Promise resolving to array of available ProviderInfo
   */
  async getAvailableProviders(
    includeModels: boolean = false
  ): Promise<ProviderInfo[]> {
    const all = await this.listProviders(includeModels);
    return all.filter((p) => p.status === "available");
  }

  /**
   * Validate an API key for a provider
   * @param request - Validation request with provider, api_key, model
   * @returns Promise resolving to ValidateKeyResponse
   */
  async validateApiKey(
    request: ValidateKeyRequest
  ): Promise<ValidateKeyResponse> {
    const response = await fetch(`${API_BASE_URL}/providers/validate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to validate API key: ${response.statusText}`);
    }

    return response.json();
  }
}

// Export singleton instance
const providerService = new ProviderService();
export default providerService;

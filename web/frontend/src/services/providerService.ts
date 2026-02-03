// Provider API Service
import type {
  ProviderInfo,
  ValidateKeyRequest,
  ValidateKeyResponse,
} from "../types/providers";
import { API_BASE_URL, apiFetch } from "../config/api";

class ProviderService {
  /**
   * Get list of available LLM providers
   * @param includeModels - Whether to include model lists
   * @returns Promise resolving to array of ProviderInfo
   */
  async listProviders(includeModels: boolean = false): Promise<ProviderInfo[]> {
    return apiFetch<ProviderInfo[]>(
      `${API_BASE_URL}/providers?include_models=${includeModels}`
    );
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
    return apiFetch<ValidateKeyResponse>(
      `${API_BASE_URL}/providers/validate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }
    );
  }
}

// Export singleton instance
const providerService = new ProviderService();
export default providerService;

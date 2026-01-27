// @ts-nocheck - Test file with legacy string literal types
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ProviderSelector from "./ProviderSelector";
import providerService from "../services/providerService";
import type { ProviderType } from "../types/providers";

jest.mock("../services/providerService");

describe("ProviderSelector Component", () => {
  const mockProviderService =
    providerService as jest.Mocked<typeof providerService>;

  const mockProviders = [
    {
      id: "mock",
      name: "Mock Provider",
      requires_api_key: false,
      supported_models: ["mock-model"],
      api_key_env_var: null,
      status: "available" as const,
    },
    {
      id: "ollama",
      name: "Ollama",
      requires_api_key: false,
      supported_models: ["llama2", "mistral"],
      api_key_env_var: null,
      status: "available" as const,
    },
    {
      id: "openai",
      name: "OpenAI",
      requires_api_key: true,
      supported_models: ["gpt-4", "gpt-3.5-turbo"],
      api_key_env_var: "OPENAI_API_KEY",
      status: "available" as const,
    },
    {
      id: "anthropic",
      name: "Anthropic",
      requires_api_key: true,
      supported_models: ["claude-3-opus"],
      api_key_env_var: "ANTHROPIC_API_KEY",
      status: "coming_soon" as const,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    mockProviderService.listProviders.mockResolvedValue(mockProviders);
  });

  test("renders provider selector", async () => {
    const onProviderChange = jest.fn();
    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    await waitFor(() => {
      expect(screen.getByLabelText(/Provider:/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Model:/i)).toBeInTheDocument();
    });
  });

  test("loads and displays providers", async () => {
    const onProviderChange = jest.fn();
    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    await waitFor(() => {
      expect(mockProviderService.listProviders).toHaveBeenCalledWith(true);
    });

    // Wait for loading state to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const providerSelect = screen.getByLabelText(/Provider:/i) as HTMLSelectElement;
    expect(providerSelect.value).toBe("mock");
  });

  test("handles provider change", async () => {
    const user = userEvent.setup();
    const onProviderChange = jest.fn();

    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const providerSelect = screen.getByLabelText(/Provider:/i);
    await user.selectOptions(providerSelect, "ollama");

    await waitFor(() => {
      expect(onProviderChange).toHaveBeenCalledWith("ollama", "llama2");
    });
  });

  test("displays available models for selected provider", async () => {
    const onProviderChange = jest.fn();
    render(
      <ProviderSelector
        selectedProvider="ollama"
        selectedModel="llama2"
        onProviderChange={onProviderChange}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const modelSelect = screen.getByLabelText(/Model:/i) as HTMLSelectElement;
    expect(modelSelect.value).toBe("llama2");
    
    // Check that both models are available as options
    const options = Array.from(modelSelect.options).map(opt => opt.value);
    expect(options).toContain("llama2");
    expect(options).toContain("mistral");
  });

  test("handles model change", async () => {
    const user = userEvent.setup();
    const onProviderChange = jest.fn();

    render(
      <ProviderSelector
        selectedProvider="ollama"
        selectedModel="llama2"
        onProviderChange={onProviderChange}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const modelSelect = screen.getByLabelText(/Model:/i);
    await user.selectOptions(modelSelect, "mistral");

    await waitFor(() => {
      expect(onProviderChange).toHaveBeenCalledWith("ollama", "mistral");
    });
  });

  test("disables provider/model selectors when disabled prop is true", async () => {
    const onProviderChange = jest.fn();

    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
        disabled={true}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const providerSelect = screen.getByLabelText(/Provider:/i);
    const modelSelect = screen.getByLabelText(/Model:/i);

    expect(providerSelect).toBeDisabled();
    expect(modelSelect).toBeDisabled();
  });

  test("shows coming soon providers as disabled", async () => {
    const onProviderChange = jest.fn();

    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    const providerSelect = screen.getByLabelText(/Provider:/i);
    const options = providerSelect.querySelectorAll("option");

    // Find Anthropic option (coming_soon)
    const anthropicOption = Array.from(options).find((opt) =>
      opt.textContent?.includes("Anthropic")
    ) as HTMLOptionElement;

    expect(anthropicOption).toBeDisabled();
    expect(anthropicOption?.textContent).toContain("Coming Soon");
  });

  test("displays API key warning for providers that require it", async () => {
    const onProviderChange = jest.fn();

    render(
      <ProviderSelector
        selectedProvider="openai"
        selectedModel="gpt-4"
        onProviderChange={onProviderChange}
      />
    );

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading providers/i)).not.toBeInTheDocument();
    });

    // Check that API key warning is displayed for OpenAI
    expect(screen.getByText(/Requires API key/i)).toBeInTheDocument();
  });

  test("handles loading state", () => {
    mockProviderService.listProviders.mockImplementationOnce(
      () =>
        new Promise((resolve) =>
          setTimeout(() => resolve(mockProviders), 100)
        )
    );

    const onProviderChange = jest.fn();
    render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    expect(screen.getByText(/Loading providers/i)).toBeInTheDocument();
  });

  test("handles error and allows retry", async () => {
    const user = userEvent.setup();
    mockProviderService.listProviders.mockRejectedValueOnce(
      new Error("Load failed")
    );

    const onProviderChange = jest.fn();
    const { rerender } = render(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Failed to load providers/i)).toBeInTheDocument();
    });

    // Reset mock to succeed on retry
    mockProviderService.listProviders.mockResolvedValueOnce(mockProviders);

    const retryButton = screen.getByRole("button", { name: /Retry/i });
    await user.click(retryButton);

    // Re-render to see updated state after retry
    rerender(
      <ProviderSelector
        selectedProvider="mock"
        selectedModel="mock-model"
        onProviderChange={onProviderChange}
      />
    );

    // Should eventually load providers
    await waitFor(() => {
      expect(
        screen.queryByText(/Failed to load providers/i)
      ).not.toBeInTheDocument();
    });
  });
});

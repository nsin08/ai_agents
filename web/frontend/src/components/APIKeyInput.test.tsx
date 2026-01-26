// @ts-nocheck - Test file with legacy string literal types
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import APIKeyInput from "./APIKeyInput";
import providerService from "../services/providerService";

jest.mock("../services/providerService");

describe("APIKeyInput Component", () => {
  const mockProviderService =
    providerService as jest.Mocked<typeof providerService>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders nothing when key is not required", () => {
    const onKeyChange = jest.fn();
    const { container } = render(
      <APIKeyInput
        provider={"mock" as any}
        model="mock-model"
        requiresKey={false}
        onKeyChange={onKeyChange}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  test("renders input when key is required", () => {
    const onKeyChange = jest.fn();
    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    expect(screen.getByPlaceholderText(/Enter openai API key/i)).toBeInTheDocument();
  });

  test("handles API key input", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i);
    await user.type(input, "sk-1234567890");

    expect(onKeyChange).toHaveBeenCalledWith("sk-1234567890");
  });

  test("toggles API key visibility", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i) as HTMLInputElement;
    const toggleButton = screen.getByTitle(/Show key|Hide key/i);

    // Initially hidden
    expect(input.type).toBe("password");

    // Toggle to show
    await user.click(toggleButton);
    expect(input.type).toBe("text");

    // Toggle to hide
    await user.click(toggleButton);
    expect(input.type).toBe("password");
  });

  test("validates API key", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    mockProviderService.validateApiKey.mockResolvedValueOnce({
      valid: true,
      message: "API key is valid",
      models_available: ["gpt-4", "gpt-3.5-turbo"],
    });

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i);
    await user.type(input, "sk-1234567890");

    const validateButton = screen.getByRole("button", { name: /Validate/i });
    await user.click(validateButton);

    await waitFor(() => {
      expect(mockProviderService.validateApiKey).toHaveBeenCalledWith({
        provider: "openai",
        api_key: "sk-1234567890",
        model: "gpt-4",
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/API key is valid/i)).toBeInTheDocument();
    });
  });

  test("shows error message for invalid API key", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    mockProviderService.validateApiKey.mockResolvedValueOnce({
      valid: false,
      message: "Invalid API key format",
      models_available: null,
    });

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i);
    await user.type(input, "invalid-key");

    const validateButton = screen.getByRole("button", { name: /Validate/i });
    await user.click(validateButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid API key format/i)).toBeInTheDocument();
    });
  });

  test("shows error when validation fails", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    mockProviderService.validateApiKey.mockRejectedValueOnce(
      new Error("Network error")
    );

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i);
    await user.type(input, "sk-1234567890");

    const validateButton = screen.getByRole("button", { name: /Validate/i });
    await user.click(validateButton);

    await waitFor(() => {
      expect(
        screen.getByText(/Validation failed: Network error/i)
      ).toBeInTheDocument();
    });
  });

  test("prevents validation with empty key", async () => {
    const onKeyChange = jest.fn();

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    // Validate button should be disabled when no key is entered
    const validateButton = screen.getByRole("button", { name: /Validate/i });
    expect(validateButton).toBeDisabled();
    expect(mockProviderService.validateApiKey).not.toHaveBeenCalled();
  });

  test("disables input when disabled prop is true", () => {
    const onKeyChange = jest.fn();
    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
        disabled={true}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i) as HTMLInputElement;
    expect(input).toBeDisabled();
  });

  test("clears validation when key changes", async () => {
    const user = userEvent.setup();
    const onKeyChange = jest.fn();

    mockProviderService.validateApiKey.mockResolvedValueOnce({
      valid: true,
      message: "API key is valid",
      models_available: null,
    });

    render(
      <APIKeyInput
        provider="openai"
        model="gpt-4"
        requiresKey={true}
        onKeyChange={onKeyChange}
      />
    );

    const input = screen.getByPlaceholderText(/Enter openai API key/i);
    await user.type(input, "sk-1234567890");

    const validateButton = screen.getByRole("button", { name: /Validate/i });
    await user.click(validateButton);

    await waitFor(() => {
      expect(screen.getByText(/API key is valid/i)).toBeInTheDocument();
    });

    // Type more characters
    await user.type(input, "x");

    // Validation message should be cleared
    expect(screen.queryByText(/API key is valid/i)).not.toBeInTheDocument();
  });
});

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Chat from "./Chat";
import chatService from "../services/chatService";
import providerService from "../services/providerService";
import configService from "../services/configService";

// Mock services
jest.mock("../services/chatService");
jest.mock("../services/providerService");
jest.mock("../services/configService");

describe("Chat Component", () => {
  const mockChatService = chatService as jest.Mocked<typeof chatService>;
  const mockProviderService =
    providerService as jest.Mocked<typeof providerService>;
  const mockConfigService =
    configService as jest.Mocked<typeof configService>;

  beforeEach(() => {
    jest.clearAllMocks();

    // Setup default mock implementations
    mockChatService.createSession.mockResolvedValue("session-123");
    mockChatService.sendMessage.mockResolvedValue({
      success: true,
      response: "Test response from agent",
      metadata: {
        provider: "mock",
        model: "mock-model",
        latency_ms: 100,
      },
    });

    mockProviderService.listProviders.mockResolvedValue([
      {
        id: "mock",
        name: "Mock Provider",
        requires_api_key: false,
        supported_models: ["mock-model"],
        api_key_env_var: null,
        status: "available",
      },
      {
        id: "ollama",
        name: "Ollama",
        requires_api_key: false,
        supported_models: ["llama2", "mistral"],
        api_key_env_var: null,
        status: "available",
      },
    ]);

    mockConfigService.getDefaultConfig.mockResolvedValue({
      config: {
        provider: "mock",
        model: "mock-model",
        api_key: null,
        temperature: 0.7,
        max_tokens: 1000,
        timeout: 30,
      },
      preset: "default",
    });
  });

  test("renders chat component", async () => {
    render(<Chat />);

    // Wait for session to be created
    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    // Check for main UI elements
    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Send/i })).toBeInTheDocument();
  });

  test("loads providers on mount", async () => {
    render(<Chat />);

    await waitFor(() => {
      expect(mockProviderService.listProviders).toHaveBeenCalledWith(true);
    });
  });

  test("sends message and displays response", async () => {
    const user = userEvent.setup();
    render(<Chat />);

    // Wait for initial setup
    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    // Type a message
    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, "Hello, agent!");

    // Send message
    const sendButton = screen.getByRole("button", { name: /Send/i });
    await user.click(sendButton);

    // Wait for response
    await waitFor(() => {
      expect(mockChatService.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          message: "Hello, agent!",
          provider: "mock",
          model: "mock-model",
        })
      );
    });

    // Check that response is displayed
    await waitFor(() => {
      expect(screen.getByText(/Test response from agent/i)).toBeInTheDocument();
    });

    // Check that input is cleared
    expect(input).toHaveValue("");
  });

  test("shows loading state while sending message", async () => {
    const user = userEvent.setup();

    // Make sendMessage slower to observe loading state
    mockChatService.sendMessage.mockImplementationOnce(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                success: true,
                response: "Delayed response",
                metadata: {},
              }),
            100
          )
        )
    );

    render(<Chat />);

    // Wait for setup
    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    // Type and send message
    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, "Test");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    // Check for loading indicator (button disabled, input cleared)
    await waitFor(() => {
      const sendButton = screen.getByRole("button", { name: /Send/i });
      const inputField = screen.getByPlaceholderText(/Type your message/i) as HTMLTextAreaElement;
      expect(sendButton).toBeDisabled();
      expect(inputField.value).toBe("");
    });

    // Wait for response to appear
    await waitFor(() => {
      expect(screen.getByText("Delayed response")).toBeInTheDocument();
    });
  });

  test("displays error message on failed response", async () => {
    const user = userEvent.setup();

    mockChatService.sendMessage.mockResolvedValueOnce({
      success: false,
      response: "Agent error",
      metadata: {
        error: "Provider not configured",
      },
    });

    render(<Chat />);

    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, "Test message");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getByText(/Agent error/i)).toBeInTheDocument();
    });
  });

  test("prevents sending empty messages", async () => {
    const user = userEvent.setup();
    render(<Chat />);

    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    // Try to send empty message
    const input = screen.getByPlaceholderText(/Type your message/i);
    const sendButton = screen.getByRole("button", { name: /Send/i });

    // Input should be empty
    expect(input).toHaveValue("");

    // Click send (should be disabled or prevented)
    await user.click(sendButton);

    // Service should not be called
    expect(mockChatService.sendMessage).not.toHaveBeenCalled();
  });

  test("scrolls to bottom on new messages", async () => {
    const user = userEvent.setup();
    const scrollIntoViewMock = jest.fn();
    Element.prototype.scrollIntoView = scrollIntoViewMock;

    render(<Chat />);

    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, "Hello");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalled();
    });
  });

  test("handles service errors gracefully", async () => {
    const user = userEvent.setup();

    mockChatService.sendMessage.mockRejectedValueOnce(
      new Error("Network error")
    );

    render(<Chat />);

    await waitFor(() => {
      expect(mockChatService.createSession).toHaveBeenCalled();
    });

    const input = screen.getByPlaceholderText(/Type your message/i);
    await user.type(input, "Test");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    // Should display error message or handle gracefully
    await waitFor(() => {
      expect(mockChatService.sendMessage).toHaveBeenCalled();
    });
  });
});

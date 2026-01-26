// Chat API Service
// Handles communication with the backend FastAPI server

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

class ChatService {
  /**
   * Send a message to the agent
   * @param {Object} data - Request data
   * @param {string} data.message - The user message
   * @param {string} [data.provider="mock"] - LLM provider to use
   * @param {string} [data.model="mock-model"] - Model name
   * @param {string} [data.apiKey] - Optional API key
   * @param {Object} [data.config={}] - Agent configuration
   * @param {string} [data.sessionId] - Optional session ID
   * @returns {Promise<Object>} Chat response with success, response, and metadata
   */
  async sendMessage(data) {
    try {
      const requestBody = {
        message: data.message,
        provider: data.provider || "mock",
        model: data.model || "mock-model",
        config: data.config || {},
      };

      // Add optional fields
      if (data.apiKey) {
        requestBody.api_key = data.apiKey;
      }
      if (data.sessionId) {
        requestBody.session_id = data.sessionId;
      }

      const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Chat API error:", error);
      throw error;
    }
  }

  /**
   * Create a new chat session
   * @returns {Promise<string>} Session ID
   */
  async createSession() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data.session_id;
    } catch (error) {
      console.error("Session creation error:", error);
      throw error;
    }
  }

  /**
   * Get session history
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Session data with messages
   */
  async getSession(sessionId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat/sessions/${sessionId}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Session retrieval error:", error);
      throw error;
    }
  }
}

const chatService = new ChatService();

export default chatService;

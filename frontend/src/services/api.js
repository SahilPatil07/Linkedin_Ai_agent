const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000/ws';

/**
 * Send a chat message using REST API
 * @param {string} message - User message
 * @param {Array} chatHistory - Previous chat messages
 * @returns {Promise<Object>} - Response from the API
 */
export const fetchChatResponse = async (message, chatHistory = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        messages: chatHistory.concat([{ role: 'user', content: message }]),
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.message === 'Failed to fetch') {
      throw new Error('Unable to connect to the server. Please make sure the backend server is running.');
    }
    console.error('Error fetching chat response:', error);
    throw error;
  }
};

/**
 * Generate multiple posts for a topic
 * @param {string} topic - Topic for post generation
 * @param {Array} chatHistory - Previous chat messages
 * @returns {Promise<Array>} - Array of generated posts
 */
export const generatePosts = async (topic, chatHistory = []) => {
  try {
    const response = await fetch(`${API_BASE_URL}/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: chatHistory.concat([{ role: 'user', content: topic }]),
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating posts:', error);
    throw error;
  }
};

/**
 * Set up WebSocket connection for streaming chat
 * @param {Object} callbacks - Event callbacks
 * @returns {WebSocket} - WebSocket instance
 */
export const setupChatWebSocket = ({ onMessage, onClose, onError }) => {
  const ws = new WebSocket(WS_BASE_URL);

  ws.onopen = () => {
    console.log('WebSocket connection established');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      onError(error);
    }
  };

  ws.onclose = () => {
    console.log('WebSocket connection closed');
    onClose();
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError(error);
  };

  return ws;
}; 
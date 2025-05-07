import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status);
    return response;
  },
  async (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error:', error.response.status, error.response.data);
      throw new Error(error.response.data.error || 'Server error occurred');
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      throw new Error('Could not connect to the server. Please ensure the backend is running on http://localhost:8000');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request setup error:', error.message);
      throw new Error('An error occurred while setting up the request');
    }
  }
);

// Test connection function
export const testConnection = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/test`);
    if (!response.ok) {
      throw new Error("Failed to connect to server");
    }
    return await response.json();
  } catch (error) {
    console.error("Connection test failed:", error);
    throw new Error("Could not connect to the server. Please ensure the backend is running.");
  }
};

// Generate posts function
export const generatePosts = async (topic, type = "product", chatHistory = []) => {
  try {
    const response = await api.post('/generate-posts', {
      topic,
      type,
      chat_history: chatHistory
    });

    return response.data.posts;
  } catch (error) {
    console.error('Error generating posts:', error);
    throw error;
  }
};

// Schedule post function
export const schedulePost = async (postData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    });

    if (!response.ok) {
      throw new Error('Failed to schedule post');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error in schedulePost:', error);
    throw error;
  }
};

// Get scheduled posts function
export const getScheduledPosts = async (userId) => {
  try {
    const response = await api.get(`/scheduled-posts/${userId}`);
    return response.data.posts;
  } catch (error) {
    console.error('Error getting scheduled posts:', error);
    throw error;
  }
};

// Delete scheduled post function
export const deleteScheduledPost = async (postId) => {
  try {
    const response = await api.delete(`/scheduled-post/${postId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting scheduled post:', error);
    throw error;
  }
};
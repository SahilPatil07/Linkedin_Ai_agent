import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ApiResponse {
  status: 'success' | 'error';
  message?: string;
  error?: string;
  is_post?: boolean;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized error
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    const message = error.response?.data?.detail || error.message;
    return Promise.reject(new Error(message));
  }
);

export const sendMessage = async (message: string): Promise<ApiResponse> => {
  try {
    const response = await api.post<ApiResponse>('/chat', {
      message,
      chat_history: []
    });
    
    if (!response.data) {
      throw new Error('No response data received');
    }
    
    return response.data;
  } catch (error: any) {
    console.error('Error sending message:', error);
    return {
      status: 'error',
      error: error.message || 'Failed to send message. Please try again.'
    };
  }
};

export default api; 
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 30000,
  withCredentials: true
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      // Handle connection errors
      const connectionError = new Error('Could not connect to the server. Please ensure the backend is running on http://localhost:8000');
      console.error('Connection Error:', connectionError);
      return Promise.reject(connectionError);
    }

    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

// Add request interceptor to check server availability
api.interceptors.request.use(
  async (config) => {
    try {
      await axios.get('http://localhost:8000/test', { timeout: 5000 });
      return config;
    } catch (error) {
      throw new Error('Backend server is not accessible. Please start the server and try again.');
    }
  },
  (error) => Promise.reject(error)
);

export default api;
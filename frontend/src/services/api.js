import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001/api',
});

export const executeCode = async (code) => {
  try {
    const response = await api.post('/execute', { code });
    return response.data;
  } catch (e) {
    return {
      steps: [],
      error: {
        type: "NetworkError",
        message: "Failed to connect to server",
        line: 0
      }
    };
  }
};

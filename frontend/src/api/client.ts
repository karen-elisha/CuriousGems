import axios from 'axios';

// Base API Client targeting the FastAPI backend
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;

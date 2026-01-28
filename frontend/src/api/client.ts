import axios from 'axios';
import type { NoduleEvaluationRequest, NoduleEvaluationResponse, HealthCheckResponse } from '../types';

// In production, when VITE_API_URL is empty or not set, use relative URLs
// This allows the frontend to be served from the same origin as the backend
const API_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await apiClient.get<HealthCheckResponse>('/api/health/');
  return response.data;
};

export const evaluateNodule = async (
  data: NoduleEvaluationRequest
): Promise<NoduleEvaluationResponse> => {
  const response = await apiClient.post<NoduleEvaluationResponse>(
    '/api/nodule/evaluate/',
    data
  );
  return response.data;
};

export default apiClient;

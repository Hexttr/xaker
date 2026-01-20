import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export interface Pentest {
  id: string;
  name: string;
  targetUrl: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  config: {
    targetUrl: string;
    scope?: string[];
    excludedPaths?: string[];
    maxDepth?: number;
    timeout?: number;
  };
  startedAt?: string;
  completedAt?: string;
  createdAt: string;
  results?: any;
}

export interface CreatePentestRequest {
  name: string;
  config: {
    targetUrl: string;
    scope?: string[];
    excludedPaths?: string[];
    maxDepth?: number;
    timeout?: number;
  };
}

export interface Vulnerability {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  location?: string;
}

export const pentestApi = {
  getAll: () => api.get<Pentest[]>('/pentests'),
  getById: (id: string) => api.get<Pentest>(`/pentests/${id}`),
  create: (data: CreatePentestRequest) => api.post<Pentest>('/pentests', data),
  start: (id: string) => api.post(`/pentests/${id}/start`),
  stop: (id: string) => api.post(`/pentests/${id}/stop`),
  delete: (id: string) => api.delete(`/pentests/${id}`),
  getLogs: (id: string) => api.get(`/pentests/${id}/logs`),
  getStatus: (id: string) => api.get<{ status: string }>(`/pentests/${id}/status`),
  getVulnerabilities: (id: string) => api.get<Vulnerability[]>(`/pentests/${id}/vulnerabilities`),
  generatePdfReport: async (id: string): Promise<Blob> => {
    const response = await api.get(`/pentests/${id}/generate-pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Service API
export interface Service {
  id: string;
  name: string;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateServiceRequest {
  name: string;
  url: string;
}

export interface UpdateServiceRequest {
  name?: string;
  url?: string;
}

export const serviceApi = {
  getAll: () => api.get<Service[]>('/services'),
  getById: (id: string) => api.get<Service>(`/services/${id}`),
  create: (data: CreateServiceRequest) => api.post<Service>('/services', data),
  update: (id: string, data: UpdateServiceRequest) => api.put<Service>(`/services/${id}`, data),
  delete: (id: string) => api.delete(`/services/${id}`),
};

export default api;


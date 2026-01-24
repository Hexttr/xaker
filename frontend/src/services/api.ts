import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Interceptor для добавления токена к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      (window as any).__DEBUG__?.log('[API] Токен добавлен к запросу:', config.method?.toUpperCase(), config.url);
      (window as any).__DEBUG__?.log('[API] Заголовок Authorization:', `Bearer ${token.substring(0, 20)}...`);
    } else {
      (window as any).__DEBUG__?.log('[API] ⚠️ Токен не найден для запроса:', config.method?.toUpperCase(), config.url);
      console.error('[API] ⚠️ Токен не найден в localStorage для запроса:', config.url);
    }
    return config;
  },
  (error) => {
    (window as any).__DEBUG__?.log('[API] Ошибка в request interceptor:', error);
    return Promise.reject(error);
  }
);

// Interceptor для обработки ошибок 401 (неавторизован)
api.interceptors.response.use(
  (response) => {
    (window as any).__DEBUG__?.log('[API] Ответ получен:', response.config.method?.toUpperCase(), response.config.url, response.status);
    return response;
  },
  (error) => {
    (window as any).__DEBUG__?.log('[API] Ошибка ответа:', error.response?.status, error.config?.method?.toUpperCase(), error.config?.url);
    if (error.response?.status === 401) {
      (window as any).__DEBUG__?.log('[API] ⚠️ 401 Unauthorized - удаляю токен');
      console.error('[API] ⚠️ 401 Unauthorized для:', error.config?.url, 'Токен удален из localStorage');
      // Токен истек или невалиден
      localStorage.removeItem('authToken');
      // НЕ перезагружаем страницу - ProtectedRoute сам покажет модалку логина
      // window.location.reload() вызывал бесконечный цикл перезагрузки
    }
    return Promise.reject(error);
  }
);

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

export interface VulnerabilityComparison {
  fixed: any[];
  remaining: any[];
  new: any[];
  partiallyFixed: Array<{ previous: any; current: any }>;
  worsened: Array<{ previous: any; current: any }>;
  regressed: any[];
  metrics: {
    totalFixed: number;
    totalRemaining: number;
    totalNew: number;
    fixRate: number;
    improvementRate: number;
  };
}

export interface PentestComparison {
  previousPentest?: any;
  currentPentest: any;
  comparison: VulnerabilityComparison | null;
  message?: string;
}

export const pentestApi = {
  getAll: () => api.get<Pentest[]>('/pentests'),
  getById: (id: string) => api.get<Pentest>(`/pentests/${id}`),
  compareWithPrevious: (id: string) => api.get<PentestComparison>(`/pentests/${id}/compare-with-previous`),
  create: (data: CreatePentestRequest) => api.post<Pentest>('/pentests', data),
  start: (id: string) => api.post(`/pentests/${id}/start`),
  stop: (id: string) => api.post(`/pentests/${id}/stop`),
  delete: (id: string) => api.delete(`/pentests/${id}`),
  getLogs: (id: string) => api.get(`/pentests/${id}/logs`),
  getStatus: (id: string) => api.get<{ status: string }>(`/pentests/${id}/status`),
  getVulnerabilities: (id: string) => api.get<Vulnerability[]>(`/pentests/${id}/vulnerabilities`),
  checkReportExists: (id: string) => api.get<{ exists: boolean; path: string | null }>(`/pentests/${id}/report-exists`),
  generatePdfReport: async (id: string): Promise<Blob> => {
    // Убираем таймаут для генерации PDF, так как это может занять много времени
    const response = await api.get(`/pentests/${id}/generate-pdf`, {
      responseType: 'blob',
      timeout: 0, // Без таймаута
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


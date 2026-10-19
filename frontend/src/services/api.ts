import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

export const scanAPI = {
  scan: (data: Record<string, string>) => api.post('/scan', data),
  batchScan: (emails: Record<string, string>[]) => api.post('/scan/batch', { emails }),
  getScan: (id: string) => api.get(`/scan/${id}`),
  deleteScan: (id: string) => api.delete(`/scan/${id}`),
  toggleFavorite: (id: string) => api.post(`/scan/${id}/favorite`),
};

export const historyAPI = {
  getHistory: (params: Record<string, unknown>) => api.get('/history', { params }),
  exportHistory: (format: string) => api.get('/history/export', { params: { format }, responseType: 'blob' }),
};

export const dashboardAPI = {
  getStatistics: () => api.get('/dashboard/statistics'),
  getTrends: (days = 30) => api.get('/dashboard/trends', { params: { days } }),
  getAttackTypes: () => api.get('/dashboard/attack-types'),
};

export const healthAPI = {
  check: () => api.get('/health'),
  metrics: () => api.get('/metrics'),
  modelStatus: () => api.get('/models/status'),
  modelInfo: () => api.get('/models/info'),
  modelMetrics: () => api.get('/models/metrics'),
};

export default api;

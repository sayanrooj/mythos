// api.js — Axios API client for AquaPulse backend

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

export const fetchStations = () => api.get('/stations').then(r => r.data);

export const fetchReadings = (stationId, params = {}) =>
  api.get(`/stations/${stationId}/readings`, { params }).then(r => r.data);

export const fetchStatus = (stationId) =>
  api.get(`/stations/${stationId}/status`).then(r => r.data);

export const fetchForecast = (stationId) =>
  api.get(`/stations/${stationId}/forecast`).then(r => r.data);

export const fetchAlerts = (params = {}) =>
  api.get('/alerts', { params }).then(r => r.data);

export const resolveAlert = (alertId) =>
  api.put(`/alerts/${alertId}/resolve`).then(r => r.data);

export const dispatchAlert = (alertId) =>
  api.post(`/alerts/${alertId}/dispatch`).then(r => r.data);

export const fetchDashboard = () =>
  api.get('/dashboard/summary').then(r => r.data);

export const simulateTick = () =>
  api.post('/simulate/tick').then(r => r.data);



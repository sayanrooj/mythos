// api.js — Resilient API client for AquaPulse
// Supports live Flask backend when available, and automatically falls back to in-browser
// clientEngine for 100% functional standalone execution on GitHub Pages.

import axios from 'axios';
import {
  clientGetStations,
  clientGetReadings,
  clientGetStatus,
  clientGetForecast,
  clientGetAlerts,
  clientResolveAlert,
  clientDispatchAlert,
  clientGetDashboardSummary,
  clientSimulateTick,
} from './clientEngine';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 3000,
});

export const fetchStations = async () => {
  try {
    const res = await api.get('/stations');
    return res.data;
  } catch {
    return clientGetStations();
  }
};

export const fetchReadings = async (stationId, params = {}) => {
  try {
    const res = await api.get(`/stations/${stationId}/readings`, { params });
    return res.data;
  } catch {
    return clientGetReadings(stationId, params);
  }
};

export const fetchStatus = async (stationId) => {
  try {
    const res = await api.get(`/stations/${stationId}/status`);
    return res.data;
  } catch {
    return clientGetStatus(stationId);
  }
};

export const fetchForecast = async (stationId) => {
  try {
    const res = await api.get(`/stations/${stationId}/forecast`);
    return res.data;
  } catch {
    return clientGetForecast(stationId);
  }
};

export const fetchAlerts = async (params = {}) => {
  try {
    const res = await api.get('/alerts', { params });
    return res.data;
  } catch {
    return clientGetAlerts(params);
  }
};

export const resolveAlert = async (alertId) => {
  try {
    const res = await api.put(`/alerts/${alertId}/resolve`);
    return res.data;
  } catch {
    return clientResolveAlert(alertId);
  }
};

export const dispatchAlert = async (alertId) => {
  try {
    const res = await api.post(`/alerts/${alertId}/dispatch`);
    return res.data;
  } catch {
    return clientDispatchAlert(alertId);
  }
};

export const fetchDashboard = async () => {
  try {
    const res = await api.get('/dashboard/summary');
    return res.data;
  } catch {
    return clientGetDashboardSummary();
  }
};

export const simulateTick = async () => {
  try {
    const res = await api.post('/simulate/tick');
    return res.data;
  } catch {
    return clientSimulateTick();
  }
};

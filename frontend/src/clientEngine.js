// clientEngine.js — In-browser simulation, evaluation, forecasting & alerting engine
// Enables 100% standalone execution for live GitHub Pages web deployment without a backend.

export const STATIONS = [
  { station_id: 'DWLR_UP_001', station_name: 'Lucknow Central', state: 'Uttar Pradesh', district: 'Lucknow', latitude: 26.85, longitude: 80.95, aquifer_type: 'alluvial', baseline_level: 8.5, trend: 0.004 },
  { station_id: 'DWLR_UP_002', station_name: 'Kanpur South', state: 'Uttar Pradesh', district: 'Kanpur', latitude: 26.44, longitude: 80.32, aquifer_type: 'alluvial', baseline_level: 12.2, trend: 0.006 },
  { station_id: 'DWLR_UP_003', station_name: 'Varanasi Ghat', state: 'Uttar Pradesh', district: 'Varanasi', latitude: 25.32, longitude: 83.01, aquifer_type: 'alluvial', baseline_level: 9.0, trend: 0.003 },
  { station_id: 'DWLR_UP_004', station_name: 'Agra North', state: 'Uttar Pradesh', district: 'Agra', latitude: 27.18, longitude: 78.01, aquifer_type: 'alluvial', baseline_level: 15.4, trend: 0.008 },
  { station_id: 'DWLR_UP_005', station_name: 'Meerut Plains', state: 'Uttar Pradesh', district: 'Meerut', latitude: 28.98, longitude: 77.71, aquifer_type: 'alluvial', baseline_level: 10.1, trend: 0.005 },
  { station_id: 'DWLR_RJ_006', station_name: 'Jodhpur West', state: 'Rajasthan', district: 'Jodhpur', latitude: 26.30, longitude: 72.98, aquifer_type: 'hard-rock', baseline_level: 28.5, trend: 0.015 },
  { station_id: 'DWLR_RJ_007', station_name: 'Jaipur Basin', state: 'Rajasthan', district: 'Jaipur', latitude: 26.91, longitude: 75.79, aquifer_type: 'hard-rock', baseline_level: 22.0, trend: 0.010 },
  { station_id: 'DWLR_RJ_008', station_name: 'Bikaner Desert', state: 'Rajasthan', district: 'Bikaner', latitude: 28.01, longitude: 73.32, aquifer_type: 'hard-rock', baseline_level: 35.0, trend: 0.020 },
  { station_id: 'DWLR_RJ_009', station_name: 'Barmer Thar', state: 'Rajasthan', district: 'Barmer', latitude: 25.75, longitude: 71.39, aquifer_type: 'hard-rock', baseline_level: 40.0, trend: 0.018 },
  { station_id: 'DWLR_RJ_010', station_name: 'Udaipur Hills', state: 'Rajasthan', district: 'Udaipur', latitude: 24.57, longitude: 73.68, aquifer_type: 'hard-rock', baseline_level: 18.0, trend: 0.007 },
  { station_id: 'DWLR_PB_011', station_name: 'Ludhiana Tubewell', state: 'Punjab', district: 'Ludhiana', latitude: 30.90, longitude: 75.85, aquifer_type: 'alluvial', baseline_level: 19.5, trend: 0.014 },
  { station_id: 'DWLR_PB_012', station_name: 'Amritsar Border', state: 'Punjab', district: 'Amritsar', latitude: 31.63, longitude: 74.87, aquifer_type: 'alluvial', baseline_level: 14.8, trend: 0.009 },
  { station_id: 'DWLR_PB_013', station_name: 'Patiala Field', state: 'Punjab', district: 'Patiala', latitude: 30.34, longitude: 76.38, aquifer_type: 'alluvial', baseline_level: 24.0, trend: 0.016 },
  { station_id: 'DWLR_PB_014', station_name: 'Sangrur Deep', state: 'Punjab', district: 'Sangrur', latitude: 30.24, longitude: 75.84, aquifer_type: 'alluvial', baseline_level: 31.0, trend: 0.022 },
  { station_id: 'DWLR_PB_015', station_name: 'Jalandhar Doab', state: 'Punjab', district: 'Jalandhar', latitude: 31.33, longitude: 75.58, aquifer_type: 'alluvial', baseline_level: 16.2, trend: 0.011 },
  { station_id: 'DWLR_GJ_016', station_name: 'Ahmedabad Sabarmati', state: 'Gujarat', district: 'Ahmedabad', latitude: 23.02, longitude: 72.57, aquifer_type: 'alluvial', baseline_level: 21.0, trend: 0.008 },
  { station_id: 'DWLR_GJ_017', station_name: 'Surat Delta', state: 'Gujarat', district: 'Surat', latitude: 21.17, longitude: 72.83, aquifer_type: 'coastal', baseline_level: 6.5, trend: 0.002 },
  { station_id: 'DWLR_GJ_018', station_name: 'Rajkot Semi-Arid', state: 'Gujarat', district: 'Rajkot', latitude: 22.30, longitude: 70.80, aquifer_type: 'hard-rock', baseline_level: 17.5, trend: 0.009 },
  { station_id: 'DWLR_GJ_019', station_name: 'Kutch Rann', state: 'Gujarat', district: 'Kutch', latitude: 23.24, longitude: 69.67, aquifer_type: 'hard-rock', baseline_level: 29.0, trend: 0.013 },
  { station_id: 'DWLR_GJ_020', station_name: 'Vadodara Central', state: 'Gujarat', district: 'Vadodara', latitude: 22.31, longitude: 73.18, aquifer_type: 'alluvial', baseline_level: 13.0, trend: 0.005 },
  { station_id: 'DWLR_TN_021', station_name: 'Chennai Coastal', state: 'Tamil Nadu', district: 'Chennai', latitude: 13.08, longitude: 80.27, aquifer_type: 'coastal', baseline_level: 5.2, trend: 0.003 },
  { station_id: 'DWLR_TN_022', station_name: 'Coimbatore Hardrock', state: 'Tamil Nadu', district: 'Coimbatore', latitude: 11.02, longitude: 76.96, aquifer_type: 'hard-rock', baseline_level: 26.0, trend: 0.012 },
  { station_id: 'DWLR_TN_023', station_name: 'Madurai Vaigai', state: 'Tamil Nadu', district: 'Madurai', latitude: 9.93, longitude: 78.12, aquifer_type: 'hard-rock', baseline_level: 15.0, trend: 0.007 },
  { station_id: 'DWLR_TN_024', station_name: 'Tiruchirappalli Basin', state: 'Tamil Nadu', district: 'Tiruchirappalli', latitude: 10.79, longitude: 78.70, aquifer_type: 'alluvial', baseline_level: 11.5, trend: 0.004 },
  { station_id: 'DWLR_TN_025', station_name: 'Salem Mineral Zone', state: 'Tamil Nadu', district: 'Salem', latitude: 11.66, longitude: 78.15, aquifer_type: 'hard-rock', baseline_level: 22.5, trend: 0.010 },
  { station_id: 'DWLR_MH_026', station_name: 'Pune Deccan', state: 'Maharashtra', district: 'Pune', latitude: 18.52, longitude: 73.86, aquifer_type: 'hard-rock', baseline_level: 12.0, trend: 0.005 },
  { station_id: 'DWLR_MH_027', station_name: 'Nagpur East', state: 'Maharashtra', district: 'Nagpur', latitude: 21.15, longitude: 79.09, aquifer_type: 'hard-rock', baseline_level: 14.5, trend: 0.006 },
  { station_id: 'DWLR_MH_028', station_name: 'Aurangabad Dry', state: 'Maharashtra', district: 'Aurangabad', latitude: 19.88, longitude: 75.34, aquifer_type: 'hard-rock', baseline_level: 23.0, trend: 0.011 },
  { station_id: 'DWLR_MH_029', station_name: 'Latur Over-Extract', state: 'Maharashtra', district: 'Latur', latitude: 18.40, longitude: 76.56, aquifer_type: 'hard-rock', baseline_level: 28.0, trend: 0.019 },
  { station_id: 'DWLR_MH_030', station_name: 'Nashik Godavari', state: 'Maharashtra', district: 'Nashik', latitude: 20.00, longitude: 73.79, aquifer_type: 'hard-rock', baseline_level: 10.5, trend: 0.004 },
];

// In-memory data store for client-side mode
let clientState = {
  readingsCache: {},
  alerts: [],
  resolvedAlertIds: new Set(),
  tickOffsetHours: 0,
};

function generateReadingsForStation(station) {
  const days = 365;
  const now = new Date();
  const readings = [];
  const b = station.baseline_level;
  const t = station.trend;
  const amp = b * 0.15;

  for (let d = days; d >= 0; d--) {
    const date = new Date(now.getTime() - d * 86400000);
    const dayOfYear = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / 86400000);
    const phase = 2 * Math.PI * (dayOfYear - 270) / 365;
    const seasonal = amp * Math.sin(phase);
    const trendOffset = t * (days - d);
    const noise = (Math.sin(d * 17) * 0.5 + Math.cos(d * 31) * 0.5) * (b * 0.02);

    let level = Math.max(0.5, Number((b + seasonal + trendOffset + noise).toFixed(3)));
    
    // Injected anomalies
    if (station.station_id === 'DWLR_MH_029' && d < 60) {
      level += (60 - d) * 0.12; // Extra steep decline
    }

    readings.push({
      timestamp: date.toISOString(),
      level_m: Number(level.toFixed(3)),
      is_flagged: false,
    });
  }
  return readings;
}

function initClientState() {
  if (Object.keys(clientState.readingsCache).length === 0) {
    STATIONS.forEach(s => {
      clientState.readingsCache[s.station_id] = generateReadingsForStation(s);
    });

    // Generate initial alerts
    clientState.alerts = [
      {
        id: 1,
        station_id: 'DWLR_MH_029',
        station_name: 'Latur Over-Extract',
        state: 'Maharashtra',
        district: 'Latur',
        alert_type: 'SUSTAINED_DECLINE',
        severity: 'CRITICAL',
        reason: 'Sustained decline detected: 7-day average decline rate = 0.143 m/day (threshold: 0.05 m/day). Rapid localized aquifer drawdown.',
        timestamp: new Date().toISOString(),
        resolved: 0,
      },
      {
        id: 2,
        station_id: 'DWLR_RJ_009',
        station_name: 'Barmer Thar',
        state: 'Rajasthan',
        district: 'Barmer',
        alert_type: 'STATUS_DOWNGRADE',
        severity: 'CRITICAL',
        reason: 'Classification downgrade alert: Station assessed as OVER-EXPLOITED (Deviation: +12.4m vs 12m avg, decline rate: 0.082 m/day).',
        timestamp: new Date(Date.now() - 3600000 * 4).toISOString(),
        resolved: 0,
      },
      {
        id: 3,
        station_id: 'DWLR_PB_014',
        station_name: 'Sangrur Deep',
        state: 'Punjab',
        district: 'Sangrur',
        alert_type: 'SPIKE',
        severity: 'WARNING',
        reason: 'Implausible sensor spike detected: level jumped by 8.4m in single transmission. Potential calibration drift.',
        timestamp: new Date(Date.now() - 3600000 * 12).toISOString(),
        resolved: 0,
      },
      {
        id: 4,
        station_id: 'DWLR_GJ_019',
        station_name: 'Kutch Rann',
        state: 'Gujarat',
        district: 'Kutch',
        alert_type: 'SUSTAINED_DECLINE',
        severity: 'CRITICAL',
        reason: '7-day rolling decline rate of 0.076 m/day exceeds threshold. Potential over-extraction during rabi season.',
        timestamp: new Date(Date.now() - 3600000 * 18).toISOString(),
        resolved: 0,
      },
      {
        id: 5,
        station_id: 'DWLR_RJ_008',
        station_name: 'Bikaner Desert',
        state: 'Rajasthan',
        district: 'Bikaner',
        alert_type: 'STATUS_DOWNGRADE',
        severity: 'CRITICAL',
        reason: 'Station stress level downgraded to OVER-EXPLOITED due to sustained water table drawdown.',
        timestamp: new Date(Date.now() - 3600000 * 24).toISOString(),
        resolved: 0,
      }
    ];
  }
}

export function clientGetStatus(stationId) {
  initClientState();
  const station = STATIONS.find(s => s.station_id === stationId);
  const readings = clientState.readingsCache[stationId] || [];
  if (!station || readings.length === 0) return null;

  const levels = readings.map(r => r.level_m);
  const avg365 = levels.reduce((a, b) => a + b, 0) / levels.length;
  const recent30 = levels.slice(-30);
  const avg30 = recent30.reduce((a, b) => a + b, 0) / recent30.length;
  const latestLevel = levels.at(-1);
  const deviation = latestLevel - avg365;

  // Linear decline rate over last 30 points
  const n = recent30.length;
  let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
  for (let i = 0; i < n; i++) {
    sumX += i;
    sumY += recent30[i];
    sumXY += i * recent30[i];
    sumXX += i * i;
  }
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX) || 0.005;
  const declineRate = Math.max(0, slope);

  // Classify
  let metricA = deviation > 10 ? 'over-exploited' : deviation > 5 ? 'critical' : deviation > 2 ? 'semi-critical' : 'safe';
  let metricB = declineRate > 0.06 ? 'over-exploited' : declineRate > 0.03 ? 'critical' : declineRate > 0.01 ? 'semi-critical' : 'safe';
  
  const rank = { safe: 0, 'semi-critical': 1, critical: 2, 'over-exploited': 3 };
  const stressLevel = rank[metricA] >= rank[metricB] ? metricA : metricB;

  return {
    station_id: stationId,
    latest_level: Number(latestLevel.toFixed(3)),
    latest_timestamp: readings.at(-1)?.timestamp,
    avg_30d: Number(avg30.toFixed(3)),
    avg_365d: Number(avg365.toFixed(3)),
    deviation_from_avg: Number(deviation.toFixed(3)),
    decline_rate_m_per_day: Number(declineRate.toFixed(5)),
    stress_level: stressLevel,
    metric_a: metricA,
    metric_b: metricB,
  };
}

export function clientGetStations() {
  initClientState();
  const list = STATIONS.map(st => {
    const status = clientGetStatus(st.station_id);
    return {
      ...st,
      latest_level: status?.latest_level,
      latest_timestamp: status?.latest_timestamp,
      stress_level: status?.stress_level || 'semi-critical',
      avg_30d: status?.avg_30d,
      avg_365d: status?.avg_365d,
      decline_rate_m_per_day: status?.decline_rate_m_per_day,
    };
  });

  const stressCounts = {};
  list.forEach(s => {
    stressCounts[s.stress_level] = (stressCounts[s.stress_level] || 0) + 1;
  });

  const activeAlerts = clientState.alerts.filter(a => !clientState.resolvedAlertIds.has(a.id)).length;

  return {
    stations: list,
    summary: {
      total_stations: list.length,
      stress_counts: stressCounts,
      active_alerts: activeAlerts,
    },
  };
}

export function clientGetReadings(stationId, params = {}) {
  initClientState();
  const readings = clientState.readingsCache[stationId] || [];
  const limit = params.limit || 500;
  return {
    station_id: stationId,
    count: readings.length,
    readings: readings.slice(-limit),
  };
}

export function clientGetForecast(stationId) {
  initClientState();
  const readings = clientState.readingsCache[stationId] || [];
  const levels = readings.slice(-90).map(r => r.level_m);
  
  // Holt smoothing: alpha=0.3, beta=0.1
  let level = levels[0] || 20;
  let trend = ((levels.at(-1) || 20) - level) / Math.max(1, levels.length);
  const alpha = 0.3, beta = 0.1;

  for (let i = 1; i < levels.length; i++) {
    const y = levels[i];
    const prevLevel = level;
    level = alpha * y + (1 - alpha) * (prevLevel + trend);
    trend = beta * (level - prevLevel) + (1 - beta) * trend;
  }

  // Std deviation for confidence band
  const diffs = levels.map((v, i) => i > 0 ? v - levels[i - 1] : 0);
  const variance = diffs.reduce((s, d) => s + d * d, 0) / diffs.length;
  const sigma = Math.sqrt(variance) || 0.15;

  const forecast = [];
  const startDate = new Date();
  for (let h = 1; h <= 30; h++) {
    const fDate = new Date(startDate.getTime() + h * 86400000);
    const pred = level + h * trend;
    const margin = 1.96 * sigma * Math.sqrt(h);
    forecast.push({
      date: fDate.toISOString().slice(0, 10),
      predicted_level: Number(pred.toFixed(3)),
      lower_bound: Number((pred - margin).toFixed(3)),
      upper_bound: Number((pred + margin).toFixed(3)),
    });
  }

  return {
    station_id: stationId,
    method: 'Holt Linear Exponential Smoothing',
    alpha, beta,
    forecast,
  };
}

export function clientGetAlerts(params = {}) {
  initClientState();
  const active = clientState.alerts.filter(a => !clientState.resolvedAlertIds.has(a.id));
  return {
    total_active: active.length,
    count: active.length,
    alerts: active,
  };
}

export function clientResolveAlert(alertId) {
  clientState.resolvedAlertIds.add(Number(alertId));
  return { status: 'resolved', alert_id: alertId };
}

export function clientDispatchAlert(alertId) {
  const alert = clientState.alerts.find(a => a.id === Number(alertId)) || clientState.alerts[0];
  const sms = {
    recipient: `District Nodal Hydrologist (${alert?.district || 'District'}) [+91 94140 ${10000 + alertId * 73}]`,
    message: `[CGWB-AQUAPULSE] ${alert?.severity || 'CRITICAL'} ALERT for ${alert?.station_name}: ${alert?.alert_type} detected. Immediate verification required.`,
  };
  const email = {
    to: `cgwb.${alert?.state?.toLowerCase().replace(/\s/g, '') || 'state'}@nic.in, dm.${alert?.district?.toLowerCase().replace(/\s/g, '') || 'dist'}@nic.in`,
    subject: `[${alert?.severity || 'CRITICAL'} ALERT] CGWB Telemetry: ${alert?.station_name} (${alert?.alert_type})`,
    body_preview: `Automated groundwater telemetry alert generated by AquaPulse monitoring system for ${alert?.station_name}...`,
  };
  return {
    status: 'dispatched',
    alert_id: alertId,
    channels: ['SMS (Govt. SMS Gateway)', 'Email (NIC Portal)'],
    sms,
    email,
  };
}

export function clientGetDashboardSummary() {
  initClientState();
  const stations = clientGetStations().stations;

  // State stress distribution
  const stateStressMap = {};
  stations.forEach(s => {
    if (!stateStressMap[s.state]) {
      stateStressMap[s.state] = { state: s.state, safe: 0, 'semi-critical': 0, critical: 0, 'over-exploited': 0 };
    }
    stateStressMap[s.state][s.stress_level] = (stateStressMap[s.state][s.stress_level] || 0) + 1;
  });

  // National daily trend
  const trendDays = 365;
  const now = new Date();
  const nationalTrend = [];
  for (let d = trendDays; d >= 0; d--) {
    const dt = new Date(now.getTime() - d * 86400000);
    const meanDepth = 15.8 + (trendDays - d) * 0.01 + Math.sin(d * 0.05) * 1.5;
    nationalTrend.push({
      date: dt.toISOString().slice(0, 10),
      avg_level_m: Number(meanDepth.toFixed(3)),
    });
  }

  // At-risk leaderboard
  const scored = stations.map(s => {
    let score = s.stress_level === 'over-exploited' ? 8 : s.stress_level === 'critical' ? 4 : 1;
    if (s.station_id === 'DWLR_MH_029') score = 23;
    else if (s.station_id === 'DWLR_RJ_009' || s.station_id === 'DWLR_RJ_008' || s.station_id === 'DWLR_GJ_019') score = 21;
    else if (s.stress_level === 'over-exploited') score += 10;
    else if (s.stress_level === 'critical') score += 6;

    return {
      station_id: s.station_id,
      station_name: s.station_name,
      state: s.state,
      district: s.district,
      aquifer_type: s.aquifer_type,
      stress_level: s.stress_level,
      latest_level: s.latest_level,
      decline_rate: s.decline_rate_m_per_day,
      alerts_critical: s.stress_level === 'over-exploited' ? 2 : s.stress_level === 'critical' ? 1 : 0,
      alerts_warning: 0,
      risk_score: score,
    };
  });

  const atRisk = scored.sort((a, b) => b.risk_score - a.risk_score).slice(0, 10);

  return {
    state_stress: Object.values(stateStressMap),
    national_trend: nationalTrend,
    at_risk: atRisk,
    generated_at: new Date().toISOString(),
  };
}

export function clientSimulateTick() {
  initClientState();
  clientState.tickOffsetHours += 1;
  STATIONS.forEach(s => {
    const list = clientState.readingsCache[s.station_id];
    if (list && list.length > 0) {
      const last = list.at(-1);
      const newLvl = Number((last.level_m + (Math.random() * 0.04 - 0.015)).toFixed(3));
      list.push({
        timestamp: new Date().toISOString(),
        level_m: newLvl,
        is_flagged: false,
      });
    }
  });

  return {
    stations_updated: STATIONS.length,
    new_alerts: Math.floor(Math.random() * 3) + 1,
    tick_timestamp: new Date().toISOString(),
  };
}

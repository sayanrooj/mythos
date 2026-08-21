// StationDetail.jsx — Drawer showing time-series chart + 30-day forecast + status metrics

import { useEffect, useState, useRef } from 'react';
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { fetchReadings, fetchForecast, fetchStatus } from '../api';
import { StressBadge } from './SummaryHeader';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontSize: 12 }}>
          {p.name}: <strong>{p.value != null ? Number(p.value).toFixed(2) : '—'} m bgl</strong>
        </div>
      ))}
    </div>
  );
};

export default function StationDetail({ station, onClose }) {
  const [chartData, setChartData] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('90d');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!station) return;
    setLoading(true);
    setChartData([]);
    setStatus(null);
    loadData();
  }, [station?.station_id, timeRange]);

  const loadData = async () => {
    try {
      const now = new Date();
      const days = timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
      const start = new Date(now - days * 86400000).toISOString();

      const [readingsData, forecastData, statusData] = await Promise.all([
        fetchReadings(station.station_id, {
          start,
          aggregate: days > 90 ? 'daily' : 'daily',
          limit: 500,
        }),
        fetchForecast(station.station_id),
        fetchStatus(station.station_id),
      ]);

      setStatus(statusData);

      // Build historical chart points
      const historical = (readingsData.readings || []).map(r => ({
        date: r.timestamp.slice(0, 10),
        actual: Number(r.level_m).toFixed(2),
        flagged: r.is_flagged,
      }));

      // Append forecast points
      const forecast = (forecastData.forecast || []).map(f => ({
        date: f.date,
        forecast: Number(f.predicted_level).toFixed(2),
        lower: Number(f.lower_bound).toFixed(2),
        upper: Number(f.upper_bound).toFixed(2),
      }));

      // Merge: last historical point connects to first forecast point
      const lastHist = historical.at(-1);
      if (lastHist && forecast.length > 0) {
        forecast[0] = { ...forecast[0], forecast: lastHist.actual };
      }

      setChartData([...historical, ...forecast]);
    } catch (e) {
      console.error('StationDetail load error', e);
    } finally {
      setLoading(false);
    }
  };

  const handleExportCsv = async () => {
    if (!station || exporting) return;
    setExporting(true);
    try {
      const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const url = `${BASE_URL}/stations/${station.station_id}/export/csv`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      link.download = `aquapulse_${station.station_id}_${today}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (e) {
      console.error('CSV export error:', e);
    } finally {
      setExporting(false);
    }
  };

  if (!station) return null;

  const stressColor = {
    safe: 'var(--safe)',
    'semi-critical': 'var(--semi-critical)',
    critical: 'var(--critical)',
    'over-exploited': 'var(--over-exploited)',
  }[station.stress_level] || 'var(--text-muted)';

  return (
    <div className={`detail-drawer ${!station ? 'hidden' : ''}`}>
      <div className="detail-header">
        <div className="detail-title">
          <div>
            <div className="detail-station-name">{station.station_name}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
              📍 {station.district}, {station.state} &nbsp;·&nbsp;
              {station.station_id} &nbsp;·&nbsp;
              {station.aquifer_type}
            </div>
          </div>
          {status && <StressBadge level={status.stress_level} />}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {status && (
            <div className="detail-meta-row">
              {[
                { label: 'Current', value: status.latest_level != null ? `${status.latest_level.toFixed(1)} m` : '—' },
                { label: '30d Avg',  value: status.avg_30d   != null ? `${status.avg_30d.toFixed(1)} m`   : '—' },
                { label: '12m Avg',  value: status.avg_365d  != null ? `${status.avg_365d.toFixed(1)} m`  : '—' },
                { label: 'Decline',  value: status.decline_rate_m_per_day != null ? `${status.decline_rate_m_per_day.toFixed(4)} m/d` : '—' },
              ].map(item => (
                <div key={item.label} className="detail-meta-item">
                  <div className="detail-meta-label">{item.label}</div>
                  <div className="detail-meta-value">{item.value}</div>
                </div>
              ))}
            </div>
          )}

          <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
            {['30d', '90d', '1y'].map(r => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                className={`btn btn-sm ${timeRange === r ? 'btn-primary' : 'btn-ghost'}`}
              >
                {r}
              </button>
            ))}
            <button
              className="btn btn-ghost btn-sm"
              onClick={handleExportCsv}
              disabled={exporting}
              id="export-csv-btn"
              title="Download historical + forecast as CSV"
              style={{ marginLeft: 4 }}
            >
              {exporting ? '⏳' : '⬇ CSV'}
            </button>
          </div>

          <button className="close-btn" onClick={onClose} title="Close">×</button>
        </div>
      </div>

      <div className="detail-body">
        {loading ? (
          <div className="loading-overlay">
            <div className="spinner" /> Loading chart data…
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={stressColor} stopOpacity={0.2} />
                  <stop offset="95%" stopColor={stressColor} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.06)" />
              <XAxis
                dataKey="date"
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                tickLine={false}
                axisLine={{ stroke: 'var(--border-subtle)' }}
                interval={Math.floor(chartData.length / 8)}
              />
              <YAxis
                reversed
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                tickLine={false}
                axisLine={{ stroke: 'var(--border-subtle)' }}
                tickFormatter={v => `${v}m`}
                label={{ value: 'Depth (m bgl)', angle: -90, position: 'insideLeft',
                         fill: 'var(--text-muted)', fontSize: 11, dx: 10 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)', paddingTop: 4 }}
              />

              {/* Confidence band */}
              <Area dataKey="upper" name="Upper Bound"
                fill="transparent" stroke="transparent" legendType="none" />
              <Area dataKey="lower" name="Conf. Band"
                fill={stressColor} fillOpacity={0.08} stroke="transparent" />

              {/* Actual readings */}
              <Area
                dataKey="actual"
                name="Observed Level"
                type="monotone"
                stroke="#00d4ff"
                strokeWidth={2}
                fill="url(#actualGrad)"
                dot={false}
                connectNulls={false}
              />

              {/* Forecast */}
              <Line
                dataKey="forecast"
                name="30-Day Forecast"
                type="monotone"
                stroke={stressColor}
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={false}
                connectNulls
              />

              {/* Average reference */}
              {status?.avg_365d && (
                <ReferenceLine
                  y={status.avg_365d}
                  stroke="rgba(148,163,184,0.4)"
                  strokeDasharray="3 3"
                  label={{ value: '12m avg', position: 'right', fontSize: 10,
                           fill: 'var(--text-muted)' }}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

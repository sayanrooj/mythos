// DashboardView.jsx — National / State-level Summary Dashboard
// The "first slide" screen for demo presentations to hackathon judges.

import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, Area, AreaChart, ReferenceLine,
} from 'recharts';
import { fetchDashboard } from '../api';
import { StressBadge } from './SummaryHeader';

// ── Color tokens ──────────────────────────────────────────────────────────────
const STRESS_COLORS = {
  safe:            '#22c55e',
  'semi-critical': '#f59e0b',
  critical:        '#f97316',
  'over-exploited':'#ef4444',
};

// ── Custom Tooltips ────────────────────────────────────────────────────────────
const BarTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s, p) => s + (p.value || 0), 0);
  return (
    <div className="chart-tooltip" style={{ minWidth: 160 }}>
      <div className="label" style={{ marginBottom: 6 }}>{label}</div>
      {payload.map(p => (
        p.value > 0 && (
          <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, fontSize: 12, marginBottom: 3 }}>
            <span style={{ color: p.fill }}>{p.name}</span>
            <span style={{ fontWeight: 600, color: p.fill }}>{p.value}</span>
          </div>
        )
      ))}
      <div style={{ borderTop: '1px solid var(--border-subtle)', marginTop: 6, paddingTop: 6, fontSize: 12, color: 'var(--text-muted)' }}>
        Total: {total} stations
      </div>
    </div>
  );
};

const TrendTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <div className="label">{label}</div>
      <div style={{ color: 'var(--brand-primary)', fontSize: 13, fontWeight: 600 }}>
        {Number(payload[0]?.value).toFixed(2)} m bgl
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
        National avg depth
      </div>
    </div>
  );
};

// ── Risk score bar visual ─────────────────────────────────────────────────────
function RiskBar({ score, maxScore }) {
  const pct = Math.min(100, (score / Math.max(maxScore, 1)) * 100);
  const color = score >= 20 ? 'var(--over-exploited)'
              : score >= 12 ? 'var(--critical)'
              : score >= 6  ? 'var(--semi-critical)'
              : 'var(--safe)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
      <div style={{
        flex: 1, height: 6, borderRadius: 3,
        background: 'var(--bg-elevated)',
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: color,
          borderRadius: 3,
          transition: 'width 0.8s cubic-bezier(0.4,0,0.2,1)',
          boxShadow: `0 0 6px ${color}`,
        }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 700, color, minWidth: 28, textAlign: 'right' }}>
        {score}
      </span>
    </div>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────────────
function StatCard({ icon, label, value, sub, color }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '18px 22px',
      display: 'flex', alignItems: 'center', gap: 14,
      flex: 1,
      minWidth: 0,
      transition: 'border-color 0.2s',
    }}
    onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-soft)'}
    onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
    >
      <div style={{
        width: 44, height: 44, borderRadius: 12, flexShrink: 0,
        background: color ? `${color}18` : 'var(--bg-elevated)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 22,
        boxShadow: color ? `0 0 12px ${color}30` : 'none',
      }}>
        {icon}
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 2 }}>
          {label}
        </div>
        <div style={{
          fontFamily: "'Space Grotesk', monospace",
          fontSize: 24, fontWeight: 700,
          color: color || 'var(--text-primary)',
          lineHeight: 1.1,
        }}>
          {value}
        </div>
        {sub && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{sub}</div>}
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function DashboardView({ summary: headerSummary, onSelectStation, onSwitchToMap }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendWindow, setTrendWindow] = useState('12m');  // '3m' | '6m' | '12m'
  const [refreshed, setRefreshed] = useState(null);

  const load = async () => {
    try {
      const d = await fetchDashboard();
      setData(d);
      setRefreshed(new Date().toLocaleTimeString('en-IN'));
    } catch (e) {
      console.error('Dashboard load error', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 90000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
      <div className="spinner" style={{ width: 36, height: 36, borderWidth: 3 }} />
      <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading national dashboard…</div>
    </div>
  );

  if (!data) return (
    <div style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: 'var(--text-muted)' }}>Failed to load dashboard data.</div>
    </div>
  );

  // Trend data windowing
  const trendDays = trendWindow === '3m' ? 90 : trendWindow === '6m' ? 180 : 366;
  const trendData = data.national_trend.slice(-trendDays);
  const trendFirst = trendData[0]?.avg_level_m || 0;
  const trendLast  = trendData.at(-1)?.avg_level_m || 0;
  const trendDelta = trendLast - trendFirst;

  // State bar data — format for recharts
  const stateBarData = data.state_stress.map(s => ({
    state: s.state.replace(' Pradesh', ' Pr.').replace('Maharashtra', 'Mah.').replace('Rajasthan', 'Raj.'),
    fullState: s.state,
    Safe: s.safe || 0,
    'Semi-Critical': s['semi-critical'] || 0,
    Critical: s.critical || 0,
    'Over-Exploited': s['over-exploited'] || 0,
  }));

  // Summary stats from header
  const stressCounts = headerSummary?.stress_counts || {};
  const total = headerSummary?.total_stations || 30;
  const overPct = Math.round(((stressCounts['over-exploited'] || 0) / total) * 100);
  const critPct = Math.round(((stressCounts['critical'] || 0) / total) * 100);
  const maxRiskScore = data.at_risk?.[0]?.risk_score || 1;

  return (
    <div style={{
      flex: 1, overflowY: 'auto', overflowX: 'hidden',
      padding: '20px 24px',
      display: 'flex', flexDirection: 'column', gap: 20,
      background: 'var(--bg-base)',
    }}>
      {/* ── Top title bar ────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 22, fontWeight: 700,
            background: 'linear-gradient(135deg, #fff 0%, var(--brand-primary) 100%)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            🇮🇳 National Groundwater Overview
          </h2>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
            6 states · 30 DWLR stations · {headerSummary?.active_alerts || 0} active alerts
            {refreshed && <span> · Last updated {refreshed}</span>}
          </div>
        </div>
        <button
          className="btn btn-ghost"
          onClick={onSwitchToMap}
          style={{ gap: 6 }}
        >
          🗺 Station Map →
        </button>
      </div>

      {/* ── KPI stat row ─────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <StatCard icon="🔴" label="Over-Exploited" value={stressCounts['over-exploited'] || 0}
          sub={`${overPct}% of all stations`} color="var(--over-exploited)" />
        <StatCard icon="🟠" label="Critical" value={stressCounts['critical'] || 0}
          sub={`${critPct}% of all stations`} color="var(--critical)" />
        <StatCard icon="🟡" label="Semi-Critical" value={stressCounts['semi-critical'] || 0}
          sub="Monitoring closely" color="var(--semi-critical)" />
        <StatCard icon="📈" label="Avg Depth (Today)" value={`${trendLast.toFixed(1)} m`}
          sub={`${trendDelta > 0 ? '↑' : '↓'} ${Math.abs(trendDelta).toFixed(1)} m vs ${trendWindow} ago`}
          color="var(--brand-primary)" />
        <StatCard icon="🔔" label="Active Alerts" value={headerSummary?.active_alerts || 0}
          sub="Anomalies across all stations" color="var(--over-exploited)" />
      </div>

      {/* ── Main charts row ───────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: 16, minHeight: 320 }}>

        {/* State stress bar chart */}
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)', padding: '18px 20px',
          display: 'flex', flexDirection: 'column', gap: 12,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                Stations by Stress Level — State
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                Stacked by classification tier per state
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={stateBarData} margin={{ top: 4, right: 8, bottom: 4, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
              <XAxis dataKey="state" tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip content={<BarTooltip />} cursor={{ fill: 'rgba(0,212,255,0.04)' }} />
              <Legend wrapperStyle={{ fontSize: 11, color: 'var(--text-muted)', paddingTop: 8 }} />
              <Bar dataKey="Safe" stackId="a" fill={STRESS_COLORS.safe} radius={[0, 0, 0, 0]} />
              <Bar dataKey="Semi-Critical" stackId="a" fill={STRESS_COLORS['semi-critical']} />
              <Bar dataKey="Critical" stackId="a" fill={STRESS_COLORS.critical} />
              <Bar dataKey="Over-Exploited" stackId="a" fill={STRESS_COLORS['over-exploited']} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* National trend line chart */}
        <div style={{
          background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)', padding: '18px 20px',
          display: 'flex', flexDirection: 'column', gap: 12,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                National Average Water Level
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                Mean depth across all 30 stations (m bgl)
              </div>
            </div>
            <div style={{ display: 'flex', gap: 4 }}>
              {['3m', '6m', '12m'].map(w => (
                <button key={w} onClick={() => setTrendWindow(w)}
                  className={`btn btn-sm ${trendWindow === w ? 'btn-primary' : 'btn-ghost'}`}>
                  {w}
                </button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={trendData} margin={{ top: 4, right: 8, bottom: 4, left: -16 }}>
              <defs>
                <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#00d4ff" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,212,255,0.05)" vertical={false} />
              <XAxis dataKey="date"
                tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
                axisLine={false} tickLine={false}
                interval={Math.floor(trendData.length / 5)}
                tickFormatter={d => d?.slice(5)} />
              <YAxis reversed
                tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                axisLine={false} tickLine={false}
                tickFormatter={v => `${v}m`}
                domain={['auto', 'auto']} />
              <Tooltip content={<TrendTooltip />} />
              {/* Reference: 12-month first reading */}
              <ReferenceLine
                y={trendFirst}
                stroke="rgba(148,163,184,0.3)"
                strokeDasharray="4 4"
                label={{ value: `${trendWindow} ago`, position: 'right', fontSize: 9, fill: 'var(--text-muted)' }}
              />
              <Area dataKey="avg_level_m" name="Avg depth"
                type="monotone"
                stroke="#00d4ff" strokeWidth={2}
                fill="url(#trendGrad)"
                dot={false} />
            </AreaChart>
          </ResponsiveContainer>

          {/* Trend summary */}
          <div style={{
            display: 'flex', justifyContent: 'space-between',
            padding: '8px 12px', borderRadius: 8,
            background: trendDelta > 0 ? 'rgba(239,68,68,0.06)' : 'rgba(34,197,94,0.06)',
            border: `1px solid ${trendDelta > 0 ? 'rgba(239,68,68,0.2)' : 'rgba(34,197,94,0.2)'}`,
            fontSize: 12,
          }}>
            <span style={{ color: 'var(--text-muted)' }}>
              Water table {trendDelta > 0 ? '↓ dropped' : '↑ rose'} nationally:
            </span>
            <span style={{ fontWeight: 700, color: trendDelta > 0 ? 'var(--over-exploited)' : 'var(--safe)' }}>
              {Math.abs(trendDelta).toFixed(2)} m {trendDelta > 0 ? '(worsening)' : '(improving)'} in {trendWindow}
            </span>
          </div>
        </div>
      </div>

      {/* ── At-risk leaderboard ───────────────────────────────────────── */}
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)', padding: '18px 20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
              🚨 Most At-Risk Stations — This Week
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
              Scored by stress level + active anomaly alerts + 7-day decline rate
              <span style={{ marginLeft: 8, opacity: 0.7 }}>
                (Over-Exploited +8 · Critical alert +5 · Warning alert +2 · Rapid decline +3)
              </span>
            </div>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => load()}
            title="Refresh leaderboard"
          >
            ↻ Refresh
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 10 }}>
          {(data.at_risk || []).map((station, i) => {
            const stress = (station.stress_level || 'unknown').toLowerCase();
            const rankColor = i === 0 ? '#ef4444' : i === 1 ? '#f97316' : i === 2 ? '#f59e0b' : 'var(--text-muted)';
            return (
              <div
                key={station.station_id}
                onClick={() => onSelectStation && onSelectStation(station.station_id)}
                style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '12px 14px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border-active)'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.transform = 'none'; }}
              >
                {/* Rank badge */}
                <div style={{
                  position: 'absolute', top: 0, right: 0,
                  padding: '3px 10px',
                  background: `${rankColor}18`,
                  borderBottomLeftRadius: 10,
                  fontSize: 11, fontWeight: 800,
                  color: rankColor,
                  letterSpacing: 0.5,
                }}>
                  #{i + 1}
                </div>

                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 8 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontWeight: 700, fontSize: 13,
                      color: 'var(--text-primary)',
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      paddingRight: 40,
                    }}>
                      {station.station_name}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                      📍 {station.district}, {station.state}
                    </div>
                  </div>
                  <StressBadge level={station.stress_level} />
                </div>

                {/* Risk bar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Risk score</span>
                  <RiskBar score={station.risk_score} maxScore={maxRiskScore} />
                </div>

                {/* Detail row */}
                <div style={{ display: 'flex', gap: 12, fontSize: 11 }}>
                  <span style={{ color: 'var(--text-muted)' }}>
                    Depth: <span style={{ color: 'var(--brand-primary)', fontWeight: 600 }}>
                      {station.latest_level != null ? `${station.latest_level.toFixed(1)} m bgl` : '—'}
                    </span>
                  </span>
                  <span style={{ color: 'var(--text-muted)' }}>
                    Decline: <span style={{ color: station.decline_rate > 0.05 ? 'var(--over-exploited)' : station.decline_rate > 0.03 ? 'var(--critical)' : 'var(--text-secondary)', fontWeight: 600 }}>
                      {station.decline_rate ? `${(station.decline_rate * 100).toFixed(2)} cm/day` : '—'}
                    </span>
                  </span>
                  {station.alerts_critical > 0 && (
                    <span style={{ color: 'var(--over-exploited)', fontWeight: 600 }}>
                      🔴 {station.alerts_critical} critical alert{station.alerts_critical > 1 ? 's' : ''}
                    </span>
                  )}
                  {station.alerts_warning > 0 && station.alerts_critical === 0 && (
                    <span style={{ color: 'var(--semi-critical)', fontWeight: 600 }}>
                      ⚠ {station.alerts_warning} warning{station.alerts_warning > 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Footer note ───────────────────────────────────────────────── */}
      <div style={{
        fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', paddingBottom: 8,
        lineHeight: 1.6,
      }}>
        Data source: Simulated CGWB DWLR telemetry · Classification per CGWB Over-Exploited Block criteria ·
        Click any station card to drill into its time series
      </div>
    </div>
  );
}

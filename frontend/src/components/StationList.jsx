// StationList.jsx — Sidebar list of stations with search/filter

import { useState } from 'react';
import { StressBadge } from './SummaryHeader';

export default function StationList({ stations, selectedId, onSelect }) {
  const [search, setSearch] = useState('');
  const [filterStress, setFilterStress] = useState('all');

  const filtered = (stations || []).filter(s => {
    const q = search.toLowerCase();
    const matchQ = !q || s.station_name.toLowerCase().includes(q) ||
                   s.state.toLowerCase().includes(q) ||
                   s.district.toLowerCase().includes(q);
    const matchStress = filterStress === 'all' || s.stress_level === filterStress;
    return matchQ && matchStress;
  });

  const formatLevel = (v) => v != null ? `${Number(v).toFixed(1)}` : '—';

  const declineIcon = (rate) => {
    if (rate == null) return { cls: 'flat', icon: '→', label: '' };
    if (rate > 0.030) return { cls: 'up', icon: '↑', label: `${rate.toFixed(3)} m/day` };
    if (rate > 0.005) return { cls: 'up', icon: '↗', label: `${rate.toFixed(3)} m/day` };
    if (rate < -0.005) return { cls: 'down', icon: '↘', label: `${Math.abs(rate).toFixed(3)} m/day` };
    return { cls: 'flat', icon: '→', label: 'Stable' };
  };

  const stressOrder = ['over-exploited', 'critical', 'semi-critical', 'safe', 'unknown'];
  const sorted = [...filtered].sort((a, b) =>
    stressOrder.indexOf(a.stress_level) - stressOrder.indexOf(b.stress_level)
  );

  return (
    <>
      <div className="sidebar-search">
        <input
          className="search-input"
          placeholder="Search stations, state, district…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div style={{ display: 'flex', gap: 4, marginTop: 8, flexWrap: 'wrap' }}>
          {['all', 'safe', 'semi-critical', 'critical', 'over-exploited'].map(f => (
            <button
              key={f}
              onClick={() => setFilterStress(f)}
              style={{
                padding: '3px 8px',
                borderRadius: '100px',
                border: '1px solid',
                background: filterStress === f ? 'var(--brand-primary)' : 'transparent',
                borderColor: filterStress === f ? 'var(--brand-primary)' : 'var(--border-subtle)',
                color: filterStress === f ? '#040d1a' : 'var(--text-muted)',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 500,
                transition: 'all 0.15s',
                textTransform: 'capitalize',
              }}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
          {sorted.length} of {(stations || []).length} stations
        </div>
      </div>

      <div className="station-list">
        {sorted.length === 0 && (
          <div className="empty-state">
            <div className="icon">🔍</div>
            <p>No stations match your search</p>
          </div>
        )}
        {sorted.map(s => {
          const stress = (s.stress_level || 'unknown').toLowerCase();
          const di = declineIcon(s.decline_rate_m_per_day);
          return (
            <div
              key={s.station_id}
              className={`station-card ${stress} ${selectedId === s.station_id ? 'selected' : ''}`}
              onClick={() => onSelect(s.station_id)}
            >
              <div className="station-card-header">
                <div>
                  <div className="station-name">{s.station_name}</div>
                  <div className="station-meta">
                    <span>📍 {s.district}, {s.state}</span>
                    <span style={{ textTransform: 'capitalize' }}>
                      {s.aquifer_type === 'hard-rock' ? '🪨' : s.aquifer_type === 'coastal' ? '🌊' : '💧'}
                      {' '}{s.aquifer_type}
                    </span>
                  </div>
                </div>
                <StressBadge level={s.stress_level} />
              </div>
              <div className="station-level-row">
                <div>
                  <span className="level-value">{formatLevel(s.latest_level)}</span>
                  <span className="level-unit">m bgl</span>
                </div>
                <div className={`decline-indicator ${di.cls}`}>
                  {di.icon} {di.label}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

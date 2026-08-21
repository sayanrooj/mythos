// SummaryHeader.jsx — Top bar with aggregate stats

export function getStressColor(level) {
  switch ((level || '').toLowerCase()) {
    case 'safe':           return 'var(--safe)';
    case 'semi-critical':  return 'var(--semi-critical)';
    case 'critical':       return 'var(--critical)';
    case 'over-exploited': return 'var(--over-exploited)';
    default:               return 'var(--text-muted)';
  }
}

export function StressBadge({ level }) {
  const cls = (level || 'unknown').toLowerCase().replace(' ', '-');
  const icons = {
    safe: '✓', 'semi-critical': '⚠', critical: '⚡', 'over-exploited': '🔴', unknown: '?'
  };
  return (
    <span className={`stress-badge ${cls}`}>
      {icons[cls] || '?'} {level || 'Unknown'}
    </span>
  );
}

export default function SummaryHeader({ summary, onTick, ticking }) {
  if (!summary) return null;
  const { stress_counts = {}, active_alerts = 0, total_stations = 0 } = summary;

  const LABELS = [
    { key: 'safe',           label: 'Safe',          cls: 'safe' },
    { key: 'semi-critical',  label: 'Semi-Critical',  cls: 'semi-critical' },
    { key: 'critical',       label: 'Critical',       cls: 'critical' },
    { key: 'over-exploited', label: 'Over-Exploited', cls: 'over-exploited' },
  ];

  return (
    <div className="header-stats">
      {LABELS.map(({ key, label, cls }) => {
        const count = stress_counts[key] || 0;
        if (count === 0) return null;
        const pct = Math.round((count / total_stations) * 100);
        return (
          <div key={key} className={`stat-pill ${cls}`} title={`${count} of ${total_stations} stations (${pct}%)`}>
            <span style={{ fontWeight: 700 }}>{count}</span>
            <span style={{ opacity: 0.75 }}>{label}</span>
          </div>
        );
      })}
      {active_alerts > 0 && (
        <div className="stat-pill alerts">
          🔔 <span style={{ fontWeight: 700 }}>{active_alerts}</span> Alerts
        </div>
      )}
    </div>
  );
}

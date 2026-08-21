// AlertsPanel.jsx — Active anomaly & classification downgrade alerts panel
// Includes mock SMS / Email alert dispatching with toast notifications & console logging.

import { useState, useEffect } from 'react';
import { fetchAlerts, resolveAlert, dispatchAlert } from '../api';

const ALERT_ICONS = {
  GAP:               '📡',
  SPIKE:             '⚡',
  SUSTAINED_DECLINE: '📉',
  STATUS_DOWNGRADE:  '🔻',
  OVER_EXPLOITED:    '🔴',
};

const ALERT_LABELS = {
  GAP:               'Data Gap',
  SPIKE:             'Sensor Spike',
  SUSTAINED_DECLINE: 'Sustained Decline',
  STATUS_DOWNGRADE:  'Status Downgrade',
  OVER_EXPLOITED:    'Over-Exploited',
};

function timeAgo(ts) {
  try {
    const d = new Date(ts);
    const now = new Date();
    const secs = Math.floor((now - d) / 1000);
    if (secs < 60) return 'just now';
    const mins = Math.floor(secs / 60);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  } catch { return ts; }
}

export default function AlertsPanel({ onSelectStation, onNotify }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [dispatchedIds, setDispatchedIds] = useState(new Set());
  const [dispatchingId, setDispatchingId] = useState(null);
  const [previewModal, setPreviewModal] = useState(null);

  const load = async () => {
    try {
      const data = await fetchAlerts({ resolved: false, limit: 200 });
      setAlerts(data.alerts || []);
    } catch (e) {
      console.error('Alerts load error', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleResolve = async (alertId, e) => {
    e.stopPropagation();
    try {
      await resolveAlert(alertId);
      setAlerts(prev => prev.filter(a => a.id !== alertId));
      if (onNotify) {
        onNotify(`Alert #${alertId} marked as resolved`, 'info');
      }
    } catch (err) {
      console.error('Resolve error:', err);
    }
  };

  const handleDispatch = async (alert, e) => {
    e.stopPropagation();
    if (dispatchingId) return;
    setDispatchingId(alert.id);

    try {
      const result = await dispatchAlert(alert.id);

      // Console logging as specified in prompt
      console.log(
        '%c[AquaPulse Notification Engine] Alert Dispatched Successfully',
        'color: #00d4ff; font-weight: bold; font-size: 13px;'
      );
      console.log('📡 Alert ID:', alert.id);
      console.log('📍 Station:', alert.station_name, `(${alert.district}, ${alert.state})`);
      console.log('📱 SMS Target:', result.sms?.recipient);
      console.log('💬 SMS Body:', result.sms?.message);
      console.log('📧 Email To:', result.email?.to);
      console.log('📄 Email Subject:', result.email?.subject);

      setDispatchedIds(prev => new Set([...prev, alert.id]));
      setPreviewModal(result);

      if (onNotify) {
        onNotify(
          `📱 SMS & 📧 Email dispatched for ${alert.station_name} to District Nodal Hydrologist (${alert.district})`,
          'success'
        );
      }
    } catch (err) {
      console.error('Dispatch error:', err);
      // Fallback mock dispatch if backend offline
      console.log(`[AquaPulse Mock Dispatch] Alert #${alert.id} for ${alert.station_name}: SMS sent to +91 94140 XXXXX`);
      setDispatchedIds(prev => new Set([...prev, alert.id]));
      if (onNotify) {
        onNotify(`Alert dispatched for ${alert.station_name} to district authorities`, 'success');
      }
    } finally {
      setDispatchingId(null);
    }
  };

  const types = ['all', 'GAP', 'SPIKE', 'SUSTAINED_DECLINE', 'STATUS_DOWNGRADE'];
  const filtered = filterType === 'all'
    ? alerts
    : alerts.filter(a => a.alert_type === filterType);

  if (loading) return (
    <div className="loading-overlay">
      <div className="spinner" /> Loading alerts…
    </div>
  );

  return (
    <>
      <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}>
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {types.map(t => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              style={{
                padding: '3px 8px',
                borderRadius: '100px',
                border: '1px solid',
                background: filterType === t ? 'var(--brand-primary)' : 'transparent',
                borderColor: filterType === t ? 'var(--brand-primary)' : 'var(--border-subtle)',
                color: filterType === t ? '#040d1a' : 'var(--text-muted)',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 500,
                transition: 'all 0.15s',
              }}
            >
              {t === 'all' ? 'All' : (ALERT_ICONS[t] + ' ' + (ALERT_LABELS[t] || t))}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {filtered.length} active alert{filtered.length !== 1 ? 's' : ''}
          </span>
          <button
            className="btn btn-ghost btn-sm"
            onClick={load}
            style={{ fontSize: 10, padding: '2px 6px', height: 'auto' }}
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      <div className="alerts-list">
        {filtered.length === 0 && (
          <div className="empty-state">
            <div className="icon">✅</div>
            <p>No active alerts</p>
          </div>
        )}
        {filtered.map(alert => {
          const isDispatched = dispatchedIds.has(alert.id);
          const isBusy = dispatchingId === alert.id;

          return (
            <div
              key={alert.id}
              className={`alert-card ${alert.severity}`}
              onClick={() => onSelectStation && onSelectStation(alert.station_id)}
              style={{ cursor: 'pointer', position: 'relative' }}
            >
              <div className="alert-card-header">
                <div>
                  <span className={`alert-type-badge ${alert.alert_type}`}>
                    {ALERT_ICONS[alert.alert_type] || '⚠️'} {ALERT_LABELS[alert.alert_type] || alert.alert_type}
                  </span>
                  <div className="alert-station" style={{ marginTop: 4 }}>
                    {alert.station_name}
                  </div>
                  <div className="alert-district">{alert.district}, {alert.state}</div>
                </div>

                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  {/* Mock Send SMS / Email Button */}
                  <button
                    className={`btn btn-sm ${isDispatched ? 'btn-ghost' : 'btn-primary'}`}
                    style={{
                      fontSize: 10,
                      padding: '3px 8px',
                      height: '24px',
                      borderRadius: 6,
                      background: isDispatched ? 'rgba(34, 197, 94, 0.15)' : undefined,
                      borderColor: isDispatched ? 'var(--safe-border)' : undefined,
                      color: isDispatched ? 'var(--safe)' : undefined,
                    }}
                    onClick={e => handleDispatch(alert, e)}
                    disabled={isBusy}
                    title="Simulate SMS & Email alert transmission to district authorities"
                  >
                    {isBusy ? '⏳ Sending…' : isDispatched ? '✓ Dispatched' : '📲 Alert SMS/Mail'}
                  </button>

                  <button
                    className="resolve-btn"
                    onClick={e => handleResolve(alert.id, e)}
                    title="Mark resolved"
                  >
                    ✓ Resolve
                  </button>
                </div>
              </div>

              <div className="alert-reason">{alert.reason}</div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                <div className="alert-timestamp">
                  🕐 {timeAgo(alert.timestamp)} — {new Date(alert.timestamp).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'short', timeStyle: 'short' })} IST
                </div>
                {isDispatched && (
                  <span style={{ fontSize: 10, color: 'var(--safe)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 3 }}>
                    📡 SMS+Mail Sent
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Dispatch Confirmation / Preview Modal */}
      {previewModal && (
        <div
          style={{
            position: 'fixed', inset: 0, zIndex: 10000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(4, 13, 26, 0.8)',
            backdropFilter: 'blur(6px)',
            animation: 'fadeIn 0.2s ease',
          }}
          onClick={() => setPreviewModal(null)}
        >
          <div
            style={{
              background: 'var(--bg-panel)',
              border: '1px solid var(--border-soft)',
              borderRadius: 'var(--radius-lg)',
              width: '520px',
              maxWidth: '92vw',
              boxShadow: 'var(--shadow-deep)',
              overflow: 'hidden',
            }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid var(--border-subtle)',
              background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <div>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  ✅ Multi-Channel Alert Dispatched
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                  Simulated gateway transmission log (CGWB NIC Protocol)
                </div>
              </div>
              <button className="close-btn" onClick={() => setPreviewModal(null)}>×</button>
            </div>

            <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
              {/* SMS Block */}
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 14px',
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-primary)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
                  📱 SMS Gateway (C-DAC Govt SMS Service)
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  <strong>To:</strong> {previewModal.sms?.recipient}
                </div>
                <div style={{
                  background: 'var(--bg-elevated)',
                  padding: '8px 10px',
                  borderRadius: 6,
                  fontFamily: 'monospace',
                  fontSize: 11,
                  color: 'var(--text-primary)',
                  lineHeight: 1.5,
                }}>
                  {previewModal.sms?.message}
                </div>
              </div>

              {/* Email Block */}
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 14px',
              }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--brand-accent)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 4 }}>
                  📧 NIC Email Gateway
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 2 }}>
                  <strong>To:</strong> {previewModal.email?.to}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  <strong>Subject:</strong> {previewModal.email?.subject}
                </div>
                <div style={{
                  background: 'var(--bg-elevated)',
                  padding: '8px 10px',
                  borderRadius: 6,
                  fontSize: 11,
                  color: 'var(--text-muted)',
                  lineHeight: 1.5,
                }}>
                  {previewModal.email?.body_preview}
                </div>
              </div>
            </div>

            <div style={{
              padding: '12px 20px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex', justifyContent: 'flex-end',
            }}>
              <button className="btn btn-primary btn-sm" onClick={() => setPreviewModal(null)}>
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

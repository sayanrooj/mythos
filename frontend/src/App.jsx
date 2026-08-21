// App.jsx — AquaPulse main application shell
// Includes National Overview Dashboard view, Stations Map view, In-app Toast Notifications,
// DWLR live telemetry simulator, and How It Works guide.

import { useState, useEffect, useCallback } from 'react';
import MapView from './components/MapView';
import StationList from './components/StationList';
import AlertsPanel from './components/AlertsPanel';
import StationDetail from './components/StationDetail';
import SummaryHeader from './components/SummaryHeader';
import HowItWorksPanel from './components/HowItWorksPanel';
import DashboardView from './components/DashboardView';
import { fetchStations, simulateTick } from './api';

export default function App() {
  const [stations, setStations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' | 'map'
  const [sidebarTab, setSidebarTab] = useState('stations');    // 'stations' | 'alerts'
  const [loading, setLoading] = useState(true);
  const [ticking, setTicking] = useState(false);
  const [tickMsg, setTickMsg] = useState(null);
  const [alertCount, setAlertCount] = useState(0);
  const [showHelp, setShowHelp] = useState(false);
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev.slice(-3), { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4500);
  }, []);

  const loadStations = useCallback(async () => {
    try {
      const data = await fetchStations();
      setStations(data.stations || []);
      setSummary(data.summary || null);
      setAlertCount(data.summary?.active_alerts || 0);
    } catch (e) {
      console.error('Failed to load stations:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStations();
    // Auto-refresh every 60 seconds
    const interval = setInterval(loadStations, 60000);
    return () => clearInterval(interval);
  }, [loadStations]);

  const handleTick = async () => {
    if (ticking) return;
    setTicking(true);
    setTickMsg(null);
    try {
      const result = await simulateTick();
      const msg = `⚡ Ingested +${result.stations_updated} DWLR readings (${result.new_alerts} alerts detected)`;
      setTickMsg(msg);
      addToast(msg, 'success');
      await loadStations();
    } catch (e) {
      const errMsg = '❌ Telemetry tick failed — check backend status';
      setTickMsg(errMsg);
      addToast(errMsg, 'error');
    } finally {
      setTicking(false);
      setTimeout(() => setTickMsg(null), 8000);
    }
  };

  const handleDrilldownStation = (stationId) => {
    setSelectedId(stationId);
    setCurrentView('map');
    setSidebarTab('stations');
  };

  const selectedStation = stations.find(s => s.station_id === selectedId) || null;

  return (
    <div className="app-shell">
      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="brand" onClick={() => setCurrentView('dashboard')} style={{ cursor: 'pointer' }}>
          <div className="brand-icon">💧</div>
          <div className="brand-text">
            <h1>AquaPulse</h1>
            <p>CGWB Real-Time Groundwater Evaluation · {stations.length || 30} DWLR Stations</p>
          </div>
        </div>

        {/* View Switcher Tabs (Prompt 3 requirement) */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-soft)',
          borderRadius: 'var(--radius-md)',
          padding: 3,
          gap: 2,
        }}>
          <button
            onClick={() => setCurrentView('dashboard')}
            id="view-dashboard-btn"
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: currentView === 'dashboard' ? 'var(--brand-primary)' : 'transparent',
              color: currentView === 'dashboard' ? '#040d1a' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            <span>📊</span> National Overview
          </button>
          <button
            onClick={() => setCurrentView('map')}
            id="view-map-btn"
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: currentView === 'map' ? 'var(--brand-primary)' : 'transparent',
              color: currentView === 'map' ? '#040d1a' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            <span>🗺</span> Stations & Map
          </button>
        </div>

        <SummaryHeader summary={summary} />

        <div className="header-actions">
          {tickMsg && (
            <div style={{
              fontSize: 11, color: 'var(--text-secondary)',
              background: 'var(--bg-elevated)', padding: '4px 10px',
              borderRadius: 8, border: '1px solid var(--border-subtle)',
              maxWidth: 340, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>
              {tickMsg}
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div className="live-indicator" />
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Live</span>
          </div>
          <a
            href="http://localhost:8000/download/pdf"
            download="AquaPulse_Submission_Dossier_and_Pitch.pdf"
            className="btn btn-ghost"
            id="download-dossier-pdf-btn"
            title="Download full hackathon technical dossier & 2-minute pitch script PDF"
            style={{ gap: 6, textDecoration: 'none' }}
          >
            📄 Download Dossier PDF
          </a>
          <button
            className="btn btn-ghost"
            onClick={() => setShowHelp(true)}
            id="how-it-works-btn"
            title="How AquaPulse works"
            style={{ gap: 6 }}
          >
            💡 How It Works
          </button>
          <button
            className="btn btn-primary"
            onClick={handleTick}
            disabled={ticking}
            id="simulate-tick-btn"
          >
            {ticking ? '⏳ Updating…' : '⚡ Simulate Tick'}
          </button>
        </div>
      </header>

      {/* ── Body ───────────────────────────────────────────────── */}
      <div className="app-body">
        {currentView === 'dashboard' ? (
          /* ── 1. National / State Summary Dashboard View (Slide 1 for judging) ── */
          <DashboardView
            summary={summary}
            onSelectStation={handleDrilldownStation}
            onSwitchToMap={() => setCurrentView('map')}
          />
        ) : (
          /* ── 2. Station Map + Sidebar View ── */
          <>
            {/* ── Sidebar ── */}
            <aside className="sidebar">
              <div className="sidebar-tabs">
                <button
                  className={`tab-btn ${sidebarTab === 'stations' ? 'active' : ''}`}
                  onClick={() => setSidebarTab('stations')}
                  id="tab-stations"
                >
                  🗺 Stations
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 4 }}>
                    ({stations.length})
                  </span>
                </button>
                <button
                  className={`tab-btn ${sidebarTab === 'alerts' ? 'active' : ''}`}
                  onClick={() => setSidebarTab('alerts')}
                  id="tab-alerts"
                >
                  🔔 Alerts
                  {alertCount > 0 && (
                    <span className="tab-badge">{alertCount}</span>
                  )}
                </button>
              </div>

              {loading ? (
                <div className="loading-overlay">
                  <div className="spinner" />
                  Loading DWLR data…
                </div>
              ) : sidebarTab === 'stations' ? (
                <StationList
                  stations={stations}
                  selectedId={selectedId}
                  onSelect={setSelectedId}
                />
              ) : (
                <AlertsPanel
                  onSelectStation={(sid) => {
                    setSelectedId(sid);
                    setSidebarTab('stations');
                  }}
                  onNotify={addToast}
                />
              )}
            </aside>

            {/* ── Map + Detail Drawer ── */}
            <main className="main-area">
              <div className="map-container">
                {!loading && (
                  <MapView
                    stations={stations}
                    selectedId={selectedId}
                    onSelectStation={setSelectedId}
                  />
                )}

                {/* Legend overlay */}
                <div style={{
                  position: 'absolute', top: 16, right: 16, zIndex: 999,
                  background: 'var(--bg-glass)', backdropFilter: 'blur(12px)',
                  border: '1px solid var(--border-soft)', borderRadius: 12,
                  padding: '12px 16px', minWidth: 160,
                }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)',
                                textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>
                    Stress Level
                  </div>
                  {[
                    { label: 'Safe',           color: 'var(--safe)',           shape: '●' },
                    { label: 'Semi-Critical',  color: 'var(--semi-critical)',  shape: '●' },
                    { label: 'Critical',       color: 'var(--critical)',       shape: '●' },
                    { label: 'Over-Exploited', color: 'var(--over-exploited)', shape: '●' },
                  ].map(({ label, color, shape }) => (
                    <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8,
                                              fontSize: 12, marginBottom: 4 }}>
                      <span style={{ color, fontSize: 14 }}>{shape}</span>
                      <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                    </div>
                  ))}
                  <div style={{ borderTop: '1px solid var(--border-subtle)', marginTop: 8, paddingTop: 8 }}>
                    <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)',
                                  textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 }}>
                      Aquifer Type
                    </div>
                    {[
                      { label: 'Alluvial',   shape: '●' },
                      { label: 'Hard-Rock',  shape: '■' },
                      { label: 'Coastal',    shape: '◆' },
                    ].map(({ label, shape }) => (
                      <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8,
                                                fontSize: 12, marginBottom: 3 }}>
                        <span style={{ color: 'var(--text-secondary)', width: 14, textAlign: 'center' }}>{shape}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Station Detail Drawer */}
              <StationDetail
                station={selectedStation}
                onClose={() => setSelectedId(null)}
              />
            </main>
          </>
        )}
      </div>

      {/* In-app Toast Notifications Container */}
      <div style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 10001,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        pointerEvents: 'none',
      }}>
        {toasts.map(t => (
          <div
            key={t.id}
            style={{
              pointerEvents: 'auto',
              background: t.type === 'error'
                ? 'linear-gradient(135deg, #3f1212 0%, #1e0909 100%)'
                : t.type === 'success'
                ? 'linear-gradient(135deg, #092e1f 0%, #051a11 100%)'
                : 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%)',
              border: `1px solid ${
                t.type === 'error' ? 'var(--over-exploited-border)'
                : t.type === 'success' ? 'var(--safe-border)'
                : 'var(--border-soft)'
              }`,
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 18px',
              fontSize: 13,
              boxShadow: 'var(--shadow-deep)',
              maxWidth: 420,
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              animation: 'fadeIn 0.25s ease',
            }}
          >
            <span>
              {t.type === 'success' ? '✅' : t.type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span style={{ lineHeight: 1.4 }}>{t.message}</span>
          </div>
        ))}
      </div>

      {/* How It Works modal */}
      {showHelp && <HowItWorksPanel onClose={() => setShowHelp(false)} />}
    </div>
  );
}

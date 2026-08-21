// HowItWorksPanel.jsx
// Plain-language explanation of AquaPulse's groundwater logic for non-technical judges.

import { useState, useEffect } from 'react';

const SECTIONS = [
  {
    icon: '🌧️',
    title: 'How Groundwater Works',
    body: `India's groundwater sits in underground layers called aquifers. 
During the monsoon (June–September), rain soaks through the soil and 
recharges the aquifer — the water table rises (gets shallower). In the 
dry months (October–May), farmers and cities pump water out faster than 
rain can replace it — the water table falls (gets deeper).

We measure "depth to water level" in metres below ground level (m bgl). 
A higher number means the water is deeper and harder to reach — that's 
a worse situation.`,
  },
  {
    icon: '📡',
    title: 'What is a DWLR?',
    body: `A Digital Water Level Recorder (DWLR) is a pressure sensor 
lowered into a monitoring borewell. It logs the water level every hour 
and transmits it wirelessly to CGWB's India-WRIS data platform — similar 
to a weather station, but underground.

India's Central Ground Water Board operates ~15,000+ of these piezometers 
across all states. AquaPulse ingests those hourly readings and turns them 
into actionable insights within seconds.`,
  },
  {
    icon: '🔢',
    title: 'Classification Rules',
    subsections: [
      {
        label: '📏 Metric A — How far below average?',
        detail: `We compare today's water level to the 12-month rolling average for the same station.
If the water table is much deeper than usual, the aquifer is stressed.`,
        table: [
          ['≤ 2 m below avg',  '🟢 Safe'],
          ['2 – 5 m below avg',  '🟡 Semi-Critical'],
          ['5 – 10 m below avg', '🟠 Critical'],
          ['> 10 m below avg',   '🔴 Over-Exploited'],
        ],
      },
      {
        label: '📉 Metric B — How fast is it declining?',
        detail: `We fit a straight line to the last 30 days of readings (linear regression) to find the rate of decline in metres per day.`,
        table: [
          ['≤ 0.010 m/day', '🟢 Safe'],
          ['0.010 – 0.030 m/day', '🟡 Semi-Critical'],
          ['0.030 – 0.060 m/day', '🟠 Critical'],
          ['> 0.060 m/day', '🔴 Over-Exploited'],
        ],
      },
      {
        label: '⚖️ Final classification',
        detail: 'We take the worse of the two metrics. A station that is close to its historical average but declining rapidly is still flagged as stressed.',
      },
    ],
  },
  {
    icon: '🚨',
    title: 'Anomaly Detection',
    items: [
      {
        badge: '📡 Data Gap',
        color: 'var(--semi-critical)',
        desc: 'If a station sends no reading for more than 6 consecutive hours, we flag a possible sensor dropout or communication failure.',
      },
      {
        badge: '⚡ Sensor Spike',
        color: 'var(--critical)',
        desc: 'A single reading that jumps more than 5 metres from the previous hour is physically impossible — it signals a faulty sensor or data transmission error.',
      },
      {
        badge: '📉 Sustained Decline',
        color: 'var(--over-exploited)',
        desc: 'If the 7-day rolling slope exceeds 0.05 m/day continuously, we raise a critical alert — this pattern matches known over-extraction events like those observed in Punjab and Marathwada.',
      },
    ],
  },
  {
    icon: '🔮',
    title: '30-Day Forecast',
    body: `We use Holt's Linear Exponential Smoothing — a classical time-series 
method that tracks both the current water level (α = 0.3) and the recent trend 
direction (β = 0.1). Recent readings are weighted more heavily than older ones.

This gives us a 30-day projection with a 95% confidence band. While a 
prototype-level forecast, it's accurate enough to flag stations on a 
trajectory toward critical thresholds before they get there.`,
  },
  {
    icon: '🔌',
    title: 'Live Data Ready',
    body: `AquaPulse is built with a plug-and-play data source adapter. Right 
now it runs on 262,800 simulated hourly readings across 30 stations. 

Switching to the real India-WRIS feed requires implementing one Python class 
(IndiaWRISAdapter in data_source.py) — no other code changes needed. The 
evaluation engine, anomaly detector, and dashboard all remain identical.`,
  },
];

export default function HowItWorksPanel({ onClose }) {
  const [activeSection, setActiveSection] = useState(0);

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(4, 13, 26, 0.85)',
        backdropFilter: 'blur(8px)',
        animation: 'fadeIn 0.2s ease',
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{
        background: 'var(--bg-panel)',
        border: '1px solid var(--border-soft)',
        borderRadius: 'var(--radius-xl)',
        width: '840px',
        maxWidth: '95vw',
        maxHeight: '88vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--shadow-deep)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
          background: 'linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-card) 100%)',
        }}>
          <div>
            <div style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 20, fontWeight: 700,
              background: 'linear-gradient(135deg, #fff 0%, var(--brand-primary) 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            }}>
              💧 How AquaPulse Works
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
              A plain-language guide to groundwater evaluation for hackathon judges
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Nav */}
          <div style={{
            width: 200, flexShrink: 0,
            borderRight: '1px solid var(--border-subtle)',
            padding: '12px 8px',
            overflowY: 'auto',
          }}>
            {SECTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => setActiveSection(i)}
                style={{
                  width: '100%', textAlign: 'left',
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: 'none',
                  background: activeSection === i ? 'rgba(0,212,255,0.08)' : 'transparent',
                  borderLeft: activeSection === i ? '3px solid var(--brand-primary)' : '3px solid transparent',
                  color: activeSection === i ? 'var(--brand-primary)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: 13,
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: activeSection === i ? 600 : 400,
                  transition: 'all 0.15s',
                  marginBottom: 4,
                  lineHeight: 1.4,
                  display: 'flex', alignItems: 'flex-start', gap: 8,
                }}
              >
                <span style={{ fontSize: 16, flexShrink: 0 }}>{s.icon}</span>
                <span>{s.title}</span>
              </button>
            ))}
          </div>

          {/* Content */}
          <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
            <SectionContent section={SECTIONS[activeSection]} />
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
          fontSize: 11, color: 'var(--text-muted)',
        }}>
          <span>
            {activeSection + 1} / {SECTIONS.length} — click a section on the left or press Esc to close
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            {activeSection > 0 && (
              <button className="btn btn-ghost btn-sm"
                onClick={() => setActiveSection(s => s - 1)}>
                ← Prev
              </button>
            )}
            {activeSection < SECTIONS.length - 1 ? (
              <button className="btn btn-primary btn-sm"
                onClick={() => setActiveSection(s => s + 1)}>
                Next →
              </button>
            ) : (
              <button className="btn btn-primary btn-sm" onClick={onClose}>
                ✓ Got it
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SectionContent({ section }) {
  return (
    <div style={{ animation: 'fadeIn 0.2s ease' }}>
      <div style={{
        fontSize: 28, marginBottom: 8,
      }}>{section.icon}</div>
      <h2 style={{
        fontFamily: "'Space Grotesk', sans-serif",
        fontSize: 20, fontWeight: 700,
        color: 'var(--text-primary)', marginBottom: 16,
      }}>
        {section.title}
      </h2>

      {/* Plain text body */}
      {section.body && (
        <p style={{
          fontSize: 14, lineHeight: 1.8,
          color: 'var(--text-secondary)',
          whiteSpace: 'pre-line',
        }}>
          {section.body}
        </p>
      )}

      {/* Subsections (for Classification Rules) */}
      {section.subsections && section.subsections.map((sub, i) => (
        <div key={i} style={{ marginBottom: 24 }}>
          <div style={{
            fontSize: 13, fontWeight: 600,
            color: 'var(--text-primary)', marginBottom: 8,
          }}>
            {sub.label}
          </div>
          {sub.detail && (
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 12 }}>
              {sub.detail}
            </p>
          )}
          {sub.table && (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-soft)' }}>
                  <th style={{ padding: '6px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Condition</th>
                  <th style={{ padding: '6px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500 }}>Classification</th>
                </tr>
              </thead>
              <tbody>
                {sub.table.map(([cond, cls], j) => (
                  <tr key={j} style={{
                    background: j % 2 === 0 ? 'transparent' : 'rgba(0,212,255,0.02)',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}>
                    <td style={{ padding: '8px 12px', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>{cond}</td>
                    <td style={{ padding: '8px 12px', color: 'var(--text-primary)', fontWeight: 500 }}>{cls}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      ))}

      {/* Alert items */}
      {section.items && section.items.map((item, i) => (
        <div key={i} style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '14px 16px',
          marginBottom: 12,
          borderLeft: `3px solid ${item.color}`,
        }}>
          <div style={{
            fontWeight: 600, fontSize: 13,
            color: item.color, marginBottom: 6,
          }}>
            {item.badge}
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            {item.desc}
          </div>
        </div>
      ))}
    </div>
  );
}

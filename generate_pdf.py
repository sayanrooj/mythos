"""
generate_pdf.py — Generates AquaPulse Submission Dossier & Pitch Script PDF
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header
        self.drawString(54, letter[1] - 36, "AquaPulse by Team Mythos — Real-Time Groundwater Resource Evaluation")
        self.drawRightString(letter[0] - 54, letter[1] - 36, "CGWB / Ministry of Jal Shakti Hackathon")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        self.line(54, 46, letter[0] - 54, 46)
        self.drawString(54, 32, "Confidential — Team Mythos Hackathon Dossier & Demo Script")
        self.drawRightString(letter[0] - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(filename="AquaPulse_Submission_Dossier_and_Pitch.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0f2647")
    ACCENT = colors.HexColor("#0284c7")
    DARK = colors.HexColor("#0f172a")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_CARD = colors.HexColor("#f8fafc")
    BORDER = colors.HexColor("#e2e8f0")
    SAFE = colors.HexColor("#16a34a")
    CRITICAL = colors.HexColor("#dc2626")
    WARNING = colors.HexColor("#d97706")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=ACCENT,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=DARK,
        spaceAfter=8
    )

    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=DARK,
        spaceAfter=8
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=PRIMARY
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=12,
        textColor=DARK
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=DARK
    )

    table_cell_head = ParagraphStyle(
        'TableCellHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # COVER / EXECUTIVE TITLE BLOCK
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 15))
    story.append(Paragraph("AQUAPULSE · TEAM MYTHOS", ParagraphStyle('Tag', fontName='Helvetica-Bold', fontSize=10, textColor=ACCENT, spaceAfter=4)))
    story.append(Paragraph("Real-Time Groundwater Resource Evaluation Platform", title_style))
    story.append(Paragraph("Technical Dossier & 2-Minute Demo Presentation Script — by Team Mythos", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=14))

    meta_table_data = [
        [
            Paragraph("<b>Team Name:</b> <b>Team Mythos</b>", table_cell),
            Paragraph("<b>Status:</b> Demo-Ready Verified Prototype", table_cell)
        ],
        [
            Paragraph("<b>Target Body:</b> Ministry of Jal Shakti / CGWB", table_cell),
            Paragraph("<b>Test Suite:</b> 33/33 Unit & Boundary Tests Passed (100%)", table_cell)
        ],
        [
            Paragraph("<b>Technology:</b> React 18, Vite, Flask, SQLite, Holt Smoothing", table_cell),
            Paragraph("<b>Live Website:</b> <code>sayanrooj.github.io/mythos</code>", table_cell)
        ]
    ]
    t_meta = Table(meta_table_data, colWidths=[260, 244])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # 1. EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Executive Summary & Problem Statement", h1_style))
    story.append(Paragraph(
        "Groundwater accounts for <b>over 60% of India's irrigated agriculture and 85% of rural drinking water supplies</b>. "
        "Under the National Hydrology Project (NHP), the Central Ground Water Board (CGWB) operates an expanding telemetry network of "
        "<b>~15,000+ Digital Water Level Recorder (DWLR) piezometers</b> that record groundwater depths hourly and transmit data wirelessly to India-WRIS.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Operational Challenge:</b> Conventional dynamic groundwater resource assessments are conducted annually or periodically. "
        "Because assessments are retrospective, severe localized extraction surges—such as sudden agricultural pumping spikes or seasonal drying trends—"
        "often go unnoticed for months before administrative intervention occurs. Furthermore, field sensors regularly encounter data noise, "
        "transmission dropouts, and electromagnetic spikes that corrupt raw feeds without automated quality filtering.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution:</b> <b>AquaPulse</b> bridges the gap between raw hourly telemetry and automated governance. It provides a real-time "
        "stream processing pipeline that ingests DWLR readings, applies a 2-metric classification engine (deviation vs. baseline + 30-day linear decline rate), "
        "filters data anomalies, computes 30-day predictive forecasts via Holt Linear Smoothing, and automatically simulates multi-channel emergency "
        "dispatch (SMS & NIC Email) to District Nodal Hydrologists and District Magistrates.",
        body_style
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 2. KEY PLATFORM CAPABILITIES
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Key Platform Capabilities", h1_style))

    caps_data = [
        [
            Paragraph("<b>National & State Dashboard</b>", table_cell_bold),
            Paragraph("Slide-1 executive screen featuring stacked bar charts of stress tiers across 6 states, a 12-month national mean water table drying curve, and a top-10 at-risk station leaderboard with composite scoring.", table_cell)
        ],
        [
            Paragraph("<b>Geospatial Stress Map</b>", table_cell_bold),
            Paragraph("Interactive Leaflet map with dark CARTO tiles, featuring pulsing markers dual-encoded by stress classification (Green, Yellow, Orange, Red) and hydrogeological aquifer type (Alluvial, Hard-Rock, Coastal).", table_cell)
        ],
        [
            Paragraph("<b>2-Metric Evaluation Engine</b>", table_cell_bold),
            Paragraph("Evaluates both current depth deviation vs. 12-month baseline (Metric A) and 30-day linear decline velocity (Metric B), taking the maximum severity to classify into Safe, Semi-Critical, Critical, or Over-Exploited.", table_cell)
        ],
        [
            Paragraph("<b>Anomaly & Downgrade Alerts</b>", table_cell_bold),
            Paragraph("Automated detectors for Sensor Dropouts (>6h gaps), Spikes (>5m single-hour jumps), Sustained Declines (>0.05 m/day over 7 days), and Status Downgrades (Safe to Stressed).", table_cell)
        ],
        [
            Paragraph("<b>30-Day Predictive Forecasting</b>", table_cell_bold),
            Paragraph("Holt Linear Exponential Smoothing with 95% confidence intervals (±1.96σ) providing interpretable, low-compute projections to alert authorities before critical drawdown thresholds are breached.", table_cell)
        ],
        [
            Paragraph("<b>Multi-Channel Dispatch</b>", table_cell_bold),
            Paragraph("Automated emergency alert routing simulating C-DAC Govt SMS Gateway and NIC Email dispatch to District Nodal Hydrologists and District Disaster Management Authorities.", table_cell)
        ],
        [
            Paragraph("<b>Plug-and-Play Adapter Layer</b>", table_cell_bold),
            Paragraph("Strategy-pattern architecture allowing seamless zero-codebase swapping between local simulated SQLite data and live India-WRIS REST API telemetry via environment variables.", table_cell)
        ],
        [
            Paragraph("<b>CSV Export & In-App Guide</b>", table_cell_bold),
            Paragraph("One-click CSV download of 365 observed days + 30 forecast days per station, plus an interactive in-app guide explaining recharge/discharge hydrology for non-technical evaluation committees.", table_cell)
        ]
    ]
    t_caps = Table(caps_data, colWidths=[150, 354])
    t_caps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ffffff")),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_caps)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SCIENTIFIC & EVALUATION METHODOLOGY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("3. Scientific & Evaluation Methodology", h1_style))
    story.append(Paragraph(
        "AquaPulse follows hydrogeological evaluation principles established by the Central Ground Water Board (CGWB) "
        "and India-WRIS. Depth to water level is measured in <b>metres below ground level (m bgl)</b>, where higher values represent deeper, more depleted water tables.",
        body_style
    ))

    story.append(Paragraph("A. Two-Metric Classification Matrix", h2_style))
    story.append(Paragraph(
        "<b>Metric A (Baseline Deviation):</b> Difference between the latest reading and the station's 12-month rolling mean.<br/>"
        "<b>Metric B (Decline Rate):</b> 30-day linear regression slope (m/day) computed via Ordinary Least Squares (OLS).<br/>"
        "<b>Final Stress Level:</b> Maximum severity tier between Metric A and Metric B.",
        body_style
    ))

    matrix_data = [
        [
            Paragraph("Classification Tier", table_cell_head),
            Paragraph("Metric A: Deviation vs. 12m Avg", table_cell_head),
            Paragraph("Metric B: 30-Day Decline Rate", table_cell_head),
            Paragraph("Operational Status & Recommended Action", table_cell_head)
        ],
        [
            Paragraph("🟢 <b>Safe</b>", table_cell),
            Paragraph("≤ 2.0 metres", table_cell),
            Paragraph("≤ 0.010 m/day (≤ 30 cm/mo)", table_cell),
            Paragraph("Normal water table balance; routine seasonal monitoring.", table_cell)
        ],
        [
            Paragraph("🟡 <b>Semi-Critical</b>", table_cell),
            Paragraph("2.0 – 5.0 metres", table_cell),
            Paragraph("0.010 – 0.030 m/day", table_cell),
            Paragraph("Moderate stress; heightened telemetry check & crop advisory.", table_cell)
        ],
        [
            Paragraph("🟠 <b>Critical</b>", table_cell),
            Paragraph("5.0 – 10.0 metres", table_cell),
            Paragraph("0.030 – 0.060 m/day", table_cell),
            Paragraph("Severe drawdown; trigger block-level extraction audit.", table_cell)
        ],
        [
            Paragraph("🔴 <b>Over-Exploited</b>", table_cell),
            Paragraph("> 10.0 metres", table_cell),
            Paragraph("> 0.060 m/day (> 1.8 m/mo)", table_cell),
            Paragraph("Extreme depletion; immediate multi-channel alert dispatch to DDMA.", table_cell)
        ],
    ]
    t_mat = Table(matrix_data, colWidths=[90, 130, 130, 154])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_mat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("B. Holt's Linear Exponential Smoothing (30-Day Forecasting)", h2_style))
    story.append(Paragraph(
        "To provide forward-looking visibility without the black-box opacity or compute cost of heavy deep learning models, "
        "AquaPulse employs Holt's Linear Smoothing (Level smoothing α = 0.3, Trend smoothing β = 0.1) trained on 90 days of daily aggregates:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Level Update:</b> <i>L<sub>t</sub> = α Y<sub>t</sub> + (1 - α)(L<sub>t-1</sub> + T<sub>t-1</sub>)</i><br/>"
        "• <b>Trend Update:</b> <i>T<sub>t</sub> = β (L<sub>t</sub> - L<sub>t-1</sub>) + (1 - β)T<sub>t-1</sub></i><br/>"
        "• <b>Forecast (h steps ahead):</b> <i>Ŷ<sub>t+h</sub> = L<sub>t</sub> + h · T<sub>t</sub></i><br/>"
        "• <b>95% Confidence Bounds:</b> <i>Ŷ<sub>t+h</sub> ± 1.96 · σ · √h</i>",
        code_style
    ))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. SYSTEM ARCHITECTURE & DATA ADAPTER
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 4))
    story.append(Paragraph("4. System Architecture & Live Data Integration", h1_style))
    story.append(Paragraph(
        "AquaPulse is structured in 5 decoupled layers: Data Ingestion, Analytical Storage & Processing, REST API Gateway, "
        "React Frontend, and Multi-Channel Notification Gateway.",
        body_style
    ))

    adapter_data = [
        [
            Paragraph("Layer / Component", table_cell_head),
            Paragraph("Prototype Implementation", table_cell_head),
            Paragraph("Production India-WRIS Deployment", table_cell_head)
        ],
        [
            Paragraph("<b>Data Source Adapter</b>", table_cell),
            Paragraph("<code>SimulatedDataSource</code> (Local SQLite DB)", table_cell),
            Paragraph("<code>IndiaWRISAdapter</code> (Live CGWB REST API)", table_cell)
        ],
        [
            Paragraph("<b>Station Network</b>", table_cell),
            Paragraph("30 Stations across UP, RJ, PB, GJ, TN, MH", table_cell),
            Paragraph("15,000+ Nationwide DWLR Telemetric Piezometers", table_cell)
        ],
        [
            Paragraph("<b>Readings Ingestion</b>", table_cell),
            Paragraph("262,800 Hourly Readings (12-Month Seed)", table_cell),
            Paragraph("Live Hourly Telemetry Stream / Webhook Daemon", table_cell)
        ],
        [
            Paragraph("<b>Authentication</b>", table_cell),
            Paragraph("Local Development Mode", table_cell),
            Paragraph("OAuth2 Bearer Token via India-WRIS IAM", table_cell)
        ],
        [
            Paragraph("<b>Alert Dispatch</b>", table_cell),
            Paragraph("Console Log + In-App Modal & Toast", table_cell),
            Paragraph("C-DAC Govt SMS Gateway + NIC SMTP Relay", table_cell)
        ],
    ]
    t_adapt = Table(adapter_data, colWidths=[120, 180, 204])
    t_adapt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_adapt)

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # 5. COMPLETE 2-MINUTE DEMO PRESENTATION SCRIPT
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("5. Official 2-Minute Hackathon Demo Script", h1_style))
    story.append(Paragraph(
        "<i>Designed for a timed 120-second evaluation pitch before the hackathon judging panel.</i>",
        callout_style
    ))
    story.append(Spacer(1, 6))

    script_data = [
        [
            Paragraph("Time", table_cell_head),
            Paragraph("Section & Focus", table_cell_head),
            Paragraph("Click-Through Action on Screen", table_cell_head),
            Paragraph("Exact Spoken Words & Pitch", table_cell_head)
        ],
        [
            Paragraph("<b>0:00<br/>to<br/>0:25</b>", table_cell_bold),
            Paragraph("<b>Hook & Slide-1 Overview</b>", table_cell_bold),
            Paragraph("Start on <b>📊 National Overview</b> dashboard.<br/>Hover over state stress bars and national 12-month drying curve.", table_cell),
            Paragraph("<i>'Respected judges, India operates over 15,000 DWLR piezometers, but conventional assessments are annual—missing sudden localized over-extraction. <b>AquaPulse</b> turns live telemetry streams into instant intelligence. Our executive dashboard tracks groundwater stress across states, national drying velocity, and flags our top 10 at-risk stations.'</i>", table_cell)
        ],
        [
            Paragraph("<b>0:25<br/>to<br/>0:55</b>", table_cell_bold),
            Paragraph("<b>Station Drilldown & Forecasting</b>", table_cell_bold),
            Paragraph("Click <b>#1 Latur Over-Extract</b>.<br/>App transitions to <b>🗺 Map View</b> & opens drawer. Toggle 90d range, point out forecast band, click <b>⬇ CSV</b>.", table_cell),
            Paragraph("<i>'Drilling into Latur reveals our 2-metric engine evaluating historical baseline deviation against 30-day decline rates. Using <b>Holt Linear Exponential Smoothing</b>, AquaPulse projects water levels 30 days ahead with 95% confidence bands—alerting authorities weeks before critical drawdown thresholds are breached.'</i>", table_cell)
        ],
        [
            Paragraph("<b>0:55<br/>to<br/>1:25</b>", table_cell_bold),
            Paragraph("<b>Anomaly Engine & Dispatch</b>", table_cell_bold),
            Paragraph("Click <b>🔔 Alerts</b> tab in sidebar.<br/>Filter by <i>Status Downgrade</i>.<br/>Click <b>📲 Alert SMS/Mail</b>.<br/>Show Modal & live toast.", table_cell),
            Paragraph("<i>'Raw telemetry is noisy. Our engine continuously detects sensor dropouts (>6h gaps), electromagnetic spikes (>5m jumps), and status downgrades. With one click, our automated dispatch gateway routes targeted SMS alerts to District Hydrologists and official NIC emails to District Magistrates.'</i>", table_cell)
        ],
        [
            Paragraph("<b>1:25<br/>to<br/>1:45</b>", table_cell_bold),
            Paragraph("<b>Live Telemetry Simulation</b>", table_cell_bold),
            Paragraph("Click <b>⚡ Simulate Tick</b> in header.<br/>Watch button spinner, live toast, and reading counters increment.", table_cell),
            Paragraph("<i>'To demonstrate real-world ingestion, clicking <b>Simulate Tick</b> ingests a new hourly reading packet across all 30 stations, advances the virtual telemetry timeline, and re-evaluates anomaly filters in sub-second time.'</i>", table_cell)
        ],
        [
            Paragraph("<b>1:45<br/>to<br/>2:00</b>", table_cell_bold),
            Paragraph("<b>Production Ready & Closing</b>", table_cell_bold),
            Paragraph("Click <b>💡 How It Works</b> in header.<br/>Show judge guide modal and return to dashboard.", table_cell),
            Paragraph("<i>'Finally, AquaPulse is architected for immediate rollout. Through our plug-and-play <b>DataSourceAdapter</b>, connecting to live India-WRIS REST APIs requires zero changes to the analytical code. AquaPulse bridges the gap between raw sensors and proactive groundwater governance. Thank you!'</i>", table_cell)
        ],
    ]
    t_script = Table(script_data, colWidths=[42, 100, 140, 222])
    t_script.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_script)

    # ══════════════════════════════════════════════════════════════════════════
    # 6. JUDGE Q&A CHEAT SHEET & FUTURE ROADMAP
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Judge Q&A Cheat Sheet & Future Roadmap", h1_style))

    qa_data = [
        [
            Paragraph("Anticipated Judge Question", table_cell_head),
            Paragraph("Recommended Winning Response", table_cell_head)
        ],
        [
            Paragraph("<b>Why Holt's Smoothing over Deep Learning (LSTM)?</b>", table_cell_bold),
            Paragraph("<i>'Holt's Linear Smoothing provides 100% mathematical interpretability, sub-millisecond execution on edge servers, and captures level + trend dynamics robustly without requiring heavy GPU training on thousands of new sensors.'</i>", table_cell)
        ],
        [
            Paragraph("<b>How does the system handle missing sensor packets?</b>", table_cell_bold),
            Paragraph("<i>'Missing readings under 6 hours are handled via spline interpolation for moving averages. If data is missing for >6 consecutive hours, our Gap Detector triggers a WARNING alert for field maintenance.'</i>", table_cell)
        ],
        [
            Paragraph("<b>How do you scale to 15,000+ national DWLR stations?</b>", table_cell_bold),
            Paragraph("<i>'Our backend is decoupled via the Strategy Pattern. In production, we deploy an Apache Kafka/MQTT ingestion pipeline with TimescaleDB, easily handling 15,000+ telemetry packets per second.'</i>", table_cell)
        ],
    ]
    t_qa = Table(qa_data, colWidths=[180, 324])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Future Roadmap Horizons:", h2_style))
    story.append(Paragraph(
        "• <b>Phase 1: Multi-Source Data Fusion:</b> Ingest NASA GRACE satellite gravity data and IMD Doppler rainfall grids.<br/>"
        "• <b>Phase 2: 3D Hydrogeological Strata:</b> Connect borehole lithology logs to map unconfined/confined aquifer depths.<br/>"
        "• <b>Phase 3: Hyperlocal Gram Panchayat Alerts:</b> Automated WhatsApp Business API and IVR voice broadcasts in local languages.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    build_pdf()

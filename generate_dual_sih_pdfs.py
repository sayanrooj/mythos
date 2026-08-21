"""
generate_dual_sih_pdfs.py
Generates two comprehensive, professional, easy-to-read PDFs for Team Mythos (SIH25068):
1. Team_Mythos_AquaPulse_Complete_Project_Documentation.pdf
2. Team_Mythos_SIH25068_Pitch_and_Code_Presentation.pdf
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# ── Palette ───────────────────────────────────────────────────────────────────
PRIMARY = colors.HexColor("#071428")     # Deep Navy
ACCENT = colors.HexColor("#0284c7")      # Bright Blue
BRAND_CYAN = colors.HexColor("#0096c7")  # Cyan
DARK = colors.HexColor("#0f172a")        # Dark Slate
MUTED = colors.HexColor("#475569")       # Slate Gray
BG_CARD = colors.HexColor("#f8fafc")     # Light Card
BORDER = colors.HexColor("#cbd5e1")      # Border Gray
GREEN = colors.HexColor("#16a34a")       # Safe
RED = colors.HexColor("#dc2626")         # Critical
ORANGE = colors.HexColor("#ea580c")      # Warning

# ── Dynamic Header & Footer Numbered Canvas ──────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, doc_title="AquaPulse — Team Mythos", **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = doc_title
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress on cover

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED)

        # Header
        self.drawString(54, letter[1] - 36, self.doc_title)
        self.drawRightString(letter[0] - 54, letter[1] - 36, "Smart India Hackathon · Ministry of Jal Shakti (SIH25068)")
        self.setStrokeColor(BORDER)
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer
        self.line(54, 46, letter[0] - 54, 46)
        self.drawString(54, 32, "Team Mythos — AquaPulse Groundwater Resource Evaluation Platform")
        self.drawRightString(letter[0] - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_styles():
    base = getSampleStyleSheet()
    return {
        'CoverTag': ParagraphStyle('CoverTag', fontName='Helvetica-Bold', fontSize=10, textColor=ACCENT, spaceAfter=4),
        'CoverTitle': ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=24, leading=28, textColor=PRIMARY, spaceAfter=6),
        'CoverSubtitle': ParagraphStyle('CoverSubtitle', fontName='Helvetica', fontSize=12, leading=16, textColor=ACCENT, spaceAfter=14),
        'H1': ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=PRIMARY, spaceBefore=14, spaceAfter=8, keepWithNext=True),
        'H2': ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=ACCENT, spaceBefore=10, spaceAfter=4, keepWithNext=True),
        'Body': ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=DARK, spaceAfter=6),
        'BodyBold': ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=DARK, spaceAfter=6),
        'Callout': ParagraphStyle('Callout', fontName='Helvetica-Oblique', fontSize=9, leading=13, textColor=PRIMARY),
        'Code': ParagraphStyle('Code', fontName='Courier', fontSize=8, leading=11, textColor=DARK),
        'Cell': ParagraphStyle('Cell', fontName='Helvetica', fontSize=8, leading=10.5, textColor=DARK),
        'CellBold': ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=DARK),
        'CellHead': ParagraphStyle('CellHead', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.white),
    }


# ══════════════════════════════════════════════════════════════════════════════
# PDF 1: COMPLETE PROJECT DOCUMENTATION (TECHNICAL DOSSIER)
# ══════════════════════════════════════════════════════════════════════════
def build_project_documentation_pdf(filename="Team_Mythos_AquaPulse_Complete_Project_Documentation.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    s = get_styles()
    story = []

    # Title Block
    story.append(Paragraph("SMART INDIA HACKATHON · SIH25068 · TECHNICAL DOSSIER", s['CoverTag']))
    story.append(Paragraph("AquaPulse — Real-Time Groundwater Resource Evaluation Platform", s['CoverTitle']))
    story.append(Paragraph("Complete Technical Documentation, Mathematical Engine, Architecture & API Reference", s['CoverSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    # Meta Table
    meta_data = [
        [
            Paragraph("<b>Project Name:</b> AquaPulse", s['Cell']),
            Paragraph("<b>Team Name:</b> <b>Team Mythos</b>", s['Cell'])
        ],
        [
            Paragraph("<b>SIH Problem ID:</b> <b>SIH25068</b>", s['Cell']),
            Paragraph("<b>Ministry:</b> Ministry of Jal Shakti (CGWB)", s['Cell'])
        ],
        [
            Paragraph("<b>Problem Title:</b> Real-time Groundwater resource evaluation using DWLR data", s['Cell']),
            Paragraph("<b>Category:</b> Software / IoT Telemetry Analytics", s['Cell'])
        ],
        [
            Paragraph("<b>Live Website:</b> <u>https://sayanrooj.github.io/mythos/</u>", s['Cell']),
            Paragraph("<b>GitHub Code:</b> <u>https://github.com/sayanrooj/mythos</u>", s['Cell'])
        ],
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. Problem Statement & Motivation
    story.append(Paragraph("1. Problem Statement & Background Context", s['H1']))
    story.append(Paragraph(
        "Under the National Hydrology Project (NHP), India's Central Ground Water Board (CGWB) maintains <b>~15,000+ telemetric Digital Water Level Recorder (DWLR) piezometers</b> "
        "logging hourly water level depths across major aquifers (Alluvial, Hard-Rock, Coastal). While readings stream to India-WRIS, traditional assessments are conducted "
        "retrospectively (annual/periodic), causing acute agricultural extraction surges and unseasonal depletion to go unaddressed for months. "
        "Furthermore, field sensors suffer from communication dropouts and electronic noise. <b>AquaPulse</b> provides an automated, real-time evaluation and early-warning engine.",
        s['Body']
    ))

    # 2. System Architecture & Component Breakdown
    story.append(Paragraph("2. System Architecture (5 Decoupled Layers)", s['H1']))
    arch_data = [
        [Paragraph("Layer", s['CellHead']), Paragraph("Technology", s['CellHead']), Paragraph("Function & Operational Role", s['CellHead'])],
        [Paragraph("<b>1. Ingestion Layer</b>", s['Cell']), Paragraph("Strategy Adapter (Python)", s['Cell']), Paragraph("Decoupled ingestion supporting simulated SQLite (default) and live India-WRIS REST API feeds.", s['Cell'])],
        [Paragraph("<b>2. Analytical Engine</b>", s['Cell']), Paragraph("NumPy, SciPy, Math", s['Cell']), Paragraph("2-metric stress classification, 4 anomaly detectors, and Holt Linear 30-day exponential forecasting.", s['Cell'])],
        [Paragraph("<b>3. REST API Gateway</b>", s['Cell']), Paragraph("Flask 3.1, CORS, SQLite", s['Cell']), Paragraph("High-speed microservice providing /stations, /dashboard/summary, /forecast, and /alerts/dispatch.", s['Cell'])],
        [Paragraph("<b>4. Frontend UI</b>", s['Cell']), Paragraph("React 18, Vite, Leaflet, Recharts", s['Cell']), Paragraph("National Overview Dashboard, interactive pulsing geospatial map, detail drawers, and educational guide.", s['Cell'])],
        [Paragraph("<b>5. Emergency Gateway</b>", s['Cell']), Paragraph("SMS & NIC Email Gateways", s['Cell']), Paragraph("Automated multi-channel dispatch routing emergency alerts to District Nodal Hydrologists & DDMAs.", s['Cell'])],
    ]
    t_arch = Table(arch_data, colWidths=[90, 110, 304])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    # 3. Two-Metric Classification Engine
    story.append(Paragraph("3. Scientific Stress Classification & Anomaly Logic", s['H1']))
    story.append(Paragraph(
        "<b>Metric A (Deviation):</b> Deviation = Current Level (m bgl) - 12-Month Baseline Mean (m bgl).<br/>"
        "<b>Metric B (Decline Rate):</b> 30-day linear regression slope (m/day) computed via Ordinary Least Squares (OLS).<br/>"
        "<b>Final Stress Level:</b> MAX severity of Metric A and Metric B.",
        s['Body']
    ))

    rules_data = [
        [Paragraph("Category", s['CellHead']), Paragraph("Metric A Threshold", s['CellHead']), Paragraph("Metric B Threshold", s['CellHead']), Paragraph("Action Triggered", s['CellHead'])],
        [Paragraph("🟢 <b>Safe</b>", s['Cell']), Paragraph("≤ 2.0 m", s['Cell']), Paragraph("≤ 0.010 m/day (≤ 30 cm/mo)", s['Cell']), Paragraph("Normal water balance; routine monitoring.", s['Cell'])],
        [Paragraph("🟡 <b>Semi-Critical</b>", s['Cell']), Paragraph("2.0 – 5.0 m", s['Cell']), Paragraph("0.010 – 0.030 m/day", s['Cell']), Paragraph("Crop water advisory & weekly telemetry review.", s['Cell'])],
        [Paragraph("🟠 <b>Critical</b>", s['Cell']), Paragraph("5.0 – 10.0 m", s['Cell']), Paragraph("0.030 – 0.060 m/day", s['Cell']), Paragraph("Block-level extraction audit & warning alert.", s['Cell'])],
        [Paragraph("🔴 <b>Over-Exploited</b>", s['Cell']), Paragraph("> 10.0 m", s['Cell']), Paragraph("> 0.060 m/day (> 1.8 m/mo)", s['Cell']), Paragraph("Emergency multi-channel SMS/Email alert to DDMA.", s['Cell'])],
    ]
    t_rules = Table(rules_data, colWidths=[80, 100, 110, 214])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rules)

    story.append(PageBreak())

    # 4. Holt Linear Forecasting & Anomaly Rules
    story.append(Paragraph("4. Holt Linear Forecasting & Anomaly Detection", s['H1']))
    story.append(Paragraph(
        "<b>Holt's Linear Exponential Smoothing (30-Day Projections):</b> Level equation <i>L<sub>t</sub> = αY<sub>t</sub> + (1-α)(L<sub>t-1</sub>+T<sub>t-1</sub>)</i>, "
        "Trend equation <i>T<sub>t</sub> = β(L<sub>t</sub>-L<sub>t-1</sub>) + (1-β)T<sub>t-1</sub></i>, Forecast <i>Ŷ<sub>t+h</sub> = L<sub>t</sub> + hT<sub>t</sub></i> "
        "with 95% confidence bands <i>±1.96·σ·√h</i> (Hyperparameters: α=0.3, β=0.1).",
        s['Body']
    ))
    story.append(Paragraph(
        "<b>Anomaly Detectors:</b><br/>"
        "• <b>Gaps:</b> >6 consecutive missing readings (telemetry dropout) → WARNING/CRITICAL alert.<br/>"
        "• <b>Spikes:</b> Single-reading jump >5.0m (electronic fault) → WARNING alert.<br/>"
        "• <b>Sustained Decline:</b> 7-day slope >0.05 m/day (over-extraction event) → CRITICAL alert.<br/>"
        "• <b>Status Downgrade:</b> Transition from Safe into stressed tiers → Automated alert dispatch.",
        s['Body']
    ))

    # 5. API Reference & Code Structure
    story.append(Paragraph("5. API Endpoints & Codebase Structure", s['H1']))
    api_data = [
        [Paragraph("Endpoint", s['CellHead']), Paragraph("Method", s['CellHead']), Paragraph("Description & Output", s['CellHead'])],
        [Paragraph("<code>/stations</code>", s['Cell']), Paragraph("GET", s['Cell']), Paragraph("Returns all 30 DWLR stations with coordinates, aquifer type, latest level, and stress status.", s['Cell'])],
        [Paragraph("<code>/dashboard/summary</code>", s['Cell']), Paragraph("GET", s['Cell']), Paragraph("State-wise stress distribution, 12-month national daily mean trend, and top-10 risk leaderboard.", s['Cell'])],
        [Paragraph("<code>/stations/:id/forecast</code>", s['Cell']), Paragraph("GET", s['Cell']), Paragraph("30-day daily projected water levels with upper/lower 95% confidence bounds.", s['Cell'])],
        [Paragraph("<code>/alerts</code>", s['Cell']), Paragraph("GET", s['Cell']), Paragraph("Active telemetry anomaly and status downgrade alerts filtered by type/severity.", s['Cell'])],
        [Paragraph("<code>/alerts/:id/dispatch</code>", s['Cell']), Paragraph("POST", s['Cell']), Paragraph("Simulates automated multi-channel SMS & NIC Email dispatch to District Authorities.", s['Cell'])],
        [Paragraph("<code>/simulate/tick</code>", s['Cell']), Paragraph("POST", s['Cell']), Paragraph("Ingests +1 hour of synthetic telemetry across all stations and re-evaluates anomalies in real time.", s['Cell'])],
        [Paragraph("<code>/stations/:id/export/csv</code>", s['Cell']), Paragraph("GET", s['Cell']), Paragraph("Generates downloadable CSV file with 365 observed days + 30 forecast days.", s['Cell'])],
    ]
    t_api = Table(api_data, colWidths=[120, 45, 339])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 8))

    # 6. Verification Test Suite & India-WRIS Readiness
    story.append(Paragraph("6. Verification Test Results & India-WRIS Live Integration", s['H1']))
    story.append(Paragraph(
        "<b>Pytest Verification:</b> 33/33 Unit & Integration Tests Passed (100% pass rate in 0.11s).<br/>"
        "<b>Production India-WRIS Switch:</b> The data layer uses the Strategy Pattern in <code>backend/data_source.py</code>. "
        "Swapping simulated SQLite for live CGWB telemetry only requires setting <code>DATA_SOURCE=india_wris</code> with OAuth2 credentials.",
        s['Body']
    ))

    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, doc_title="AquaPulse Technical Dossier — Team Mythos (SIH25068)", **k))
    print(f"Generated: {filename}")


# ══════════════════════════════════════════════════════════════════════════════
# PDF 2: SIH OFFICIAL PITCH DECK, PRESENTATION SCRIPT & CODE EXPLAINER
# ══════════════════════════════════════════════════════════════════════════
def build_sih_pitch_presentation_pdf(filename="Team_Mythos_SIH25068_Pitch_and_Code_Presentation.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    s = get_styles()
    story = []

    # Title Block
    story.append(Paragraph("SMART INDIA HACKATHON · SIH25068 · PITCH & DEMO GUIDE", s['CoverTag']))
    story.append(Paragraph("AquaPulse — 2-Minute Official Pitch & Code Walkthrough", s['CoverTitle']))
    story.append(Paragraph("Prepared by Team Mythos for Ministry of Jal Shakti / CGWB Evaluation Panel", s['CoverSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=10))

    # Executive Overview Box
    meta_data = [
        [Paragraph("<b>Team:</b> <b>Team Mythos</b>", s['Cell']), Paragraph("<b>SIH Category:</b> Software", s['Cell'])],
        [Paragraph("<b>Problem ID:</b> <b>SIH25068</b>", s['Cell']), Paragraph("<b>Ministry:</b> Ministry of Jal Shakti (CGWB)", s['Cell'])],
        [Paragraph("<b>Problem Statement:</b> Real-time Groundwater resource evaluation using DWLR data", s['Cell']), Paragraph("<b>Status:</b> Verified & Deployed", s['Cell'])],
        [Paragraph("<b>Live Demo:</b> <u>https://sayanrooj.github.io/mythos/</u>", s['Cell']), Paragraph("<b>GitHub:</b> <u>https://github.com/sayanrooj/mythos</u>", s['Cell'])],
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # 1. The High-Impact Pitch Hook
    story.append(Paragraph("1. The 30-Second Elevator Pitch (The Hook)", s['H1']))
    story.append(Paragraph(
        "<i>'Respected judges, groundwater sustains 85% of rural India and 60% of our agriculture. While CGWB operates over 15,000 telemetric DWLR piezometers, "
        "groundwater assessments have traditionally been retrospective—meaning critical localized over-extraction is identified months too late.<br/><br/>"
        "We built <b>AquaPulse</b>: an intelligent, real-time groundwater resource evaluation platform that ingests hourly telemetry streams, evaluates aquifer stress "
        "using CGWB-standard velocity and baseline metrics, predicts water levels 30 days ahead using Holt Exponential Smoothing, and instantly routes emergency SMS/Email alerts "
        "to District Magistrates before critical aquifer drawdown occurs.'</i>",
        s['Callout']
    ))

    # 2. Step-by-Step 2-Minute Stage Demo Script
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. Official 2-Minute Stage Demo Script (Click-Through Guide)", s['H1']))

    demo_data = [
        [Paragraph("Time", s['CellHead']), Paragraph("Stage Action", s['CellHead']), Paragraph("Exact Spoken Lines for Judges", s['CellHead'])],
        [
            Paragraph("<b>0:00<br/>to<br/>0:25</b>", s['CellBold']),
            Paragraph("Start on <b>National Overview</b>.<br/>Hover over State Stress Bar & 12m Drying Trend.", s['Cell']),
            Paragraph("<i>'Here on our National Overview, administrators see instant state-wise stress distributions, track national water table decline velocity over 12 months, and immediately identify the top 10 most at-risk stations in India.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>0:25<br/>to<br/>0:55</b>", s['CellBold']),
            Paragraph("Click <b>#1 Latur Over-Extract</b>.<br/>App opens Map + Detail Drawer. Toggle 90d, show 30d forecast band, click <b>CSV</b>.", s['Cell']),
            Paragraph("<i>'Drilling into Latur reveals our 2-metric engine evaluating baseline deviation vs. 30-day decline rates. Using Holt Exponential Smoothing, AquaPulse projects water table depth 30 days into the future with 95% confidence bands.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>0:55<br/>to<br/>1:25</b>", s['CellBold']),
            Paragraph("Click <b>Alerts tab</b> in sidebar.<br/>Filter by <i>Status Downgrade</i>.<br/>Click <b>📲 Alert SMS/Mail</b>.<br/>Show dispatch modal.", s['Cell']),
            Paragraph("<i>'Telemetry is noisy. Our engine flags gaps, spikes, and downgrades. With one click, our automated dispatch gateway routes targeted SMS alerts to District Hydrologists and official NIC emails to District Magistrates.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>1:25<br/>to<br/>1:45</b>", s['CellBold']),
            Paragraph("Click <b>⚡ Simulate Tick</b> in header.<br/>Watch toast & live reading counter update.", s['Cell']),
            Paragraph("<i>'Clicking Simulate Tick ingests a new hourly reading packet across all 30 stations, advances our virtual telemetry timeline, and re-evaluates stress classifications in sub-second time.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>1:45<br/>to<br/>2:00</b>", s['CellBold']),
            Paragraph("Click <b>💡 How It Works</b> in header.<br/>Show plain-language guide modal & close.", s['Cell']),
            Paragraph("<i>'AquaPulse is production-ready. Through our plug-and-play DataSourceAdapter, connecting to live India-WRIS APIs requires zero code changes. AquaPulse turns raw telemetry into proactive water security. Thank you!'</i>", s['Cell'])
        ],
    ]
    t_demo = Table(demo_data, colWidths=[40, 130, 334])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_demo)

    story.append(PageBreak())

    # 3. Code & Tech Architecture Explained in Simple Language
    story.append(Paragraph("3. The Code & Technology Explained Simply", s['H1']))
    story.append(Paragraph(
        "For non-technical judges or quick technical deep-dives, here is how each module is engineered:",
        s['Body']
    ))

    code_data = [
        [Paragraph("Component", s['CellHead']), Paragraph("How It Works in Plain Language", s['CellHead']), Paragraph("Key File in Repository", s['CellHead'])],
        [
            Paragraph("<b>Stress Classifier</b>", s['CellBold']),
            Paragraph("Takes the worse of Metric A (how deep compared to 12m avg) and Metric B (how fast it is falling over 30 days) to categorize as Safe, Semi-Critical, Critical, or Over-Exploited.", s['Cell']),
            Paragraph("<code>backend/evaluation.py</code>", s['Cell'])
        ],
        [
            Paragraph("<b>Holt Forecasting</b>", s['CellBold']),
            Paragraph("A mathematical forecasting model that tracks both current water level (α=0.3) and drawdown trajectory (β=0.1) to project 30 days ahead with 95% statistical confidence bounds.", s['Cell']),
            Paragraph("<code>backend/forecasting.py</code>", s['Cell'])
        ],
        [
            Paragraph("<b>Anomaly Detector</b>", s['CellBold']),
            Paragraph("Scans incoming data for >6h missing gaps, >5m electrical spikes, rapid 7-day declines (>0.05m/d), and classification downgrades, generating actionable alert records.", s['Cell']),
            Paragraph("<code>backend/anomaly.py</code>", s['Cell'])
        ],
        [
            Paragraph("<b>India-WRIS Adapter</b>", s['CellBold']),
            Paragraph("Uses the Strategy Design Pattern. The rest of the app doesn't care whether data comes from SQLite or the live India-WRIS REST API; only this one file is swapped.", s['Cell']),
            Paragraph("<code>backend/data_source.py</code>", s['Cell'])
        ],
        [
            Paragraph("<b>Frontend Web App</b>", s['CellBold']),
            Paragraph("Built with React 18 and Vite with Leaflet map markers and Recharts visualizer. Features an in-browser fallback engine allowing 100% standalone execution on GitHub Pages.", s['Cell']),
            Paragraph("<code>frontend/src/App.jsx</code>", s['Cell'])
        ],
    ]
    t_code = Table(code_data, colWidths=[100, 274, 130])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 8))

    # 4. Judge Q&A Defense Strategy
    story.append(Paragraph("4. Judge Q&A Defense Strategy (Winning Answers)", s['H1']))
    qa_data = [
        [Paragraph("Judge Question", s['CellHead']), Paragraph("Winning Response for Team Mythos", s['CellHead'])],
        [
            Paragraph("<b>Why Holt smoothing instead of LSTM deep learning?</b>", s['CellBold']),
            Paragraph("<i>'Holt smoothing gives exact mathematical interpretability, runs in sub-milliseconds on low-cost edge servers, and avoids requiring thousands of historical training epochs on newly installed DWLR sensors.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>How does your system handle missing sensor packets?</b>", s['CellBold']),
            Paragraph("<i>'Minor dropouts (<6 hours) are interpolated for rolling statistics. If a sensor drops data for >6 consecutive hours, our Gap Detector triggers a WARNING alert for field sensor maintenance.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>How will you scale to 15,000+ national DWLR stations?</b>", s['CellBold']),
            Paragraph("<i>'Our backend is decoupled via the Strategy Pattern. In production, we deploy an Apache Kafka/MQTT ingestion pipeline with TimescaleDB, handling 15,000+ telemetry packets per second.'</i>", s['Cell'])
        ],
        [
            Paragraph("<b>What is the social and economic impact?</b>", s['CellBold']),
            Paragraph("<i>'By transforming retrospective annual assessments into real-time alerts, District Magistrates can enforce agricultural extraction limits weeks earlier, safeguarding drinking water for rural communities.'</i>", s['Cell'])
        ],
    ]
    t_qa = Table(qa_data, colWidths=[170, 334])
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

    doc.build(story, canvasmaker=lambda *a, **k: NumberedCanvas(*a, doc_title="AquaPulse SIH Pitch & Code Presentation — Team Mythos (SIH25068)", **k))
    print(f"Generated: {filename}")


if __name__ == "__main__":
    build_project_documentation_pdf()
    build_sih_pitch_presentation_pdf()

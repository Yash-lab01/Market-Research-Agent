import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

REPORTS_DIR = os.getenv("REPORTS_DIR", "data/reports")

# ── Colour palette ────────────────────────────────────────────────────────────
INDIGO   = colors.HexColor("#6366f1")
DARK     = colors.HexColor("#1a1a2e")
LIGHT_BG = colors.HexColor("#f0f0ff")
GREY     = colors.HexColor("#6b7280")
WHITE    = colors.white

# ── Helpers ───────────────────────────────────────────────────────────────────

def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title2", parent=base["Title"],
                                fontSize=22, textColor=WHITE,
                                alignment=TA_CENTER, spaceAfter=6),
        "subtitle": ParagraphStyle("Sub", parent=base["Normal"],
                                   fontSize=11, textColor=colors.HexColor("#c7d2fe"),
                                   alignment=TA_CENTER, spaceAfter=4),
        "h1": ParagraphStyle("H1", parent=base["Heading1"],
                              fontSize=14, textColor=INDIGO,
                              spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("Body", parent=base["Normal"],
                               fontSize=10, textColor=DARK,
                               leading=14, spaceAfter=4),
        "bullet": ParagraphStyle("Bullet", parent=base["Normal"],
                                 fontSize=10, textColor=DARK,
                                 leading=13, leftIndent=14, spaceAfter=3),
        "small": ParagraphStyle("Small", parent=base["Normal"],
                                fontSize=8, textColor=GREY, spaceAfter=2),
    }


def _cover(query: str, s: dict) -> list:
    """Returns flowables for a coloured cover block."""
    return [
        Spacer(1, 0.4 * inch),
        Table(
            [[Paragraph("📊 Market Research Report", s["title"])],
             [Paragraph(query, s["subtitle"])],
             [Paragraph(datetime.now().strftime("%B %d, %Y"), s["subtitle"])]],
            colWidths=[6.5 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), DARK),
                ("ROUNDEDCORNERS", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 18),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
                ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ]),
        ),
        Spacer(1, 0.3 * inch),
    ]


def _section(title: str, s: dict) -> list:
    return [
        HRFlowable(width="100%", thickness=1, color=INDIGO, spaceAfter=4),
        Paragraph(title, s["h1"]),
    ]


def _bullet_list(items: list, s: dict) -> list:
    return [Paragraph(f"• {item}", s["bullet"]) for item in items if item]


def _swot_table(swot: dict, s: dict) -> Table:
    def cell(title, items):
        content = f"<b>{title}</b><br/>" + "<br/>".join(f"• {i}" for i in items[:4])
        return Paragraph(content, s["body"])

    data = [
        [cell("💪 Strengths", swot.get("strengths", [])),
         cell("⚠️ Weaknesses", swot.get("weaknesses", []))],
        [cell("🚀 Opportunities", swot.get("opportunities", [])),
         cell("🔴 Threats", swot.get("threats", []))],
    ]
    return Table(
        data, colWidths=[3.1 * inch, 3.1 * inch],
        style=TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.5, INDIGO),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e7ff")),
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#eef2ff")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fff7ed")),
            ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#f0fdf4")),
            ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#fef2f2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]),
    )


def _company_table(companies: list, s: dict) -> Table:
    headers = [
        Paragraph("<b>Company</b>", s["body"]),
        Paragraph("<b>Position</b>", s["body"]),
        Paragraph("<b>Notable</b>", s["body"]),
    ]
    rows = [headers]
    for c in companies[:8]:
        rows.append([
            Paragraph(c.get("name", ""), s["body"]),
            Paragraph(c.get("market_position", ""), s["body"]),
            Paragraph(c.get("notable", c.get("description", ""))[:120], s["body"]),
        ])
    return Table(
        rows, colWidths=[1.6 * inch, 1.4 * inch, 3.2 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.HexColor("#f8f9ff"), WHITE]),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d2fe")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0e7ff")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]),
    )


# ── Main builder ──────────────────────────────────────────────────────────────

def build_pdf(session_id: str, query: str, output: dict) -> str:
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
    filename = str(Path(REPORTS_DIR) / f"report_{session_id[:8]}.pdf")

    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    s = _styles()
    story = []

    # Cover
    story += _cover(query, s)
    story.append(PageBreak())

    # Market data summary row
    md = output.get("market_data", {})
    if any(md.values()):
        mdata = [[
            Paragraph(f"<b>Size</b><br/>{md.get('market_size','N/A')}", s["body"]),
            Paragraph(f"<b>CAGR</b><br/>{md.get('growth_rate','N/A')}", s["body"]),
            Paragraph(f"<b>Forecast</b><br/>{md.get('forecast_year','N/A')}", s["body"]),
            Paragraph(f"<b>Region</b><br/>{md.get('key_geography','N/A')}", s["body"]),
        ]]
        story.append(Table(mdata, colWidths=[1.6*inch]*4,
            style=TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
                ("BOX", (0,0), (-1,-1), 0.5, INDIGO),
                ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#c7d2fe")),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("TOPPADDING", (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ])
        ))
        story.append(Spacer(1, 0.2*inch))

    # Executive Summary
    story += _section("Executive Summary", s)
    story.append(Paragraph(output.get("executive_summary", ""), s["body"]))
    story.append(Spacer(1, 0.15*inch))

    # Key Findings
    story += _section("Key Findings", s)
    story += _bullet_list(output.get("key_findings", []), s)
    story.append(Spacer(1, 0.15*inch))

    # Companies
    companies = output.get("companies", [])
    if companies:
        story += _section("Company Landscape", s)
        story.append(_company_table(companies, s))
        story.append(Spacer(1, 0.15*inch))

    # Trends
    trends = output.get("trends", [])
    if trends:
        story += _section("Market Trends", s)
        for t in trends:
            direction = t.get("direction", "")
            icon = "📈" if direction == "Growing" else ("📉" if direction == "Declining" else "🌱")
            story.append(Paragraph(
                f"{icon} <b>{t.get('name','')} ({direction})</b> — {t.get('description','')}", s["body"]))
        story.append(Spacer(1, 0.15*inch))

    # SWOT
    swot = output.get("swot", {})
    if any(swot.values()):
        story += _section("SWOT Analysis", s)
        story.append(_swot_table(swot, s))
        story.append(Spacer(1, 0.15*inch))

    # Citations
    citations = output.get("citations", [])
    if citations:
        story += _section("Sources & Citations", s)
        for c in citations[:12]:
            story.append(Paragraph(
                f"• {c.get('claim','')} — <i>{c.get('source','')}</i>", s["small"]))

    doc.build(story)
    return filename

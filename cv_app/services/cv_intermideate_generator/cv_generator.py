# cv_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any, List
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from django.conf import settings
from reportlab.platypus import Image
from PIL import Image as PILImage
import os
import io

def create_header(data, styles, image_max_size=40*mm):
    flow = []

    # ---------------- Profile Image ----------------
    profile_image = None
    profile_image_data = data.get("profile_image")
    if profile_image_data:
        relative_path = profile_image_data
        if profile_image_data.startswith(settings.MEDIA_URL):
            relative_path = profile_image_data[len(settings.MEDIA_URL):]
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path.lstrip("/"))

        if os.path.exists(full_path):
            try:
                pil_img = PILImage.open(full_path)
                if pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")
                img_buffer = io.BytesIO()
                pil_img.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                profile_image = Image(img_buffer, width=image_max_size, height=image_max_size)
            except Exception as e:
                print(f"⚠️ Failed to load profile image: {e}")
        else:
            print(f"⚠️ Image path does not exist: {full_path}")

    # ---------------- Full Name ----------------
    full_name = Paragraph(
        data.get("full_name", "").upper(),
        ParagraphStyle(
            name="HeaderName",
            fontName="Times-Bold",
            fontSize=22,
            textColor=colors.HexColor("#1E40AF"),
            leading=22,
        )
    )

    # ---------------- Contact Info ----------------
    contact_info_text = " | ".join(filter(None, [
        data.get('phone',''),
        data.get('email',''),
        data.get('address',''),
        data.get('github',''),
        data.get('linkedin','')
    ]))
    
    contact_info = Paragraph(
        contact_info_text,
        ParagraphStyle(
            name="HeaderContact",
            fontName="Times-Roman",
            fontSize=10,
            textColor=colors.HexColor("#1E40AF"),
            leading=12,  # slight spacing
            alignment=0,
        )
    )

    # ---------------- Nested Table for Full Name + Contact Below ----------------
    # Add TOPPADDING to contact info row to create space below full_name
    name_contact_table = Table(
        [[full_name], [contact_info]],
        colWidths=[160*mm - image_max_size - 3*mm]
    )
    name_contact_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (0,0), 0),   # no extra padding above full name
        ('BOTTOMPADDING', (0,0), (0,0), 2), # small padding below full name
        ('TOPPADDING', (0,1), (0,1), 3),    # small padding above contact info
        ('BOTTOMPADDING', (0,1), (0,1), 0),
    ]))

    # ---------------- Main Table: Image + Name+Contact ----------------
    if profile_image:
        table_data = [
            [profile_image, name_contact_table]
        ]
        col_widths = [image_max_size + 3*mm, 160*mm - image_max_size - 3*mm]
    else:
        table_data = [[name_contact_table]]
        col_widths = [160*mm]

    table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 3),  # small top padding
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    flow.append(Spacer(1, 5))  # small space from top of page
    flow.append(table)
    flow.append(Spacer(1, 2))  # minimal gap after header

    return flow

# ------------------------------
#  FONT & STYLE DEFINITIONS
# ------------------------------

def get_styles():
    styles = getSampleStyleSheet()

    # Register Times New Roman if available
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf'))
        base_font = 'TimesNewRoman'
    except:
        base_font = 'Times-Roman'

    # Full Name / Title (uppercase, 12pt)
    styles.add(ParagraphStyle(
        name="Name",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=colors.HexColor("#111827"),
    ))

    # Contact line (12pt)
    styles.add(ParagraphStyle(
        name="Meta",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
    ))

    # Section header (uppercase, blue line)
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        textColor=colors.HexColor("#0b63d6"),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT,
    ))

    # Normal paragraph
    styles.add(ParagraphStyle(
        name="NormalJust",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#374151"),
    ))

    # Small and italic text (still 12pt for uniformity)
    styles.add(ParagraphStyle(
        name="Small",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        textColor=colors.HexColor("#374151"),
    ))
    styles.add(ParagraphStyle(
        name="SmallItalic",
        fontName=base_font,
        fontSize=12,
        leading=12 * 1.5,
        textColor=colors.HexColor("#6b7280"),
        italic=True,
    ))

    return styles


# ------------------------------
#  STRUCTURAL HELPERS
# ------------------------------
def section_header_table(title: str, styles):
    p = Paragraph(title.upper(), styles['SectionHeader'])
    tbl = Table([[p]], colWidths=[None])
    tbl.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor("#0b63d6"))
    ]))
    return tbl


def gray_card(flowable_list, styles, card_padding=6):
    tbl = Table([[flowable_list]], colWidths=[None])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('LEFTPADDING', (0, 0), (-1, -1), card_padding),
        ('RIGHTPADDING', (0, 0), (-1, -1), card_padding),
        ('TOPPADDING', (0, 0), (-1, -1), card_padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), card_padding),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return tbl


def two_column_grid(left_blocks: List, right_blocks: List):
    from reportlab.platypus import Spacer
    rows = []
    max_len = max(len(left_blocks), len(right_blocks))
    for i in range(max_len):
        left = left_blocks[i] if i < len(left_blocks) else Spacer(1, 1)
        right = right_blocks[i] if i < len(right_blocks) else Spacer(1, 1)
        rows.append([left, right])
    tbl = Table(rows, colWidths=[None, None])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return tbl


# ------------------------------
#  SECTION BUILDERS
# ------------------------------
def build_header(flow, data, styles):
    """
    Adds the CV header section to the flowables.
    Uses `create_header` to include profile image, full name, and contact info.
    """
    # Use the create_header function to generate flowables for the header
    header_flowables = create_header(data, styles)
    
    # Append all returned flowables to the main flow
    flow.extend(header_flowables)

def build_profile_summary(flow, data, styles):
    flow.append(gray_card([
        section_header_table("Profile Summary", styles),
        Paragraph(data.get('profile_summary', ''), styles['NormalJust'])
    ], styles))
    flow.append(Spacer(1, 8))


def build_education(flow, educations, styles):
    flow.append(section_header_table("Education", styles))
    left_blocks, right_blocks = [], []
    for i, edu in enumerate(educations):
        card = [
            Paragraph(f"<b>{edu.get('degree','')}</b>", styles['Small']),
            Paragraph(edu.get('institution',''), styles['Small']),
            Paragraph(f"{edu.get('location','')} • {edu.get('start_date','')} – {edu.get('end_date','')}", styles['Small']),
            Paragraph(f"Grade: {edu.get('grade','')}", styles['Small']),
        ]
        gray = gray_card(card, styles)
        (left_blocks if i % 2 == 0 else right_blocks).append(gray)
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


def build_work_experience(flow, experiences, styles):
    flow.append(section_header_table("Work Experience", styles))
    left_blocks, right_blocks = [], []
    for i, w in enumerate(experiences):
        card = [
            Paragraph(f"<b>{w.get('job_title','')}</b>", styles['Small']),
            Paragraph(f"<i>{w.get('company','')}</i>", styles['SmallItalic']),
            Paragraph(f"{w.get('location','')}  •  {w.get('start_date','')} – {w.get('end_date','Present')}", styles['Small']),
        ]
        if w.get('responsibilities'):
            bullets = ListFlowable(
                [ListItem(Paragraph(r, styles['Small'])) for r in w['responsibilities']],
                bulletType='bullet'
            )
            card.append(bullets)
        gray = gray_card(card, styles)
        (left_blocks if i % 2 == 0 else right_blocks).append(gray)
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


def build_projects(flow, projects, styles):
    flow.append(section_header_table("Projects", styles))
    left_blocks, right_blocks = [], []
    for i, p in enumerate(projects):
        card = [
            Paragraph(f"<b>{p.get('title','')}</b>", styles['Small']),
            Paragraph(p.get('description',''), styles['Small']),
        ]
        if p.get('link'):
            card.append(Paragraph(f'<u>{p["link"]}</u>', styles['Small']))
        techs = p.get('technologies') or []
        if techs:
            card.append(Paragraph("Technologies: " + ", ".join(techs), styles['Small']))
        gray = gray_card(card, styles)
        (left_blocks if i % 2 == 0 else right_blocks).append(gray)
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


def build_skills(flow, data, styles):
    flow.append(section_header_table("Skills", styles))

    tech_skills = data.get('technical_skills', [])
    soft_skills = data.get('soft_skills', [])

    # Create separate cards
    left_blocks = []
    right_blocks = []

    if tech_skills:
        tech_card = gray_card([
            Paragraph("<b>Technical Skills</b>", styles['Small']),
            Paragraph(", ".join(tech_skills), styles['Small'])
        ], styles)
        left_blocks.append(tech_card)

    if soft_skills:
        soft_card = gray_card([
            Paragraph("<b>Soft Skills</b>", styles['Small']),
            Paragraph(", ".join(soft_skills), styles['Small'])
        ], styles)
        right_blocks.append(soft_card)

    # Render in a two-column grid
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


def build_languages(flow, languages, styles):
    flow.append(section_header_table("Languages", styles))
    left_blocks, right_blocks = [], []
    for i, lang in enumerate(languages):
        card = [
            Paragraph(lang.get('language',''), styles['Small']),
            Paragraph(lang.get('proficiency',''), styles['SmallItalic']),
        ]
        gray = gray_card(card, styles)
        (left_blocks if i % 2 == 0 else right_blocks).append(gray)
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


def build_references(flow, references, styles):
    flow.append(section_header_table("References", styles))
    left_blocks, right_blocks = [], []
    for i, r in enumerate(references):
        card = [
            Paragraph(f"<b>{r.get('name','')}</b>", styles['Small']),
            Paragraph(r.get('position',''), styles['Small']),
            Paragraph(r.get('email',''), styles['Small']),
            Paragraph(r.get('phone',''), styles['Small']),
        ]
        gray = gray_card(card, styles)
        (left_blocks if i % 2 == 0 else right_blocks).append(gray)
    flow.append(two_column_grid(left_blocks, right_blocks))
    flow.append(Spacer(1, 8))


# ------------------------------
#  MAIN GENERATOR FUNCTION
# ------------------------------
def generate_cv(data: Dict[str, Any], output_path: str):
    styles = get_styles()
    flow = []

    # Always show header
    build_header(flow, data, styles)

    # Profile Summary (only if content exists)
    profile_summary = data.get('profile_summary', '').strip()
    if profile_summary:
        build_profile_summary(flow, data, styles)

    # Education
    educations = data.get('educations', [])
    if educations:
        build_education(flow, educations, styles)

    # Work Experience
    work_experiences = data.get('work_experiences', [])
    if work_experiences:
        build_work_experience(flow, work_experiences, styles)

    # Projects
    projects = data.get('projects', [])
    if projects:
        build_projects(flow, projects, styles)

    # Skills
    technical_skills = data.get('technical_skills', [])
    soft_skills = data.get('soft_skills', [])
    if technical_skills or soft_skills:
        build_skills(flow, data, styles)

    # Languages
    languages = data.get('languages', [])
    if languages:
        build_languages(flow, languages, styles)

    # References
    references = data.get('references', [])
    if references:
        build_references(flow, references, styles)

    # Generate PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )
    doc.build(flow)
    return output_path

# advanced_cv_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any, List
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, FrameBreak
from django.conf import settings
from reportlab.platypus import Image
from PIL import Image as PILImage
import os
import io
# ------------------------------
# FONT & STYLES
# ------------------------------

from reportlab.platypus import KeepTogether

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






def get_styles():
    styles = getSampleStyleSheet()
    # Register Times New Roman
    try:
        pdfmetrics.registerFont(TTFont('TimesNewRoman', '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf'))
        base_font = 'TimesNewRoman'
    except:
        base_font = 'Times-Roman'

    # Full name
    styles.add(ParagraphStyle(
        name="Name",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=6
    ))
    # Contact info
    styles.add(ParagraphStyle(
        name="Meta",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151")
    ))
    # Section headers
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        textColor=colors.HexColor("#0b63d6"),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT
    ))
    # Normal paragraph
    styles.add(ParagraphStyle(
        name="NormalJust",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#374151"),
    ))
    # Small text
    styles.add(ParagraphStyle(
        name="Small",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        textColor=colors.HexColor("#374151")
    ))
    # Small italic
    styles.add(ParagraphStyle(
        name="SmallItalic",
        fontName=base_font,
        fontSize=12,
        leading=12*1.5,
        textColor=colors.HexColor("#6b7280"),
        italic=True
    ))
    return styles

# ------------------------------
# HELPERS
# ------------------------------
def section_header_table(title: str, styles):
    p = Paragraph(title.upper(), styles['SectionHeader'])
    tbl = Table([[p]], colWidths=[None])
    tbl.setStyle(TableStyle([
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#0b63d6"))
    ]))
    return tbl

def gray_card(flowable_list, bg_color=colors.HexColor("#f8fafc"), left_border=None, card_padding=6):
    tbl = Table([[flowable_list]], colWidths=[None])
    style_cmds = [
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('LEFTPADDING', (0,0), (-1,-1), card_padding),
        ('RIGHTPADDING', (0,0), (-1,-1), card_padding),
        ('TOPPADDING', (0,0), (-1,-1), card_padding),
        ('BOTTOMPADDING', (0,0), (-1,-1), card_padding),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]
    if left_border:
        style_cmds.append(('LINEBEFORE', (0,0), (0,0), 4, left_border))
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

def two_column_grid(left_blocks: List, right_blocks: List):
    from reportlab.platypus import Spacer
    rows = []
    max_len = max(len(left_blocks), len(right_blocks))
    for i in range(max_len):
        left = left_blocks[i] if i < len(left_blocks) else Spacer(1,1)
        right = right_blocks[i] if i < len(right_blocks) else Spacer(1,1)
        rows.append([left, right])
    tbl = Table(rows, colWidths=[None, None])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    return tbl

# ------------------------------
# BUILDERS
# ------------------------------
def build_header(flow, data, styles):
    """
    Reuses create_header to add the header (profile image, full name, contacts) to the flow.
    """
    header_flowables = create_header(data, styles)
    flow.extend(header_flowables)  # append all flowables from create_header

def build_profile_summary(flow, data, styles):
    flow.append(gray_card([
        section_header_table("Profile Summary", styles),
        Paragraph(data.get('profile_summary',''), styles['NormalJust'])
    ], bg_color=colors.HexColor("#ebf8ff")))
    flow.append(Spacer(1,6))


def build_languages(flow, languages, styles, max_pills_per_row=3):
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    flow.append(section_header_table("Languages", styles))
    flow.append(Spacer(1, 6))

    def language_pills(langs: list):
        """
        Convert list of languages into rows of pill-like Tables with rounded edges and no background.
        """
        rows = []
        for i in range(0, len(langs), max_pills_per_row):
            row_langs = langs[i:i+max_pills_per_row]
            row_flowables = []
            for lang in row_langs:
                text = f"{lang.get('language','')} ({lang.get('proficiency','')})"
                pill = Table([[Paragraph(text, styles['Small'])]],
                             style=TableStyle([
                                 ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#111827")),
                                 ('LEFTPADDING', (0,0), (-1,-1), 6),
                                 ('RIGHTPADDING', (0,0), (-1,-1), 6),
                                 ('TOPPADDING', (0,0), (-1,-1), 2),
                                 ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                                 ('ROUNDED', (0,0), (-1,-1), 6)
                             ]),
                             colWidths=None)
                row_flowables.append(pill)
            rows.append(row_flowables)
        return rows

    if languages:
        flow.append(
            gray_card(
                sum(language_pills(languages), []),  # flatten list of rows
                bg_color=colors.HexColor("#f0f9ff"),
                left_border=colors.HexColor("#3b82f6"),
                card_padding=6
            )
        )
        flow.append(Spacer(1, 6))



def build_education(flow, educations, styles):
    flow.append(section_header_table("Education", styles))
    flow.append(Spacer(1, 6))  # <-- Add vertical space after header
    blocks = []
    for edu in educations:
        card = [
            Paragraph(f"<b>{edu.get('degree','')}</b>", styles['Small']),
            Paragraph(f"<i>{edu.get('institution','')}</i>", styles['SmallItalic']),
            Paragraph(f"{edu.get('location','')}  •  {edu.get('start_date','')} – {edu.get('end_date','')}", styles['Small']),
            Paragraph(f"Grade: {edu.get('grade','')}", styles['Small'])
        ]
        gray = gray_card(card, bg_color=colors.white, left_border=colors.HexColor("#60a5fa"), card_padding=8)
        blocks.append(gray)
    for blk in blocks:
        flow.append(blk)
        flow.append(Spacer(1,6))


def build_work_experience(flow, experiences, styles):
    flow.append(section_header_table("Work Experience", styles))
    flow.append(Spacer(1, 6))  # <-- Add space here
    blocks = []
    for w in experiences:
        header_line = [
            Paragraph(f"<b>{w.get('job_title','')}</b>  <i>{w.get('company','')}</i>", styles['Small'])
        ]
        sub_line = [
            Paragraph(f"{w.get('location','')}  •  {w.get('start_date','')} – {w.get('end_date','Present')}", styles['SmallItalic'])
        ]
        card_content = header_line + sub_line
        if w.get('responsibilities'):
            bullets = ListFlowable(
                [ListItem(Paragraph(r, styles['Small'])) for r in w['responsibilities']],
                bulletType='bullet',
                bulletFontName='Times-Roman',
                leftIndent=12
            )
            card_content.append(bullets)
        gray = gray_card(card_content, bg_color=colors.HexColor("#f1f5f9"), left_border=colors.HexColor("#34d399"), card_padding=8)
        blocks.append(gray)
    for blk in blocks:
        flow.append(blk)
        flow.append(Spacer(1,6))

def build_projects(flow, projects, styles):
    # Section header
    flow.append(section_header_table("Projects", styles))
    flow.append(Spacer(1, 6))  # vertical space after header

    for p in projects:
        # Card content
        card_content = [
            Paragraph(f"<b>{p.get('title','')}</b>", styles['Small']),
            Paragraph(p.get('description',''), styles['Small'])
        ]

        if p.get('link'):
            card_content.append(Paragraph(f'<u>{p["link"]}</u>', styles['Small']))

        techs = p.get('technologies') or []
        if techs:
            card_content.append(
                Paragraph("Technologies: " + ", ".join(techs), styles['Small'])
            )

        # Gray card like work experience
        gray = gray_card(
            card_content,
            bg_color=colors.HexColor("#f1f5f9"),
            left_border=colors.HexColor("#6366f1"),  # purple left border
            card_padding=8
        )

        flow.append(gray)
        flow.append(Spacer(1, 6))  # space between projects


def build_projects(flow, projects, styles):
    flow.append(section_header_table("Projects", styles))
    flow.append(Spacer(1, 6))

    for p in projects:
        card_content = [
            Paragraph(f"<b>{p.get('title','')}</b>", styles['Small']),
            Paragraph(p.get('description',''), styles['Small'])
        ]

        if p.get('link'):
            card_content.append(Paragraph(f'<u>{p["link"]}</u>', styles['Small']))

        techs = p.get('technologies') or []
        if techs:
            card_content.append(Paragraph("Technologies: " + ", ".join(techs), styles['Small']))

        gray = gray_card(
            card_content,
            bg_color=colors.HexColor("#f1f5f9"),
            left_border=colors.HexColor("#6366f1"),
            card_padding=8
        )

        # Wrap in KeepTogether to avoid splitting mid-card
        flow.append(KeepTogether(gray))
        flow.append(Spacer(1,6))


def build_skills(flow, data, styles):
    from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem

    tech_skills = data.get('technical_skills', [])
    soft_skills = data.get('soft_skills', [])

    def build_skill_list(title, skills, card_bg, border_color):
        if not skills:
            return

        # Section header
        header = Paragraph(title, styles['Small'])

        # Build unordered list of skills
        bullets = ListFlowable(
            [ListItem(Paragraph(skill, styles['Small']), bulletColor=colors.HexColor("#111827"))
             for skill in skills],
            bulletType='bullet',
            leftIndent=12,
            bulletFontName='Times-Roman',
            bulletFontSize=10
        )

        # Wrap list in a gray_card
        flow.append(
            gray_card(
                [header, bullets],
                bg_color=card_bg,
                left_border=border_color,
                card_padding=6
            )
        )
        flow.append(Spacer(1, 6))

    # Technical Skills
    build_skill_list(
        "Technical Skills", tech_skills,
        card_bg=colors.HexColor("#f0f9ff"),
        border_color=colors.HexColor("#3b82f6")
    )

    # Soft Skills
    build_skill_list(
        "Soft Skills", soft_skills,
        card_bg=colors.HexColor("#f0fdf4"),
        border_color=colors.HexColor("#10b981")
    )


def build_references(flow, references, styles):
    """
    Build references section using full width (no two columns).
    Each reference is a gray card with left border.
    """
    # Section header
    flow.append(section_header_table("References", styles))
    flow.append(Spacer(1, 6))  # vertical space after header

    for r in references:
        card_content = [
            Paragraph(f"<b>{r.get('name','')}</b>", styles['Small']),
            Paragraph(r.get('position',''), styles['Small']),
            Paragraph(r.get('email',''), styles['Small']),
            Paragraph(r.get('phone',''), styles['Small'])
        ]

        gray = gray_card(
            card_content,
            bg_color=colors.HexColor("#f1f5f9"),
            left_border=colors.HexColor("#a78bfa"),
            card_padding=8
        )

        # Append directly to flow (full width)
        flow.append(gray)
        flow.append(Spacer(1, 4))  # space between references



# ------------------------------
def two_column_flow(left_blocks: list, right_blocks: list, col_width=240*mm/2):
    """
    Safely create a two-column layout without LayoutError.
    Each block is wrapped in KeepTogether to avoid splitting mid-card.
    """
    from reportlab.platypus import Spacer, Table, TableStyle

    rows = []
    max_len = max(len(left_blocks), len(right_blocks))
    for i in range(max_len):
        left = left_blocks[i] if i < len(left_blocks) else Spacer(1,1)
        right = right_blocks[i] if i < len(right_blocks) else Spacer(1,1)
        rows.append([KeepTogether(left), KeepTogether(right)])

    tbl = Table(rows, colWidths=[col_width, col_width])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    return tbl

# ------------------------------

def build_achievements(flow, achievements: List[str], styles):
    from reportlab.platypus import Paragraph, Spacer, ListFlowable, ListItem

    if not achievements:
        return

    # Section header
    flow.append(section_header_table("Achievements", styles))
    flow.append(Spacer(1, 6))

    # Create an unordered list of achievements
    bullets = ListFlowable(
        [ListItem(Paragraph(a, styles['Small']), bulletColor=colors.HexColor("#111827"))
         for a in achievements],
        bulletType='bullet',
        leftIndent=12,
        bulletFontName='Times-Roman',
        bulletFontSize=10
    )

    # Wrap the list in a gray card with left border
    flow.append(
        gray_card(
            [bullets],
            bg_color=colors.HexColor("#fef3c7"),  # light yellow card background
            left_border=colors.HexColor("#f59e0b"),  # orange left border
            card_padding=6
        )
    )
    flow.append(Spacer(1, 6))


def generate_cv_safe(data: Dict[str, Any], output_path: str):
    styles = get_styles()
    
    doc = BaseDocTemplate(
        output_path, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )
    
    # Single full-width frame for everything
    full_frame = Frame(
        18*mm, 18*mm,
        A4[0] - 36*mm,
        A4[1] - 36*mm,
        id='full'
    )

    template = PageTemplate(id='FullPage', frames=[full_frame])
    doc.addPageTemplates([template])
    
    flow = []

    # Header
    build_header(flow, data, styles)

    # Profile, Education
    build_profile_summary(flow, data, styles)
    build_education(flow, data.get('educations', []), styles)
    
    # Languages in two columns
    build_languages(flow, data.get('languages', []), styles)
    
    # Work Experience (single-column)
    build_work_experience(flow, data.get('work_experiences', []), styles)
    
    # Projects (single-column)
    build_projects(flow, data.get('projects', []), styles)

    # Skills (optional two-column)
    build_skills(flow, data, styles)
    
    build_achievements(flow, data.get('achievements', []), styles)
    # References (full-width)
    build_references(flow, data.get('references', []), styles)

    doc.build(flow)
    return output_path


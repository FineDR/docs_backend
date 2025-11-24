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
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return datetime.min  # for missing or invalid dates

# Sort experiences by start date descending (latest first)
    valid_exp.sort(key=lambda w: parse_date(w.get('start_date') or ""), reverse=True)

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

def build_profile_summary(flow, data,styles,top_margin=12):
    profile_text = data.get('profile_summary', '').strip()
    if not profile_text:
        return  # Skip section if empty

    flow.append(Spacer(1, top_margin))
    # Add left colored border
    flow.append(
        gray_card(
            [
                section_header_table("Profile Summary", styles),
                Paragraph(profile_text, styles['NormalJust'])
            ],
            bg_color=colors.HexColor("#ebf8ff"),        # light blue background
            left_border=colors.HexColor("#14b8a6"),     # blue left border like languages section
            card_padding=6
        )
    )
    flow.append(Spacer(1, 6))




def build_languages(flow, languages, styles, max_pills_per_row=3):
    if not languages:
        return  # Skip if no languages

    # Filter out empty language entries
    valid_languages = [l for l in languages if l.get('language')]
    if not valid_languages:
        return

    flow.append(section_header_table("Languages", styles))
    flow.append(Spacer(1, 6))

    def language_pills(langs: list):
        rows = []
        for i in range(0, len(langs), max_pills_per_row):
            row_langs = langs[i:i + max_pills_per_row]
            row_flowables = []
            for lang in row_langs:
                lang_name = lang.get('language', '').strip()
                prof = lang.get('proficiency', '').strip()
                if not lang_name:
                    continue
                text = f"{lang_name} ({prof})" if prof else lang_name
                pill = Table([[Paragraph(text, styles['Small'])]],
                             style=TableStyle([
                                 ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#111827")),
                                 ('LEFTPADDING', (0,0), (-1,-1), 6),
                                 ('RIGHTPADDING', (0,0), (-1,-1), 6),
                                 ('TOPPADDING', (0,0), (-1,-1), 2),
                                 ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                                 ('ROUNDED', (0,0), (-1,-1), 6)
                             ]))
                row_flowables.append(pill)
            if row_flowables:
                rows.append(row_flowables)
        return rows

    flow.append(
        gray_card(
            sum(language_pills(valid_languages), []),  # flatten rows
            bg_color=colors.HexColor("#f0f9ff"),
            left_border=colors.HexColor("#3b82f6"),
            card_padding=6
        )
    )
    flow.append(Spacer(1, 6))


def build_education(flow, educations, styles):
    if not educations:
        return  # Skip section if empty

    # Filter out completely empty entries
    valid_edu = []
    for edu in educations:
        if any(edu.get(k) for k in ['degree', 'institution', 'location', 'start_date', 'end_date', 'grade']):
            valid_edu.append(edu)

    if not valid_edu:
        return

    # --- SORT EDUCATION BY END DATE DESCENDING (newest first) ---
    def parse_date(date_str):
        from datetime import datetime
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return datetime.min  # fallback for missing/invalid dates

    valid_edu.sort(key=lambda e: parse_date(e.get('end_date', '') or ''), reverse=True)

    flow.append(section_header_table("Education", styles))
    flow.append(Spacer(1, 6))

    for edu in valid_edu:
        card_content = []

        degree = (edu.get('degree') or '').strip()
        if degree:
            card_content.append(Paragraph(f"<b>{degree}</b>", styles['Small']))

        institution = (edu.get('institution') or '').strip()
        if institution:
            card_content.append(Paragraph(f"<i>{institution}</i>", styles['SmallItalic']))

        location = (edu.get('location') or '').strip()
        start = (edu.get('start_date') or '').strip()
        end = (edu.get('end_date') or '').strip()
        if location or start or end:
            line = f"{location}" if location else ""
            if start or end:
                line += f"  •  {start or ''} – {end or ''}"
            card_content.append(Paragraph(line, styles['Small']))

        grade = (edu.get('grade') or '').strip()
        if grade:
            card_content.append(Paragraph(f"Grade: {grade}", styles['Small']))

        if card_content:
            gray = gray_card(
                card_content,
                bg_color=colors.white,
                left_border=colors.HexColor("#60a5fa"),
                card_padding=8
            )
            flow.append(gray)
            flow.append(Spacer(1, 6))

def build_work_experience(flow, experiences, styles):
    if not experiences:
        return  # skip entire section if empty

    # Filter out completely empty entries
    valid_exp = []
    for w in experiences:
        if any(w.get(k) for k in ['job_title', 'company', 'location', 'start_date', 'end_date', 'responsibilities']):
            valid_exp.append(w)

    if not valid_exp:
        return

    # --- SORT EXPERIENCES BY START DATE DESCENDING (latest first) ---
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return datetime.min  # fallback for missing/invalid dates

    valid_exp.sort(key=lambda w: parse_date(w.get('start_date') or ""), reverse=True)

    flow.append(section_header_table("Work Experience", styles))
    flow.append(Spacer(1, 6))

    for w in valid_exp:
        card_content = []

        # Safely get string fields and strip
        job_title = (w.get('job_title') or "").strip()
        company = (w.get('company') or "").strip()
        if job_title or company:
            card_content.append(Paragraph(f"<b>{job_title}</b>  <i>{company}</i>", styles['Small']))

        location = (w.get('location') or "").strip()
        start = (w.get('start_date') or "").strip()
        end = (w.get('end_date') or "").strip() or 'Present'
        if location or start or end:
            line = f"{location}" if location else ""
            if start or end:
                line += f"  •  {start or ''} – {end or ''}"
            card_content.append(Paragraph(line, styles['SmallItalic']))

        # Safely handle responsibilities
        responsibilities = w.get('responsibilities') or []
        responsibilities = [r.strip() for r in responsibilities if r and r.strip()]
        if responsibilities:
            bullets = ListFlowable(
                [ListItem(Paragraph(r, styles['Small'])) for r in responsibilities],
                bulletType='bullet',
                bulletFontName='Times-Roman',
                leftIndent=12
            )
            card_content.append(bullets)

        # Add card to flow if any content exists
        if card_content:
            gray = gray_card(
                card_content,
                bg_color=colors.HexColor("#f1f5f9"),
                left_border=colors.HexColor("#34d399"),
                card_padding=8
            )
            flow.append(KeepTogether(gray))
            flow.append(Spacer(1,6))


def build_projects(flow, projects, styles):
    if not projects:
        return

    # Filter out completely empty projects
    valid_projects = []
    for p in projects:
        if any(p.get(k) for k in ['title', 'description', 'link', 'technologies', 'start_date']):
            valid_projects.append(p)

    if not valid_projects:
        return

    # --- SORT PROJECTS BY START DATE DESCENDING (newest first) ---
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return datetime.min  # fallback for missing/invalid dates

    valid_projects.sort(key=lambda p: parse_date(p.get('start_date') or ""), reverse=True)

    flow.append(section_header_table("Projects", styles))
    flow.append(Spacer(1, 6))

    for p in valid_projects:
        card_content = []

        title = (p.get('title') or '').strip()
        if title:
            card_content.append(Paragraph(f"<b>{title}</b>", styles['Small']))

        description = (p.get('description') or '').strip()
        if description:
            card_content.append(Paragraph(description, styles['Small']))

        link = (p.get('link') or '').strip()
        if link:
            card_content.append(Paragraph(f'<u>{link}</u>', styles['Small']))

        techs = [t.strip() for t in (p.get('technologies') or []) if t.strip()]
        if techs:
            card_content.append(Paragraph("Technologies: " + ", ".join(techs), styles['Small']))

        if card_content:
            gray = gray_card(
                card_content,
                bg_color=colors.HexColor("#f1f5f9"),
                left_border=colors.HexColor("#6366f1"),
                card_padding=8
            )
            flow.append(KeepTogether(gray))
            flow.append(Spacer(1,6))

def build_skills(flow, data, styles):
    tech_skills = [s.strip() for s in (data.get('technical_skills') or []) if s.strip()]
    soft_skills = [s.strip() for s in (data.get('soft_skills') or []) if s.strip()]

    def build_skill_list(title, skills, card_bg, border_color):
        if not skills:
            return
        header = Paragraph(title, styles['Small'])
        bullets = ListFlowable(
            [ListItem(Paragraph(skill, styles['Small']), bulletColor=colors.HexColor("#111827"))
             for skill in skills],
            bulletType='bullet',
            leftIndent=12,
            bulletFontName='Times-Roman',
            bulletFontSize=10
        )
        flow.append(gray_card([header, bullets], bg_color=card_bg, left_border=border_color, card_padding=6))
        flow.append(Spacer(1, 6))

    build_skill_list(
        "Technical Skills", tech_skills,
        card_bg=colors.HexColor("#f0f9ff"),
        border_color=colors.HexColor("#3b82f6")
    )

    build_skill_list(
        "Soft Skills", soft_skills,
        card_bg=colors.HexColor("#f0fdf4"),
        border_color=colors.HexColor("#10b981")
    )

def build_references(flow, references, styles):
    """
    Build references section using full width.
    Skip empty references and fields.
    """
    if not references:
        return  # skip entire section if empty

    # Filter out references that have no meaningful data
    valid_refs = []
    for r in references:
        if any(r.get(k) for k in ['name', 'position', 'email', 'phone']):
            valid_refs.append(r)

    if not valid_refs:
        return

    # --- SORT REFERENCES ALPHABETICALLY BY NAME ---
    valid_refs.sort(key=lambda r: (r.get('name') or "").lower())

    # Section header
    flow.append(section_header_table("References", styles))
    flow.append(Spacer(1, 6))  # vertical space after header

    for r in valid_refs:
        card_content = []

        name = (r.get('name') or '').strip()
        if name:
            card_content.append(Paragraph(f"<b>{name}</b>", styles['Small']))

        position = (r.get('position') or '').strip()
        if position:
            card_content.append(Paragraph(position, styles['Small']))

        email = (r.get('email') or '').strip()
        if email:
            card_content.append(Paragraph(email, styles['Small']))

        phone = (r.get('phone') or '').strip()
        if phone:
            card_content.append(Paragraph(phone, styles['Small']))

        if card_content:
            gray = gray_card(
                card_content,
                bg_color=colors.HexColor("#f1f5f9"),
                left_border=colors.HexColor("#a78bfa"),
                card_padding=8
            )
            flow.append(KeepTogether(gray))
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

    # Filter out empty achievements
    valid_achievements = [a.strip() for a in achievements if a and a.strip()]
    if not valid_achievements:
        return  # skip section if empty

    # Section header
    flow.append(section_header_table("Achievements", styles))
    flow.append(Spacer(1, 6))

    # Create an unordered list of achievements
    bullets = ListFlowable(
        [ListItem(Paragraph(a, styles['Small']), bulletColor=colors.HexColor("#111827"))
         for a in valid_achievements],
        bulletType='bullet',
        leftIndent=12,
        bulletFontName='Times-Roman',
        bulletFontSize=10
    )

    # Wrap the list in a gray card with left border
    flow.append(
        gray_card(
            [bullets],
            bg_color=colors.HexColor("#fef3c7"),  # light yellow background
            left_border=colors.HexColor("#f59e0b"),  # orange left border
            card_padding=6
        )
    )
    flow.append(Spacer(1, 6))


def build_certificates(flow, certificates: List[Dict[str,str]], styles):
    # Use 'name' instead of 'title'
    valid_certs = [c for c in certificates if c.get('name')]
    if not valid_certs:
        return

    flow.append(section_header_table("Certificates", styles))
    flow.append(Spacer(1,6))

    for c in valid_certs:
        card_content = []
        title = c.get('name','').strip()         # updated
        issuer = c.get('issuer','').strip()
        date = c.get('date','').strip()

        if title:
            card_content.append(Paragraph(f"<b>{title}</b>", styles['Small']))
        if issuer:
            card_content.append(Paragraph(f"Issuer: {issuer}", styles['SmallItalic']))
        if date:
            card_content.append(Paragraph(f"Date: {date}", styles['Small']))

        if card_content:
            gray = gray_card(
                card_content,
                bg_color=colors.HexColor("#fff7ed"),
                left_border=colors.HexColor("#f97316"),
                card_padding=6
            )
            flow.append(gray)
            flow.append(Spacer(1,4))


def generate_cv_safe(data: Dict[str, Any], output_path: str):
    import traceback
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

    # Helper to safely call builder functions
    def safe_build(func, *args):
        try:
            func(*args)
        except Exception as e:
            print(f"⚠️ Error in {func.__name__}: {e}")
            print(traceback.format_exc())

    # Header
    if any([data.get("full_name"), data.get("profile_image"), data.get("phone"), data.get("email")]):
        safe_build(build_header, flow, data, styles)

    # Profile Summary
    safe_build(build_profile_summary, flow, data, styles)

    # Education
    safe_build(build_education, flow, data.get('educations', []), styles)

    # Languages
    safe_build(build_languages, flow, data.get('languages', []), styles)

    # Work Experience
    safe_build(build_work_experience, flow, data.get('work_experiences', []), styles)

    # Projects
    safe_build(build_projects, flow, data.get('projects', []), styles)

    safe_build(build_certificates, flow, data.get('certificates', []), styles)
    print("Certificates Data:", data.get('certificates', []))

    # Skills
    safe_build(build_skills, flow, data, styles)

    # Achievements
    safe_build(build_achievements, flow, data.get('achievements', []), styles)

    # References
    safe_build(build_references, flow, data.get('references', []), styles)

    # Finally, build the PDF
    try:
        doc.build(flow)
    except Exception as e:
        print(f"⚠️ Error during doc.build: {e}")
        print(traceback.format_exc())

    return output_path

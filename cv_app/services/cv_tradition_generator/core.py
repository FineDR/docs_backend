import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle, ListFlowable, ListItem, Flowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from django.conf import settings
from reportlab.platypus import Image
from PIL import Image as PILImage

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







# -------------------- Styles --------------------
def create_styles():
    styles = getSampleStyleSheet()
    styles.BLUE = colors.HexColor("#1e40af")
    styles.GRAY = colors.HexColor("#4b5563")
    styles.LIGHT_GRAY = colors.HexColor("#f3f4f6")
    styles.BLACK = colors.HexColor("#000000")

    base_font_size = 12
    line_spacing = base_font_size * 1.5

    # Name
    styles.add(ParagraphStyle(
        name="Name",
        fontName="Times-Bold",
        fontSize=base_font_size + 8,
        leading=(base_font_size + 8) * 1.5,
        alignment=TA_CENTER,
        textColor=styles.BLUE,
        spaceAfter=6
    ))

    # Subtitle
    styles.add(ParagraphStyle(
        name="Subtitle",
        fontName="Times-Roman",
        fontSize=base_font_size,
        leading=line_spacing,
        alignment=TA_CENTER,
        textColor=styles.GRAY,
        spaceAfter=12
    ))

    # Section Title
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=base_font_size + 2,
        leading=(base_font_size + 2) * 1.5,
        alignment=TA_LEFT,
        textColor=styles.GRAY,
        spaceAfter=6,
    ))

    # Body Text
    styles.add(ParagraphStyle(
        name="MyBodyText",
        fontName="Times-Roman",
        fontSize=base_font_size,
        leading=line_spacing,
        alignment=TA_LEFT,
        textColor=styles.BLACK,
        spaceAfter=4
    ))

    return styles


# -------------------- Generic Section --------------------
def create_section(title, content, styles):
    flow = []
    border = Table([[Paragraph(title.upper(), styles["SectionTitle"])]])
    border.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 1, styles.BLUE), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    flow.append(border)
    flow.append(Spacer(1, 4))
    if isinstance(content, list):
        list_items = [ListItem(Paragraph(str(item), styles["MyBodyText"]), leftIndent=10) for item in content]
        flow.append(ListFlowable(list_items, bulletType='bullet', start='•', leftIndent=10))
    else:
        flow.append(Paragraph(str(content), styles["MyBodyText"]))
    flow.append(Spacer(1, 8))
    return flow


# -------------------- Skills Flowables --------------------
class SkillPill(Flowable):
    def __init__(self, text, height=20, bg_color=colors.HexColor("#DBEAFE"),
                 text_color=colors.HexColor("#1E40AF"), padding=6, font_name="Times-Bold", font_size=10):
        super().__init__()
        self.text = text
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.padding = padding
        self.font_name = font_name
        self.font_size = font_size
        self.width = None

    def wrap(self, availWidth, availHeight):
        text_width = stringWidth(self.text, self.font_name, self.font_size)
        self.width = text_width + 2 * self.padding
        return self.width, self.height

    def draw(self):
        self.canv.setFillColor(self.bg_color)
        self.canv.roundRect(0, 0, self.width, self.height, radius=self.height/2, fill=1, stroke=0)
        self.canv.setFillColor(self.text_color)
        self.canv.setFont(self.font_name, self.font_size)
        text_width = stringWidth(self.text, self.font_name, self.font_size)
        self.canv.drawString((self.width - text_width)/2, (self.height - self.font_size)/2, self.text)


class HorizontalPillFlowable(Flowable):
    def __init__(self, items, max_width=160*mm, height=20, padding=6, gap=4,
                 bg_color=colors.HexColor("#DBEAFE"), text_color=colors.HexColor("#1E40AF")):
        super().__init__()
        self.items = items
        self.max_width = max_width
        self.height = height
        self.padding = padding
        self.gap = gap
        self.bg_color = bg_color
        self.text_color = text_color
        self.pills = [SkillPill(item, height=height, bg_color=bg_color, text_color=text_color, padding=padding)
                      for item in items]

    def wrap(self, availWidth, availHeight):
        self.lines = []
        current_line = []
        current_width = 0
        for pill in self.pills:
            pill_width, _ = pill.wrap(0, 0)
            if current_line and (current_width + pill_width + self.gap > self.max_width):
                self.lines.append(current_line)
                current_line = []
                current_width = 0
            current_line.append(pill)
            current_width += pill_width + self.gap
        if current_line:
            self.lines.append(current_line)
        self.total_height = len(self.lines) * self.height + (len(self.lines)-1) * self.gap
        return self.max_width, self.total_height

    def draw(self):
        y = self.total_height
        for line in self.lines:
            x = 0
            y -= self.height
            for pill in line:
                pill.canv = self.canv
                pill.drawOn(self.canv, x, y)
                pill_width, _ = pill.wrap(0,0)
                x += pill_width + self.gap
            y -= self.gap


# -------------------- Skills Section --------------------
def create_skills_section(data, styles):
    flow = []
    border = Table([[Paragraph("SKILLS", styles["SectionTitle"])]])
    border.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 1, styles.BLUE), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    flow.append(border)
    flow.append(Spacer(1, 4))

    tech = data.get("technical_skills", [])
    if tech:
        flow.append(Paragraph("Technical Skills:", styles["MyBodyText"]))
        flow.append(HorizontalPillFlowable(tech, bg_color=colors.HexColor("#DBEAFE"), text_color=colors.HexColor("#1E40AF")))
        flow.append(Spacer(1, 4))

    soft = data.get("soft_skills", [])
    if soft:
        flow.append(Paragraph("Soft Skills:", styles["MyBodyText"]))
        flow.append(HorizontalPillFlowable(soft, bg_color=colors.HexColor("#DCFCE7"), text_color=colors.HexColor("#166534")))
        flow.append(Spacer(1, 4))

    return flow


# -------------------- Projects Section --------------------
def create_projects_section(projects, styles):
    flow = []
    if not projects:
        return flow

    border = Table([[Paragraph("PROJECTS", styles["SectionTitle"])]])
    border.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 1, styles.BLUE), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    flow.append(border)
    flow.append(Spacer(1, 4))

    for p in projects:
        flow.append(Paragraph(f"<b>{p.get('title','')}</b>: {p.get('description','')}", styles["MyBodyText"]))
        flow.append(Spacer(1, 2))
        if p.get("link"):
            flow.append(Paragraph(f"Link: {p['link']}", styles["MyBodyText"]))
            flow.append(Spacer(1, 2))
        techs = p.get("technologies", [])
        flow.append(HorizontalPillFlowable(techs, bg_color=colors.HexColor("#FEF3C7"), text_color=colors.HexColor("#92400E")))
        flow.append(Spacer(1, 4))

    return flow


# -------------------- Generate CV --------------------
def generate_cv(data, output_path=None):
    """
    Generate CV as PDF.
    - output_path: file path or BytesIO object
    """
    styles = create_styles()

    doc = SimpleDocTemplate(
        output_path if output_path else "cv_full.pdf",
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    flow = []
    flow.extend(create_header(data, styles))
    # flow.extend(create_section("Profile Summary", data.get("profile_summary",""), styles))
    profile_summary = data.get("profile_summary", "").strip()
    if profile_summary:
        flow.extend(create_section("Profile Summary", profile_summary, styles))


    # flow.extend(create_section("Career Objective", data.get("career_objective",""), styles))
    career_objective = data.get("career_objective", "").strip()
    if career_objective:
        flow.extend(create_section("Career Objective", career_objective, styles))

    
    # flow.extend(create_section("Education", [f"{e['degree']} — {e['institution']} ({e['start_date']} to {e['end_date']})" for e in data.get("educations", [])], styles))
    # Education
    education_content = []
    for e in data.get("educations", []):
        line = f"{e['degree']} — {e['institution']} ({e['start_date']} to {e['end_date']})"
        if e.get("grade"):
            line += f", Grade: {e['grade']}"
        if e.get("location"):
            line += f", Location: {e['location']}"
        education_content.append(line)
    if education_content:
        flow.extend(create_section("Education", education_content, styles))

    # Work Experience
    work_exp_content = []
    for w in data.get("work_experiences", []):
        lines = [f"{w['job_title']} at {w['company']} ({w['start_date']} – {w.get('end_date','Present')})"]
        if w.get("responsibilities"):
            lines.extend([f"- {r}" for r in w["responsibilities"]])
        work_exp_content.append("\n".join(lines))
    if work_exp_content:
        flow.extend(create_section("Work Experience", work_exp_content, styles))


    # flow.extend(create_projects_section(data.get("projects", []), styles))
    projects = data.get("projects", [])
    if projects:
        flow.extend(create_projects_section(projects, styles))

    # flow.extend(create_skills_section(data, styles))
    skills= data.get("technical_skills", []) + data.get("soft_skills", [])
    if skills:
        flow.extend(create_skills_section(data, styles))


    # flow.extend(create_section("Achievements", data.get("achievements", []), styles))
    achievements = data.get("achievements", [])
    if achievements:
        flow.extend(create_section("Achievements", achievements, styles))

    # flow.extend(create_section("Languages", [f"{l['language']} ({l['proficiency']})" for l in data.get("languages", [])], styles))
    languages = data.get("languages", [])
    if languages:
        lang_content = [f"{l['language']} ({l['proficiency']})" for l in languages]
        flow.extend(create_section("Languages", lang_content, styles))
    

    # flow.extend(create_section("Certifications", [f"{c['name']} — {c['issuer']} ({c['date']})" for c in data.get("certificates", [])], styles))
    certificates = data.get("certificates", [])
    if certificates:
        cert_content = [f"{c['name']} — {c['issuer']} ({c['date']})" for c in certificates]
        flow.extend(create_section("Certifications", cert_content, styles))

    # flow.extend(create_section("References", [f"{r['name']} — {r['position']} ({r['email']}, {r['phone']})" for r in data.get("references", [])], styles))
    references = data.get("references", [])
    if references:
        ref_content = [f"{r['name']} — {r['position']} ({r['email']}, {r['phone']})" for r in references]
        flow.extend(create_section("References", ref_content, styles))
    doc.build(flow)
    print("✅ CV generated successfully")

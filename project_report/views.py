import base64
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.utils import ImageReader
import json

@csrf_exempt
def generate_project_pdf(request):
    if request.method != "POST":
        return HttpResponse("Only POST allowed", status=405)

    # ===== Parse input data =====
    data = {}
    logo_image = None

    if request.content_type.startswith("multipart/form-data"):
        data_json = request.POST.get("data")
        if not data_json:
            return HttpResponse("No data provided", status=400)
        data = json.loads(data_json)
        logo_file = request.FILES.get("logo")
        if logo_file:
            try:
                logo_bytes = BytesIO(logo_file.read())
                logo_image = ImageReader(logo_bytes)
            except Exception as e:
                return HttpResponse(f"Invalid image file: {str(e)}", status=400)
    else:
        try:
            data = json.loads(request.body)
        except Exception as e:
            return HttpResponse(f"Invalid JSON: {str(e)}", status=400)

    # ===== Create PDF =====
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    PAGE_WIDTH, PAGE_HEIGHT = A4
    MARGIN = 50

    # ===== Logo & University =====
    img_width, img_height = 120, 110
    x = (PAGE_WIDTH - img_width) / 2
    y = PAGE_HEIGHT - MARGIN - img_height - 50

    if logo_image:
        pdf.drawImage(logo_image, x, y, img_width, img_height)

    if "university" in data:
        pdf.setFont("Times-Bold", 12)
        pdf.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 30, data["university"])

    # ===== Content Fields =====
    y = PAGE_HEIGHT - MARGIN - img_height - 20  # logo_y
    y -= 20 
    line_count = 0

    for key, value in data.items():
        if key in ["university", "logo_base64"]:
            continue

        if isinstance(value, (str, int, float)):
            pdf.setFont("Times-Roman", 12)
            y -= 30 if line_count == 0 else 20
            pdf.drawCentredString(PAGE_WIDTH / 2, y, f"{key.replace('_',' ').upper()}: {value}")
            line_count += 1

        elif isinstance(value, list) and all(isinstance(item, dict) for item in value):
            pdf.setFont("Times-Bold", 12)
            pdf.drawCentredString(PAGE_WIDTH / 2, y-20, "GROUP MEMBERS")
            y -= 30

            table_data = [["S/NO", "Reg No", "Name", "Role"]]
            for i, member in enumerate(value, start=1):
                table_data.append([i, member["reg_no"], member["name"], member["role"]])

            table = Table(table_data, colWidths=[30, 100, 200, 120])
            style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)
            table.wrapOn(pdf, PAGE_WIDTH, PAGE_HEIGHT)
            table_height = len(table_data) * 20 + 20
            table.drawOn(pdf, (PAGE_WIDTH - 450) / 2, y - table_height + 20)
            y -= table_height + 20

    # ===== Borders =====
    pdf.rect(MARGIN, MARGIN, PAGE_WIDTH - 2*MARGIN, PAGE_HEIGHT - 2*MARGIN)
    gap = 4
    pdf.setLineWidth(0.5)
    pdf.rect(MARGIN + gap, MARGIN + gap, PAGE_WIDTH - 2*(MARGIN + gap), PAGE_HEIGHT - 2*(MARGIN + gap))

    # ===== Save & Return =====
    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="project_report.pdf"'
    return response

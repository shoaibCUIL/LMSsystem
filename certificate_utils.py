from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io


def generate_certificate(student_name, course_name, completed_at, cert_id):
    buffer = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Background
    c.setFillColor(colors.HexColor('#f9f6f0'))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Border
    c.setStrokeColor(colors.HexColor('#2c3e50'))
    c.setLineWidth(6)
    c.rect(30, 30, w - 60, h - 60, fill=0, stroke=1)
    c.setLineWidth(2)
    c.rect(40, 40, w - 80, h - 80, fill=0, stroke=1)

    # Title
    c.setFillColor(colors.HexColor('#2c3e50'))
    c.setFont('Helvetica-Bold', 36)
    c.drawCentredString(w / 2, h - 130, 'Certificate of Completion')

    # Subtitle
    c.setFont('Helvetica', 18)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(w / 2, h - 175, 'This is to certify that')

    # Student name
    c.setFont('Helvetica-Bold', 42)
    c.setFillColor(colors.HexColor('#1a252f'))
    c.drawCentredString(w / 2, h - 240, student_name)

    # Course text
    c.setFont('Helvetica', 18)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(w / 2, h - 285, 'has successfully completed the course')

    # Course name
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(colors.HexColor('#2980b9'))
    c.drawCentredString(w / 2, h - 330, course_name)

    # Date
    c.setFont('Helvetica', 14)
    c.setFillColor(colors.HexColor('#777777'))
    date_str = completed_at.strftime('%B %d, %Y')
    c.drawCentredString(w / 2, h - 380, f'Completed on: {date_str}')

    # Certificate ID
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#aaaaaa'))
    c.drawCentredString(w / 2, 60, f'Certificate ID: {cert_id}')

    c.save()
    buffer.seek(0)
    return buffer.read()
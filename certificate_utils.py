import io
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import math


def draw_security_guilloche(c, x, y, w, h):
    """Draw subtle guilloche-style security pattern in corners."""
    c.saveState()
    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(0.3)
    c.setFillAlpha(0.15)
    c.setStrokeAlpha(0.25)

    # Corner rosettes
    for cx, cy in [(x + 60, y + 60), (x + w - 60, y + 60),
                   (x + 60, y + h - 60), (x + w - 60, y + h - 60)]:
        for r in range(5, 35, 5):
            c.circle(cx, cy, r, stroke=1, fill=0)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            c.line(cx, cy,
                   cx + 32 * math.cos(rad),
                   cy + 32 * math.sin(rad))

    c.restoreState()


def draw_border(c, w, h):
    """Draw professional multi-layered border."""
    # Outer dark border
    c.setStrokeColor(HexColor('#1a3a5c'))
    c.setLineWidth(8)
    c.rect(20, 20, w - 40, h - 40, fill=0, stroke=1)

    # Gold border
    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(3)
    c.rect(32, 32, w - 64, h - 64, fill=0, stroke=1)

    # Inner thin dark border
    c.setStrokeColor(HexColor('#1a3a5c'))
    c.setLineWidth(1)
    c.rect(38, 38, w - 76, h - 76, fill=0, stroke=1)

    # Corner ornaments
    gold = HexColor('#c8a96e')
    c.setStrokeColor(gold)
    c.setFillColor(gold)
    size = 12
    for cx, cy in [(38, 38), (w - 38, 38), (38, h - 38), (w - 38, h - 38)]:
        c.circle(cx, cy, size / 2, stroke=1, fill=1)

    # Top & bottom decorative lines
    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(1.5)
    mid = w / 2
    for offset in [-120, 120]:
        c.line(mid + offset, h - 95, mid + offset + 60, h - 95)
        c.line(mid + offset, 95, mid + offset + 60, 95)


def draw_seal(c, x, y, radius=38):
    """Draw a circular seal / stamp."""
    c.saveState()
    c.setStrokeColor(HexColor('#1a3a5c'))
    c.setFillColor(HexColor('#1a3a5c'))
    c.setLineWidth(2)
    c.circle(x, y, radius, stroke=1, fill=1)

    c.setStrokeColor(HexColor('#c8a96e'))
    c.setFillColor(HexColor('#c8a96e'))
    c.setLineWidth(1.5)
    c.circle(x, y, radius - 5, stroke=1, fill=0)

    # Star in centre
    c.setFillColor(HexColor('#c8a96e'))
    c.setFont('Helvetica-Bold', 22)
    c.drawCentredString(x, y - 8, '★')

    c.setFont('Helvetica-Bold', 7)
    c.setFillColor(HexColor('#c8a96e'))
    # Curved text around seal (simplified as straight)
    c.drawCentredString(x, y + 14, 'EDULEARN')
    c.drawCentredString(x, y - 22, 'CERTIFIED')
    c.restoreState()


def generate_qr(data, size=90):
    qr = qrcode.QRCode(version=1, box_size=3, border=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1a3a5c', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def generate_certificate(student_name, course_name, completed_at, cert_id):
    buffer = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ── Background ────────────────────────────────────────────
    c.setFillColor(HexColor('#fdfaf4'))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Subtle diagonal line pattern
    c.saveState()
    c.setStrokeColor(HexColor('#e8dfc8'))
    c.setLineWidth(0.4)
    for i in range(-int(h), int(w) + int(h), 18):
        c.line(i, 0, i + h, h)
    c.restoreState()

    # ── Security pattern ──────────────────────────────────────
    draw_security_guilloche(c, 0, 0, w, h)

    # ── Borders ───────────────────────────────────────────────
    draw_border(c, w, h)

    # ── Header: EduLearn branding ─────────────────────────────
    c.setFillColor(HexColor('#1a3a5c'))
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(w / 2, h - 70, 'E D U L E A R N')

    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(1.2)
    c.line(w / 2 - 160, h - 80, w / 2 + 160, h - 80)

    # ── Title ─────────────────────────────────────────────────
    c.setFillColor(HexColor('#1a3a5c'))
    c.setFont('Helvetica-Bold', 40)
    c.drawCentredString(w / 2, h - 135, 'Certificate of Completion')

    # ── Decorative divider ────────────────────────────────────
    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(1)
    c.line(w / 2 - 200, h - 150, w / 2 + 200, h - 150)

    # ── Body text ─────────────────────────────────────────────
    c.setFont('Helvetica', 14)
    c.setFillColor(HexColor('#555555'))
    c.drawCentredString(w / 2, h - 180, 'This is to proudly certify that')

    # ── Student Name ──────────────────────────────────────────
    c.setFont('Helvetica-Bold', 46)
    c.setFillColor(HexColor('#1a3a5c'))
    c.drawCentredString(w / 2, h - 235, student_name)

    # Underline for name
    name_w = c.stringWidth(student_name, 'Helvetica-Bold', 46)
    c.setStrokeColor(HexColor('#c8a96e'))
    c.setLineWidth(1.5)
    c.line(w / 2 - name_w / 2, h - 245, w / 2 + name_w / 2, h - 245)

    # ── Course text ───────────────────────────────────────────
    c.setFont('Helvetica', 15)
    c.setFillColor(HexColor('#555555'))
    c.drawCentredString(w / 2, h - 275, 'has successfully completed the course')

    # ── Course Name ───────────────────────────────────────────
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(HexColor('#c8a96e'))
    c.drawCentredString(w / 2, h - 315, course_name)

    # ── Date ──────────────────────────────────────────────────
    c.setFont('Helvetica', 13)
    c.setFillColor(HexColor('#666666'))
    date_str = completed_at.strftime('%B %d, %Y')
    c.drawCentredString(w / 2, h - 350, f'Date of Completion:  {date_str}')

    # ── Signature section ─────────────────────────────────────
    sig_y = 110
    left_x  = w / 2 - 180
    right_x = w / 2 + 180

    # Signature lines
    c.setStrokeColor(HexColor('#1a3a5c'))
    c.setLineWidth(1)
    c.line(left_x - 70, sig_y, left_x + 70, sig_y)
    c.line(right_x - 70, sig_y, right_x + 70, sig_y)

    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(HexColor('#1a3a5c'))
    c.drawCentredString(left_x, sig_y - 14, 'Muhammad Shoaib Tahir')
    c.drawCentredString(right_x, sig_y - 14, student_name)

    c.setFont('Helvetica', 9)
    c.setFillColor(HexColor('#888888'))
    c.drawCentredString(left_x, sig_y - 26, 'Lead Trainer & Instructor')
    c.drawCentredString(right_x, sig_y - 26, 'Graduate')

    # ── Seal ──────────────────────────────────────────────────
    draw_seal(c, w / 2, sig_y - 5)

    # ── QR Code ───────────────────────────────────────────────
    verify_url = f'https://lmssystem-production.up.railway.app/verify/{cert_id}'
    qr_buf = generate_qr(verify_url)
    from reportlab.lib.utils import ImageReader
    qr_img = ImageReader(qr_buf)
    qr_size = 65
    c.drawImage(qr_img, w - 115, 55, qr_size, qr_size, mask='auto')
    c.setFont('Helvetica', 7)
    c.setFillColor(HexColor('#aaaaaa'))
    c.drawCentredString(w - 82, 50, 'Scan to verify')

    # ── Certificate ID ────────────────────────────────────────
    c.setFont('Helvetica', 8)
    c.setFillColor(HexColor('#aaaaaa'))
    c.drawString(48, 55, f'Certificate ID: {cert_id}')
    c.drawString(48, 44, f'Issued by EduLearn  ·  {date_str}')

    c.save()
    buffer.seek(0)
    return buffer.read()
"""Agrega el enlace del video de demostración al PDF entregable del Taller 3.

    python aux_files/add_video_to_pdf.py <pdf_original> <pdf_salida>

Superpone (sin regenerar el resto del documento) una línea en la portada, la entrada
"7. Video de demostración" en el índice y la sección 7 al final, con enlaces clicables.
"""
import io
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color, black
from reportlab.pdfgen import canvas

VIDEO_URL = "https://youtu.be/01Ss10SWZ38"
PAGE_W, PAGE_H = 612, 792
ACCENT = Color(0.101961, 0.235294, 0.203922)  # color de los títulos del documento
LINK = Color(0.05, 0.3, 0.7)


def y(top, size):
    """Convierte la coordenada 'top' (desde arriba, como la reporta pdfplumber) a línea base."""
    return PAGE_H - top - size * 0.78


def overlay(draw):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    draw(c)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def centered_link(c, text, top, size):
    width = c.stringWidth(text, "Helvetica", size)
    x = (PAGE_W - width) / 2
    c.setFont("Helvetica", size)
    c.setFillColor(LINK)
    c.drawString(x, y(top, size), text)
    c.linkURL(VIDEO_URL, (x, y(top, size) - 2, x + width, y(top, size) + size), relative=0)


def cover(c):
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    c.drawCentredString(PAGE_W / 2, y(421, 11), "Video de demostración:")
    centered_link(c, VIDEO_URL, 433, 11)


def index(c):
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(black)
    c.drawString(64, y(342, 11), "7. Video de demostración")


def last_page(c):
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(ACCENT)
    c.drawString(64, y(370, 13), "7. VIDEO DE DEMOSTRACIÓN")
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(64, y(399, 10), "Recorrido en video por la aplicación y la ejecución de los comandos del taller:")
    c.setFont("Helvetica", 10)
    c.setFillColor(LINK)
    c.drawString(64, y(415, 10), VIDEO_URL)
    w = c.stringWidth(VIDEO_URL, "Helvetica", 10)
    c.linkURL(VIDEO_URL, (64, y(415, 10) - 2, 64 + w, y(415, 10) + 10), relative=0)


def main(src, dst):
    reader = PdfReader(src)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        draw = {0: cover, 1: index, len(reader.pages) - 1: last_page}.get(i)
        if draw:
            page.merge_page(overlay(draw))
        writer.add_page(page)
    with open(dst, "wb") as f:
        writer.write(f)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

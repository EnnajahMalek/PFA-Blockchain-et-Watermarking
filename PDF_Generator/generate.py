import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_landscape_diploma(
    student_name,
    output_path,
    student_id=None,
    program="Computer Science",
    date_str=None,
):
    if date_str is None:
        date_str = datetime.now().strftime("%d/%m/%Y")

    width, height = landscape(A4)

    c = canvas.Canvas(output_path, pagesize=landscape(A4))

    c.setStrokeColorRGB(0.1, 0.1, 0.3)
    c.setLineWidth(3)
    c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)

    c.setStrokeColorRGB(0.4, 0.4, 0.6)
    c.setLineWidth(1)
    c.rect(20 * mm, 20 * mm, width - 40 * mm, height - 40 * mm)

    c.setFont("Helvetica-Bold", 48)
    c.setFillColorRGB(0.1, 0.1, 0.3)
    c.drawCentredString(width / 2, height - 55 * mm, "DIPLÔME")

    c.setFont("Helvetica", 18)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawCentredString(width / 2, height - 80 * mm, "Ceci certifie que")

    c.setFont("Helvetica-BoldOblique", 36)
    c.setFillColorRGB(0, 0, 0.4)
    c.drawCentredString(width / 2, height - 115 * mm, student_name)

    c.setFont("Helvetica", 16)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.drawCentredString(width / 2, height - 145 * mm, f"a complété avec succès le programme {program}")

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawCentredString(width / 2, height - 170 * mm, f"Date : {date_str}")

    if student_id:
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawString(25 * mm, 40 * mm, f"ID Étudiant : {student_id}")

    c.drawRightString(width - 25 * mm, 40 * mm, f"Délivré le : {date_str}")

    c.showPage()
    c.save()
    return output_path


if __name__ == "__main__":
    generate_landscape_diploma(
        "Alice Johnson", "diploma_alice.pdf", student_id="STU-001", program="Computer Science"
    )

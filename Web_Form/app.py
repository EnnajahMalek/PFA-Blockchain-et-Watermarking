import os
import sys
import json
import hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Blockchain.interact import register_hash
from Blockchain.pdf_interact import verify_pdf, strip_images_from_pdf, find_key_case_insensitive
from Embedding.embed import embed_data_in_logo, extract_data_from_logo
from PDF_Generator.generate import generate_landscape_diploma

app = Flask(__name__)
app.secret_key = "projet-final-secret-key"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_STORE = os.path.join(BASE_DIR, "Embedding", "data.json")
LOGO_PATH = os.path.join(BASE_DIR, "Embedding", "logo.png")
STEGO_LOGO_PATH = os.path.join(BASE_DIR, "Embedding", "stego_logo.png")
PDF_DIR = os.path.join(BASE_DIR, "PDF_Generator")


def load_store():
    with open(DATA_STORE) as f:
        return json.load(f)


def save_store(store):
    with open(DATA_STORE, "w") as f:
        json.dump(store, f, indent=2)


@app.route("/")
def index():
    return render_template("issue.html")


def _build_watermark_packet(image_path):
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    import io
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    c.drawImage(image_path, 20 * mm, 20 * mm, width=150, height=150, mask="auto")
    c.save()
    packet.seek(0)
    return packet


def _merge_watermark(base_pdf_path, watermark_packet, output_path):
    from pypdf import PdfReader, PdfWriter
    watermark_page = PdfReader(watermark_packet).pages[0]
    reader = PdfReader(base_pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)


@app.route("/issue", methods=["GET", "POST"])
def issue():
    if request.method == "POST":
        student_name = request.form["student_name"].strip()
        student_id = request.form.get("student_id", "").strip()
        program = request.form.get("program", "Informatique").strip()

        if not student_name:
            flash("Le nom de l'étudiant est requis", "error")
            return render_template("issue.html")

        base_name = student_id or student_name.replace(" ", "_")
        pdf_path = os.path.join(PDF_DIR, f"diploma_{base_name}.pdf")
        final_path = pdf_path.replace(".pdf", "_final.pdf")

        generate_landscape_diploma(
            student_name=student_name,
            output_path=pdf_path,
            student_id=student_id or None,
            program=program,
        )

        salt = os.urandom(32).hex()

        # ---- etape 1 hna kan7sbo lhash sans WATERMARK
        embed_data_in_logo(LOGO_PATH, placeholder_combo, STEGO_LOGO_PATH)

        temp_final = pdf_path.replace(".pdf", "_temp_final.pdf")
        pkt1 = _build_watermark_packet(STEGO_LOGO_PATH)
        _merge_watermark(pdf_path, pkt1, temp_final)

        pdf_hash = hash_pdf_stripped(temp_final)
        os.remove(temp_final)

        hash_combo = hashlib.sha256((pdf_hash + salt).encode()).hexdigest()

        # ---- Pass 2: creation watermakr finale
        embed_data_in_logo(LOGO_PATH, hash_combo, STEGO_LOGO_PATH)
        pkt2 = _build_watermark_packet(STEGO_LOGO_PATH)
        _merge_watermark(pdf_path, pkt2, final_path)

        final_filename = os.path.basename(final_path)
        store = load_store()
        store[student_name] = {"pdf_hash": pdf_hash, "salt": salt, "final_pdf": final_filename}
        save_store(store)

        try:
            tx_hash, block = register_hash(hash_combo)
            flash(f"Diplôme émis et enregistré sur la blockchain. TX : {tx_hash}", "success")
        except Exception as e:
            flash(f"Diplôme généré mais échec de l'enregistrement blockchain : {e}", "warning")

        return redirect(url_for("download_diploma", student_name=student_name))

    return render_template("issue.html")


def hash_pdf_stripped(pdf_path):
    stripped = strip_images_from_pdf(pdf_path)
    with open(stripped, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    os.remove(stripped)
    return h


@app.route("/verify", methods=["GET", "POST"])
def verify():
    result = None
    student_name = ""
    if request.method == "POST":
        student_name = request.form["student_name"].strip()
        pdf_file = request.files.get("pdf_file")

        if not student_name or not pdf_file:
            flash("Le nom de l'étudiant et le fichier PDF sont requis", "error")
            return render_template("verify.html")

        pdf_path = "/tmp/_verify_upload.pdf"
        pdf_file.save(pdf_path)

        result = verify_pdf(pdf_path, student_name, DATA_STORE)
        os.remove(pdf_path)

        if result.get("valid"):
            flash("VÉRIFIÉ : Le diplôme est authentique et enregistré sur la blockchain !", "success")
        else:
            flash("Échec de la vérification", "error")

    return render_template("verify.html", result=result, student_name=student_name)


@app.route("/download/<student_name>")
def download_diploma(student_name):
    store = load_store()
    key = find_key_case_insensitive(store, student_name)
    if key is None:
        flash("Étudiant introuvable dans le registre", "error")
        return redirect(url_for("verify"))
    record = store[key]
    final_pdf = record.get("final_pdf")
    if not final_pdf:
        flash("Aucun fichier de diplôme émis trouvé pour cet étudiant", "error")
        return redirect(url_for("verify"))
    return send_from_directory(PDF_DIR, final_pdf, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

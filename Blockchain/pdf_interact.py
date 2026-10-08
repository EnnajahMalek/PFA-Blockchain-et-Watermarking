import os
import re
import sys
import hashlib
import fitz
import io
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Embedding.embed import extract_data_from_logo
from Blockchain.interact import verify_hash


def extract_logo_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            logo_path = f"/tmp/_extracted_logo_{page_num}_{img_index}.png"
            image.save(logo_path)
            doc.close()
            return logo_path
    doc.close()
    return None


def strip_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            page.delete_image(xref)
        page.clean_contents()
    stripped_path = pdf_path.replace(".pdf", "_noimg.pdf")
    doc.save(stripped_path, garbage=4, deflate=True)
    doc.close()
    with open(stripped_path, 'rb') as f:
        data = f.read()
    data = re.sub(rb'/ID\s*\[<[^>]*>\s*<[^>]*>\]', b'/ID[<00000000000000000000000000000000><00000000000000000000000000000000>]', data)
    with open(stripped_path, 'wb') as f:
        f.write(data)
    return stripped_path


def hash_pdf(pdf_path):
    stripped = strip_images_from_pdf(pdf_path)
    with open(stripped, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    os.remove(stripped)
    return h


def compute_hash_combo(pdf_hash, salt):
    return hashlib.sha256((pdf_hash + salt).encode()).hexdigest()


def find_key_case_insensitive(store, student_name):
    if student_name in store:
        return student_name
    lower = student_name.lower()
    for key in store:
        if key.lower() == lower:
            return key
    return None


def verify_pdf(pdf_path, student_name, data_store_path=None):
    if data_store_path is None:
        data_store_path = os.path.join(
            os.path.dirname(__file__), "..", "Embedding", "data.json"
        )

    import json
    with open(data_store_path) as f:
        store = json.load(f)

    key = find_key_case_insensitive(store, student_name)
    if key is None:
        return {"valid": False, "error": "Student not found in registry"}

    record = store[key]
    salt = record["salt"]

    logo_path = extract_logo_from_pdf(pdf_path)
    if logo_path is None:
        return {"valid": False, "error": "No logo found in PDF"}

    extracted_combo = extract_data_from_logo(logo_path)
    os.remove(logo_path)

    if extracted_combo is None:
        return {"valid": False, "error": "No embedded data found in logo"}

    pdf_hash = hash_pdf(pdf_path)
    expected_combo = compute_hash_combo(pdf_hash, salt)

    integrity_ok = extracted_combo == expected_combo

    exists, timestamp, issuer = verify_hash(extracted_combo)

    return {
        "valid": integrity_ok and exists,
        "integrity_ok": integrity_ok,
        "onchain_exists": exists,
        "extracted_combo": extracted_combo,
        "expected_combo": expected_combo,
        "timestamp": timestamp,
        "issuer": issuer,
    }

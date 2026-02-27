import re
import json
import pdfplumber


def extract_text(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def normalize_text(text):
    # Fix broken decimals like "8 .75" → "8.75"
    text = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text


def extract_biomarkers(pdf_path, json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        biomarker_defs = json.load(f)

    lookup = {}
    for b in biomarker_defs:
        canonical = b["biomarker"]
        lookup[canonical.lower()] = canonical
        for alias in b.get("aliases", []):
            lookup[alias.lower()] = canonical

    raw_text = extract_text(pdf_path)
    text = normalize_text(raw_text)

    results = {}

    for alias, canonical in lookup.items():
        pattern = rf"{re.escape(alias)}.*?(\d+\.\d+|\d+)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = float(match.group(1))

            if 0 < value < 100000:
                results[canonical] = value

    return results
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

from backend.extractor import extract_biomarkers
from backend.comparator import load_benchmarks, compare
from backend.rag import generate_summary
from pathlib import Path
app = FastAPI(title="AI Lab Report Analyzer API")

# Enable CORS (for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



BASE_DIR = Path(__file__).resolve().parent
BENCHMARK_PATH = BASE_DIR / "medical_benchmark.json"


@app.post("/analyze")
async def analyze_report(
    file: UploadFile = File(...),
    patient_name: str = Form("Patient"),
    gender: str = Form("male")
):
    try:
        # Save uploaded file temporarily
        temp_filename = f"temp_{uuid.uuid4()}.pdf"

        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run your existing pipeline
        extracted = extract_biomarkers(temp_filename, BENCHMARK_PATH)

        if not extracted:
            return {"error": "No biomarkers found in PDF"}

        benchmarks = load_benchmarks(BENCHMARK_PATH)
        compared = compare(extracted, benchmarks, gender=gender)

        summary = generate_summary(
            compared,
            benchmarks,
            patient_name=patient_name,
            gender=gender
        )

        # Delete temp file
        os.remove(temp_filename)

        return {
            "biomarkers": compared,
            "summary": summary
        }

    except Exception as e:
        return {"error": str(e)}
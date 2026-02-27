import os
import time
from extractor import extract_biomarkers
from comparator import load_benchmarks, compare, group_by_category
from rag import generate_summary

# ── CONFIG ──────────────────────────────────────────────────────
PDF_PATH       = "C:/Users/konap/OneDrive/Desktop/lab report agent/lab-report-agent/261290000978_Report (1).pdf"
BENCHMARK_PATH = "C:/Users/konap/OneDrive/Desktop/lab report agent/lab-report-agent/medical_benchmark.json"
PATIENT_NAME   = "Saivenkat"
GENDER         = "male"   # "male" or "female"
# ────────────────────────────────────────────────────────────────


def print_results(compared: dict):
    STATUS_ICON = {"normal": "🟢", "low": "🟡", "high": "🔴", "unknown": "⚪"}
    grouped = group_by_category(compared)

    print("\n" + "="*60)
    print("        LAB REPORT — EXTRACTED VALUES")
    print("="*60)

    for category, markers in grouped.items():
        print(f"\n📋 {category}")
        print("-" * 40)
        for name, data in markers.items():
            icon = STATUS_ICON.get(data["status"], "⚪")
            range_str = f"  (ref: {data['range']} {data['unit']})" if data["range"] != "N/A" else ""
            print(f"  {icon}  {name}: {data['value']} {data['unit']}{range_str}")


def main():
    print("🔍 Extracting biomarkers from PDF...")
    extracted = extract_biomarkers(PDF_PATH, BENCHMARK_PATH)

    if not extracted:
        print("❌ No biomarkers found. Check your PDF path or benchmark JSON.")
        return

    print(f"✅ Found {len(extracted)} biomarkers: {list(extracted.keys())}")

    print("\n📊 Comparing against benchmarks...")
    benchmarks = load_benchmarks(BENCHMARK_PATH)
    compared = compare(extracted, benchmarks, gender=GENDER)

    print_results(compared)

    # ── GENERATION & SLEEP ARE NOW SAFELY INSIDE main() ──
    print("\n\n🤖 Generating patient-friendly summary...\n")
    time.sleep(3) # A quick 3-second buffer to keep the API happy
    
    summary = generate_summary(compared, benchmarks, patient_name=PATIENT_NAME, gender=GENDER)

    print("="*60)
    print("        PATIENT SUMMARY")
    print("="*60)
    print(summary)


# ── THIS STAYS EXTREMELY SIMPLE ──
if __name__ == "__main__":
    main()
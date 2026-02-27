import json


def load_benchmarks(json_path):
    with open(json_path) as f:
        return json.load(f)


def compare(extracted: dict, benchmarks: list, gender: str = "male") -> dict:
    """
    Compare extracted biomarker values against reference ranges.
    gender: "male" or "female"
    
    Returns dict like:
    {
        "Haemoglobin": {
            "value": 9.1,
            "unit": "g/dL",
            "status": "low",       # "low", "high", "normal"
            "range": "13.8 - 17.2",
            "category": "Complete Blood Count",
            "plain_english": "...",
            "clinical_meaning": "...",
            "potential_causes": [...],
            "related_markers": [...]
        }
    }
    """
    # Build lookup by canonical name
    benchmark_map = {b["biomarker"]: b for b in benchmarks}

    results = {}

    for name, value in extracted.items():
        if name not in benchmark_map:
            # Still include it, just without benchmark context
            results[name] = {
                "value": value,
                "unit": "",
                "status": "unknown",
                "range": "N/A",
                "category": "Other",
                "plain_english": "",
                "clinical_meaning": "",
                "potential_causes": [],
                "related_markers": []
            }
            continue

        b = benchmark_map[name]
        unit = b.get("unit", "")
        category = b.get("category", "Other")
        plain_english = b.get("plain_english_function", "")

        # Get reference range for gender
        ref = b.get("reference_ranges", {})
        gender_ref = ref.get(gender) or ref.get("general") or {}
        
        min_val = gender_ref.get("min")
        max_val = gender_ref.get("max")

        # Determine status
        if min_val is not None and max_val is not None:
            range_str = f"{min_val} - {max_val}"
            if value < min_val:
                status = "low"
            elif value > max_val:
                status = "high"
            else:
                status = "normal"
        else:
            range_str = "N/A"
            status = "unknown"

        # Pull clinical context
        clinical = b.get("clinical_context", {})
        context = clinical.get(status, {})
        meaning = context.get("meaning", "")
        causes = context.get("potential_causes", [])
        related = context.get("related_markers_to_check", [])

        results[name] = {
            "value": value,
            "unit": unit,
            "status": status,
            "range": range_str,
            "category": category,
            "plain_english": plain_english,
            "clinical_meaning": meaning,
            "potential_causes": causes,
            "related_markers": related
        }

    return results


def group_by_category(compared: dict) -> dict:
    grouped = {}
    for name, data in compared.items():
        cat = data["category"]
        if cat not in grouped:
            grouped[cat] = {}
        grouped[cat][name] = data
    return grouped
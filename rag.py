import json
import os
from google import genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
# Free local embeddings — no API key needed
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def build_vectorstore(benchmarks: list) -> FAISS:
    docs = []
    for b in benchmarks:
        content = f"""
Biomarker: {b['biomarker']}
Category: {b.get('category', '')}
What it does: {b.get('plain_english_function', '')}
Low meaning: {b.get('clinical_context', {}).get('low', {}).get('meaning', '')}
Low causes: {', '.join(b.get('clinical_context', {}).get('low', {}).get('potential_causes', []))}
High meaning: {b.get('clinical_context', {}).get('high', {}).get('meaning', '')}
High causes: {', '.join(b.get('clinical_context', {}).get('high', {}).get('potential_causes', []))}
        """.strip()
        docs.append(Document(page_content=content, metadata={"biomarker": b["biomarker"]}))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    return FAISS.from_documents(split_docs, embeddings)


def retrieve_context(vectorstore: FAISS, abnormal_markers: dict) -> str:
    if not abnormal_markers:
        return ""
    query = "Medical explanation for: " + ", ".join(abnormal_markers.keys())
    docs = vectorstore.similarity_search(query, k=min(len(abnormal_markers) * 2, 10))
    return "\n\n".join([d.page_content for d in docs])


def generate_summary(compared: dict, benchmarks: list, patient_name: str = "the patient", gender: str = "male") -> str:
    vectorstore = build_vectorstore(benchmarks)

    abnormal = {k: v for k, v in compared.items() if v["status"] in ("low", "high")}
    context = retrieve_context(vectorstore, abnormal)

    simplified = {}
    for name, data in compared.items():
        simplified[name] = {
            "value": f"{data['value']} {data['unit']}",
            "status": data["status"],
            "normal_range": data["range"],
            "meaning": data["clinical_meaning"]
        }

    prompt = f"""
You are a compassionate doctor explaining lab results to a patient in simple, clear language.
The patient's name is {patient_name} and they are {gender}.

Here are their lab results with status (normal/low/high):
{json.dumps(simplified, indent=2)}

Here is relevant medical context:
{context}

Write a warm, clear, human-friendly summary following this structure:

1. **Overall Health Snapshot** — 2-3 sentence overview, reassuring tone
2. **What Needs Attention** — Only abnormal values, explained simply. For each: what it is, what the value means, why it might be happening, what to do next.
3. **What Looks Good** — Briefly mention normal values to reassure the patient
4. **Next Steps** — Simple actionable advice

Rules:
- No medical jargon. If you must use a term, explain it immediately.
- Never say "you might have X disease" — say "this could be worth discussing with your doctor"
- Be calm and reassuring. The goal is clarity, not alarm.
- Keep it under 400 words.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
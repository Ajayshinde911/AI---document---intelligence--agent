# extractor.py - QA extraction with regex fallback for emails & phone numbers
from transformers import pipeline
from collections import Counter
import re

# QA model (smaller and fast; change to a stronger model if you want)
_qa = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Default schemas
SCHEMAS = {
    "invoice": ["invoice_number", "date", "total_amount", "currency", "vendor"],
    "bill": ["bill_number", "date", "amount", "provider"],
    "prescription": ["patient_name", "medicine", "dosage", "instructions"],
    "resume": ["name", "email", "phone", "skills", "experience"],
    "id card": ["name", "dob", "id_number", "phone"],
    "contract": ["parties", "start_date", "end_date"],
    "letter": ["sender", "receiver", "date", "subject"],
    "other": ["raw_text"]
}

def _make_question(field: str) -> str:
    """Human-friendly QA question for a field."""
    q_map = {
        "invoice_number": "What is the invoice number?",
        "bill_number": "What is the bill number?",
        "date": "What is the date?",
        "total_amount": "What is the total amount?",
        "amount": "What is the amount?",
        "currency": "What is the currency?",
        "vendor": "Who is the vendor?",
        "provider": "Who is the provider?",
        "patient_name": "What is the patient's name?",
        "medicine": "Which medicine is prescribed?",
        "dosage": "What is the dosage?",
        "instructions": "What are the instructions?",
        "name": "What is the name?",
        "email": "What is the email address?",
        "phone": "What is the phone number?",
        "skills": "List the skills.",
        "experience": "Describe the experience.",
        "dob": "What is the date of birth?",
        "id_number": "What is the ID number?",
        "parties": "Who are the parties?",
        "start_date": "What is the start date?",
        "end_date": "What is the end date?",
        "sender": "Who is the sender?",
        "receiver": "Who is the receiver?",
        "subject": "What is the subject?",
        "raw_text": "Provide the main text."
    }
    return q_map.get(field, f"What is the {field}?")

# Regex helpers
EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
PHONE_REGEXES = [
    re.compile(r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}"),
    re.compile(r"\b\d{10}\b"),  # 10-digit numbers
]

def _extract_via_regex(field: str, text: str):
    """Try to extract email/phone from text using regex as a fallback."""
    if "email" in field.lower():
        m = EMAIL_REGEX.findall(text)
        return m[0] if m else ""
    if "phone" in field.lower() or "contact" in field.lower():
        for rx in PHONE_REGEXES:
            m = rx.findall(text)
            if m:
                # return first match (string)
                return m[0]
    return ""

def _normalize(field: str, value: str) -> str:
    """Small normalization for dates, amounts, phones, emails."""
    if not value:
        return value
    v = value.strip()
    # Normalize email (lowercase)
    if "email" in field.lower():
        return v.lower()
    # Normalize phone: keep digits and leading +
    if "phone" in field.lower():
        # remove spaces, dots, parentheses, hyphens except leading +
        v2 = re.sub(r"[()\s\.\-]", "", v)
        # ensure at least digits left
        digits = re.sub(r"[^\d+]", "", v2)
        return digits
    # Normalize amounts
    if "amount" in field or "total" in field:
        m = re.search(r"[\d,]+(?:\.\d{1,2})?", v.replace(" ", ""))
        if m:
            return m.group(0).replace(",", "")
    # Dates: try common patterns
    m = re.search(r"\d{4}-\d{2}-\d{2}", v)
    if m:
        return m.group(0)
    m2 = re.search(r"\d{2}[-/]\d{2}[-/]\d{4}", v)
    if m2:
        return m2.group(0)
    return v

def extract_fields_for_type(doc_type: str, text: str, custom_fields: list = None, runs: int = 3, qa_threshold: float = 0.35):
    """
    Extract fields with self-consistency and regex fallback for email & phone.
    - runs: number of QA runs for self-consistency
    - qa_threshold: if average QA confidence < threshold, use regex fallback for email/phone
    Returns: dict {field: {"value": ..., "confidence": 0-1}}
    """
    if custom_fields and len(custom_fields) > 0:
        fields = custom_fields
    else:
        fields = SCHEMAS.get(doc_type, SCHEMAS["other"])

    results = {}
    for field in fields:
        q = _make_question(field)
        answers = []
        scores = []
        for _ in range(runs):
            try:
                out = _qa(question=q, context=text)
                ans = out.get("answer", "").strip()
                score = float(out.get("score", 0.0))
            except Exception:
                ans = ""
                score = 0.0
            answers.append(ans)
            scores.append(score)

        # Majority vote (QA)
        most_common = Counter(answers).most_common(1)[0][0] if answers else ""
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # If QA result is empty or below threshold AND field is email/phone, try regex fallback
        if (not most_common or avg_score < qa_threshold) and ("email" in field.lower() or "phone" in field.lower()):
            reg_val = _extract_via_regex(field, text)
            if reg_val:
                # treat regex fallback as decent confidence (0.5) if QA failed
                most_common = reg_val
                avg_score = max(avg_score, 0.5)

        normalized = _normalize(field, most_common)
        results[field] = {"value": normalized if normalized != "" else most_common, "confidence": round(avg_score, 2)}

    return results

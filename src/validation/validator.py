# validator.py - small validation + auto-correction

import re

def validate_and_fix(results: dict) -> dict:
    """
    Run simple checks and fixes:
     - normalize date formats if possible
     - ensure amounts are numeric strings
     - validate email formats
     - leave phone numbers as normalized strings (digits and +)
    """
    fixed = {}
    for k, v in results.items():
        value = v.get("value", "")
        conf = v.get("confidence", 0.0)
        new_val = value

        if isinstance(value, str):
            # date patterns
            m = re.search(r"\d{4}-\d{2}-\d{2}", value)
            if m:
                new_val = m.group(0)
            else:
                m2 = re.search(r"\d{2}[-/]\d{2}[-/]\d{4}", value)
                if m2:
                    new_val = m2.group(0)

            # amount
            if "amount" in k or "total" in k:
                m3 = re.search(r"[\d,]+(?:\.\d{1,2})?", value.replace(" ", ""))
                if m3:
                    new_val = m3.group(0).replace(",", "")

            # email
            if k.lower() == "email":
                m4 = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value)
                if m4:
                    new_val = m4.group(0).lower()

            # phone: ensure normalized digits / leading +
            if "phone" in k.lower():
                new_val = re.sub(r"[^\d+]", "", value)

        fixed[k] = {"value": new_val, "confidence": conf}
    return fixed

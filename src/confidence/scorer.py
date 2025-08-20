# scorer.py - overall confidence and low-confidence flagging

def overall_confidence(results: dict) -> float:
    """Average of all field confidences (value between 0 and 1)."""
    if not results:
        return 0.0
    vals = [v.get("confidence", 0.0) for v in results.values()]
    return round(sum(vals) / len(vals), 2)

def flag_low_confidence(results: dict, threshold: float = 0.6) -> dict:
    """Mark fields where confidence < threshold with flag True."""
    out = {}
    for k, v in results.items():
        val = v.get("value")
        conf = v.get("confidence", 0.0)
        out[k] = {"value": val, "confidence": conf, "flag": conf < threshold}
    return out

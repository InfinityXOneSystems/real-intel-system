"""Rule-based production scorer for lead records.

Provides a deterministic, explainable scoring function as a safe
production-ready fallback when an LLM scorer isn't available.

API:
- score_record(record) -> dict with 'score' (float 0..1) and 'explanation' (str)
- score_records(records) -> list of dicts
"""
from typing import Dict, List, Tuple


KEYWORD_BOOST = [
    "foreclosure",
    "pre-foreclosure",
    "auction",
    "bankruptcy",
    "tax lien",
    "vacant",
    "delinquent",
    "behind on payments",
]


def _text_score(text: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    score = 0.0
    for kw in KEYWORD_BOOST:
        if kw in t:
            score += 0.15
    # cap contribution
    return min(score, 0.6)


def _numeric_ratio(a: float, b: float) -> float:
    try:
        a_f = float(a or 0)
        b_f = float(b or 0)
        if b_f <= 0:
            return 0.0
        return max(0.0, min(1.0, a_f / b_f))
    except Exception:
        return 0.0


def score_record(record: Dict) -> Dict:
    """Score a single lead record using simple heuristics.

    Expected fields (optional):
    - estimated_value (float)
    - mortgage_balance (float)
    - days_delinquent (int)
    - vacant (bool)
    - description / notes (str)
    - tags (list or comma-separated str)

    Returns dict: { 'score': float, 'explanation': str }
    """
    base = 0.3

    desc = record.get("description") or record.get("notes") or ""
    text_boost = _text_score(desc)
    base += text_boost

    # Tags
    tags = record.get("tags") or record.get("keywords") or ""
    if isinstance(tags, (list, tuple)):
        tags_text = " ".join([str(t) for t in tags])
    else:
        tags_text = str(tags)
    base += _text_score(tags_text) * 0.5

    # Balance ratio: mortgage_balance / estimated_value
    est = record.get("estimated_value") or record.get("est_value")
    mort = record.get("mortgage_balance") or record.get("mortgage")
    bal_ratio = _numeric_ratio(mort, est)
    # higher balance ratio -> more likely distressed
    base += bal_ratio * 0.25

    # Days delinquent
    days = 0
    try:
        days = int(record.get("days_delinquent") or record.get("daysDelinquent") or 0)
    except Exception:
        days = 0
    if days >= 90:
        base += 0.25
    elif days >= 30:
        base += 0.12
    elif days > 0:
        base += 0.05

    # Vacant property
    vac = record.get("vacant")
    if isinstance(vac, str):
        vac = vac.lower() in ("true", "yes", "1")
    if vac:
        base += 0.18

    # Normalize to 0..1
    score = float(max(0.0, min(1.0, base)))

    explanation = (
        f"text_boost={text_boost:.2f}, tags_text='{tags_text}', bal_ratio={bal_ratio:.2f}, "
        f"days={days}, vacant={bool(vac)}"
    )

    return {"score": round(score, 4), "explanation": explanation}


def score_records(records: List[Dict]) -> List[Dict]:
    return [score_record(r) for r in records]

from services.real_estate_intelligence.autonomous.production_scorer import (
    score_record, score_records)


def test_score_simple_keywords():
    r = {"description": "Property in foreclosure and vacant"}
    out = score_record(r)
    assert isinstance(out["score"], float)
    assert out["score"] > 0.4


def test_score_balance_and_days():
    r = {"estimated_value": 200000, "mortgage_balance": 180000, "days_delinquent": 120}
    out = score_record(r)
    assert out["score"] >= 0.8 or out["score"] <= 1.0


def test_score_records_list():
    records = [
        {"description": "default"},
        {"description": "auction and tax lien", "vacant": True},
    ]
    res = score_records(records)
    assert len(res) == 2
    assert res[1]["score"] > res[0]["score"]

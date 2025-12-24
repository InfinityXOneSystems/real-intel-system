from services.real_estate_intelligence.autonomous.telephony_adapter import \
    make_call_safe


def test_make_call_dryrun():
    res = make_call_safe("+17722090266", from_number=None, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True

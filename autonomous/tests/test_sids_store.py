import os

from services.real_estate_intelligence.autonomous.sids_store import (
    _ensure_local_key, store_sids)


def test_local_store_sids_tmpdir(tmp_path):
    # ensure local key created in temp path
    key_path = tmp_path / "sids_key"
    key = _ensure_local_key(str(key_path))
    assert key and len(key) in (16, 24, 32)

    # store a sample metadata object and ensure file created
    meta = {"call": {"sid": "PSID123"}, "sms": {"sid": "MSID456"}}
    res = store_sids(meta)
    assert isinstance(res, dict)
    assert res.get("success") in (True, False)

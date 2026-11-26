import json

import pytest

from champions_path.features import load_form_snapshot


def test_form_snapshot_requires_uniform_team_coverage(tmp_path):
    path = tmp_path / "form.json"
    path.write_text(
        json.dumps(
            {
                "provider": "fixture",
                "as_of": "2026-11-23",
                "teams": {
                    "A": {"domestic_elo_delta": 20, "xg_difference_per_90": 0.4, "matches": 8}
                },
            }
        ),
        encoding="utf-8",
    )
    snapshot = load_form_snapshot(path, {"A"})
    assert snapshot.teams["A"].rating_adjustment > 0
    with pytest.raises(ValueError, match="coverage mismatch"):
        load_form_snapshot(path, {"A", "B"})

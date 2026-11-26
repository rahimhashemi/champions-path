import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class TeamFormFeature:
    domestic_elo_delta: float
    xg_difference_per_90: float
    matches: int

    @property
    def rating_adjustment(self) -> float:
        reliability = self.matches / (self.matches + 8)
        raw = 0.55 * self.domestic_elo_delta + 45 * self.xg_difference_per_90
        return float(np.clip(reliability * raw, -90, 90))


@dataclass(frozen=True, slots=True)
class FormSnapshot:
    provider: str
    as_of: str
    teams: dict[str, TeamFormFeature]


def load_form_snapshot(path: Path, expected_teams: set[str]) -> FormSnapshot:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_teams = payload.get("teams", {})
    actual_teams = set(raw_teams)
    if actual_teams != expected_teams:
        missing = sorted(expected_teams - actual_teams)
        extra = sorted(actual_teams - expected_teams)
        raise ValueError(f"Form snapshot team coverage mismatch; missing={missing}, extra={extra}")
    teams = {
        team: TeamFormFeature(
            domestic_elo_delta=float(values["domestic_elo_delta"]),
            xg_difference_per_90=float(values["xg_difference_per_90"]),
            matches=int(values["matches"]),
        )
        for team, values in raw_teams.items()
    }
    if not payload.get("provider") or not payload.get("as_of"):
        raise ValueError("Form snapshot requires provider and as_of provenance fields")
    return FormSnapshot(str(payload["provider"]), str(payload["as_of"]), teams)

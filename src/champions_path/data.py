import re
from pathlib import Path

from champions_path.domain import HistoricalMatch


STAGE_PATTERN = re.compile(r"^▪ League, Matchday (\d+)$")
MATCH_PATTERN = re.compile(
    r"^(?:\d{2}:\d{2}\s+)?(.+?)\s+\([A-Z]{3}\)\s+v\s+"
    r"(.+?)\s+\([A-Z]{3}\)\s+(\d+)-(\d+)(?:\s|$)"
)


def parse_openfootball_league_phase(path: Path, season: str) -> list[HistoricalMatch]:
    matches: list[HistoricalMatch] = []
    matchday: int | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        stage_match = STAGE_PATTERN.match(line)
        if stage_match:
            matchday = int(stage_match.group(1))
            continue
        if line.startswith("▪ ") and not line.startswith("▪ League,"):
            matchday = None
            continue
        if matchday is None:
            continue

        result = MATCH_PATTERN.match(line)
        if result:
            matches.append(
                HistoricalMatch(
                    season=season,
                    matchday=matchday,
                    home=result.group(1).strip(),
                    away=result.group(2).strip(),
                    home_goals=int(result.group(3)),
                    away_goals=int(result.group(4)),
                )
            )

    return matches


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_historical_season(season: str) -> list[HistoricalMatch]:
    path = project_root() / "data" / "historical" / f"{season}-cl.txt"
    matches = parse_openfootball_league_phase(path, season)
    if len(matches) != 144:
        raise ValueError(f"Expected 144 league-phase matches for {season}, found {len(matches)}")
    return matches

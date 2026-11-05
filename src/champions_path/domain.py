from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HistoricalMatch:
    season: str
    matchday: int
    home: str
    away: str
    home_goals: int
    away_goals: int

    @property
    def outcome(self) -> int:
        if self.home_goals > self.away_goals:
            return 0
        if self.home_goals == self.away_goals:
            return 1
        return 2

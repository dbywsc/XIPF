"""Core data models for ICPC contest tracking."""

from dataclasses import dataclass, field
from collections import Counter


@dataclass
class Problem:
    alias: str
    accepted: int
    submitted: int


@dataclass
class ProblemStatus:
    """A team's result on a single problem."""
    alias: str
    result: str  # "AC", "WA", "TLE", etc.
    time: int  # seconds
    tries: int


@dataclass
class TeamMember:
    """A contestant's participation in a specific team."""
    name: str
    gender: str  # "male", "female", or ""


@dataclass
class Team:
    """A team in a specific contest."""
    id: str
    name: str
    organization: str
    official: bool
    solved: int
    penalty: int  # seconds
    problems: list[ProblemStatus] = field(default_factory=list)
    members: list[TeamMember] = field(default_factory=list)
    rank: int = 0
    girl_team: bool = False
    medal: str = ""  # "gold", "silver", "bronze", or ""
    champion: str = ""  # "冠军", "亚军", "季军", or ""


@dataclass
class Contest:
    """A single contest."""
    id: str
    title: str
    date: str
    duration: int  # seconds
    frozen_duration: int  # seconds
    problems: list[Problem] = field(default_factory=list)
    teams: list[Team] = field(default_factory=list)
    gold_count: int = 0
    silver_count: int = 0
    bronze_count: int = 0


@dataclass
class ContestRecord:
    """A contestant's record in one contest."""
    contest_id: str
    contest_title: str
    date: str
    team_name: str
    rank: int
    medal: str
    champion: str = ""  # "冠军", "亚军", "季军", or ""
    solved: int = 0
    penalty: int = 0


@dataclass
class Contestant:
    """A real person, tracked across contests."""
    id: str
    name: str
    gender: str
    organization: str  # primary org (most recent or most frequent)
    records: list[ContestRecord] = field(default_factory=list)

    @property
    def medal_summary(self) -> dict:
        c = Counter(r.medal for r in self.records if r.medal)
        cc = Counter(r.champion for r in self.records if r.champion)
        return {
            "champion": cc.get("冠军", 0), "runner_up": cc.get("亚军", 0), "third": cc.get("季军", 0),
            "gold": c["gold"], "silver": c["silver"], "bronze": c["bronze"],
        }


@dataclass
class Organization:
    """A school/university."""
    id: str
    canonical: str
    aliases: list[str] = field(default_factory=list)
    province: str = ""
    city: str = ""
    contest_stats: dict = field(default_factory=lambda: {"gold": 0, "silver": 0, "bronze": 0, "count": 0})

    def add_medal(self, medal: str):
        if medal:
            self.contest_stats[medal] += 1
        self.contest_stats["count"] += 1

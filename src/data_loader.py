"""
Data loader for F1 History AI Chatbot.

Downloads and caches historical F1 data from Jolpica-F1 API and FastF1.
Falls back to bundled local data when offline or when API calls fail.

Seasons covered: 2021-2025 (plus forward-compatible 2026 stub).
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Local fallback data lives in data/local/
LOCAL_DATA_DIR = BASE_DIR / "data" / "local"
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Seasons this project covers.  2026 is a placeholder ready for future data.
SUPPORTED_SEASONS: list[int] = [2021, 2022, 2023, 2024, 2025]
FUTURE_SEASON = 2026

# Jolpica-F1 is a free, no-key F1 REST API.
JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"

# Cache expiry for API calls (seconds).
CACHE_TTL = 86400  # 24 hours


def season_dir(season: int) -> Path:
    return LOCAL_DATA_DIR / str(season)


def season_dir_exist(season: int) -> bool:
    d = season_dir(season)
    return d.exists()


def _url_for(path: str) -> str:
    return f"{JOLPICA_BASE}/{path}"


def _cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> Path:
    return CACHE_DIR / f"{_cache_key(url)}.json"


def _read_cache(path: Path, ttl: int = CACHE_TTL) -> dict | None:
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def get_json(url: str, *, ttl: int = CACHE_TTL, timeout: int = 15) -> dict | None:
    """Fetch JSON from an API URL with disk caching.

    Returns None on network failure or non-200 status so the caller can
    fall back to local data gracefully.
    """
    cached = _read_cache(_cache_path(url), ttl=ttl)
    if cached is not None:
        return cached

    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "f1-history-chatbot/1.0"})
        if resp.status_code != 200:
            return None
        data = resp.json()
        _write_cache(_cache_path(url), data)
        return data
    except (requests.RequestException, ValueError):
        # Network failure or invalid JSON — return None so a fallback is used.
        return None


def clear_cache() -> None:
    """Remove every cached API file (used by tests)."""
    for child in CACHE_DIR.glob("*.json"):
        child.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Local data fallback
# ---------------------------------------------------------------------------

def _load_local(season: int, name: str) -> list[dict]:
    """Load a bundled JSON list from data/local/<season>/<name>.json."""
    file = season_dir(season) / f"{name}.json"
    if not file.exists():
        return []
    try:
        with open(file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, OSError):
        return []


# ---------------------------------------------------------------------------
# High-level data fetchers
# ---------------------------------------------------------------------------

def fetch_season_race_schedule(season: int) -> list[dict]:
    """Return the race schedule for a season.

    Each entry: {round, race_name, date, circuit, location}
    """
    races_json = get_json(_url_for(f"{season}/races.json"))
    if races_json:
        out = []
        for r in races_json.get("MRData", {}).get("RaceTable", {}).get("Races", []):
            out.append({
                "round": int(r.get("round", 0)),
                "race_name": r.get("raceName", ""),
                "date": r.get("date", ""),
                "circuit": r.get("Circuit", {}).get("circuitName", ""),
                "location": r.get("Circuit", {}).get("Location", {}).get("locality", ""),
            })
        return out
    # Fallback to local data
    return _load_local(season, "schedule")


@functools.lru_cache(maxsize=64)
def fetch_driver_standings(season: int) -> list[dict]:
    """Championship driver standings at end of a season."""
    url = _url_for(f"{season}/driverstandings.json")
    data = get_json(url)
    if data:
        standings = (
            data.get("MRData", {})
            .get("StandingsTable", {})
            .get("StandingsLists", [{}])[0]
            .get("DriverStandings", [])
        )
        out = []
        for s in standings:
            out.append({
                "position": int(s.get("position", 0)),
                "points": float(s.get("points", 0)),
                "driver": f"{s.get('Driver', {}).get('givenName', '')} {s.get('Driver', {}).get('familyName', '')}",
                "team": s.get("Constructors", [{}])[0].get("name", ""),
                "nationality": s.get("Driver", {}).get("nationality", ""),
                "wins": int(s.get("wins", 0)),
            })
        return out
    return _load_local(season, "driver_standings")


@functools.lru_cache(maxsize=64)
def fetch_constructor_standings(season: int) -> list[dict]:
    """Championship constructor standings at end of a season."""
    url = _url_for(f"{season}/constructorstandings.json")
    data = get_json(url)
    if data:
        standings = (
            data.get("MRData", {})
            .get("StandingsTable", {})
            .get("StandingsLists", [{}])[0]
            .get("ConstructorStandings", [])
        )
        out = []
        for s in standings:
            out.append({
                "position": int(s.get("position", 0)),
                "points": float(s.get("points", 0)),
                "team": s.get("Constructor", {}).get("name", ""),
                "nationality": s.get("Constructor", {}).get("nationality", ""),
                "wins": int(s.get("wins", 0)),
            })
        return out
    return _load_local(season, "constructor_standings")


@functools.lru_cache(maxsize=128)
def fetch_race_results(season: int, round_num: int | None = None) -> list[dict]:
    """Race finish results (not qualifying).

    If round_num is None, returns results for all races that season.
    """
    if round_num is not None:
        url = _url_for(f"{season}/{round_num}/results.json")
    else:
        # Paginate to get all season race results (API max 100 per page)
        all_results = []
        offset = 0
        while True:
            url = _url_for(f"{season}/results.json?limit=100&offset={offset}")
            data = get_json(url)
            if not data:
                break
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
            for race in races:
                for r in race.get("Results", []):
                    all_results.append({
                        "season": season,
                        "round": int(race.get("round", 0)),
                        "race_name": race.get("raceName", ""),
                        "date": race.get("date", ""),
                        "position": int(r.get("position", 0)),
                        "driver": f"{r.get('Driver', {}).get('givenName', '')} {r.get('Driver', {}).get('familyName', '')}",
                        "team": r.get("Constructor", {}).get("name", ""),
                        "points": float(r.get("points", 0)),
                        "status": r.get("status", ""),
                    })
            total = int(data.get("MRData", {}).get("total", 0))
            offset += 100
            if len(races) == 0 or offset >= total:
                break
        return all_results
    data = get_json(url)
    if data:
        out = []
        race_table = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        for race in race_table:
            rr = race.get("Results", [])
            for r in rr:
                out.append({
                    "season": season,
                    "round": int(race.get("round", 0)),
                    "race_name": race.get("raceName", ""),
                    "date": race.get("date", ""),
                    "position": int(r.get("position", 0)),
                    "driver": f"{r.get('Driver', {}).get('givenName', '')} {r.get('Driver', {}).get('familyName', '')}",
                    "team": r.get("Constructor", {}).get("name", ""),
                    "points": float(r.get("points", 0)),
                    "status": r.get("status", ""),
                })
        return out
    # Fallback
    name = f"race_results_r{round_num}" if round_num else "race_results"
    return _load_local(season, name)


@functools.lru_cache(maxsize=128)
def fetch_qualifying_results(season: int, round_num: int | None = None) -> list[dict]:
    """Qualifying results."""
    if round_num is not None:
        url = _url_for(f"{season}/{round_num}/qualifying.json")
    else:
        url = _url_for(f"{season}/qualifying.json?limit=500")
    data = get_json(url)
    if data:
        out = []
        race_table = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        for race in race_table:
            for q in race.get("QualifyingResults", []):
                out.append({
                    "season": season,
                    "round": int(race.get("round", 0)),
                    "race_name": race.get("raceName", ""),
                    "date": race.get("date", ""),
                    "position": int(q.get("position", 0)),
                    "driver": f"{q.get('Driver', {}).get('givenName', '')} {q.get('Driver', {}).get('familyName', '')}",
                    "team": q.get("Constructor", {}).get("name", ""),
                    "q1": q.get("Q1", ""),
                    "q2": q.get("Q2", ""),
                    "q3": q.get("Q3", ""),
                })
        return out
    name = f"qualifying_r{round_num}" if round_num else "qualifying"
    return _load_local(season, name)


@functools.lru_cache(maxsize=64)
def fetch_sprint_results(season: int) -> list[dict]:
    """Sprint race results for a season (2021+)."""
    url = _url_for(f"{season}/sprint.json")
    data = get_json(url)
    out = []
    if data:
        race_table = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        for race in race_table:
            for r in race.get("SprintResults", []):
                out.append({
                    "season": season,
                    "round": int(race.get("round", 0)),
                    "race_name": race.get("raceName", ""),
                    "position": int(r.get("position", 0)),
                    "driver": f"{r.get('Driver', {}).get('givenName', '')} {r.get('Driver', {}).get('familyName', '')}",
                    "team": r.get("Constructor", {}).get("name", ""),
                    "points": float(r.get("points", 0)),
                    "status": r.get("status", ""),
                })
        return out
    return _load_local(season, "sprint_results")


@functools.lru_cache(maxsize=128)
def fetch_pole_positions(season: int) -> list[dict]:
    """Pole position (qualifying winner) per race."""
    qual = fetch_qualifying_results(season)
    poles = []
    seen_rounds: set[int] = set()
    for q in qual:
        rnd = q["round"]
        if rnd in seen_rounds:
            continue
        seen_rounds.add(rnd)
        poles.append({
            "season": season,
            "round": rnd,
            "race_name": q["race_name"],
            "date": q["date"],
            "driver": q["driver"],
            "team": q["team"],
        })
    return poles


# ---------------------------------------------------------------------------
# Download / cache seeding
# ---------------------------------------------------------------------------

def download_season(season: int) -> dict:
    """Pre-fetch and cache all data for a season. Returns a summary dict."""
    if season not in SUPPORTED_SEASONS + [FUTURE_SEASON]:
        raise ValueError(f"Season {season} not supported. Use {SUPPORTED_SEASONS + [FUTURE_SEASON]}")

    summary = {"season": season, "sources": [], "errors": []}

    fetchers: list[tuple[str, Any]] = [
        ("schedule", lambda: fetch_season_race_schedule(season)),
        ("driver_standings", lambda: fetch_driver_standings(season)),
        ("constructor_standings", lambda: fetch_constructor_standings(season)),
        ("race_results", lambda: fetch_race_results(season)),
        ("qualifying", lambda: fetch_qualifying_results(season)),
        ("sprint_results", lambda: fetch_sprint_results(season)),
        ("pole_positions", lambda: fetch_pole_positions(season)),
    ]
    for name, fn in fetchers:
        try:
            data = fn()
            n = len(data) if isinstance(data, list) else len(str(data))
            summary["sources"].append(f"{name}:{n}")
        except Exception as exc:  # noqa: BLE001 - broad catch for download resilience
            summary["errors"].append(f"{name}:{exc}")

    summary["timestamp"] = datetime.utcnow().isoformat()
    return summary


def download_all_seasons(seasons: list[int] | None = None) -> dict:
    """Download all supported seasons into cache."""
    if seasons is None:
        seasons = SUPPORTED_SEASONS
    results: dict[int, dict] = {}
    for s in seasons:
        results[s] = download_season(s)
    return {"summary": results}


# ---------------------------------------------------------------------------
# FastF1 integration (optional - telemetry/timing when available)
# ---------------------------------------------------------------------------

def fastf1_available() -> bool:
    """Check whether the fastf1 package is installed."""
    try:
        import importlib
        importlib.import_module("fastf1")
        return True
    except ImportError:
        return False


def fetch_fastf1_session(season: int, round_num: int, session_type: str = "Race"):
    """Fetch a FastF1 session. Returns None if fastf1 is unavailable or fetch fails.

    session_type: Race, Qualifying, Sprint, FP1, FP2, FP3
    """
    if not fastf1_available():
        return None
    try:
        import fastf1
        from fastf1 import utils  # noqa: F401
        fastf1.cache.Cache.enable_cache(str(CACHE_DIR / "fastf1"))
        race = fastf1.get_race_weekend(season, round_num, force=True)
        if session_type.lower() == "race":
            sess = race.race
        elif session_type.lower() == "qualifying":
            sess = race.qualifying
        elif session_type.lower() == "sprint":
            sess = race.sprint
        else:
            sess = getattr(race, session_type.lower(), race.race)
        sess.load()
        return sess
    except Exception:
        return None


if __name__ == "__main__":
    print(download_all_seasons())

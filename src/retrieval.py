"""
Retrieval layer — queries historical F1 data from cache/API.
Maps natural-language concepts to data lookups.
"""

from src.data_loader import (
    fetch_race_results,
    fetch_qualifying_results,
    fetch_sprint_results,
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_season_race_schedule,
    fetch_pole_positions,
    SUPPORTED_SEASONS,
)


def get_race_winners(season: int) -> list[dict]:
    results = fetch_race_results(season)
    winners = {}
    for r in results:
        if r["position"] == 1:
            winners[r["round"]] = r
    return sorted(winners.values(), key=lambda w: w["round"])


def get_champion(season: int, category: str = "drivers") -> dict | None:
    if category == "drivers":
        standings = fetch_driver_standings(season)
    else:
        standings = fetch_constructor_standings(season)
    if standings and standings[0]["position"] == 1:
        return standings[0]
    return None


def find_driver(season: int, name_fragment: str) -> list[dict]:
    fragment = name_fragment.lower()
    races = fetch_race_results(season)
    found = []
    for r in races:
        if fragment in r["driver"].lower():
            found.append(r)
    return found


def get_season_summary(season: int) -> dict:
    return {
        "season": season,
        "champion": get_champion(season, "drivers"),
        "constructor_champion": get_champion(season, "constructors"),
        "scheduled_races": len(fetch_season_race_schedule(season)),
        "pole_positions": len(fetch_pole_positions(season)),
    }

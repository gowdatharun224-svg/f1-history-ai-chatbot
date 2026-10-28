"""Tests for data retrieval cases fixed in this session."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data_loader import fetch_driver_standings, fetch_constructor_standings, fetch_race_results, fetch_season_race_schedule, clear_cache

def test_2021_champion_max_verstappen():
    clear_cache()
    standings = fetch_driver_standings(2021)
    assert standings[0]["driver"] == "Max Verstappen"
    assert standings[0]["position"] == 1

def test_2023_champion_max_verstappen():
    clear_cache()
    standings = fetch_driver_standings(2023)
    assert standings[0]["driver"] == "Max Verstappen"

def test_2023_constructor_red_bull():
    clear_cache()
    cons = fetch_constructor_standings(2023)
    assert cons[0]["team"] == "Red Bull"

def test_2024_monaco_winner():
    clear_cache()
    results = fetch_race_results(2024, 8)
    winner = [r for r in results if r["position"] == 1]
    assert len(winner) == 1
    assert winner[0]["driver"] == "Charles Leclerc"

def test_2021_schedule_available():
    clear_cache()
    sched = fetch_season_race_schedule(2021)
    assert len(sched) == 22

def test_2024_schedule_available():
    clear_cache()
    sched = fetch_season_race_schedule(2024)
    assert len(sched) > 0

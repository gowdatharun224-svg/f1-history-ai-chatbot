#!/usr/bin/env python
"""Seed local fallback data files for offline operation."""
import json
from pathlib import Path

base = Path("data/local")
seasons = [2021, 2022, 2023, 2024, 2025]

minimal_data = {
    "2021": {
        "driver_standings": [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 395, "nationality": "Dutch", "wins": 15},
            {"position": 2, "driver": "Lewis Hamilton", "team": "Mercedes", "points": 387, "nationality": "British", "wins": 8},
        ],
        "constructor_standings": [
            {"position": 1, "team": "Mercedes", "points": 613, "nationality": "German", "wins": 9},
            {"position": 2, "team": "Red Bull Racing", "points": 585, "nationality": "Austrian", "wins": 16},
        ],
        "schedule": [
            {"round": 1, "race_name": "Bahrain Grand Prix", "date": "2021-03-28", "circuit": "Bahrain International Circuit", "location": "Sakhir"},
            {"round": 2, "race_name": "Emilia Romagna Grand Prix", "date": "2021-04-18", "circuit": "Imola Circuit", "location": "Imola"},
            {"round": 22, "race_name": "Abu Dhabi Grand Prix", "date": "2021-12-12", "circuit": "Yas Marina Circuit", "location": "Abu Dhabi"},
        ],
        "race_results": [
            {"season": 2021, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2021-03-28", "position": 1, "driver": "Lewis Hamilton", "team": "Mercedes", "points": 25, "status": "Finished"},
            {"season": 2021, "round": 22, "race_name": "Abu Dhabi Grand Prix", "date": "2021-12-12", "position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 25, "status": "Finished"},
        ],
        "qualifying": [
            {"season": 2021, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2021-03-28", "position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "q1": "1:29.795", "q2": "1:29.275", "q3": "1:28.997"},
        ],
        "sprint_results": [],
        "pole_positions": [{"season": 2021, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2021-03-28", "driver": "Max Verstappen", "team": "Red Bull Racing"}],
    },
    "2022": {
        "driver_standings": [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 454, "nationality": "Dutch", "wins": 15},
            {"position": 2, "driver": "Charles Leclerc", "team": "Ferrari", "points": 308, "nationality": "Monegasque", "wins": 3},
        ],
        "constructor_standings": [
            {"position": 1, "team": "Red Bull Racing", "points": 759, "nationality": "Austrian", "wins": 17},
            {"position": 2, "team": "Ferrari", "points": 554, "nationality": "Italian", "wins": 4},
        ],
        "schedule": [
            {"round": 1, "race_name": "Bahrain Grand Prix", "date": "2022-03-20", "circuit": "Bahrain International Circuit", "location": "Sakhir"},
            {"round": 22, "race_name": "Abu Dhabi Grand Prix", "date": "2022-11-20", "circuit": "Yas Marina Circuit", "location": "Abu Dhabi"},
        ],
        "race_results": [
            {"season": 2022, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2022-03-20", "position": 1, "driver": "Charles Leclerc", "team": "Ferrari", "points": 25, "status": "Finished"},
        ],
        "qualifying": [],
        "sprint_results": [],
        "pole_positions": [],
    },
    "2023": {
        "driver_standings": [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 575, "nationality": "Dutch", "wins": 19},
            {"position": 2, "driver": "Sergio Perez", "team": "Red Bull Racing", "points": 285, "nationality": "Mexican", "wins": 2},
        ],
        "constructor_standings": [
            {"position": 1, "team": "Red Bull Racing", "points": 860, "nationality": "Austrian", "wins": 21},
            {"position": 2, "team": "Mercedes", "points": 409, "nationality": "German", "wins": 0},
        ],
        "schedule": [
            {"round": 1, "race_name": "Bahrain Grand Prix", "date": "2023-03-05", "circuit": "Bahrain International Circuit", "location": "Sakhir"},
        ],
        "race_results": [
            {"season": 2023, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2023-03-05", "position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 25, "status": "Finished"},
        ],
        "qualifying": [],
        "sprint_results": [],
        "pole_positions": [],
    },
    "2024": {
        "driver_standings": [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 437, "nationality": "Dutch", "wins": 9},
            {"position": 2, "driver": "Lando Norris", "team": "McLaren", "points": 374, "nationality": "British", "wins": 4},
        ],
        "constructor_standings": [
            {"position": 1, "team": "McLaren", "points": 666, "nationality": "British", "wins": 6},
            {"position": 2, "team": "Red Bull Racing", "points": 581, "nationality": "Austrian", "wins": 9},
        ],
        "schedule": [
            {"round": 1, "race_name": "Bahrain Grand Prix", "date": "2024-03-02", "circuit": "Bahrain International Circuit", "location": "Sakhir"},
        ],
        "race_results": [
            {"season": 2024, "round": 1, "race_name": "Bahrain Grand Prix", "date": "2024-03-02", "position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 25, "status": "Finished"},
        ],
        "qualifying": [],
        "sprint_results": [],
        "pole_positions": [],
    },
    "2025": {
        "driver_standings": [
            {"position": 1, "driver": "Max Verstappen", "team": "Red Bull Racing", "points": 0, "nationality": "Dutch", "wins": 0},
        ],
        "constructor_standings": [
            {"position": 1, "team": "Red Bull Racing", "points": 0, "nationality": "Austrian", "wins": 0},
        ],
        "schedule": [
            {"round": 1, "race_name": "Australian Grand Prix", "date": "2025-03-16", "circuit": "Albert Park Circuit", "location": "Melbourne"},
        ],
        "race_results": [],
        "qualifying": [],
        "sprint_results": [],
        "pole_positions": [],
    },
}

for season_str, data in minimal_data.items():
    for key, value in data.items():
        file = base / season_str / f"{key}.json"
        file.write_text(json.dumps(value, indent=2))
        print(f"Created {file}")
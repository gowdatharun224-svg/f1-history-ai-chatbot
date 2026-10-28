"""
Tests for retrieval layer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from retrieval import (
    get_race_winners,
    get_champion,
    find_driver,
    get_season_summary,
)


def test_retrieval_race_winners_2021():
    winners = get_race_winners(2021)
    assert isinstance(winners, list)
    assert len(winners) > 0
    assert winners[0]["position"] == 1


def test_retrieval_champion_2021():
    champ = get_champion(2021, "drivers")
    assert champ is not None
    assert champ["position"] == 1


def test_retrieval_find_driver():
    results = find_driver(2021, "Verstappen")
    assert isinstance(results, list)


def test_retrieval_summary():
    summary = get_season_summary(2021)
    assert summary["season"] == 2021
    assert summary["champion"] is not None

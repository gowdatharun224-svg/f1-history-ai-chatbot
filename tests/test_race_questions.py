"""Tests for race-specific question retrieval."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from chatbot import F1Chatbot, chatbot_answer

def _run(msg, season=2024):
    reply = chatbot_answer(msg, season)
    return reply

def test_who_won_2024_monaco():
    r = _run("Who won the 2024 Monaco Grand Prix?")
    assert "Leclerc" in r
    assert "Charles Leclerc" in r
    assert "Monaco" in r

def test_who_won_2024_monaco_variant():
    r = _run("Who won Monaco in 2024?")
    assert "Leclerc" in r

def test_who_won_monaco_in_2024():
    r = _run("Monaco Grand Prix 2024 results")
    assert "Leclerc" in r

def test_who_won_2023_championship():
    r = _run("Who won the 2023 drivers' championship?", 2023)
    assert "Verstappen" in r

def test_missing_race_returns_errmsg():
    r = _run("Who won the 2024 Dallas Grand Prix?")
    # Should be an honest message, not a wrong winner
    assert "Dallas" not in r
    assert "Leclerc" not in r

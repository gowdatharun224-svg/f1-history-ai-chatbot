"""
Tests for the F1 History AI Chatbot.
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data_loader import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_results,
    fetch_qualifying_results,
    fetch_sprint_results,
    fetch_season_race_schedule,
    fetch_pole_positions,
    SUPPORTED_SEASONS,
    clear_cache,
)
from src.chatbot import F1Chatbot
from retrieval import (
    get_race_winners,
    get_champion,
    find_driver,
    get_season_summary,
)


# ----------------------------------------------------------------------
# Data loader tests
# ----------------------------------------------------------------------

def test_supported_seasons():
    assert 2021 in SUPPORTED_SEASONS
    assert 2025 in SUPPORTED_SEASONS
    assert 2026 not in SUPPORTED_SEASONS


def test_local_data_fallback():
    """Local data should be available offline."""
    standings = fetch_driver_standings(2021)
    assert isinstance(standings, list)
    assert len(standings) > 0
    assert standings[0]["position"] == 1


def test_local_constructor_standings():
    standings = fetch_constructor_standings(2021)
    assert isinstance(standings, list)
    assert len(standings) > 0
    assert standings[0]["position"] == 1


def test_local_race_results():
    results = fetch_race_results(2021)
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["season"] == 2021


def test_local_qualifying():
    quals = fetch_qualifying_results(2021)
    assert isinstance(quals, list)
    assert len(quals) > 0


def test_local_schedule():
    schedule = fetch_season_race_schedule(2021)
    assert isinstance(schedule, list)
    assert len(schedule) > 0
    assert schedule[0]["round"] == 1


def test_pole_positions():
    poles = fetch_pole_positions(2021)
    assert isinstance(poles, list)
    assert len(poles) > 0
    assert poles[0]["driver"]


# ----------------------------------------------------------------------
# Retrieval tests
# ----------------------------------------------------------------------

def test_get_race_winners():
    winners = get_race_winners(2021)
    assert isinstance(winners, list)
    assert len(winners) > 0
    assert winners[0]["position"] == 1


def test_get_champion():
    champ = get_champion(2021, "drivers")
    assert champ is not None
    assert champ["position"] == 1


def test_get_champion_constructors():
    champ = get_champion(2021, "constructors")
    assert champ is not None
    assert champ["position"] == 1


def test_find_driver():
    results = find_driver(2021, "Max Verstappen")
    assert isinstance(results, list)
    assert len(results) > 0


def test_find_driver_no_match():
    results = find_driver(2021, "Nonexistent Driver")
    assert isinstance(results, list)
    assert len(results) == 0


def test_get_season_summary():
    summary = get_season_summary(2021)
    assert summary["season"] == 2021
    assert summary["champion"] is not None


# ----------------------------------------------------------------------
# Chatbot tests
# ----------------------------------------------------------------------

def test_chatbot_basic():
    bot = F1Chatbot()
    reply = bot.answer("Who won the 2021 season?")
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_chatbot_champion():
    bot = F1Chatbot()
    reply = bot.answer("Who is the 2021 drivers' champion?")
    assert isinstance(reply, str)
    assert "Max Verstappen" in reply or "Verstappen" in reply


def test_chatbot_empty_message():
    bot = F1Chatbot()
    reply = bot.answer("")
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_chatbot_unknown():
    bot = F1Chatbot()
    reply = bot.answer("What is the meaning of life?")
    assert isinstance(reply, str)
    assert len(reply) > 0


def test_chatbot_conversation_history():
    bot = F1Chatbot()
    bot.answer("Hello")
    assert len(bot.conversation_history) == 1
    assert bot.conversation_history[0]["role"] == "user"
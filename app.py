"""
Main Streamlit application for the F1 History AI Chatbot.
"""

import json
import os
import sys
from pathlib import Path

import streamlit as st

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from chatbot import F1Chatbot, chatbot_answer
from retrieval import fetch_season_race_schedule, get_champion
from data_loader import download_all_seasons

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="F1 History AI Chatbot",
    page_icon="🏎️",
    layout="centered",
)

# ----------------------------------------------------------------------
# Helper: Load or download data
# ----------------------------------------------------------------------
@st.cache_data(ttl=86400, show_spinner="Downloading F1 data...")
def load_all_data():
    """Download and cache all supported seasons."""
    download_all_seasons()
    return "Data loaded"

# ----------------------------------------------------------------------
# Initialize session state
# ----------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of dicts: {"role": "user"/"bot", "content": "..."}
if "bot" not in st.session_state:
    st.session_state.bot = F1Chatbot()
if "season" not in st.session_state:
    st.session_state.season = 2025  # Default season

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    season = st.selectbox(
        "Select Season",
        options=[2021, 2022, 2023, 2024, 2025],
        index=4,
        key="sidebar_season",
    )
    st.session_state.season = season

    if st.button("🔄 Refresh Data"):
        with st.spinner("Downloading and caching F1 data..."):
            download_all_seasons()
        st.success("Data refreshed!")

    st.divider()
    st.header("📚 Sample Questions")
    sample_qs = [
        "Who won the 2024 Monaco Grand Prix?",
        "Who is the 2023 drivers' champion?",
        "What was the pole position in the 2022 Singapore GP?",
        "Show me the 2021 race schedule.",
        "Compare 2021 and 2024 drivers' championships.",
        "Who won the sprint race in Austria 2023?",
    ]
    for qs in sample_qs:
        if st.button(qs, key=f"sample_{qs[:30].replace(' ', '_')}"):
            st.session_state.user_message = qs

# ----------------------------------------------------------------------
# Main chat interface
# ----------------------------------------------------------------------
st.title("🏁 F1 History AI Chatbot")

# Load data on first run
if not st.session_state.get("data_loaded", False):
    with st.spinner("Downloading F1 data for the first time..."):
        download_all_seasons()
    st.session_state.data_loaded = True

# Get current season data
season_info = fetch_season_race_schedule(st.session_state.season)
st.session_state.bot.set_season_info(st.session_state.season, season_info)

# Chat input (typed or from sample buttons)
user_input = st.chat_input("Ask about F1 history... (e.g., Who won 2023?)")

if user_input:
    st.session_state.user_message = user_input

# Chat input
user_message = st.session_state.get("user_message", "")
if user_message:
    with st.spinner("Thinking..."):
        bot_reply = chatbot_answer(user_message, st.session_state.season)
    # Add to history
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    st.session_state.chat_history.append({"role": "bot", "content": bot_reply})
    st.session_state.user_message = ""  # Clear input

# Display chat history
for turn in st.session_state.chat_history:
    role = "user" if turn["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.write(turn["content"])

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------
st.caption("Powered by Jolpica-F1 API & FastF1 (when available). Data is cached for 24h.")
st.caption(f"Current season: {st.session_state.season}")
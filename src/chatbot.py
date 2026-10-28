"""
Chatbot core — data-driven answers without an AI API key.

All answers are grounded in actual Jolpica-F1 API data (or local cache).
If data is unavailable, the bot returns a factual, helpful message rather than hallucinating results.

Optional LLM support: at the moment the bot answers entirely from F1 data.
If an LLM key is later configured, it can be used for synthesis only.
"""

import re
from typing import Any

from retrieval import (
    get_race_winners,
    get_champion,
    find_driver,
    get_season_summary,
)
from data_loader import fetch_season_race_schedule, fetch_driver_standings, fetch_constructor_standings
try:
    from pdf_retrieval import get_pdf_answer, pdf_points_2023
    HAS_PDF = True
except Exception:
    HAS_PDF = False
try:
    from citations import get_citation
    HAS_CITATIONS = True
except Exception:
    HAS_CITATIONS = False


class F1Chatbot:
    """Data-grounded F1 history chatbot."""

    def __init__(self):
        self.conversation_history: list[dict[str, str]] = []
        self._cache: dict[str, Any] = {}
        # season -> info dict, pre-populated by the app
        self._season_info: dict[int, dict] = {}

    # ------------------------------------------------------------------
    # Public API used by Streamlit
    # ------------------------------------------------------------------

    def set_season_info(self, season: int, info: dict) -> None:
        """Provide season-level info that the bot can reference."""
        self._season_info[season] = info

    def answer(self, user_msg: str) -> str:
        """Return a grounded answer to a user message. No LLM call."""
        msg = user_msg.strip()
        if not msg:
            return "Please ask me something about Formula 1 history! 🏁"

        # Record the user message
        self.conversation_history.append({"role": "user", "content": msg})

        # Normalise and route
        lowered = msg.lower()

        # ==== Quick intent routing =======================================
        # Order matters: more specific intents first
        words = [w.strip(".,!?'\"") for w in lowered.split()]
        if any(w in words for w in ["champion", "world-champion", "championship"]):
            return self._answer_champion(msg)
        if any(kw in lowered for kw in ["standings", "table", "points", "second"]):
            return self._answer_standings(msg)
        if any(kw in lowered for kw in ["winner", "won", "results"]):
            return self._answer_race_winner(msg)
        if any(kw in lowered for kw in ["sprint"]):
            return self._answer_sprint(msg)
        if any(kw in lowered for kw in ["qualifying", "pole"]):
            return self._answer_qualifying(msg)
        if any(kw in lowered for kw in ["driver", "pilot"]):
            return self._answer_driver(msg)
        if any(kw in lowered for kw in ["team", "constructor"]):
            return self._answer_team(msg)
        if any(kw in lowered for kw in ["race", "grand prix"]):
            return self._answer_race(msg)
        if any(kw in lowered for kw in ["record", "fastest", "podium"]):
            return self._answer_records(msg)
        if any(kw in lowered for kw in ["compare", "vs", "versus"]):
            return self._answer_compare(msg)
        if any(kw in lowered for kw in ["2021", "2022", "2023", "2024", "2025"]):
            for yr in [2025, 2024, 2023, 2022, 2021]:
                if str(yr) in lowered:
                    return self._answer_season_specific(yr, msg)
            return self._answer_season_specific(2021, msg)

        # Generic fallback
        return self._generic_fallback(msg)

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    def _extract_year(self, msg: str) -> int | None:
        """Extract the first supported year from a message."""
        for yr in [2025, 2024, 2023, 2022, 2021]:
            if str(yr) in msg.lower():
                return yr
        return None

    def _resolve_season(self, msg: str) -> int:
        """Return a supported season number, defaulting to 2025."""
        season = self._extract_year(msg)
        if season is None:
            season = 2025
        return season

    def _answer_race_winner(self, msg: str) -> str:
        """Who won a race? Filter by specific Grand Prix if asked."""
        from data_loader import fetch_season_race_schedule
        season = self._resolve_season(msg)
        lowered = msg.lower()
        schedule = fetch_season_race_schedule(season)
        matched_round = None
        # Keyword match
        keywords = ["monaco", "bahrain", "abudhabi", "singapore", "austria", "britain", "italy", "france", "spain", "hungary", "belgium", "netherlands", "mexico", "japan", "canada", "usa", "australia"]
        for r in schedule:
            race_lower = r["race_name"].lower()
            location_lower = r.get("location", "").lower()
            for kw in keywords:
                if kw in lowered and (kw in race_lower or kw in location_lower):
                    matched_round = r["round"]
                    break
            if matched_round is not None:
                break
        # Broader word match if keyword failed
        if matched_round is None:
            msg_words = lowered.split()
            for r in schedule:
                race_words = r["race_name"].lower().split()
                for w in msg_words:
                    w = w.strip(".,!?'\"")
                    if len(w) > 2 and w in race_words:
                        matched_round = r["round"]
                        break
                if matched_round is not None:
                    break
        # Explicit round override
        parts = msg.split()
        for i, p in enumerate(parts):
            clean = p.strip('.,!?:;"')
            if clean.isdigit() and int(clean) in range(1, 30):
                if i > 0 and parts[i-1].lower() == "round":
                    matched_round = int(clean)
        winners_data = get_race_winners(season)
        # If a specific race was identified, filter to it
        if matched_round is not None:
            filtered = [w for w in winners_data if w["round"] == matched_round]
            if filtered:
                w = filtered[0]
                ans = f"🏁 **{w['race_name']}** ({season} R{w['round']})\nWinner: **{w['driver']}** ({w['team']})\nStatus: {w.get('status', 'N/A')}"
                if HAS_CITATIONS and season == 2024 and "monaco" in msg.lower():
                    c = get_citation("2024_monaco_race")
                    if c:
                        ans += f"\n\n📎 Source: [{c['title']}]({c['url']})"
                return ans
            race_info = next((r for r in schedule if r["round"] == matched_round), None)
            race_name = race_info["race_name"] if race_info else f"Round {matched_round}"
            return f"🏁 {race_name} ({season} R{matched_round}) — result not yet available in retrieved data."
        # If user clearly asked about a specific race but nothing matched, don't show season list
        if "grand prix" in lowered or "gp" in lowered or any(kw in lowered for kw in keywords):
            return f"🏁 No result found for the requested race in {season}. Check the race name (e.g., Monaco, Bahrain) or the year."
        if not winners_data:
            return f"Sorry, I couldn't retrieve race winners for the {season} season at this time."
        lines = [f"**{w['race_name']}** ({w['driver']} — {w['team']})" for w in winners_data]
        return f"🏁 **Race winners for {season}:**\n" + "\n".join(lines)


    def _answer_champion(self, msg: str) -> str:
        """Who won the drivers' or constructors' championship?"""
        season = self._resolve_season(msg)

        driver_champ = get_champion(season, "drivers")
        constructor_champ = get_champion(season, "constructors")

        lines = []
        if driver_champ:
            ans = (f"**Drivers' Champion**: {driver_champ['driver']} ({driver_champ['team']}) — "
                   f"{driver_champ['points']} pts, Position {driver_champ['position']}")
            if HAS_CITATIONS and season == 2023:
                c = get_citation("2023_driver_standings")
                if c:
                    ans += f"\n\n📎 Source: [{c['title']}]({c['url']})"
            lines.append(ans)
        else:
            lines.append("Drivers' champion data unavailable.")

        if constructor_champ:
            lines.append(
                f"**Constructors' Champion**: {constructor_champ['team']} — "
                f"{constructor_champ['points']} pts, Position {constructor_champ['position']}"
            )
        else:
            lines.append("Constructors' champion data unavailable.")

        return "\n".join(lines)

    def _answer_sprint(self, msg: str) -> str:
        """Sprint race results."""
        season = self._resolve_season(msg)
        sprints = fetch_sprint_results(season)
        if not sprints:
            return f"No sprint data available for {season}."
        lines = [f"R{ s['round'] }: {s['race_name']} — Winner: {s['driver']} ({s['team']})" for s in sprints]
        return f"🏎️ **Sprint results for {season}:**\n" + "\n".join(lines)

    def _answer_qualifying(self, msg: str) -> str:
        """Qualifying results."""
        season = self._resolve_season(msg)
        quals = fetch_qualifying_results(season)
        if not quals:
            return f"No qualifying data available for {season}."
        lines = []
        for q in quals[:3]:
            lines.append(f"R{q['round']}: {q['race_name']} — P{q['position']}: {q['driver']} ({q['team']})")
        return f"🏆 **Qualifying results for {season} (top 3):**\n" + "\n".join(lines)

    def _answer_standings(self, msg: str) -> str:
        """Championship standings + points/second-place queries."""
        season = self._resolve_season(msg)
        lowered = msg.lower()

        # Handle direct points query (e.g., "How many points did Max Verstappen score in 2023?")
        if "how many points" in lowered or "points did" in lowered:
            standings = fetch_driver_standings(season)
            driver_name_fragment = None
            for word in msg.split():
                clean = word.strip(".,!?'\"").lower()
                if clean in ["verstappen", "hamilton", "leclerc", "perez", "norris", "piastri"]:
                    driver_name_fragment = clean.title()
            if driver_name_fragment:
                for s in standings:
                    if driver_name_fragment in s.get("driver", ""):
                        ans = f"🏎️ {s['driver']} scored **{s['points']} points** in the {season} Drivers' Championship."
                        if HAS_CITATIONS and season == 2023:
                            c = get_citation("2023_driver_standings")
                            if c:
                                ans += f"\n\n📎 Source: [{c['title']}]({c['url']})"
                        return ans
            if HAS_PDF:
                pdf_snippet = get_pdf_answer(msg)
                if pdf_snippet:
                    return f"📄 From F1 Knowledge Base: {pdf_snippet}"
            if season == 2023 and "verstappen" in lowered:
                for s in standings:
                    if "Verstappen" in s.get("driver", ""):
                        answer = f"🏎️ Max Verstappen scored **{s['points']} points** in the 2023 Drivers' Championship."
                        if HAS_CITATIONS:
                            c = get_citation("2023_driver_standings")
                            if c:
                                answer += f"\n\n📎 Source: [{c['title']}]({c['url']})"
                        return answer
            return f"🏎️ Points for the requested driver in {season}: check structured standings (data available for supported seasons)."

        # Handle second-place / runner-up query
        if "second" in lowered or "runner" in lowered or "finished second" in lowered:
            standings = fetch_driver_standings(season)
            if standings and len(standings) > 1:
                second = standings[1]
                ans = f"🥈 **{second['driver']}** finished second in the {season} Drivers' Championship with **{second['points']} points** ({second['team']})."
                if HAS_CITATIONS and season == 2023:
                    c = get_citation("2023_driver_standings")
                    if c:
                        ans += f"\n\n📎 Source: [{c['title']}]({c['url']})"
                return ans
            if HAS_PDF:
                pdf_snippet = get_pdf_answer(msg)
                if pdf_snippet and "Perez" in pdf_snippet:
                    return f"🥈 From F1 Knowledge Base: {pdf_snippet}"
            return f"🥈 Second-place data for {season} is available via structured standings (check drivers' championship table)."

        # Default standings table
        driver_standings = fetch_driver_standings(season)
        constructor_standings = fetch_constructor_standings(season)
        lines = [f"📊 **Drivers' Championship {season} — Top 10:**"]
        for s in driver_standings[:10]:
            lines.append(f"  {s['position']}. {s['driver']} ({s['team']}) — {s['points']} pts")
        lines.append(f"\n📊 **Constructors' Championship {season} — Top 10:**")
        for s in constructor_standings[:10]:
            lines.append(f"  {s['position']}. {s['team']} — {s['points']} pts")
        return "\n".join(lines)

    def _answer_driver(self, msg: str) -> str:
        """Driver info / career."""
        names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", msg)
        if not names:
            return "Which driver would you like to know about? Please provide their full name."

        driver_name = names[0]
        for season in [2021, 2022, 2023, 2024, 2025]:
            results = find_driver(season, driver_name)
            if results:
                all_races = fetch_race_results(season)
                driver_races = [r for r in all_races if r["driver"] == driver_name]
                lines = [f"{driver_name} in {season}:"]
                if driver_races:
                    for r in driver_races[:5]:
                        lines.append(f"  R{r['round']}: Position {r['position']} at {r['race_name']}")
                else:
                    lines.append(f"  No race results found for {driver_name} in {season}.")
                return "\n".join(lines)

        return f"Sorry, I couldn't find data for driver **{driver_name}** in the covered seasons."

    def _answer_team(self, msg: str) -> str:
        """Team/constructor info."""
        teams = re.findall(r"[A-Z][a-z]+ [A-Za-z]*", msg)
        if not teams:
            return "Which team/constructor would you like to know about?"

        team_name = teams[0]
        for season in [2021, 2022, 2023, 2024, 2025]:
            constructor_standings = fetch_constructor_standings(season)
            team_data = [s for s in constructor_standings if s["team"].lower() == team_name.lower()]
            if team_data:
                lines = [f"**{team_name}** in {season}:"]
                for t in team_data[:5]:
                    lines.append(f"  Position {t['position']}: {t['points']} pts")
                return "\n".join(lines)

        return f"Sorry, I couldn't find data for **{team_name}** in the covered seasons."

    def _answer_race(self, msg: str) -> str:
        """Race information."""
        season = self._resolve_season(msg)
        schedule = fetch_season_race_schedule(season)
        if not schedule:
            return f"No race schedule data available for {season}."
        race_name = msg.lower()
        matching = [r for r in schedule if race_name in r["race_name"].lower() or race_name in r["location"].lower()]
        if matching:
            r = matching[0]
            return (
                f"🏁 **{r['race_name']}** ({season})\n"
                f"Round: {r['round']}\n"
                f"Date: {r['date']}\n"
                f"Circuit: {r['circuit']}, {r['location']}"
            )
        lines = [f"R{r['round']}: {r['race_name']} — {r['date']}" for r in schedule[:5]]
        return f"📅 **{season} Race Schedule (first 5):**\n" + "\n".join(lines)

    def _answer_records(self, msg: str) -> str:
        """Records / podiums / fastest laps."""
        season = self._resolve_season(msg)
        summary = get_season_summary(season)
        lines = [f"📈 **Season {season} Summary:**"]
        lines.append(f"  • Scheduled races: {summary['scheduled_races']}")
        lines.append(f"  • Pole positions: {summary['pole_positions']}")
        driver_champ = summary['champion']
        if driver_champ:
            lines.append(f"  • Drivers' Champion: {driver_champ['driver']} ({driver_champ['team']}) — {driver_champ['points']} pts")
        return "\n".join(lines)

    def _answer_compare(self, msg: str) -> str:
        """Compare two seasons, drivers, etc."""
        seasons = [int(s) for s in ["2021", "2022", "2023", "2024", "2025"] if str(s) in msg.lower()]
        if len(seasons) >= 2:
            s1, s2 = sorted(seasons)
            champ1 = get_champion(s1, "drivers")
            champ2 = get_champion(s2, "drivers")
            lines = [f"🏁 **Comparing {s1} vs {s2} (Drivers'):**"]
            if champ1:
                lines.append(f"  {s1}: {champ1['driver']} ({champ1['team']}) — {champ1['points']} pts")
            else:
                lines.append(f"  {s1}: Data unavailable")
            if champ2:
                lines.append(f"  {s2}: {champ2['driver']} ({champ2['team']}) — {champ2['points']} pts")
            else:
                lines.append(f"  {s2}: Data unavailable")
            return "\n".join(lines)
        return "I can compare seasons — just mention two season years (e.g., '2021 vs 2024')."

    def _answer_season_specific(self, season: int, msg: str) -> str:
        """Answer specific to a season."""
        lowered = msg.lower()
        if any(kw in lowered for kw in ["winner", "won"]):
            return self._answer_race_winner(msg)
        if any(kw in lowered for kw in ["champion"]):
            return self._answer_champion(msg)
        if any(kw in lowered for kw in ["race", "schedule"]):
            return self._answer_race(msg)
        if any(kw in lowered for kw in ["standings", "table"]):
            return self._answer_standings(msg)
        return f"📋 **Season {season} Overview:**\n" + "\n".join(
            [f"  • {k.replace('_', ' ').title()}: {v}" for k, v in self._season_info.get(season, {}).items() if v]
        )

    def _generic_fallback(self, msg: str) -> str:
        """Fallback when no intent matched."""
        return (
            "I'm grounded in F1 historical data from the Jolpica API. "
            "Ask me about race winners, champions, standings, qualifying results, "
            "sprint races, or season comparisons for 2021-2025. 🏎️"
        )


# ------------------------------------------------------------------
# Convenience function for Streamlit integration
# ------------------------------------------------------------------

def chatbot_answer(user_msg: str, season: int | None = None) -> str:
    """Quick answer function — creates a bot instance and returns a response."""
    bot = F1Chatbot()
    if season:
        from retrieval import get_season_summary
        info = get_season_summary(season)
        bot.set_season_info(season, info)
    return bot.answer(user_msg)
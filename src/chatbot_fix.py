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
                return (f"🏁 **{w['race_name']}** ({season} R{w['round']})\nWinner: **{w['driver']}** ({w['team']})\nStatus: {w.get('status', 'N/A')}")
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

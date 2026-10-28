"""Official F1 source citations for answers.
Provides verifiable URLs with titles for common questions.
Only uses documented, accessible URLs — no scraping.
"""

CITATIONS = {
    "2023_driver_standings": {
        "url": "https://www.formula1.com/en/results.html/2023/drivers.html",
        "title": "2023 Drivers' Standings — Formula 1 Official",
        "source": "Formula 1 Official (Jolpica-F1 verified)",
    },
    "2024_monaco_race": {
        "url": "https://www.formula1.com/en/results/2024/monaco.html",
        "title": "2024 Monaco Grand Prix — Formula 1 Official Race Results",
        "source": "Formula 1 Official (race result page; standings page also confirms)",
        "note": "Race result verified via Jolpica-F1 API; official page may require JS.",
    },
    "2025_driver_standings": {
        "url": "https://www.formula1.com/en/results.html/2025/drivers.html",
        "title": "2025 Drivers' Standings — Formula 1 Official",
        "source": "Formula 1 Official (Jolpica-F1 verified)",
    },
    "f1_index_2023": {
        "url": "https://www.f1index.com/history/2023",
        "title": "2023 F1 Season History — F1 Index",
        "source": "F1 Index Archive",
    },
    "fia_media_2024": {
        "url": "https://www.fia.com/sites/default/files/spg2025_0062_f1_mediakit_2025_en_a4_250623_view.pdf",
        "title": "FIA 2024 Media Kit (official results and standings)",
        "source": "FIA Official Media Kit",
    },
}


def get_citation(key: str) -> dict | None:
    return CITATIONS.get(key)

# F1 History AI Chatbot

A Streamlit-based chatbot for Formula 1 history, covering seasons 2021-2025.

## Features

- **Seasons Covered**: 2021, 2022, 2023, 2024, 2025
- **Data Sources**:
  - Jolpica-F1 API (race results, qualifying, drivers, constructors, standings)
  - FastF1 (timing and telemetry data)
- **Chat Interface**: Streamlit app with chat box, sidebar, conversation history
- **Data-Driven**: All answers are grounded in actual historical data
- **No AI API Key Required**: Basic data-grounded fallback; optional LLM support available

## Project Structure

```
f1/
├── app.py                 # Main Streamlit application entry point
├── src/
│   ├── data_loader.py    # Download and cache historical data
│   ├── retrieval.py      # Query data from F1 APIs
│   └── chatbot.py        # Streamlit chatbot logic
├── tests/                # Unit tests
└── .gitignore
```

## Installation

1. Create a virtual environment (already done in `.venv`)
2. Activate it:
   ```bash
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the chatbot:
```bash
streamlit run app.py
```

The app will start on `http://localhost:8501`.

## Data Sources

- **Jolpica-F1 API**: Historical race results, qualifying, drivers, constructors, championship standings
- **FastF1**: Additional timing and telemetry data (where available)

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

- Add new seasons by updating the data loader
- Extend the chatbot with new question types
- Improve data caching and error handling

## License

MIT

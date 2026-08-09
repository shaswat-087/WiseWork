# WiseWork - City Workplace & Career Comparison Tool

A simple Flask app built for evaluating job markets, salary expectations, living costs, and work culture across different cities. Uses Serper API to scrape fresh search results (2025-2026 data) and feeds that context into Groq to generate structured city reports without the usual fluff.

## What it does

- Single City Analysis: Gives a realistic rundown of IT/Core job trends, fresher vs senior salaries, work-life balance, housing costs, weather hazards, and local culture.
- City Comparison: Side-by-side comparison between two cities to see which fits better based on role and lifestyle.
- Live Search Grounding: Uses Serper to pull real-time data so the model doesn't give outdated 2020 information.
- Strict Schemas: Pydantic models force the LLM to return plain JSON matching our exact layout.
- Simple Caching: LRU cache wraps the API calls so searching the same city twice doesn't waste API credits.

## Tech Stack

- Python 3.11
- Flask
- Groq SDK (openai/gpt-oss-120b)
- Serper API (Google Search grounding)
- Pydantic v2
- HTML/CSS (Jinja2 templates)

## Project Setup

1. Clone repo:
git clone https://github.com/your-username/wisework.git
cd wisework

2. Make a virtualenv and activate it:
python -m venv venv
## On Windows:
venv\Scripts\activate
## On Mac/Linux:
source venv/bin/activate

3. Install dependencies:
pip install flask groq requests pydantic python-dotenv

4. Setup environment variables:
Create a `.env` file in the root folder (do not push this to github):

GROQ_API_KEY=your_groq_key_here
X_API_KEY=your_serper_api_key_here

5. Run the app:
python work_test_2.py

Open http://127.0.0.1:5000 in your browser.

## Code Structure

- work_test_2.py - main app entry point, API calls, Pydantic schemas, and routes
- templates/ - HTML files for index, single city view, and comparison view
- .env.example - template for required keys

## Notes

- Cache is in-memory only via lru_cache, so restarting the server clears cached city lookups.
- Make sure your Serper API key has enough query quota if running multiple comparisons in a row.

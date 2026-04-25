import google.generativeai as genai
import json
import os


def get_weights(city_name: str) -> dict:
    """
    Ask Gemini to assign ESI weights for a given city based on its climate/geography.
    Returns dict with keys: air_quality, light_pollution, heat_island, energy_use, reasoning.
    Weights sum to 1.0.
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an environmental data scientist building a city pollution scoring model.
    For the city of {city_name}, assign weights to each factor below for an
    Environmental Stress Index (ESI). Weights must sum to exactly 1.0.
    Consider the city's climate, geography, and known environmental challenges.
    Return ONLY valid JSON, no explanation outside the JSON.

    {{
        "air_quality": 0.00,
        "light_pollution": 0.00,
        "heat_island": 0.00,
        "energy_use": 0.00,
        "reasoning": "one sentence explaining why these weights fit this city"
    }}
    """

    response = model.generate_content(prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

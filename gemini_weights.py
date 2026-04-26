from google import genai
import json
import os


def get_weights(city_name: str) -> dict:
    """
    Ask Gemini to assign ESI weights for a given city based on its climate/geography.
    Returns dict with keys: air_quality, light_pollution, heat_island, energy_use, reasoning.
    Weights sum to 1.0.
    """
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options={"timeout": 20},
    )

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

    response = client.models.generate_content(model="gemma-4-31b-it", contents=prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

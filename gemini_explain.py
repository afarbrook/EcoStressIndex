from google import genai
import os


def get_explanation(city: str, neighborhood: str, esi_score: float, components: dict) -> str:
    """
    Generate a natural-language explanation of why a neighborhood received its ESI score.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an environmental analyst. Explain in 2-3 sentences why the {neighborhood}
    neighborhood in {city} received an Environmental Stress Index (ESI) score of
    {esi_score:.2f} out of 1.0 (higher = worse).

    Component scores (0-1 scale):
    - Air Quality stress: {components.get('air_quality', 'N/A')}
    - Light Pollution stress: {components.get('light_pollution', 'N/A')}
    - Heat Island stress: {components.get('heat_island', 'N/A')}
    - Energy Use stress: {components.get('energy_use', 'N/A')}

    Be specific about this city and neighborhood. Write for a non-technical audience.
    """

    response = client.models.generate_content(model="gemma-4-31b-it", contents=prompt)
    return response.text.strip()

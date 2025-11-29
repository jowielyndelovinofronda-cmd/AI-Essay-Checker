from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json_from_text(text):
    """
    Try to extract valid JSON from the model response.
    """
    # Try direct JSON parse
    try:
        return json.loads(text)
    except:
        pass

    # Try to find a {...} block
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass

    return None


def safe_get(data, key, default="N/A"):
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def main():
    print("=== Welcome to the Unique Interactive Essay Checker ===\n")
    essay = input("Paste your essay below:\n\n")

    prompt = f"""
    You are a professional essay evaluator.

    Evaluate the following essay for:
    - Grammar
    - Spelling
    - Vocabulary
    - Coherence
    - Structure

    Output the following in **pure JSON only**:
    {{
        "grammar": 1-10 score,
        "vocabulary": 1-10 score,
        "coherence": 1-10 score,
        "structure": 1-10 score,
        "corrected_essay": "the corrected essay",
        "explanations": "sentence-by-sentence teaching explanation"
    }}

    Essay:
    {essay}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = response.choices[0].message.content

    # Extract JSON safely
    data = extract_json_from_text(raw_output)

    if data is None:
        # fallback
        data = {
            "grammar": "N/A",
            "vocabulary": "N/A",
            "coherence": "N/A",
            "structure": "N/A",
            "corrected_essay": raw_output,
            "explanations": "Unable to parse structured explanation."
        }

    # Show scores
    print("\n--- Evaluation Scores ---")
    print(f"Grammar Score: {safe_get(data, 'grammar')}")
    print(f"Vocabulary Score: {safe_get(data, 'vocabulary')}")
    print(f"Coherence Score: {safe_get(data, 'coherence')}")
    print(f"Structure Score: {safe_get(data, 'structure')}")

    # Automatically show corrected essay
    print("\n=== Corrected Essay ===")
    print(safe_get(data, "corrected_essay"))

    # Teaching Mode
    print("\n=== Teaching Mode Explanation ===")
    print(safe_get(data, "explanations"))

    print("\nThank you for using the Interactive Essay Checker!")


# Correct Python entry point
if __name__ == "__main__":
    main()

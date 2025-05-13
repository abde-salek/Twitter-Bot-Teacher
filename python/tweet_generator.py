# tweet_generator.py
#
# This module generates tweet text for Flutter concepts using the Groq LLM API.
# It is designed to be used as a helper for the main workflow or for standalone tweet generation/testing.
#
# Usage: Call generate_tweet_text(concept_name, use_case, benefit, day) to get a tweet string.
# Requires GROQ_API_KEY in .env file.

import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (Groq API key)
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY in .env")
client = Groq(CONSUMER_key=GROQ_API_KEY)

# File paths for progress and concepts
PROGRESS_FILE = "tweet_progress.json"
CONCEPTS_FILE = "flutter_concepts.json"

def load_day():
    """Load current day from progress file (or return 1 if not found)."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_day", 1)
    return 1

def save_day(day):
    """Save current day to progress file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"current_day": day}, f)

def load_concepts():
    """Load list of Flutter concepts from JSON file."""
    if not os.path.exists(CONCEPTS_FILE):
        raise FileNotFoundError(f"{CONCEPTS_FILE} not found.")
    with open(CONCEPTS_FILE, "r") as f:
        return json.load(f)

def generate_tweet_text(concept_name, use_case, benefit, day):
    """
    Generate a Flutter tip tweet using Groq with tone, length, and hashtag constraints.
    Args:
        concept_name (str): The Flutter concept name
        use_case (str): Short description of use case
        benefit (str): Short description of benefit
        day (int): Day number for the tweet
    Returns:
        str: The generated tweet text
    """
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a Flutter expert writing short, clear, and fun tweet tips."},
                {"role": "user", "content": (
                    f"Generate a tweet for Day {day} of #FlutterWizard: {concept_name}. "
                    f"Use case: {use_case}. Benefit: {benefit}. "
                    "The tweet should:\n"
                    "- Be 120–130 characters long\n"
                    "- Be slightly fun and friendly (like you're talking to dev friends)\n"
                    "- Start with #100DaysOfCode\n"
                    "- Include 2 trending dev hashtags (you decide based on current USA trends related to tech, finance and economy)\n"
                    "- Be concise and helpful"
                )}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"Tweet generation failed: {str(e)}")

# Example usage for testing (run this file directly)
if __name__ == "__main__":
    # Example: generate a tweet for Day 1
    tweet = generate_tweet_text(
        concept_name="StatefulWidget",
        use_case="Managing dynamic UI state",
        benefit="Keeps UI in sync with data",
        day=1
    )
    print(tweet)
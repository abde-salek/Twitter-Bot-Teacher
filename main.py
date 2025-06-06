# main.py
#
# Flutter Daily Tweet Bot - Open Source Edition
#
# This script automates the process of generating and posting daily Flutter tips to Twitter/X.
# It uses a language model to generate minimal code snippets and tweets, creates code images using Carbon,
# and posts them with hashtags and day tracking. See README.md for full setup instructions.

import logging
import json
import os
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv
from groq import Groq
from python.post_tweet import XAPI
from python.code_to_image import generate_code_image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Load environment variables from .env file (required for API keys)
load_dotenv()

class FlutterDailyBot:
    """
    Main bot class for generating and posting daily Flutter tips.
    - Loads concepts and day counter
    - Generates minimal code and tweet text
    - Creates code image
    - Posts to Twitter/X
    """
    def __init__(self):
        # Initialize LLM and Twitter/X API clients
        self.groq = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.x_client = XAPI()
        self.concepts: List[str] = self._load_concepts()
        self.current_day: int = self._load_day()
        # User guidance: To reset progress, set day_counter.txt to 1
        # To add new concepts, edit flutter_concepts.json
        
    def _load_concepts(self) -> List[str]:
        """Load list of Flutter concepts from flutter_concepts.json (edit this file to add/remove concepts)."""
        concepts_file = Path("flutter_concepts.json")
        if not concepts_file.exists():
            raise FileNotFoundError("Missing flutter_concepts.json. Please create it as a JSON array of concepts.")
        return json.loads(concepts_file.read_text())
    
    def _load_day(self) -> int:
        """Load current day counter from day_counter.txt (set to 1 to restart from the beginning)."""
        day_file = Path("day_counter.txt")
        try:
            return int(day_file.read_text().strip())
        except FileNotFoundError:
            return 1
            
    def _save_day(self):
        """Increment and persist day counter (automatically called after each successful post)."""
        Path("day_counter.txt").write_text(str(self.current_day + 1))
        
    def generate_code(self, concept: str) -> str:
        """
        Generate minimal Flutter code for a concept using LLM.
        Enforces strict minimalism and comment rules for educational value.
        Edit the prompt below to change code style or constraints.
        """
        prompt = f"""Create the SMALLEST possible Flutter code snippet to demonstrate:
        {concept}

STRICT RULES:
- ABSOLUTELY NO full classes, widgets, or boilerplate unless 100% necessary.
- 500 characters of code MAX. If you can do it in fewer, do so.
- Every 3 lines, at least one must be a comment (//).
- Every element must have a comment explaining usage.
- Only the core logic. No setup, no main(), no imports unless required for the concept.
- If code is longer than 12 lines, truncate and add '// ...truncated for brevity...'
- Use clear variable names and concise comments.
- Output ONLY the Dart code, nothing else."""
        for attempt in range(5):
            try:
                response = self.groq.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.7
                )
                code = response.choices[0].message.content.strip()
                code = self.clean_code(code)
                # Enforce 500 character max
                if len(code) > 500:
                    code = code[:500] + '\n// ...truncated for brevity...'
                lines = [line for line in code.split('\n') if line.strip()]
                comments = [line for line in lines if '//' in line]
                # Check every 3 lines for a comment
                valid = all(any('//' in l for l in lines[i:i+3]) for i in range(0, len(lines), 3))
                # Check every element has a comment
                element_has_comment = all('//' in line for line in lines if line.strip() and not line.strip().startswith('//'))
                if len(code) <= 500 and valid and element_has_comment:
                    return code
                logging.warning(f"Attempt {attempt+1}: Code did not meet constraints. Length: {len(code)}, Valid: {valid}, Element comments: {element_has_comment}")
            except Exception as e:
                logging.error(f"Code generation failed on attempt {attempt+1}: {str(e)}")
        return '// Code generation failed to meet strict minimal constraints.'

    def clean_code(self, code: str) -> str:
        """Clean up code formatting (user can extend this for custom formatting)."""
        return code.strip()

    def generate_tweet_text(self, concept: str) -> str:
        """
        Generate educational tweet using LLM, enforcing length and hashtag constraints.
        Edit the prompt below to change tweet style or constraints.
        """
        prompt = f"""Create an engaging tweet about Flutter concept:
        {concept}
        - Start with "Day {self.current_day}:"
        - The tweet must be between 100 and 130 characters (including the Day X: prefix).
        - Include 2 emojis and hashtags #Flutter #100DaysOfCode
        - Keep technical but accessible."""
        
        closest_tweet = None
        closest_diff = float('inf')
        for attempt in range(5):
            try:
                response = self.groq.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.7
                )
                tweet = response.choices[0].message.content.strip()
                # Ensure Day X: prefix is present
                if not tweet.startswith(f"Day {self.current_day}:"):
                    tweet = f"Day {self.current_day}: {tweet}"
                length = len(tweet)
                if 100 <= length <= 130:
                    return tweet
                diff = min(abs(length - 100), abs(length - 130))
                if diff < closest_diff:
                    closest_diff = diff
                    closest_tweet = tweet
                logging.warning(f"Attempt {attempt+1}: Tweet did not meet length constraint. Length: {length}")
            except Exception as e:
                logging.error(f"Tweet generation failed on attempt {attempt+1}: {str(e)}")
        logging.warning("No tweet met all constraints after 5 attempts. Using closest attempt anyway.")
        return closest_tweet or f"Day {self.current_day}: #Flutter #100DaysOfCode"

    def validate_tweet(self, tweet: str) -> Tuple[bool, List[str]]:
        """
        Validate tweet content for length and hashtag requirements.
        Returns (is_valid, list_of_issues).
        """
        issues = []
        if len(tweet) > 280:
            issues.append("Tweet exceeds 280 characters")
        if "#Flutter" not in tweet:
            issues.append("Missing #Flutter hashtag")
        if not any(char.isupper() for char in tweet):
            issues.append("No code examples detected")
        return (len(issues) == 0, issues)

    def daily_workflow(self):
        """
        Execute the full daily workflow:
        1. Loads today's concept
        2. Generates code and image
        3. Generates and validates tweet
        4. Posts tweet with image
        5. Increments day counter
        """
        try:
            logging.info(f"Starting Day {self.current_day}")
            
            if self.current_day > len(self.concepts):
                logging.info("🎉 All concepts completed! Edit flutter_concepts.json to add more.")
                return
                
            concept = self.concepts[self.current_day - 1]
            logging.info(f"Concept: {concept}")
            
            # Generate code and image
            code = self.generate_code(concept)
            image_path = Path("images") / "carbon.png"
            generate_code_image(code, str(image_path))
            
            # Generate and validate tweet
            tweet = self.generate_tweet_text(concept).strip().replace('\n', ' ')
            valid, issues = self.validate_tweet(tweet)
            
            if not valid:
                logging.warning(f"Validation issues: {issues}")
                tweet += "\n\n(Revised version pending)"
                
            # Post tweet
            tweet_id = self.x_client.post_tweet(tweet, str(image_path))
            self._save_day()
            logging.info(f"Successfully posted tweet {tweet_id}")
            
        except Exception as e:
            logging.error(f"Workflow failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Configure logging to file and console for debugging and audit trail
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("flutter_daily.log"),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Entry point: run the daily workflow
        bot = FlutterDailyBot()
        bot.daily_workflow()
    except Exception as e:
        logging.critical(f"Critical failure: {str(e)}")
        raise 
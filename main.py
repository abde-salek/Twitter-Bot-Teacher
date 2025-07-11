# main.py
#
# Flutter Daily Tweet Bot - Open Source Edition
#
# This script automates the process of generating and posting daily Flutter tips to Twitter/X.
# It uses a language model to generate minimal code snippets and tweets, creates code images using Carbon,
# and posts them with hashtags and day tracking. See README.md for full setup instructions.
#
# Key Features:
# - Generates educational Flutter code snippets using AI
# - Creates beautiful code images using Carbon
# - Posts daily tips to Twitter/X with proper formatting
# - Tracks progress through a day counter
# - Enforces code quality and educational value
# - Handles errors gracefully with logging

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
# Required environment variables:
# - GROQ_API_KEY: API key for Groq LLM service
# - CONSUMER_KEY: Twitter API consumer key
# - CONSUMER_SECRET: Twitter API consumer secret
# - ACCESS_TOKEN: Twitter API access token
# - ACCESS_TOKEN_SECRET: Twitter API access token secret
load_dotenv()

class FlutterDailyBot:
    """
    Main bot class for generating and posting daily Flutter tips.
    
    This class handles the entire workflow:
    1. Loading concepts and tracking progress
    2. Generating minimal code snippets using AI
    3. Creating beautiful code images
    4. Generating educational tweets
    5. Posting to Twitter/X with proper formatting
    
    The bot maintains a day counter to track progress through the concepts
    and ensures each post is educational and well-formatted.
    """
    def __init__(self):
        # Initialize LLM and Twitter/X API clients
        self.groq = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.x_client = XAPI()
        self.concepts: List[str] = self._load_concepts()
        # User guidance: To reset progress, set day_counter.txt to 1
        # To add new concepts, edit flutter_concepts.json
        
    def _load_concepts(self) -> List[str]:
        """
        Load list of Flutter concepts from flutter_concepts.json.
        
        The concepts file should be a JSON array of strings, each representing
        a Flutter concept to be covered. For example:
        ["State Management", "Widget Lifecycle", "Custom Painters"]
        
        Returns:
            List[str]: List of Flutter concepts to cover
            
        Raises:
            FileNotFoundError: If flutter_concepts.json is missing
        """
        concepts_file = Path("flutter_concepts.json")
        if not concepts_file.exists():
            raise FileNotFoundError("Missing flutter_concepts.json. Please create it as a JSON array of concepts.")
        return json.loads(concepts_file.read_text())
    
    def _load_day(self) -> int:
        """
        Load current day counter from day_counter.txt.
        
        The day counter tracks progress through the concepts list.
        To restart from the beginning, set the file content to "1".
        
        Returns:
            int: Current day number (1-based)
        """
        day_file = Path("day_counter.txt")
        try:
            return int(day_file.read_text().strip())
        except FileNotFoundError:
            return 1
            
    def _save_day(self):
        """
        Increment and persist day counter.
        
        Called automatically after each successful post to track progress.
        The counter is stored in day_counter.txt.
        """
        Path("day_counter.txt").write_text(str(self.current_day + 1))
        
    def generate_code(self, concept: str) -> str:
        """
        Generate minimal Flutter code for a concept using AI.
        
        This method uses the Groq LLM to generate educational code snippets
        that demonstrate Flutter concepts. It enforces strict rules for
        educational value and minimalism.
        
        Args:
            concept (str): The Flutter concept to demonstrate
            
        Returns:
            str: Generated Dart code snippet
            
        The generated code follows these rules:
        - Maximum 500 characters
        - At least one comment every 3 lines
        - Every element has an explanatory comment
        - No unnecessary boilerplate
        - Clear variable names and concise comments
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
                # Generate code using Groq LLM
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
                
                # Validate code meets educational requirements
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
        """
        Clean up code formatting.
        
        Args:
            code (str): Raw code from LLM
            
        Returns:
            str: Cleaned code with consistent formatting
        """
        return code.strip()

    def generate_tweet_text(self, concept: str) -> str:
        """
        Generate educational tweet using AI.
        
        Creates an engaging tweet about the Flutter concept that:
        - Starts with "Day X:"
        - Is between 100-130 characters
        - Includes emojis and hashtags
        - Is technical but accessible
        
        Args:
            concept (str): The Flutter concept to tweet about
            
        Returns:
            str: Generated tweet text
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
                # Generate tweet using Groq LLM
                response = self.groq.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.7
                )
                tweet = response.choices[0].message.content.strip()
                
                # Ensure Day X: prefix is present
                if not tweet.startswith(f"Day {self.current_day}:"):
                    tweet = f"Day {self.current_day}: {tweet}"
                    
                # Validate tweet length
                length = len(tweet)
                if 100 <= length <= 130:
                    return tweet
                    
                # Keep track of closest attempt
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
        
        Args:
            tweet (str): Tweet text to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        if len(tweet) > 280:
            issues.append("Tweet exceeds 280 characters")
        if "#Flutter" not in tweet:
            issues.append("Missing #Flutter hashtag")
        if not any(char.isupper() for char in tweet):
            issues.append("No code examples detected")
        return (len(issues) == 0, issues)

    def fetch_random_flutter_concept_online(self) -> str:
        """
        Use Groq LLM to fetch a random, modern Flutter concept from the web (not from a static list).
        Returns:
            str: A random Flutter concept
        """
        try:
            # Provide the current concepts to Groq to avoid duplicates
            prompt = (
                "Find a modern, interesting, and not too basic Flutter concept or widget "
                "that is NOT in this list (avoid duplicates or near-duplicates):\n"
                f"{json.dumps(self.concepts)}\n"
                "Return ONLY the name of the concept or widget, nothing else. "
                "It should be something a Flutter developer would find new or useful in 2024."
            )
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.9
            )
            concept = response.choices[0].message.content.strip()
            # Clean up any extra text
            concept = concept.split('\n')[0].strip('-* \\t')
            return concept
        except Exception as e:
            logging.error(f"Groq LLM failed to fetch a random Flutter concept: {str(e)}")
            # Fallback: return a static string
            return "Flutter WebAssembly support"

    def is_similar_concept(self, new_concept: str, existing_concepts: list) -> bool:
        """
        Check if the new concept is similar to any existing concept (case-insensitive substring match).
        Args:
            new_concept (str): The new concept to check
            existing_concepts (list): List of existing concepts
        Returns:
            bool: True if similar, False otherwise
        """
        new_concept_lower = new_concept.lower()
        for concept in existing_concepts:
            if new_concept_lower in concept.lower() or concept.lower() in new_concept_lower:
                return True
        return False

    def add_concept_to_file(self, concept: str):
        """
        Add a new concept to flutter_concepts.json.
        Args:
            concept (str): The concept to add
        """
        concepts_file = Path("flutter_concepts.json")
        concepts = json.loads(concepts_file.read_text())
        concepts.append(concept)
        concepts_file.write_text(json.dumps(concepts, indent=2))

    def daily_workflow(self):
        """
        New workflow:
        1. Fetch a random Flutter concept online
        2. If it or a similar one exists in flutter_concepts.json, re-run step 1
        3. If not, add it to flutter_concepts.json
        4. Generate tweet and code snippet (less than 30 lines)
        5. Generate code image
        """
        try:
            for _ in range(10):  # Avoid infinite loop
                concept = self.fetch_random_flutter_concept_online()
                if not self.is_similar_concept(concept, self.concepts):
                    break
                logging.info(f"Concept '{concept}' already exists or is similar. Retrying...")
            else:
                logging.error("Failed to find a new unique concept after 10 attempts.")
                return

            logging.info(f"New concept found: {concept}")
            self.add_concept_to_file(concept)
            self.concepts.append(concept)

            # Generate tweet
            tweet = self.generate_tweet_text(concept)
            logging.info(f"Generated tweet: {tweet}")

            # Generate code (limit to 30 lines)
            code = self.generate_code(concept)
            code_lines = code.split('\n')
            if len(code_lines) > 30:
                code = '\n'.join(code_lines[:30]) + '\n// ...truncated for brevity...'
            logging.info(f"Generated code:\n{code}")

            # Generate code image
            image_path = Path("images") / "carbon.png"
            generate_code_image(code, str(image_path))
            logging.info(f"Code image generated at {image_path}")

            # Post tweet and image
            tweet_id = self.x_client.post_tweet(tweet, str(image_path))
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
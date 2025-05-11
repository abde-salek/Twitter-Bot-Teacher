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

# Load environment variables
load_dotenv()

class FlutterDailyBot:
    def __init__(self):
        self.groq = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.x_client = XAPI()
        self.concepts: List[str] = self._load_concepts()
        self.current_day: int = self._load_day()
        self.image_dir = Path("image_vault")
        self.image_dir.mkdir(exist_ok=True)
        
    def _load_concepts(self) -> List[str]:
        """Load concepts from JSON file"""
        concepts_file = Path("flutter_concepts.json")
        if not concepts_file.exists():
            raise FileNotFoundError("Missing flutter_concepts.json")
        return json.loads(concepts_file.read_text())
    
    def _load_day(self) -> int:
        """Load current day counter"""
        day_file = Path("day_counter.txt")
        try:
            return int(day_file.read_text().strip())
        except FileNotFoundError:
            return 1
            
    def _save_day(self):
        """Persist day counter"""
        Path("day_counter.txt").write_text(str(self.current_day + 1))
        
    def generate_code_example(self, concept: str) -> str:
        """Generate Flutter code explanation using Groq"""
        prompt = f"""Create a concise Flutter code example demonstrating:
        {concept}
        Include brief explanatory comments in Dart."""
        
        try:
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Code generation failed: {str(e)}")
            raise

    def generate_tweet_text(self, concept: str) -> str:
        """Generate educational tweet using Groq"""
        prompt = f"""Create engaging tweet about Flutter concept:
        {concept}
        Include 2 emojis and hashtags #Flutter #100DaysOfCode
        Keep technical but accessible."""
        
        try:
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Tweet generation failed: {str(e)}")
            raise

    def validate_tweet(self, tweet: str) -> Tuple[bool, List[str]]:
        """Validate tweet content"""
        issues = []
        if len(tweet) > 280:
            issues.append("Tweet exceeds 280 characters")
        if "#Flutter" not in tweet:
            issues.append("Missing #Flutter hashtag")
        if not any(char.isupper() for char in tweet):
            issues.append("No code examples detected")
        return (len(issues) == 0, issues)

    def daily_workflow(self):
        """Execute full daily workflow"""
        try:
            logging.info(f"Starting Day {self.current_day}")
            
            if self.current_day > len(self.concepts):
                logging.info("🎉 All concepts completed!")
                return
                
            concept = self.concepts[self.current_day - 1]
            logging.info(f"Concept: {concept}")
            
            # Generate code and image
            code = self.generate_code_example(concept)
            image_path = self.image_dir / f"day_{self.current_day}_code.png"
            generate_code_image(code, str(image_path))
            
            # Generate and validate tweet
            tweet = self.generate_tweet_text(concept)
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
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("flutter_daily.log"),
            logging.StreamHandler()
        ]
    )
    
    try:
        bot = FlutterDailyBot()
        bot.daily_workflow()
    except Exception as e:
        logging.critical(f"Critical failure: {str(e)}")
        raise
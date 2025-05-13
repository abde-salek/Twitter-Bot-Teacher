import logging
import os
import json
from pathlib import Path
from typing import List, Tuple
from groq import Groq
from dotenv import load_dotenv
from .post_tweet import XAPI

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

class FlutterDailyBot:
    def __init__(self):
        self.groq = Groq(CONSUMER_KEY=os.environ["GROQ_API_KEY"])
        self.x_client = XAPI()
        self.concepts: List[str] = self._load_concepts()
        self.current_day: int = self._load_day()
        
    def _load_concepts(self) -> List[str]:
        """Load concepts from JSON file"""
        concepts_file = Path("flutter_concepts.json")
        if not concepts_file.exists():
            raise FileNotFoundError("Missing flutter_concepts.json")
        try:
            return json.loads(concepts_file.read_text())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {concepts_file}: {str(e)}")
            raise
    
            try:
                return int(day_file.read_text().strip())
            except ValueError:
                logger.warning("Non-integer value found in day_counter.txt, defaulting to 1")
                return 1
        """Load current day counter"""
        day_file = Path("day_counter.txt")
        try:
            return int(day_file.read_text().strip())
        except FileNotFoundError:
            return 1
            
    def _save_day(self):
        """Persist day counter"""
        Path("day_counter.txt").write_text(str(self.current_day + 1))
        
    def generate_code_prompt(self, concept: str) -> str:
        """Generate Flutter code explanation using Groq"""
        prompt = f"""Create a concise Flutter code example demonstrating:
        {concept}
        Include brief explanatory comments."""
        
        try:
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise

    def generate_tweet_text(self, concept: str) -> str:
        """Generate educational tweet using Groq"""
        prompt = f"""Create engaging tweet about Flutter concept:
        {concept}
        Include 2 emojis and hashtags #Flutter #100DaysOfCode"""
        
        try:
            response = self.groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Tweet generation failed: {str(e)}")
            raise

    def validate_tweet(self, tweet: str) -> Tuple[bool, List[str]]:
        """Validate tweet content"""
        if len(tweet) > 280:
            return False, ["Tweet exceeds 280 characters"]
        if "#Flutter" not in tweet:
            return False, ["Missing #Flutter hashtag"]
        return True, []

    def daily_workflow(self):
        """Execute full daily workflow"""
        try:
            if self.current_day > len(self.concepts):
                logger.info("🎉 All concepts completed!")
                return
                
            concept = self.concepts[self.current_day - 1]
            logger.info(f"📆 Day {self.current_day}: {concept}")
            
            # Generate content
            code = self.generate_code_prompt(concept)
            tweet = self.generate_tweet_text(concept)
            
            # Validate and post
            valid, issues = self.validate_tweet(tweet)
            if valid:
                self.x_client.post_tweet(tweet)
                self._save_day()
                logger.info("✅ Tweet posted successfully")
            else:
                logger.warning(f"🚨 Validation issues: {', '.join(issues)}")
                
        except Exception as e:
            logger.error(f"🔥 Workflow failed: {str(e)}")
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
    
    bot = FlutterDailyBot()
    bot.daily_workflow()
# post_tweet.py
#
# This module handles posting tweets (with optional images) to Twitter/X using Tweepy.
# It supports both v1.1 (for media upload) and v2 (for tweet posting) APIs.
#
# Usage: Create an XAPI instance and call post_tweet(text, image_path).
# Requires Twitter API credentials in .env file.

import os
import logging
import tweepy
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables (Twitter API keys)
load_dotenv()

class XAPI:
    """
    Twitter/X API client for posting tweets with or without images.
    Handles authentication and error checking.
    """
    def __init__(self, mock_mode=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mock_mode = mock_mode
        
        if not mock_mode:
            self.CONSUMER_v1 = self._authenticate_v1()
            self.client_v2 = self._authenticate_v2()
            self._validate_credentials()
        else:
            self.logger.info("Running in mock mode - no actual tweets will be posted")
            self.CONSUMER_v1 = None
            self.client_v2 = None

    def _authenticate_v1(self):
        """Authenticate with Twitter API v1.1 (required for media upload)"""
        return tweepy.API(tweepy.OAuth1UserHandler(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
        ))

    def _authenticate_v2(self):
        """Authenticate with Twitter API v2 (for posting tweets)"""
        return tweepy.Client(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
        )

    def _validate_credentials(self):
        """Verify all required credentials are present in the environment."""
        missing = []
        if not os.getenv("CONSUMER_KEY"):
            missing.append("CONSUMER_KEY")
        if not os.getenv("CONSUMER_SECRET"):
            missing.append("CONSUMER_SECRET")
        if not os.getenv("ACCESS_TOKEN"):
            missing.append("ACCESS_TOKEN")
        if not os.getenv("ACCESS_TOKEN_SECRET"):
            missing.append("ACCESS_TOKEN_SECRET")
        
        if missing:
            raise ValueError(f"Missing Twitter credentials: {', '.join(missing)}")

    def post_tweet(self, text: str, image_path: Optional[str] = None) -> str:
        """
        Post a tweet with optional image.
        Args:
            text: Tweet text content
            image_path: Path to image file (PNG/JPG)
        Returns:
            str: ID of the posted tweet
        Raises:
            tweepy.TweepyException: For Twitter API errors
        """
        # Handle mock mode for testing without API keys
        if self.mock_mode:
            self.logger.info(f"MOCK: Would post tweet: {text}")
            if image_path:
                if Path(image_path).exists():
                    self.logger.info(f"MOCK: With image: {image_path}")
                else:
                    self.logger.warning(f"MOCK: Image not found: {image_path}, would post without image")
            return "mock_tweet_id_12345"
        
        media_ids = []
        
        try:
            # Handle image upload (if provided)
            if image_path:
                image_path = str(image_path)  # Convert Path objects
                if Path(image_path).exists():
                    self.logger.info(f"Uploading image: {image_path}")
                    media = self.CONSUMER_v1.media_upload(image_path)
                    media_ids.append(media.media_id)
                    self.logger.info(f"Media uploaded (ID: {media.media_id})")
                else:
                    self.logger.warning(f"Image file not found: {image_path}, posting tweet without image")

            # Post tweet (with or without image)
            self.logger.info("Posting tweet...")
            response = self.client_v2.create_tweet(
                text=text,
                media_ids=media_ids or None
            )
            
            tweet_id = response.data["id"]
            self.logger.info(f"Successfully posted tweet ID: {tweet_id}")
            return tweet_id
            
        except tweepy.TweepyException as e:
            self.logger.error(f"Twitter API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Posting failed: {str(e)}")
            raise

# Example usage for testing (run this file directly)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    try:
        # Use mock_mode=True for testing without actual API calls
        x = XAPI(mock_mode=True)
        x.post_tweet(
            text="Test tweet with image! 🚀 #Flutter",
            image_path="test_image.png"
        )
    except Exception as e:
        print(f"Error: {str(e)}")
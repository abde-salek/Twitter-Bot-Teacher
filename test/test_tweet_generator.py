# Test script for tweet_generator.py
from tweet_generator import generate_tweet

# Test Case 1: Test generate_tweet() for Day 1
print("Test Case 1: generate_tweet() for Day 1")
tweet = generate_tweet(1)
print(f"Generated Tweet: {tweet}")
# Check that the tweet is within 150 characters (excluding hashtags)
if "#" in tweet:
    text_part = tweet[:tweet.rfind("#")].strip()
else:
    text_part = tweet
assert len(text_part) <= 150, f"Tweet text (excluding hashtags) exceeds 150 characters: {len(text_part)}"
print("Tweet length check passed (≤150 characters excluding hashtags)")

# Test Case 2: Test generate_tweet() for Day 2 (to verify previous concept reference)
print("\nTest Case 2: generate_tweet() for Day 2")
tweet = generate_tweet(2)
print(f"Generated Tweet: {tweet}")
# Check that the tweet is within 150 characters (excluding hashtags)
if "#" in tweet:
    text_part = tweet[:tweet.rfind("#")].strip()
else:
    text_part = tweet
assert len(text_part) <= 150, f"Tweet text (excluding hashtags) exceeds 150 characters: {len(text_part)}"
print("Tweet length check passed (≤150 characters excluding hashtags)")
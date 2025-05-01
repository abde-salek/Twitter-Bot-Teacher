import tweepy
import os
from image_generator import find_latest_image

# Step 1: Define X API credentials (replace with your actual credentials)
API_KEY = "qZVYSmyPvTQ03HqNwPKkCoGWo" 
API_SECRET = "81NYXAE7ryvMxjUKNOkUKG7LN9f2pHRn0fY22PlZjf0tW6o6Oh"
ACCESS_TOKEN = "1916435753342509057-UTRQ8qgILYpdCMCj4Ts7jNwsPMX3oU"
ACCESS_TOKEN_SECRET = "Ec0dnydAtRUINtXi0IwWbyFZerzkFNyDKKbvsFrO9MHRX"

# Step 2: Authenticate with X API
# For tweeting (v2 API)
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# For media upload (v1.1 API)
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Step 3: Define the tweet_poster function
def tweet_poster(tweet_text="Here's a Flutter code snippet! #Flutter #Dart"):
    """
    Post a tweet with the latest generated image.
    
    Args:
        tweet_text (str): The text to include in the tweet.
    
    Returns:
        str: The ID of the posted tweet, or None if posting fails.
    """
    # Step 3.1: Find the latest image
    image_path = find_latest_image()
    if not image_path:
        raise FileNotFoundError("No image found in the image-daily folder.")
    
    # Step 3.2: Verify the image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    # Step 3.3: Upload the image to X using API v1.1
    media = api.media_upload(image_path)
    
    # Step 3.4: Post the tweet with the image using API v2
    response = client.create_tweet(text=tweet_text, media_ids=[media.media_id])
    
    # Step 3.5: Return the tweet ID
    return response.data['id']
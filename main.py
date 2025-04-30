# Purpose: Coordinates the entire process by calling each sub-project in sequence.

# Step 1: Import required modules from other files
# We import the necessary functions from each sub-project file
from day_tracker import load_day, save_day
from tweet_generator import generate_tweet, flutter_concepts
from code_generator import generate_code_snippet
from image_generator import generate_code_image, find_latest_image
from tweet_poster import post_tweet

# Step 2: Define the run_daily_bot function
# This function coordinates the entire daily process of posting a Flutter tweet
def run_daily_bot():
    """
    Coordinate the daily bot process by calling each sub-project in sequence.
    """
    # Step 2.1: Use a try-except block to catch and report errors
    # This ensures we can debug issues without the script crashing silently
    try:
        # Step 2.2: Load the current day using day_tracker
        # This tells us which day of the 100-day challenge we're on
        day = load_day()
        print(f"Current day: {day}")
        
        # Step 2.3: Generate the tweet text using tweet_generator
        # This creates the tweet text describing the Flutter concept (without code)
        tweet_text = generate_tweet(day)
        print(f"Generated Tweet for Day {day}:\n{tweet_text}")
        
        # Step 2.4: Get the current Flutter concept and generate the code snippet
        # We use the tweet text and concept to generate a relevant code snippet
        concept = flutter_concepts[day - 1]
        code_snippet = generate_code_snippet(tweet_text, concept)
        print(f"Generated Code Snippet:\n{code_snippet}")
        
        # Step 2.5: Generate the code image using image_generator
        # This creates an image of the code snippet and returns its file path
        image_path = generate_code_image(code_snippet)
        
        # Step 2.6: Find the latest generated image
        # We ensure we have the correct image path for posting
        latest_image_path = find_latest_image()
        if not latest_image_path:
            raise FileNotFoundError("No image found in image-daily folder")
        
        # Step 2.7: Post the tweet with the image using tweet_poster
        # This posts the tweet to Twitter with the attached code image
        post_tweet(tweet_text, latest_image_path)
        
        # Step 2.8: Clean up the image file
        # We remove the image to save disk space after posting
        import os
        os.remove(latest_image_path)
        
        # Step 2.9: Save the next day using day_tracker
        # We increment the day and save it for the next run (loop back to 1 after 100)
        next_day = day + 1 if day < 100 else 1
        save_day(next_day)
    
    # Step 2.10: Catch and report any errors during the process
    # This ensures we know what went wrong if any step fails
    except Exception as e:
        print(f"Error in daily bot: {str(e)}")

# Step 3: Run the bot when the script is executed
# This makes the script executable with a single command (python main.py)
if __name__ == "__main__":
    run_daily_bot()
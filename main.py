import os
import time
import glob
from code_generator import generate_code_snippet
from image_generator import generate_code_image, IMAGE_DAILY_FOLDER
from tweet_poster import tweet_poster

def main():
    try:
        # Step 1: Generate the code snippet and tweet text
        code_snippet, tweet_text = generate_code_snippet()
        print(f"Generated code snippet:\n{code_snippet}")
        print(f"Suggested tweet text: {tweet_text}")

        # Step 2: Generate the image
        image_path = generate_code_image(code_snippet)
        print(f"Generated image at: {image_path}")

        # Step 3: Post the tweet with the dynamic tweet text
        tweet_id = tweet_poster(tweet_text=tweet_text)
        print(f"Tweet posted successfully with ID: {tweet_id}")

        # Step 4: Clean up old images
        for file in glob.glob(os.path.join(IMAGE_DAILY_FOLDER, "carbon*.png")):
            if file != image_path:  # Don't delete the file we just tweeted
                try:
                    os.remove(file)
                    print(f"Cleaned up old file: {file}")
                except Exception as e:
                    print(f"Error cleaning up file {file}: {e}")

        # Step 5: Log success
        with open("success_log.txt", "a") as f:
            f.write(f"{time.ctime()}: Tweet posted successfully with ID {tweet_id}\n")

    except Exception as e:
        print(f"Error occurred: {e}")
        with open("error_log.txt", "a") as f:
            f.write(f"{time.ctime()}: {str(e)}\n")
        raise

if __name__ == "__main__":
    main()
# Step 1: Import required modules
from groq import Groq
import time

# Step 2: Initialize the Groq API client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Step 3: Define the generate_code_snippet function
def generate_code_snippet(tweet_text, concept):
    """
    Generate a minimal Dart code snippet using the tweet text and concept as context.
    
    Args:
        tweet_text (str): The tweet text describing the concept (e.g., "Meet Scaffold. It's like a house. Gives structure.").
        concept (str): The Flutter concept for the day (e.g., "Scaffold Layout Basics").
    
    Returns:
        str: The generated Dart code snippet with comments.
    """
    # Step 3.1: Create the prompt for the Groq API
    # Updated prompt to allow up to 10 lines
    prompt = (
        "You are an AI assistant designed to generate a minimal Dart code snippet for a Flutter concept. "
        "The code snippet must: "
        "1. Demonstrate only the essential elements of the concept. "
        "2. Do not include imports, main(), or app structure unless they are part of the concept. "
        "3. Include comments on almost every line explaining each section of the code. "
        "4. Be between 3 and 10 lines long, including comments. Do not exceed 10 lines. "
        f"The Flutter concept is '{concept}'. The tweet describing this concept is: '{tweet_text}'. "
        "Generate a minimal Dart code snippet with comments that is 3-10 lines long. "
        "Return only the code snippet with comments, without any additional text or formatting."
    )
    
    # Step 3.2: Call the Groq API with retry logic
    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        # Step 3.3: Attempt to call the Groq API to generate the code snippet
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            code_snippet = chat_completion.choices[0].message.content
            # Step 3.4: Return the generated code snippet
            return code_snippet
        except Exception as e:
            # Step 3.5: Handle API call failures by retrying
            attempt += 1
            if attempt == max_retries:
                # Step 3.6: If all retries fail, raise the exception
                raise Exception(f"Failed to generate code snippet after {max_retries} attempts: {str(e)}")
            print(f"Retrying API call ({attempt}/{max_retries}) due to error: {str(e)}")
            time.sleep(2 * attempt)
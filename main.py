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
import time
import argparse
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
    def __init__(self, mock_mode=False):
        # Initialize LLM and Twitter/X API clients
        self.mock_mode = mock_mode
        if not mock_mode:
            try:
                self.groq = Groq(api_key=os.environ["GROQ_API_KEY"])
            except Exception as e:
                logging.warning(f"Failed to initialize Groq client: {str(e)}. Using mock mode for Groq.")
                self.mock_mode = True
                self.groq = None
        else:
            logging.info("Running in mock mode - no actual API calls will be made")
            self.groq = None
            
        self.x_client = XAPI(mock_mode=mock_mode)
        self.concepts: List[str] = self._load_concepts()
        self.current_day = self._load_day()
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
            # Create an empty concepts file if it doesn't exist
            concepts_file.write_text("[]")
            return []
        return json.loads(concepts_file.read_text())
    
    def _load_day(self) -> int:
        """
        Load current day counter from day_counter.txt.
        
        The day counter tracks progress through the concepts list.
        To restart from the beginning, set the file content to "1".
        
        Returns:
            int: Current day number (1-based)
        """
        day_file = Path("data/day_counter.txt")
        try:
            # Try to read the file with different encodings to handle potential encoding issues
            try:
                # First try with default encoding
                return int(day_file.read_text().strip())
            except UnicodeDecodeError:
                # If that fails, try with explicit encodings
                try:
                    with open(day_file, 'r', encoding='utf-8') as f:
                        return int(f.read().strip())
                except:
                    try:
                        with open(day_file, 'r', encoding='ascii') as f:
                            return int(f.read().strip())
                    except:
                        # If all encoding attempts fail, recreate the file
                        logging.warning("Encoding issue with day_counter.txt. Recreating file.")
                        with open(day_file, 'w', encoding='ascii') as f:
                            f.write("1")
                        return 1
        except FileNotFoundError:
            # Create the data directory if it doesn't exist
            Path("data").mkdir(exist_ok=True)
            # Create the day counter file with initial value 1
            with open(day_file, 'w', encoding='ascii') as f:
                f.write("1")
            return 1
        except ValueError:
            # If the file exists but contains invalid data, recreate it
            logging.warning("Invalid data in day_counter.txt. Recreating file.")
            with open(day_file, 'w', encoding='ascii') as f:
                f.write("1")
            return 1
            
    def _save_day(self):
        """
        Increment and persist day counter.
        
        Called automatically after each successful post to track progress.
        The counter is stored in day_counter.txt.
        """
        # Write with explicit ASCII encoding to avoid encoding issues
        with open(Path("data/day_counter.txt"), 'w', encoding='ascii') as f:
            f.write(str(self.current_day + 1))
        
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
        # If in mock mode, return a sample code snippet
        if self.mock_mode or self.groq is None:
            logging.info(f"Mock mode: Generating sample code for {concept}")
            return f"""// Sample code for {concept}
// This is a placeholder generated in mock mode
// No actual API calls were made

// Simple Flutter widget demonstrating {concept}
class Example extends StatelessWidget {{
  // Constructor with required parameters
  const Example({{Key? key}}) : super(key: key);
  
  // Build method returns the widget tree
  @override
  Widget build(BuildContext context) {{
    // Return a container with styling
    return Container(
      // Apply styling related to {concept}
      child: Text('Example of {concept}'),
    );
  }}
}}"""

        # Clean concept name to make it more manageable
        clean_concept = concept.strip()
        # For concepts with descriptions, simplify
        if ' - ' in clean_concept:
            clean_concept = clean_concept.split(' - ')[0].strip()
        if ' using ' in clean_concept:
            clean_concept = clean_concept.split(' using ')[0].strip() 
        
        # Create widget-specific prompt for common widgets
        widget_specific_prompt = ""
        if any(widget in clean_concept.lower() for widget in ['sliver', 'list', 'grid', 'custom']):
            widget_specific_prompt = "Focus specifically on creating a minimal example of a ListView, SliverList, or GridView with custom tiles."
        elif "backdrop" in clean_concept.lower():
            widget_specific_prompt = "Focus specifically on creating a minimal BackdropFilter example with a blur effect."
        elif "animation" in clean_concept.lower():
            widget_specific_prompt = "Focus specifically on creating a minimal animation example."
        
        prompt = f"""Create the SMALLEST possible Flutter code snippet to demonstrate:
        {clean_concept}

STRICT RULES:
- You CAN use ready-structured code examples from official documentation (pub.dev) if appropriate
- You MUST include at least one comprehensive comment explaining the usage of {clean_concept}
- 500 characters of code MAX. If you can do it in fewer, do so.
- Every 3 lines, at least one must be a comment (//).
- Every element must have a comment explaining usage.
- Only the core logic. No setup, no main(), no imports unless required for the concept.
- Use clear variable names and concise comments.
- IMPORTANT: Take your time to think carefully about the best way to showcase {clean_concept} in a minimal, educational way.
- Output ONLY the Dart code, nothing else.

{widget_specific_prompt}

If you need documentation on {clean_concept}, you may reference pub.dev or Flutter.dev docs to create accurate code."""
        
        for attempt in range(7):  # Increased number of attempts
            try:
                # Generate code using Groq LLM with higher temperature for creativity
                response = self.groq.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an expert Flutter developer. Take your time to think deeply about the best solution before responding. Quality is more important than speed."},
                        {"role": "user", "content": prompt}
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.75,  # Slightly higher temperature for more thoughtful outputs
                    max_tokens=2000,   # Increased token limit for more thinking space
                    top_p=0.9          # More focused sampling
                )
                code = response.choices[0].message.content.strip()
                code = self.clean_code(code)
                
                # Enforce 500 character max
                if len(code) > 500:
                    code = code[:500] + '\n// ...truncated for brevity...'
                
                # Validate code meets educational requirements
                lines = [line for line in code.split('\n') if line.strip()]
                comments = [line for line in lines if '//' in line]
                
                # Check if code has more than 30 lines - if so, retry
                if len(lines) > 30:
                    logging.warning(f"Attempt {attempt+1}: Code too long with {len(lines)} lines. Retrying...")
                    continue
                
                # Check every 3 lines for a comment
                valid = len(lines) <= 3 or all(any('//' in l for l in lines[i:i+3]) for i in range(0, len(lines), 3))
                
                # Check every element has a comment - relaxed constraint
                # Only check if there's at least one comment for every 3 lines of code
                element_has_comment = len(comments) >= max(1, len(lines) // 3)
                
                if len(code) <= 500 and (valid or element_has_comment):
                    # Ensure concept is clearly explained in comments
                    if clean_concept.lower() not in ''.join(comments).lower():
                        code = f"// This example demonstrates {clean_concept}\n" + code
                    return code
                    
                logging.warning(f"Attempt {attempt+1}: Code did not meet constraints. Length: {len(code)}, Valid: {valid}, Element comments: {element_has_comment}")
            except Exception as e:
                logging.error(f"Code generation failed on attempt {attempt+1}: {str(e)}")
                
        # Create a widget-specific fallback based on concept type
        if "sliver" in clean_concept.lower() or "list" in clean_concept.lower() or "grid" in clean_concept.lower():
            return self._generate_list_grid_fallback(clean_concept)
        elif "backdrop" in clean_concept.lower() or "filter" in clean_concept.lower():
            return self._generate_backdrop_fallback(clean_concept)
        elif "animation" in clean_concept.lower():
            return self._generate_animation_fallback(clean_concept)
        else:
            # General fallback for other concepts
            return f"""// Example for {clean_concept} in Flutter
// Below is a minimal implementation example

// Import required packages
import 'package:flutter/material.dart';

// Basic implementation of {clean_concept}
Widget build(BuildContext context) {{
  // A simple {clean_concept} example
  return Container(
    // Container with basic styling
    padding: EdgeInsets.all(8.0),
    // Example child widget
    child: Text('Example of {clean_concept}'),
  );
}}"""

    def clean_code(self, code: str) -> str:
        """
        Clean up code formatting.
        
        Args:
            code (str): Raw code from LLM
            
        Returns:
            str: Cleaned code with consistent formatting
        """
        return code.strip()

    def _generate_list_grid_fallback(self, concept):
        """Generate a fallback code snippet for List/Grid concepts"""
        return f"""// Example of {concept} in Flutter
// A simple SliverList implementation

import 'package:flutter/material.dart';

// Use CustomScrollView with a SliverList for efficient scrolling
Widget build(BuildContext context) {{
  // Return CustomScrollView containing slivers
  return CustomScrollView(
    // Add sliver widgets to the viewport
    slivers: <Widget>[
      // SliverAppBar gives a flexible app bar
      SliverAppBar(title: Text('{concept} Example')),
      
      // SliverList for list items with custom delegate
      SliverList(
        // Use SliverChildBuilderDelegate for efficient item rendering
        delegate: SliverChildBuilderDelegate(
          // Builder function creates items on demand
          (context, index) => ListTile(
            // Display the list item index
            title: Text('Item ${{index}}'),
          ),
          // Define the number of items
          childCount: 50,
        ),
      ),
    ],
  );
}}"""

    def _generate_backdrop_fallback(self, concept):
        """Generate a fallback code snippet for BackdropFilter concepts"""
        return f"""// Example of {concept} in Flutter
// Demonstrates applying a blur effect with BackdropFilter

import 'package:flutter/material.dart';
import 'dart:ui'; // Required for ImageFilter

// BackdropFilter widget applies effects to everything beneath it
Widget build(BuildContext context) {{
  // Stack allows overlapping of widgets
  return Stack(
    children: <Widget>[
      // Background image or content
      Image.network('https://picsum.photos/250'),
      
      // BackdropFilter applies visual effects to background
      BackdropFilter(
        // ImageFilter.blur creates a Gaussian blur effect
        filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
        // Child widget appears above the blurred background
        child: Container(
          // Semi-transparent overlay
          color: Colors.black.withOpacity(0.2),
          // Center text on the blurred background
          child: Center(
            child: Text(
              '{concept}',
              style: TextStyle(color: Colors.white),
            ),
          ),
        ),
      ),
    ],
  );
}}"""

    def _generate_animation_fallback(self, concept):
        """Generate a fallback code snippet for Animation concepts"""
        return f"""// Example of {concept} in Flutter
// Simple animation using AnimatedContainer

import 'package:flutter/material.dart';

// StatefulWidget needed for animation state
class AnimationExample extends StatefulWidget {{
  @override
  _AnimationExampleState createState() => _AnimationExampleState();
}}

class _AnimationExampleState extends State<AnimationExample> {{
  // Toggle for animation state
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {{
    // AnimatedContainer handles implicit animations
    return GestureDetector(
      // Toggle animation on tap
      onTap: () => setState(() => _expanded = !_expanded),
      // AnimatedContainer animates between states
      child: AnimatedContainer(
        // Animation duration
        duration: Duration(milliseconds: 300),
        // Properties that will animate
        width: _expanded ? 200.0 : 100.0,
        height: _expanded ? 200.0 : 100.0,
        color: _expanded ? Colors.blue : Colors.red,
        // Curve adds personality to the animation
        curve: Curves.easeInOut,
      ),
    );
  }}
}}"""

    def validate_tweet(self, tweet: str, concept: str) -> Tuple[bool, List[str]]:
        """
        Validate tweet content for proper formatting, explanation and hashtags.
        
        Args:
            tweet (str): Tweet text to validate
            concept (str): The concept being tweeted about
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        # Length checks
        if len(tweet) > 280:
            issues.append("Tweet exceeds 280 characters")
        if len(tweet) < 170 or len(tweet) > 200:
            issues.append(f"Tweet length ({len(tweet)}) outside target range (170-200 characters)")
            
        # Formatting checks
        day_prefix = f"Day {self.current_day}:"
        if not tweet.startswith(day_prefix):
            issues.append(f"Tweet doesn't start with '{day_prefix}'")
            
        # Content checks
        if not concept.lower() in tweet.lower():
            issues.append(f"Tweet doesn't mention concept '{concept}'")
            
        # Explanation check - tweet should contain a proper explanation
        # First, remove the day prefix and concept name to focus on explanation part
        content_only = tweet.lower().replace(day_prefix.lower(), "").replace(concept.lower(), "")
        
        # Check for explanation keywords
        explanation_words = ["is", "helps", "allows", "enables", "lets", "creates", "provides", "makes", "ensures", "manages"]
        has_explanation_keywords = any(word in content_only for word in explanation_words)
        
        # Check explanation length - after removing prefix, concept and hashtags, should have substantial content
        hashtag_text = ' '.join([word for word in tweet.split() if word.startswith('#')])
        explanation_text = tweet.replace(day_prefix, "").replace(concept, "").replace(hashtag_text, "")
        has_enough_explanation = len(explanation_text.split()) >= 10  # At least 10 words of explanation
        
        if not (has_explanation_keywords and has_enough_explanation):
            issues.append("Tweet doesn't contain a sufficient explanation of the concept")
            
        # Hashtag checks
        if "#Flutter" not in tweet:
            issues.append("Missing #Flutter hashtag")
        if "#100DaysOfCode" not in tweet:
            issues.append("Missing #100DaysOfCode hashtag")
        
        # Third hashtag check
        hashtags = [word for word in tweet.split() if word.startswith('#')]
        if len(hashtags) < 3:
            issues.append("Missing third technical hashtag")
            
        # Emoji checks - making it optional (0, 1, or 2+ emojis are all acceptable)
        # Original code required at least 2 emojis
        emoji_count = sum(1 for char in tweet if ord(char) > 0x1F000)
        # No validation error for emojis - they are now optional
        # if emoji_count < 2:
        #    issues.append(f"Contains only {emoji_count} emojis, need at least 2")
            
        return (len(issues) == 0, issues)

    def generate_tweet_text(self, concept: str) -> str:
        """
        Generate educational tweet using AI.
        
        Creates an engaging tweet about the Flutter concept that:
        - Starts with "Day X:"
        - Is between 170-200 characters
        - Includes emojis and hashtags
        - Is technical but accessible
        - Explains what the concept does in detail
        
        Args:
            concept (str): The Flutter concept to tweet about
            
        Returns:
            str: Generated tweet text
        """
        # If in mock mode, return a sample tweet
        if self.mock_mode or self.groq is None:
            logging.info(f"Mock mode: Generating sample tweet for {concept}")
            # Include a random tech hashtag in mock mode
            random_tech_hashtags = ["#MobileDev", "#DartLang", "#AppDev", "#CrossPlatform", "#UI", "#UX"]
            import random
            random_hashtag = random.choice(random_tech_hashtags)
            mock_tweet = f"Day {self.current_day}: {concept} in Flutter provides developers with powerful tools to create dynamic, responsive interfaces that adapt to different screen sizes and user interactions. Try it today! #Flutter #100DaysOfCode {random_hashtag}"
            
            # Validate even mock tweets
            is_valid, issues = self.validate_tweet(mock_tweet, concept)
            if not is_valid:
                logging.warning(f"Mock tweet has issues: {issues}")
                
            return mock_tweet
            
        # Random tech hashtag options
        tech_hashtags = [
            "#DartLang", "#MobileDev", "#AppDev", "#CrossPlatform", "#CodeSnippet", 
            "#UI", "#UX", "#Coding", "#DevTools", "#AppDesign", "#FrontEnd", 
            "#MobileApps", "#Programming", "#DevLife", "#TechTip", "#CodeTip", 
            "#DevTips", "#MobileUI", "#SoftwareDev", "#TechStack"
        ]
        # Choose a random hashtag
        import random
        random_tech_hashtag = random.choice(tech_hashtags)

        # Calculate reserved characters for fixed content
        day_prefix = f"Day {self.current_day}: "
        hashtags = f" #Flutter #100DaysOfCode {random_tech_hashtag}"
        reserved_chars = len(day_prefix) + len(hashtags) + 10  # Add extra buffer for emojis and spaces
        
        # Calculate available characters for the actual content
        max_content_chars = 190 - reserved_chars  # Target 190 chars total (middle of 170-200 range)
        min_content_chars = 160 - reserved_chars  # Minimum content to stay above 170 total

        # Create a more restrictive prompt with explicit length constraints
        basic_prompt = f"""Create an engaging tweet about Flutter concept:
        {concept}
        
        STRICT FORMAT RULES:
        - Start with EXACTLY "Day {self.current_day}:"
        - The tweet MUST be between 170 and 200 characters TOTAL, counting everything
        - The content description part should be {min_content_chars}-{max_content_chars} characters
        - Include at least one emoji
        - MUST include these exact hashtags at the end: "#Flutter #100DaysOfCode {random_tech_hashtag}"
        - MUST explain what {concept} is and does concisely
        - Keep technical but accessible
        
        Example of proper length and format:
        "Day X: ConceptName helps developers create responsive layouts with minimal code. Perfect for building cross-platform interfaces! 💻 #Flutter #100DaysOfCode #UI"
        
        DO NOT exceed 200 characters total. Count carefully."""
            
        closest_tweet = None
        closest_diff = float('inf')
        closest_length = 0
        
        # First round of attempts (up to 5)
        for attempt in range(5):
            try:
                # Generate tweet using Groq LLM with thoughtful parameters
                response = self.groq.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a technical writer who creates short, concise tweets about programming concepts. Your most important task is to carefully count characters and stay between 170-200 characters TOTAL. Verify the exact character count before finalizing your response."},
                        {"role": "user", "content": basic_prompt}
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.5,  # Lower temperature for more precise adherence to format
                    max_tokens=1000,   # Increased token limit
                    top_p=0.9          # More focused sampling
                )
                tweet = response.choices[0].message.content.strip()
                
                # Post-processing to enforce constraints
                tweet = self._enforce_tweet_constraints(tweet, day_prefix, concept, hashtags)
                
                # Validate tweet against our rules
                is_valid, issues = self.validate_tweet(tweet, concept)
                
                # Log character count
                length = len(tweet)
                logging.info(f"Generated tweet length: {length} characters")
                
                if is_valid:
                    logging.info(f"Valid tweet generated on attempt {attempt+1}")
                    return tweet
                    
                # Keep track of closest attempt (fewest issues and closest to target length)
                if length >= 170 and length <= 200:
                    logging.info(f"Tweet length OK: {length}")
                    if len(issues) < closest_diff:
                        closest_tweet = tweet
                        closest_diff = len(issues)
                        closest_length = length
                else:
                    logging.warning(f"Tweet length issue: {length}")
                    
                if closest_tweet is None or (len(issues) < closest_diff and 160 <= length <= 220):
                    closest_tweet = tweet
                    closest_diff = len(issues)
                    closest_length = length
                
                # Log validation issues
                logging.warning(f"Attempt {attempt+1}: Tweet failed validation. Issues: {issues}")
                    
            except Exception as e:
                logging.error(f"Tweet generation failed on attempt {attempt+1}: {str(e)}")
                
        logging.warning("No valid tweet after first 5 attempts. Starting second phase with detailed instructions.")
        
        # Second round - try with more detailed prompting (up to 3 more attempts)
        improved_prompt = f"""Create an engaging tweet about Flutter concept: {concept}

CRITICAL LENGTH REQUIREMENT: The ENTIRE tweet must be EXACTLY between 170 and 200 characters (currently targeting 185).

STRICT FORMAT RULES:
1. MUST start with exactly "Day {self.current_day}:" 
2. MUST be between 170 and 200 characters total - THIS IS THE MOST IMPORTANT RULE
3. MUST include at least one emoji (like 🚀, 💻, 📱)
4. MUST include these hashtags AT THE END: #Flutter #100DaysOfCode {random_tech_hashtag}
5. MUST provide a concise explanation of what {concept} does

Here is a template with the correct format (fill in only the [description] part):
"Day {self.current_day}: {concept} [description with emoji] #Flutter #100DaysOfCode {random_tech_hashtag}"

The [description] part should be approximately {min_content_chars}-{max_content_chars} characters.

BEFORE SUBMITTING: Count the EXACT number of characters in your tweet to ensure it's between 170-200.

Example of correct length:
"Day 10: ListView in Flutter enables scrollable lists with customizable items, perfect for displaying data collections efficiently. 📱 #Flutter #100DaysOfCode #UI"
(This example is exactly 184 characters)"""
        
        for attempt in range(3):
            try:
                # Generate improved tweet using Groq LLM with thoughtful parameters
                response = self.groq.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a technical writer who creates short, concise tweets about programming concepts. Your most important task is to CAREFULLY COUNT CHARACTERS and stay between 170-200 characters TOTAL. Count every character, including spaces and hashtags. Triple-check your count before submitting."},
                        {"role": "user", "content": improved_prompt}
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.4,   # Even lower temperature for more controlled output
                    max_tokens=1000,   # Increased token limit
                    top_p=0.9          # More focused sampling
                )
                tweet = response.choices[0].message.content.strip()
                
                # Normalize format (remove quotes if present)
                if tweet.startswith('"') and tweet.endswith('"'):
                    tweet = tweet[1:-1]
                
                # Post-processing to enforce constraints
                tweet = self._enforce_tweet_constraints(tweet, day_prefix, concept, hashtags)
                
                # Validate tweet
                is_valid, issues = self.validate_tweet(tweet, concept)
                
                # Log character count
                length = len(tweet)
                logging.info(f"Generated tweet length (phase 2): {length} characters")
                
                if is_valid:
                    logging.info(f"Valid tweet generated on second phase attempt {attempt+1}")
                    return tweet
                    
                logging.warning(f"Second phase attempt {attempt+1}: Tweet failed validation. Issues: {issues}")
                
                # Update closest if this attempt is better
                if length >= 170 and length <= 200:
                    logging.info(f"Tweet length OK: {length}")
                    if len(issues) < closest_diff:
                        closest_tweet = tweet
                        closest_diff = len(issues)
                        closest_length = length
                else:
                    if closest_tweet is None or (len(issues) < closest_diff and abs(185 - length) < abs(185 - closest_length)):
                        closest_tweet = tweet
                        closest_diff = len(issues)
                        closest_length = length
                    
            except Exception as e:
                logging.error(f"Second phase tweet generation failed on attempt {attempt+1}: {str(e)}")
        
        # Third round - final attempt with auto-correction
        logging.warning("No valid tweet after 8 attempts. Starting final attempt with manual corrections.")
        
        # If we have a close candidate, try to fix it
        if closest_tweet:
            logging.info("Attempting to fix closest candidate tweet")
            
            # Apply fixes to make it valid
            fixed_tweet = self._fix_tweet(closest_tweet, concept, day_prefix, hashtags)
            is_valid, issues = self.validate_tweet(fixed_tweet, concept)
            
            if is_valid:
                logging.info("Successfully fixed tweet to meet all validation criteria")
                return fixed_tweet
            else:
                logging.warning(f"Failed to fix tweet. Remaining issues: {issues}")
        
        # Ultimate fallback - create a simple template-based tweet
        try:
            final_tweet = f"Day {self.current_day}: {concept} in Flutter helps developers create efficient applications by managing resources and UI components in a structured way. Perfect for modern app development! 🚀 #Flutter #100DaysOfCode {random_tech_hashtag}"
            
            # Check length and adjust if needed
            if len(final_tweet) < 170:
                # Add more descriptive content
                final_tweet = f"Day {self.current_day}: {concept} in Flutter helps developers create more efficient and responsive applications by intelligently managing resources and UI components in a structured and optimized way. Perfect for modern app development! 🚀 #Flutter #100DaysOfCode {random_tech_hashtag}"
            elif len(final_tweet) > 200:
                # Trim descriptive content while maintaining explanation
                final_tweet = f"Day {self.current_day}: {concept} in Flutter helps developers create efficient apps by managing UI components effectively. Great for modern app development! 🚀 #Flutter #100DaysOfCode {random_tech_hashtag}"
            
            # Validate one more time
            is_valid, issues = self.validate_tweet(final_tweet, concept)
            if is_valid:
                logging.info("Valid tweet generated on final attempt with manual template")
                return final_tweet
                
            logging.warning(f"Final template tweet still has issues: {issues}")
        except Exception as e:
            logging.error(f"Final tweet attempt failed: {str(e)}")
        
        logging.warning("All tweet generation attempts failed. Using best available tweet or fallback.")
        
        # Use the closest valid tweet we found or fall back to a template
        if closest_tweet and 160 <= len(closest_tweet) <= 220:
            logging.info("Using closest tweet from previous attempts")
            return closest_tweet
            
        # Ultimate fallback
        fallback = f"Day {self.current_day}: {concept} in Flutter provides tools to create more efficient and responsive applications. It simplifies UI operations and improves performance. #Flutter #100DaysOfCode {random_tech_hashtag}"
        return fallback

    def _enforce_tweet_constraints(self, tweet: str, day_prefix: str, concept: str, hashtags: str) -> str:
        """
        Enforce tweet constraints to ensure it meets formatting requirements.
        
        Args:
            tweet (str): Original tweet text
            day_prefix (str): Day prefix that should start the tweet
            concept (str): The Flutter concept
            hashtags (str): Hashtags that should be included
            
        Returns:
            str: Processed tweet that meets constraints
        """
        # Ensure Day X: prefix is present and correct
        if not tweet.startswith(day_prefix):
            # If there's another day prefix format, replace it
            if "day" in tweet.lower() and ":" in tweet.split("\n")[0].lower():
                # Extract the tweet content after the colon
                parts = tweet.split(":", 1)
                if len(parts) > 1:
                    tweet = day_prefix + parts[1].strip()
                else:
                    tweet = day_prefix + tweet[10:].strip()  # Approximate fix
            else:
                tweet = day_prefix + tweet
        
        # Ensure hashtags are present at the end
        required_hashtags = ["#Flutter", "#100DaysOfCode"]
        for hashtag in required_hashtags:
            if hashtag not in tweet:
                tweet = tweet + " " + hashtag
        
        # Add the random tech hashtag if missing
        random_tag = hashtags.split()[-1]
        if random_tag not in tweet:
            tweet = tweet + " " + random_tag
        
        # Ensure concept is mentioned
        if concept.lower() not in tweet.lower():
            # If concept is missing, try to add it after the day prefix
            parts = tweet.split(":", 1)
            if len(parts) > 1:
                tweet = parts[0] + ": " + concept + " " + parts[1].strip()
        
        # Check length and trim if needed
        if len(tweet) > 200:
            # Find the position to trim (before hashtags)
            hashtag_pos = min(tweet.find("#Flutter"), tweet.find("#100DaysOfCode"))
            if hashtag_pos > 0:
                # Trim the content part before hashtags
                content = tweet[:hashtag_pos].strip()
                # Trim to leave room for hashtags
                max_content_len = 200 - len(hashtags) - 5  # 5 chars of buffer
                if len(content) > max_content_len:
                    content = content[:max_content_len-3].strip() + "..."
                tweet = content + " " + hashtags.strip()
        
        # Remove any line breaks or extra spaces
        tweet = ' '.join(tweet.split())
        
        return tweet
        
    def _fix_tweet(self, tweet: str, concept: str, day_prefix: str, hashtags: str) -> str:
        """
        Apply fixes to a tweet that's close to meeting requirements.
        
        Args:
            tweet (str): Tweet to fix
            concept (str): Flutter concept
            day_prefix (str): Day prefix
            hashtags (str): Required hashtags
            
        Returns:
            str: Fixed tweet
        """
        # Step 1: Ensure proper prefix
        if not tweet.startswith(day_prefix):
            tweet = day_prefix + tweet.split(":", 1)[-1].strip() if ":" in tweet else day_prefix + tweet
        
        # Step 2: Ensure concept is mentioned
        if concept.lower() not in tweet.lower():
            parts = tweet.split(":", 1)
            tweet = parts[0] + ": " + concept + " " + parts[1].strip() if len(parts) > 1 else tweet
        
        # Step 3: Ensure all hashtags are present at the end
        required_hashtags = ["#Flutter", "#100DaysOfCode"]
        hashtag_part = " ".join([tag for tag in tweet.split() if tag.startswith("#")])
        content_part = " ".join([word for word in tweet.split() if not word.startswith("#")])
        
        # Rebuild the hashtag part ensuring all required hashtags are present
        new_hashtags = []
        for tag in required_hashtags:
            if tag not in hashtag_part:
                new_hashtags.append(tag)
        
        # Add the random hashtag if needed
        random_tag = hashtags.split()[-1]
        if random_tag not in hashtag_part:
            new_hashtags.append(random_tag)
        
        # Combine existing and missing hashtags
        combined_hashtags = " ".join([tag for tag in tweet.split() if tag.startswith("#")] + new_hashtags)
        
        # Step 4: Add emoji if none exists
        emoji_exists = any(ord(char) > 0x1F000 for char in tweet)
        emoji_to_add = " 🚀" if not emoji_exists else ""
        
        # Step 5: Rebuild tweet and check length
        fixed_tweet = content_part + emoji_to_add + " " + combined_hashtags
        
        # Step 6: Adjust length
        if len(fixed_tweet) < 170:
            # Too short, add more descriptive content
            concept_pos = fixed_tweet.find(concept)
            if concept_pos > 0:
                # Add more description after the concept
                insert_pos = concept_pos + len(concept)
                fixed_tweet = fixed_tweet[:insert_pos] + " helps developers create efficient applications" + fixed_tweet[insert_pos:]
        elif len(fixed_tweet) > 200:
            # Too long, trim the middle content
            hashtag_pos = min(
                fixed_tweet.find("#Flutter") if "#Flutter" in fixed_tweet else 999,
                fixed_tweet.find("#100DaysOfCode") if "#100DaysOfCode" in fixed_tweet else 999
            )
            if hashtag_pos < 999:
                # Trim content before hashtags
                content = fixed_tweet[:hashtag_pos].strip()
                max_content_len = 200 - len(combined_hashtags) - 5
                if len(content) > max_content_len:
                    content = content[:max_content_len-3].strip() + "..."
                fixed_tweet = content + " " + combined_hashtags
        
        return fixed_tweet

    def fetch_random_flutter_concept_online(self) -> str:
        """
        Use Groq LLM to fetch a random, modern Flutter concept from the web (not from a static list).
        Returns:
            str: A random Flutter concept
        """
        # If in mock mode, return a sample concept
        if self.mock_mode or self.groq is None:
            # Generate a concept that's not in the existing list
            sample_concepts = [
                "Flutter Riverpod Generators",
                "Flutter Custom Shader Effects",
                "Flutter Impeller Rendering Engine",
                "Flutter Platform Channels with Pigeon",
                "Flutter Desktop Embedding",
                "Flutter Web Canvas Performance",
                "Flutter Deferred Components",
                "Flutter App Size Optimization",
                "Flutter Flame Game Engine",
                "Flutter Custom Painters with Rive"
            ]
            
            # Find one that's not already in the list
            for concept in sample_concepts:
                if not self.is_similar_concept(concept, self.concepts):
                    logging.info(f"Mock mode: Selected concept '{concept}'")
                    return concept
                    
            # If all are similar, just return the first one
            return sample_concepts[0]
            
        try:
            # Provide the current concepts to Groq to avoid duplicates
            prompt = (
                "Find a modern, interesting, and not too basic Flutter concept or widget "
                "that is NOT in this list (avoid duplicates or near-duplicates):\n"
                f"{json.dumps(self.concepts)}\n\n"
                "STRICT RULES:\n"
                "- Take your time to think carefully about a unique and educational Flutter concept.\n"
                "- Return ONLY the name of the concept or widget, nothing else.\n"
                "- Keep the concept name CONCISE (1-4 words maximum).\n" 
                "- Do NOT include descriptions or explanations in the name.\n"
                "- Focus on a SPECIFIC widget, class or feature (not a general area).\n"
                "- It should be something a Flutter developer would find new or useful in 2024.\n"
                "- Perfect examples: 'CustomScrollView', 'BackdropFilter', 'AnimatedContainer'"
            )
            response = self.groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a Flutter expert with deep knowledge of the framework. Take your time to carefully consider which concept would be most valuable to teach."},
                    {"role": "user", "content": prompt}
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.9,
                max_tokens=500,    # Increased token limit 
                top_p=0.9          # More focused sampling
            )
            concept = response.choices[0].message.content.strip()
            # Clean up any extra text
            concept = concept.split('\n')[0].strip('-* \\t')
            
            # Ensure the concept is not too long
            if len(concept) > 30:
                concept = concept.split(' with ')[0].strip()
            
            # Remove any descriptions in parentheses
            concept = concept.split('(')[0].strip()
            
            logging.info(f"Fetched new concept from Groq: {concept}")
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
                logging.info(f"Concept '{new_concept}' is similar to existing concept '{concept}'")
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
        logging.info(f"Added new concept to flutter_concepts.json: {concept}")

    def daily_workflow(self):
        """
        Dynamic workflow:
        1. Fetch a random Flutter concept online using Groq
        2. If it or a similar one exists in flutter_concepts.json, retry
        3. Add the new concept to flutter_concepts.json
        4. Generate tweet and code snippet
        5. Generate code image
        6. Post to Twitter
        7. Update day counter
        """
        # Create images directory if it doesn't exist
        Path("images").mkdir(exist_ok=True)
        
        try:
            # Step 1-2: Find a unique concept not in our list
            for attempt in range(10):  # Avoid infinite loop
                concept = self.fetch_random_flutter_concept_online()
                if not self.is_similar_concept(concept, self.concepts):
                    logging.info(f"Found unique concept on attempt {attempt+1}: {concept}")
                    break
                logging.info(f"Attempt {attempt+1}: Concept '{concept}' already exists or is similar. Retrying...")
            else:
                logging.error("Failed to find a new unique concept after 10 attempts.")
                return

            # Step 3: Add the new concept to our list
            self.add_concept_to_file(concept)
            self.concepts.append(concept)

            # Step 4: Generate tweet and code
            logging.info(f"Generating tweet for concept: {concept}")
            tweet = self.generate_tweet_text(concept)
            logging.info(f"Generated tweet: {tweet}")

            logging.info(f"Generating code for concept: {concept}")
            code = self.generate_code(concept)
            code_lines = code.split('\n')
            if len(code_lines) > 30:
                code = '\n'.join(code_lines[:30]) + '\n// ...truncated for brevity...'
            logging.info(f"Generated code:\n{code}")

            # Step 5: Generate code image with retry logic
            image_path = Path("images") / "carbon.png"
            logging.info(f"Generating code image at {image_path}")
            
            # Skip image generation in mock mode
            image_generated = False
            if not self.mock_mode:
                # Try to generate image with retry logic
                for img_attempt in range(5):  # Increased from 3 to 5 attempts
                    try:
                        generate_code_image(code, str(image_path))
                        # Verify the image was actually created
                        if image_path.exists() and image_path.stat().st_size > 0:
                            image_generated = True
                            logging.info(f"Code image generated successfully on attempt {img_attempt+1}")
                            
                            # Create a persistent copy of the image with unique name
                            persistent_dir = Path("images") / "archive"
                            persistent_dir.mkdir(exist_ok=True)
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            persistent_path = persistent_dir / f"code_{self.current_day}_{timestamp}.png"
                            
                            # Copy the image to the persistent location
                            import shutil
                            shutil.copy2(image_path, persistent_path)
                            logging.info(f"Created persistent copy at {persistent_path}")
                            
                            break
                        else:
                            logging.warning(f"Image file not created on attempt {img_attempt+1}")
                            # Increase wait time between attempts
                            time.sleep(3 * (img_attempt + 1))  # Progressive backoff
                    except Exception as e:
                        logging.error(f"Image generation failed on attempt {img_attempt+1}: {str(e)}")
                        time.sleep(3 * (img_attempt + 1))  # Progressive backoff
            else:
                logging.info("Mock mode: Skipping image generation")
            
            # Step 6: Post tweet with image if available, or without image if not
            if image_generated:
                # Double check that the image exists and has content before posting
                if image_path.exists() and image_path.stat().st_size > 0:
                    logging.info(f"Posting tweet with image (size: {image_path.stat().st_size} bytes)")
                    tweet_id = self.x_client.post_tweet(tweet, str(image_path))
                else:
                    # Try to use the persistent copy if the original was deleted
                    if 'persistent_path' in locals() and persistent_path.exists():
                        logging.warning(f"Original image missing, using persistent copy at {persistent_path}")
                        tweet_id = self.x_client.post_tweet(tweet, str(persistent_path))
                    else:
                        logging.warning("Image file disappeared before posting. Posting tweet without image.")
                        tweet_id = self.x_client.post_tweet(tweet)
            else:
                logging.warning("Image generation skipped or failed. Posting tweet without image.")
                tweet_id = self.x_client.post_tweet(tweet)
                
            logging.info(f"Successfully posted tweet with ID: {tweet_id}")

            # Step 7: Update day counter
            logging.info(f"Updating day counter from {self.current_day} to {self.current_day + 1}")
            self._save_day()
            
            logging.info("Daily workflow completed successfully")

        except Exception as e:
            logging.error(f"Daily workflow failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Flutter Daily Tweet Bot')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode without making actual API calls')
    args = parser.parse_args()

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
        logging.info(f"Starting Flutter Daily Bot (mock_mode={args.mock})")
        bot = FlutterDailyBot(mock_mode=args.mock)
        bot.daily_workflow()
    except Exception as e:
        logging.critical(f"Critical failure: {str(e)}")
        raise  # Re-raise the exception 
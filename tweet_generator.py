# Purpose: Generates a tweet describing the Flutter concept without a code snippet.
# Step 1: Import required modules
# We need the Groq client for API calls and time for retry logic
from groq import Groq
import time

# Step 2: Define the list of 100 Flutter concepts
# This list provides the daily concepts for the 100-day challenge
flutter_concepts = [
    "Scaffold Layout Basics", "Column vs Row Layouts", "Container Styling Techniques", "Center Widget Alignment", "SizedBox for Spacing",
    "Divider for Visual Separation", "Spacer for Dynamic Spacing", "Expanded vs Flexible Widgets", "Stateless vs Stateful Widgets", "AppBar Customization",
    "FloatingActionButton Actions", "IconButton Interactivity", "Card for UI Elevation", "ListTile for Quick Rows", "Wrap for Flow Layouts",
    "GridView for 2D Lists", "ListView Performance", "Stack for Overlapping UI", "Positioned Widget Placement", "SafeArea for Device Compatibility",
    "GestureDetector for Touch Events", "TextField Validation", "TextFormField Advanced", "Switch for Toggles", "Checkbox for Options",
    "RadioButton for Single Choice", "Slider for Range Inputs", "DropdownButton for Selections", "CircularProgressIndicator Usage", "LinearProgressIndicator for Progress",
    "SnackBar for Feedback", "AlertDialog Interactions", "DatePicker in Forms", "TimePicker for Scheduling", "Form Validation Strategies",
    "Drawer for Side Menus", "BottomNavigationBar Setup", "TabBar Navigation I", "TabBar Navigation II", "SliverAppBar for Scroll Effects",
    "Navigator for Page Transitions I", "Navigator for Page Transitions II", "PushNamed for Named Routes", "Pop for Navigation", "MaterialPageRoute Customization",
    "Hero Animations for Transitions", "AnimatedContainer Basics", "AnimatedOpacity for Fades", "FadeTransition for UI Effects", "SlideTransition for Movement",
    "ScaleTransition for Zoom", "RotationTransition for Spins", "ThemeData for App Styling", "MediaQuery for Responsive Design", "AspectRatio for Proportions",
    "ExpansionTile for Collapsible Lists", "Stepper for Multi-Step Forms", "PageView for Swiping", "CustomScrollView for Advanced Scrolling", "NestedScrollView for Complex Layouts",
    "SetState for Simple Updates", "Future vs AsyncAwait", "Stream for Continuous Data", "StreamBuilder for Real-Time Data", "FutureBuilder for Async Data",
    "ValueNotifier for Reactive Updates", "SharedPreferences for Local Storage", "HTTPRequests for APIs", "JSONSerialization in Flutter", "FlutterSecureStorage for Secrets",
    "TweenAnimationBuilder for Tweens", "AnimatedBuilder for Custom Animations I", "AnimatedBuilder for Custom Animations II", "CustomPainter for Drawing I", "CustomPainter for Drawing II",
    "InheritedWidget for State Sharing", "Provider for State Management I", "Provider for State Management II", "GetX for State and Navigation I", "GetX for State and Navigation II",
    "Riverpod for Dependency Injection I", "Riverpod for Dependency Injection II", "Bloc Pattern I", "Bloc Pattern II", "Isolate for Background Tasks",
    "FirebaseAuth Setup", "FirebaseAuth User Management", "FirebaseAuth with Google Sign-In", "FirebaseFirestore Data Storage I", "FirebaseFirestore Data Storage II",
    "FirestoreQuery for Filtering", "Firestore Realtime Updates", "FirebaseStorage for File Uploads", "FirebaseMessaging for Push Notifications I", "FirebaseMessaging for Push Notifications II",
    "FirebaseDynamicLinks for Deep Links", "FirebaseRemoteConfig for Features", "FirebaseAnalytics for Tracking", "FirebaseCrashlytics for Errors", "CloudFunctions in Flutter"
]

# Step 3: Initialize the Groq API client
# We use the Groq API to generate the tweet text, so we need to initialize the client with the API key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Step 4: Define the generate_tweet function
# This function takes the current day, selects the concept, and generates a tweet text using the Groq API
def generate_tweet(day):
    """
    Generate a tweet describing a Flutter concept using Groq API.
    
    Args:
        day (int): The current day of the 100-day challenge (1-100).
    
    Returns:
        str: The generated tweet text (without code snippet).
    """
    # Step 4.1: Select the current and previous concepts based on the day
    # We use the day to index into flutter_concepts (day - 1 because lists are 0-indexed)
    current_concept = flutter_concepts[day - 1]
    previous_concept = flutter_concepts[day - 2] if day > 1 else None

    # Step 4.2: Create the prompt for the Groq API
    # The prompt instructs the API to generate a tweet with a specific structure
    if previous_concept:
        prompt = (
            "You are an AI assistant designed to create a series of tweets, one for each day over 100 days, "
            "explaining a Flutter concept in a humorous, beginner-friendly way. "
            "Follow this structure: "
            "1. Introduce the Flutter concept briefly and engagingly (20-30 characters). "
            "2. Use a humorous or relatable analogy (20-30 characters). "
            "3. Highlight a key feature in simple terms, optionally relating it to the previous concept (20-30 characters). "
            "Do not include a code snippet in the tweet. "
            f"Yesterday, you covered {previous_concept}. Generate a tweet for Day {day} about {current_concept}. "
            "Keep the total tweet within 150 characters (excluding hashtags)."
        )
    else:
        prompt = (
            "You are an AI assistant designed to create a series of tweets, one for each day over 100 days, "
            "explaining a Flutter concept in a humorous, beginner-friendly way. "
            "Follow this structure: "
            "1. Introduce the Flutter concept briefly and engagingly (20-30 characters). "
            "2. Use a humorous or relatable analogy (20-30 characters). "
            "3. Highlight a key feature in simple terms (20-30 characters). "
            "Do not include a code snippet in the tweet. "
            f"Generate a tweet for Day {day} about {current_concept}. "
            "Keep the total tweet within 150 characters (excluding hashtags)."
        )
    
    # Step 4.3: Call the Groq API with retry logic
    # We use a loop to retry the API call up to 3 times in case of failures (e.g., network issues)
    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        # Step 4.4: Attempt to call the Groq API to generate the tweet
        # We send the prompt to the API and get the generated tweet text
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            tweet = chat_completion.choices[0].message.content
            # Step 4.5: Ensure the tweet is within 150 characters (excluding hashtags)
            # We truncate the tweet if necessary to fit within the limit
            if "#" in tweet:
                text_part = tweet[:tweet.rfind("#")].strip()
                hashtags = tweet[tweet.rfind("#"):]
                if len(text_part) > 150:
                    text_part = text_part[:147] + "..."
                tweet = f"{text_part} {hashtags}"
            elif len(tweet) > 150:
                tweet = tweet[:147] + "..."
            # Step 4.6: Return the generated tweet text
            return tweet
        except Exception as e:
            # Step 4.7: Handle API call failures by retrying
            # We increment the attempt counter and wait before retrying
            attempt += 1
            if attempt == max_retries:
                # Step 4.8: If all retries fail, raise the exception
                # This allows the caller (main.py) to handle the error
                raise Exception(f"Failed to generate tweet after {max_retries} attempts: {str(e)}")
            print(f"Retrying API call ({attempt}/{max_retries}) due to error: {str(e)}")
            time.sleep(2 * attempt)  # Exponential backoff
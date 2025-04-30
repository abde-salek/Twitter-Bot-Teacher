# Purpose: Manages the current day for the 100-day challenge (load and save the day).

# Step 1: Import the required modules for JSON file operations and path checking
# We need 'json' for reading/writing JSON data and 'os' for checking file existence
import json
import os

# Step 2: Define the path to the JSON file
# This constant specifies where the current day will be stored
DAY_FILE = "current_day.json"

# Step 3: Define the load_day function to read the current day
# This function checks if the file exists, reads the day if it does, or returns 1 if it doesn't
def load_day():
    """
    Load the current day from the JSON file.
    If the file doesn't exist or there's an error, return 1 as the default starting day.
    
    Returns:
        int: The current day (1-100).
    """
    # Step 3.1: Check if the file exists using os.path.exists
    # We use os.path.exists to avoid errors when the file hasn't been created yet
    if os.path.exists(DAY_FILE):
        # Step 3.2: Attempt to open and read the file
        # Using try-except to handle potential file reading errors (e.g., corrupted JSON, permission issues)
        try:
            # Step 3.3: Open the file in read mode and load the JSON content
            # Using 'with' ensures the file is properly closed after reading
            with open(DAY_FILE, 'r') as f:
                # Step 3.4: Parse the JSON content into a Python dictionary
                # json.load reads the file and converts JSON to a dictionary
                data = json.load(f)
                # Step 3.5: Extract and return the 'day' value from the dictionary
                # The JSON file stores a dictionary like {"day": 1}
                return data['day']
        except (json.JSONDecodeError, IOError):
            # Step 3.6: If there's an error reading or parsing the file, return 1
            # This handles cases like corrupted JSON or permission issues
            return 1
    # Step 3.7: If the file doesn't exist, return 1 as the default day
    # This ensures we start at Day 1 for a new project
    return 1

# Step 4: Define the save_day function to write the day to the file
# This function saves the given day to the JSON file for the next run
def save_day(day):
    """
    Save the given day to the JSON file for the next run.
    If there's an error, it will raise an exception to be handled by the caller.
    
    Args:
        day (int): The day to save (1-100).
    """
    # Step 4.1: Attempt to open and write to the file
    # Using try-except to handle potential file writing errors (e.g., permission issues)
    try:
        # Step 4.2: Open the file in write mode
        # Using 'with' ensures the file is properly closed after writing
        with open(DAY_FILE, 'w') as f:
            # Step 4.3: Create a dictionary with the 'day' key and the given day
            # JSON files store data as key-value pairs, so we create a dictionary
            data = {'day': day}
            # Step 4.4: Write the dictionary to the file as JSON
            # json.dump converts the dictionary to JSON and writes it to the file
            json.dump(data, f)
    except IOError as e:
        # Step 4.5: Raise an exception if there's an error writing to the file
        # This allows the caller (e.g., main.py) to handle the error appropriately
        raise IOError(f"Failed to save day to {DAY_FILE}: {str(e)}")
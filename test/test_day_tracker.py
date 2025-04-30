# Test script for day_tracker.py
import os
from day_tracker import load_day, save_day

# Test Case 1: Test load_day() when the file doesn't exist
print("Test Case 1: load_day() when file doesn't exist")
# Ensure the file doesn't exist by deleting it (if it exists)
if os.path.exists("current_day.json"):
    os.remove("current_day.json")
# Call load_day() and check if it returns 1 (default day)
day = load_day()
print(f"Expected: 1, Got: {day}")
assert day == 1, f"Expected day to be 1, but got {day}"

# Test Case 2: Test save_day() and load_day() together
print("\nTest Case 2: save_day() and load_day()")
# Save a specific day (e.g., 5)
save_day(5)
print("Saved day 5")
# Load the day and check if it matches what we saved
loaded_day = load_day()
print(f"Expected: 5, Got: {loaded_day}")
assert loaded_day == 5, f"Expected day to be 5, but got {loaded_day}"

# Test Case 3: Test load_day() with an invalid JSON file
print("\nTest Case 3: load_day() with invalid JSON file")
# Simulate a corrupted JSON file by writing invalid JSON
with open("current_day.json", "w") as f:
    f.write("{invalid json")  # Write invalid JSON
# Call load_day() and check if it returns 1 (default day due to error)
day = load_day()
print(f"Expected: 1, Got: {day}")
assert day == 1, f"Expected day to be 1 due to invalid JSON, but got {day}"

# Test Case 4: Test save_day() with a new day
print("\nTest Case 4: save_day() with a new day")
# Save a new day (e.g., 10)
save_day(10)
print("Saved day 10")
# Load the day and check if it matches the new day
loaded_day = load_day()
print(f"Expected: 10, Got: {loaded_day}")
assert loaded_day == 10, f"Expected day to be 10, but got {loaded_day}"

print("\nAll tests passed successfully!")
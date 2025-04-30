# Test script for code_generator.py
from code_generator import generate_code_snippet

# Test Case 1: Test generate_code_snippet() for Day 1 (Scaffold Layout Basics)
print("Test Case 1: generate_code_snippet() for Day 1")
tweet_text = "Meet Scaffold. It's like a house. Gives structure."
concept = "Scaffold Layout Basics"
code = generate_code_snippet(tweet_text, concept)
print(f"Generated Code Snippet:\n{code}")
# Check that the code snippet is concise (≤10 lines)
lines = code.strip().split("\n")
assert len(lines) <= 10, f"Code snippet exceeds 10 lines: {len(lines)} lines"
print("Code snippet length check passed (≤10 lines)")
# Check that the code contains "Scaffold" and has comments
assert "Scaffold" in code, "Code snippet does not contain 'Scaffold'"
assert "//" in code, "Code snippet does not contain comments"

# Test Case 2: Test generate_code_snippet() for Day 2 (Column vs Row Layouts)
print("\nTest Case 2: generate_code_snippet() for Day 2")
tweet_text = "Rows vs Columns. Like a table. Aligns widgets."
concept = "Column vs Row Layouts"
code = generate_code_snippet(tweet_text, concept)
print(f"Generated Code Snippet:\n{code}")
# Check that the code snippet is concise (≤10 lines)
lines = code.strip().split("\n")
assert len(lines) <= 10, f"Code snippet exceeds 10 lines: {len(lines)} lines"
print("Code snippet length check passed (≤10 lines)")
# Check that the code contains "Column" or "Row" and has comments
assert "Column" in code or "Row" in code, "Code snippet does not contain 'Column' or 'Row'"
assert "//" in code, "Code snippet does not contain comments"
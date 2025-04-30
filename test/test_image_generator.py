# Test script for image_generator.py
import os
from image_generator import generate_code_image, find_latest_image

# Test Case 1: Test generate_code_image() with a sample code snippet
print("Test Case 1: generate_code_image()")
code_snippet = """// Basic layout
Scaffold(
  // Top bar
  appBar: AppBar(),
  // Content
  body: Container(),
)"""
image_path = generate_code_image(code_snippet)
print(f"Generated Image Path: {image_path}")
# Check that the image file exists
assert os.path.exists(image_path), f"Image file not found at {image_path}"
print("Image file exists check passed")

# Test Case 2: Test find_latest_image()
print("\nTest Case 2: find_latest_image()")
latest_image = find_latest_image()
print(f"Latest Image Path: {latest_image}")
# Check that the latest image path matches the generated image path
assert latest_image == image_path, f"Latest image path ({latest_image}) does not match generated image path ({image_path})"
assert latest_image is not None, "No latest image found"
print("Latest image path check passed")
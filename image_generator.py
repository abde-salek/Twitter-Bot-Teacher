# Step 1: Import required modules
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Step 2: Define the folder for storing generated images
IMAGE_DAILY_FOLDER = os.path.join(os.path.dirname(__file__), "..", "image-daily")

# Step 3: Ensure the image-daily folder exists
if not os.path.exists(IMAGE_DAILY_FOLDER):
    os.makedirs(IMAGE_DAILY_FOLDER)

# Step 4: Define the generate_code_image function
def generate_code_image(code_snippet):
    """
    Generate an image of the Dart code snippet using Selenium and Carbon.now.sh.
    
    Args:
        code_snippet (str): The Dart code snippet to convert into an image.
    
    Returns:
        str: The file path to the generated image.
    """
    # Step 4.1: Set up Firefox options and service
    options = Options()
    options.headless = True
    service = Service(r"C:\Program Files\Adobe\geckodriver.exe")
    
    # Step 4.2: Initialize the Firefox driver
    driver = webdriver.Firefox(service=service, options=options)
    
    try:
        # Step 4.3: Navigate to Carbon.now.sh with pre-set parameters
        driver.get("https://carbon.now.sh/?t=night-owl&bg=rgba(171,184,195,1)&fm=Hack&fs=14px&lh=133%25&pv=56px&ph=56px&ln=false&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&si=false&es=2x&wm=false")
        
        # Step 4.4: Wait for the CodeMirror editor to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "CodeMirror")))
        
        # Step 4.5: Locate the CodeMirror editor and input the code snippet
        editor = driver.find_element(By.CLASS_NAME, "CodeMirror")
        # Ensure the editor is focused
        driver.execute_script("arguments[0].click();", editor)
        # Use JavaScript to set the CodeMirror content directly
        driver.execute_script("""
            var cm = document.querySelector('.CodeMirror').CodeMirror;
            cm.setValue(arguments[0]);
        """, code_snippet)
        # Wait for the editor to update
        time.sleep(2)
        
        # Step 4.6: Wait for the editor to render the changes
        time.sleep(2)
        
        # Step 4.7: Generate a unique filename using the current timestamp
        image_name = f"code-snippet-{int(time.time())}.png"
        image_path = os.path.join(IMAGE_DAILY_FOLDER, image_name)
        
        # Step 4.8: Take a screenshot of the editor container
        try:
            # Try the original class name
            editor_container = driver.find_element(By.CLASS_NAME, "editor-container")
        except:
            try:
                # Fallback 1: Look for a class like "code-editor" or "editor-wrapper"
                editor_container = driver.find_element(By.CSS_SELECTOR, "[class*='editor'], [class*='code']")
            except:
                # Fallback 2: Look for the parent of the CodeMirror editor
                editor_container = driver.find_element(By.XPATH, "//div[contains(@class, 'CodeMirror')]/..")
        # Take the screenshot
        editor_container.screenshot(image_path)
        
        # Step 4.9: Return the path to the generated image
        return image_path
    
    finally:
        driver.quit()

# Step 5: Define the find_latest_image function
def find_latest_image():
    """
    Find the latest generated image in the image-daily folder.
    
    Returns:
        str: The file path to the latest image, or None if no images are found.
    """
    files = [f for f in os.listdir(IMAGE_DAILY_FOLDER) if f.startswith("code-snippet-") and f.endswith(".png")]
    if not files:
        return None
    files_with_mtime = [(f, os.path.getmtime(os.path.join(IMAGE_DAILY_FOLDER, f))) for f in files]
    latest_file = max(files_with_mtime, key=lambda x: x[1])[0]
    return os.path.join(IMAGE_DAILY_FOLDER, latest_file)
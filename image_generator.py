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
import glob
import shutil

# Step 2: Define the folder for storing generated images
# image-daily is directly inside the FlutterDailyTweet project directory
IMAGE_DAILY_FOLDER = os.path.join(os.path.dirname(__file__), "image-daily")

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
    # Step 4.1: Clean up the image-daily folder of any existing carbon*.png files
    for file in glob.glob(os.path.join(IMAGE_DAILY_FOLDER, "carbon*.png")):
        try:
            os.remove(file)
            print(f"Removed existing file: {file}")
        except Exception as e:
            print(f"Error removing file {file}: {e}")

    # Step 4.2: Set up Firefox options and service
    options = Options()
    options.headless = False  # Keep headless mode off for debugging (change to True for production)
    # Configure Firefox to auto-save downloads to the image-daily folder
    options.set_preference("browser.download.folderList", 2)  # Use custom download path
    options.set_preference("browser.download.dir", os.path.abspath(IMAGE_DAILY_FOLDER))
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png")
    options.set_preference("browser.download.manager.showWhenStarting", False)  # Prevent download prompt
    service = Service(r"C:\Program Files\Adobe\geckodriver.exe")
    
    # Step 4.3: Initialize the Firefox driver
    driver = webdriver.Firefox(service=service, options=options)
    
    try:
        # Step 4.4: Navigate to Carbon.now.sh with pre-set parameters
        driver.get("https://carbon.now.sh/?t=night-owl&bg=rgba(171,184,195,1)&fm=Hack&fs=14px&lh=133%25&pv=56px&ph=56px&ln=false&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&si=false&es=2x&wm=false")
        
        # Step 4.5: Wait for the CodeMirror editor to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "CodeMirror")))
        
        # Step 4.6: Locate the CodeMirror editor and input the code snippet
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
        
        # Step 4.7: Wait for the editor to render the changes
        time.sleep(2)
        
        # Step 4.8: Click the Export button to download the image
        export_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Export')]")))
        export_button.click()
        time.sleep(1)  # Add a small delay to ensure the download starts
        
        # Step 4.9: Wait for the download to complete
        timeout = 20  # Timeout of 20 seconds
        start_time = time.time()
        downloaded_file = None
        while time.time() - start_time < timeout:
            # Look for files matching carbon*.png (includes carbon (i).png)
            downloaded_files = glob.glob(os.path.join(IMAGE_DAILY_FOLDER, "carbon*.png"))
            print(f"Checking for files in {IMAGE_DAILY_FOLDER}: {downloaded_files}")  # Debug output
            if downloaded_files:
                downloaded_file = downloaded_files[0]  # Take the first file (should be the newest)
                break
            time.sleep(1)
        if not downloaded_file:
            raise FileNotFoundError(f"Downloaded image not found in {IMAGE_DAILY_FOLDER} after timeout. Found files: {downloaded_files}")
        
        # Step 4.10: Return the path to the downloaded image (keep the original name)
        return downloaded_file
    
    finally:
        driver.quit()

# Step 5: Define the find_latest_image function
def find_latest_image():
    """
    Find the latest generated image in the image-daily folder.
    
    Returns:
        str: The file path to the latest image, or None if no images are found.
    """
    files = [f for f in os.listdir(IMAGE_DAILY_FOLDER) if f.startswith("carbon") and f.endswith(".png")]
    if not files:
        return None
    files_with_mtime = [(f, os.path.getmtime(os.path.join(IMAGE_DAILY_FOLDER, f))) for f in files]
    latest_file = max(files_with_mtime, key=lambda x: x[1])[0]
    return os.path.join(IMAGE_DAILY_FOLDER, latest_file)
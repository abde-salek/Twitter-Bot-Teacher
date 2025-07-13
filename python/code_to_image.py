# code_to_image.py
#
# This module automates the process of generating a code image from a code snippet using Carbon (https://carbon.now.sh).
# It uses Selenium to control a headless Firefox browser, paste code, and export the image.
#
# Usage: Call generate_code_image(code_text, output_path) to save a PNG image of the code.

import os
import time
import shutil
import platform
import subprocess
from pathlib import Path
import stat
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_incompatible_geckodriver():
    """Remove the incompatible geckodriver if detected"""
    try:
        # Define known incompatible geckodriver paths
        geckodriver_paths = [
            "/usr/local/bin/geckodriver",  # Linux/macOS
            "/usr/bin/geckodriver",        # Linux alternative
            "C:\\geckodriver.exe"          # Windows
        ]
        
        # Check Firefox version using the installed geckodriver
        try:
            result = subprocess.run(["firefox", "--version"], capture_output=True, text=True)
            firefox_version = result.stdout.strip()
            logger.info(f"Detected Firefox version: {firefox_version}")
        except:
            logger.warning("Could not detect Firefox version")
        
        for path in geckodriver_paths:
            if os.path.exists(path):
                try:
                    # Check geckodriver version
                    result = subprocess.run([path, "--version"], capture_output=True, text=True)
                    version_info = result.stdout.strip()
                    logger.info(f"Found geckodriver at {path}: {version_info}")
                    
                    # If it's version 0.34.0 (incompatible with Firefox 140), remove it
                    if "0.34.0" in version_info and "140" in firefox_version:
                        logger.warning(f"Removing incompatible geckodriver {version_info} at {path}")
                        
                        # Make file writable if needed
                        if not os.access(path, os.W_OK):
                            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
                        
                        # Try to remove the file
                        try:
                            os.remove(path)
                            logger.info(f"Successfully removed incompatible geckodriver at {path}")
                        except PermissionError:
                            # If permission error, try with sudo on Linux/macOS
                            if platform.system() in ["Linux", "Darwin"]:
                                logger.warning("Attempting to remove with sudo privileges...")
                                subprocess.run(["sudo", "rm", path], check=False)
                                if not os.path.exists(path):
                                    logger.info("Successfully removed with sudo")
                            else:
                                logger.error(f"Could not remove {path} - permission denied")
                except Exception as e:
                    logger.warning(f"Error checking geckodriver at {path}: {e}")
    except Exception as e:
        logger.error(f"Error in remove_incompatible_geckodriver: {e}")

def create_basic_image(code_text, output_path):
    """Create a basic image with PIL as fallback when browser automation fails"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a basic image with the code text
        width, height = 800, 600
        bg_color = (40, 44, 52)  # Dark background similar to Carbon
        text_color = (229, 229, 229)  # Light gray text
        
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Use default font
        try:
            if platform.system() == "Windows":
                font = ImageFont.truetype("arial.ttf", 14)
            elif platform.system() == "Darwin":  # macOS
                font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 14)
            elif platform.system() == "Linux":
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # Draw the code text with line breaks
        y_position = 20
        for line in code_text.split("\n"):
            draw.text((20, y_position), line, fill=text_color, font=font)
            y_position += 20
            
        img.save(output_path)
        logger.info(f"Generated basic image: {output_path}")
        
        return output_path
    except Exception as e:
        logger.error(f"Failed to create basic image: {e}")
        raise

def generate_code_image(code_text: str, output_path: str):
    """
    Generate a code image using Carbon and save it to output_path.
    Uses Firefox browser with automatic geckodriver management.
    
    Args:
        code_text (str): The code to render as an image.
        output_path (str): The file path to save the PNG image.
    Returns:
        str: The output path of the saved image.
    """
    # Create absolute paths
    abs_output_path = os.path.abspath(output_path)
    download_dir = os.path.dirname(abs_output_path)
    
    # Create download directory if it doesn't exist
    Path(download_dir).mkdir(exist_ok=True)
    
    # Create a timestamp for unique filenames to avoid file locking issues
    timestamp = str(int(time.time()))
    temp_filename = f"carbon_{timestamp}.png"
    temp_output_path = os.path.join(download_dir, temp_filename)
    
    # Clear any existing png files in the download directory
    for file in Path(download_dir).glob("carbon*.png"):
        try:
            # Don't try to delete the file we're about to create
            if file.name != temp_filename:
                os.remove(file)
        except:
            logger.warning(f"Could not remove file: {file}")
            pass
    
    # First, try to remove any incompatible geckodriver        
    remove_incompatible_geckodriver()
            
    driver = None
    logger.info("Setting up Firefox browser for image generation...")
    
    try:
        # First, try to use webdriver-manager to get the correct geckodriver version
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            
            # Setup Firefox options with improved download handling
            options = Options()
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png,application/octet-stream")
            options.set_preference("browser.download.always_ask_before_handling_new_types", False)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("pdfjs.disabled", True)
            options.add_argument("--headless")
            
            # Get the correct geckodriver with webdriver-manager
            logger.info("Downloading/using correct geckodriver version via webdriver-manager...")
            driver_path = GeckoDriverManager().install()
            logger.info(f"Using geckodriver from: {driver_path}")
            
            # Create a Firefox service with the managed driver
            firefox_service = FirefoxService(executable_path=driver_path, log_path="geckodriver.log")
            driver = webdriver.Firefox(service=firefox_service, options=options)
            logger.info("Firefox browser initialized successfully with managed driver")
        
        except Exception as e:
            logger.warning(f"Failed to initialize Firefox with managed driver: {e}")
            logger.info("Falling back to manual Firefox setup...")
            
            # Traditional setup as fallback
            options = Options()
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.download.dir", download_dir)
            options.set_preference("browser.download.manager.showWhenStarting", False)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png,application/octet-stream")
            options.set_preference("browser.download.always_ask_before_handling_new_types", False)
            options.set_preference("browser.download.useDownloadDir", True)
            options.set_preference("pdfjs.disabled", True)
            options.add_argument("--headless")
            
            # Try to use a specific geckodriver service with custom log path
            log_path = os.path.join(os.getcwd(), "geckodriver.log")
            driver = webdriver.Firefox(
                options=options,
                service=FirefoxService(log_path=log_path)
            )
            logger.info("Firefox browser initialized with default driver")
        
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 30)
        
        # Navigate to Carbon
        driver.get("https://carbon.now.sh")
        logger.info("Page loaded, waiting for editor...")
        
        # Wait for and focus editor
        editor = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror textarea"))
        )
        logger.info("Editor found")
        
        # Clear existing code
        editor.send_keys(Keys.CONTROL + "a")
        editor.send_keys(Keys.DELETE)
        time.sleep(2)

        # Paste code
        editor.send_keys(code_text)
        logger.info("Code pasted")
        time.sleep(3)

        # Try multiple approaches to download the image
        export_methods = [
            # Method 1: XPath
            lambda: wait.until(EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[1]/main/div[2]/div[2]/div[1]/div[3]/div[3]/div[2]/div[1]/button[1]')
            )).click(),
            
            # Method 2: CSS Selector
            lambda: wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-cy="export-button"]')
            )).click(),
            
            # Method 3: Keyboard shortcut
            lambda: editor.send_keys(Keys.SHIFT, Keys.CONTROL, 'e'),
            
            # Method 4: JavaScript click
            lambda: driver.execute_script("document.querySelector('button[data-cy=\"export-button\"]').click()")
        ]
        
        # Try each export method
        for i, method in enumerate(export_methods, 1):
            try:
                logger.info(f"Trying export method {i}...")
                method()
                logger.info(f"Export method {i} executed, waiting for download...")
                time.sleep(15)
                
                # Check if download was successful
                downloads = list(Path(download_dir).glob("carbon*.png"))
                if downloads:
                    newest_file = max(downloads, key=os.path.getctime)
                    logger.info(f"Found downloaded file: {newest_file}")
                    shutil.copy2(newest_file, abs_output_path)
                    logger.info(f"Image downloaded successfully: {abs_output_path}")
                    
                    # Verify file has content
                    if Path(abs_output_path).stat().st_size > 0:
                        logger.info(f"Image verified: {abs_output_path}, size: {Path(abs_output_path).stat().st_size} bytes")
                        return abs_output_path
                    else:
                        logger.warning(f"Warning: Image file has zero size: {abs_output_path}")
                        continue
                else:
                    logger.warning("No download detected, trying next method")
            except Exception as e:
                logger.warning(f"Export method {i} failed: {str(e)}")
        
        logger.error("All export methods failed with Firefox")
        
    except Exception as e:
        logger.error(f"Error with Firefox: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    # Ultimate fallback: Generate a basic image with PIL
    logger.warning("Firefox attempt failed. Creating basic image instead...")
    return create_basic_image(code_text, abs_output_path)
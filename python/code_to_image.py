# code_to_image.py
#
# This module automates the process of generating a code image from a code snippet using Carbon (https://carbon.now.sh).
# It uses Selenium to control a headless Firefox browser, paste code, and export the image.
#
# Usage: Call generate_code_image(code_text, output_path) to save a PNG image of the code.

import os
import time
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import logging

def generate_code_image(code_text: str, output_path: str):
    """
    Generate a code image using Carbon and save it to output_path.
    Uses Firefox browser only.
    
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
            print(f"Could not remove file: {file}")
            pass
            
    driver = None
    print("Setting up Firefox browser for image generation...")
    
    try:
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
        
        # Try to use a specific geckodriver service with custom log path
        log_path = os.path.join(os.getcwd(), "geckodriver.log")
        driver = webdriver.Firefox(
            options=options,
            service=FirefoxService(log_path=log_path)
        )
        print("Firefox browser initialized successfully")
        
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 30)
        
        # Navigate to Carbon
        driver.get("https://carbon.now.sh")
        print("Page loaded, waiting for editor...")
        
        # Wait for and focus editor
        editor = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror textarea"))
        )
        print("Editor found")
        
        # Clear existing code
        editor.send_keys(Keys.CONTROL + "a")
        editor.send_keys(Keys.DELETE)
        time.sleep(2)

        # Paste code
        editor.send_keys(code_text)
        print("Code pasted")
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
                print(f"Trying export method {i}...")
                method()
                print(f"Export method {i} executed, waiting for download...")
                time.sleep(15)
                
                # Check if download was successful
                downloads = list(Path(download_dir).glob("carbon*.png"))
                if downloads:
                    newest_file = max(downloads, key=os.path.getctime)
                    print(f"Found downloaded file: {newest_file}")
                    shutil.copy2(newest_file, abs_output_path)
                    print(f"Image downloaded successfully: {abs_output_path}")
                    
                    # Verify file has content
                    if Path(abs_output_path).stat().st_size > 0:
                        print(f"Image verified: {abs_output_path}, size: {Path(abs_output_path).stat().st_size} bytes")
                        return abs_output_path
                    else:
                        print(f"Warning: Image file has zero size: {abs_output_path}")
                        continue
                else:
                    print("No download detected, trying next method")
            except Exception as e:
                print(f"Export method {i} failed: {str(e)}")
        
        print("All export methods failed with Firefox")
        
    except Exception as e:
        print(f"Error with Firefox: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    # Ultimate fallback: Generate a basic image with PIL
    print("Firefox attempt failed. Trying to create a basic image...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        
        # Create a basic image with the code text
        width, height = 800, 600
        bg_color = (40, 44, 52)  # Dark background similar to Carbon
        text_color = (229, 229, 229)  # Light gray text
        
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Use default font
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
            
        # Draw the code text with line breaks
        y_position = 20
        for line in code_text.split("\n"):
            draw.text((20, y_position), line, fill=text_color, font=font)
            y_position += 20
            
        img.save(abs_output_path)
        print(f"Generated basic image: {abs_output_path}")
        
        # Verify file has content
        if Path(abs_output_path).stat().st_size > 0:
            return abs_output_path
            
    except ImportError:
        print("PIL is not installed. Cannot generate fallback image.")
    except Exception as e:
        print(f"Error generating basic image: {str(e)}")
        
    raise RuntimeError("Failed to generate code image with all methods")
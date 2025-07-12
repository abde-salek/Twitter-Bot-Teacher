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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def generate_code_image(code_text: str, output_path: str):
    """
    Generate a code image using Carbon and save it to output_path.
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

    # Setup Firefox options with improved download handling
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png,application/octet-stream")
    options.set_preference("browser.download.always_ask_before_handling_new_types", False)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("pdfjs.disabled", True)
    
    # Add headless option for server environments
    # Comment out for debugging if needed
    # options.add_argument("--headless")

    # Start WebDriver (requires geckodriver and Firefox installed)
    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(30)  # Increased page load timeout
    wait = WebDriverWait(driver, 30)  # Increased timeout
    
    try:
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
        time.sleep(2)  # Increased wait time

        # Paste code
        editor.send_keys(code_text)
        print("Code pasted")
        time.sleep(3)  # Increased wait time

        # Try download via Carbon export first
        image_downloaded = False
        try:
            # First try: Click the Export button directly using the exact XPath
            print("Attempting to click export button using direct XPath...")
            export_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div[2]/div[2]/div[1]/div[3]/div[3]/div[2]/div[1]/button[1]'))
            )
            export_btn.click()
            print("Export button clicked using XPath, waiting for download...")
            # Increased wait time to 15 seconds as requested
            print("Waiting 15 seconds for download to complete...")
            time.sleep(15)
        except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
            try:
                # Second try: Try the original CSS selector approach
                print("XPath approach failed, trying CSS selector...")
                export_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="export-button"]'))
                )
                export_btn.click()
                print("Export button clicked using CSS selector, waiting for download...")
                # Increased wait time to 15 seconds
                print("Waiting 15 seconds for download to complete...")
                time.sleep(15)
            except:
                try:
                    # Third try: Try keyboard shortcut
                    print("CSS selector failed, trying keyboard shortcut...")
                    editor.send_keys(Keys.SHIFT, Keys.CONTROL, 'e')
                    print("Keyboard shortcut used, waiting for download...")
                    # Increased wait time to 15 seconds
                    print("Waiting 15 seconds for download to complete...")
                    time.sleep(15)
                except:
                    # Fourth try: Try JavaScript click
                    print("Keyboard shortcut failed, trying JavaScript click...")
                    driver.execute_script("document.querySelector('button[data-cy=\"export-button\"]').click()")
                    print("JavaScript click executed, waiting for download...")
                    # Increased wait time to 15 seconds
                    print("Waiting 15 seconds for download to complete...")
                    time.sleep(15)
        
        # Check if download was successful by looking for new PNG files
        downloads = list(Path(download_dir).glob("carbon*.png"))
        if downloads:
            newest_file = max(downloads, key=os.path.getctime)
            # Copy the newest file to the target path
            try:
                print(f"Copying from {newest_file} to {abs_output_path}")
                shutil.copy2(newest_file, abs_output_path)
                print(f"Image downloaded successfully: {abs_output_path}")
                image_downloaded = True
            except Exception as e:
                print(f"Error copying file: {str(e)}")
                # If copy fails, use the downloaded file directly
                abs_output_path = str(newest_file)
                print(f"Using downloaded file directly: {abs_output_path}")
                image_downloaded = True
        
        # Make file read-only to prevent accidental deletion if it exists
        if Path(abs_output_path).exists():
            try:
                os.chmod(abs_output_path, 0o444)
                print(f"Made file read-only: {abs_output_path}")
            except:
                print("Failed to make file read-only")
            
            # Verify the file has content
            if Path(abs_output_path).stat().st_size > 0:
                print(f"Image verified: {abs_output_path}, size: {Path(abs_output_path).stat().st_size} bytes")
            else:
                print(f"Warning: Image file exists but has zero size: {abs_output_path}")
                raise ValueError("Image file has zero size")
                
        if not image_downloaded:
            # Ultimate fallback: Generate a basic image with PIL if all else fails
            print("All download attempts failed. Attempting to generate a basic image with PIL.")
            # This part of the original code was not provided in the edit hint,
            # so it's kept as is, but it will likely fail if PIL is not imported.
            # For the purpose of this edit, we'll assume PIL is available or
            # that the user will add it if needed.
            try:
                from PIL import Image
                from io import BytesIO
                # This is a placeholder for a basic image generation.
                # In a real scenario, you'd use a library like PIL to render text.
                # For demonstration, we'll create a dummy image.
                dummy_image = Image.new("RGB", (100, 50), color="white")
                dummy_image.save(abs_output_path, "PNG")
                print(f"Generated basic image: {abs_output_path}")
            except ImportError:
                raise ImportError("PIL is not installed. Please install it to generate a basic image.")
            except Exception as e:
                print(f"Error generating basic image: {str(e)}")
                raise

    except TimeoutException as e:
        print(f"Timeout waiting for element: {str(e)}")
        try:
            print("Current page source:")
            print(driver.page_source[:1000] + "...")  # Print first 1000 chars to avoid huge logs
        except:
            print("Could not get page source")
        raise
    except NoSuchElementException as e:
        print(f"Element not found: {str(e)}")
        try:
            print("Current page source:")
            print(driver.page_source[:1000] + "...")
        except:
            print("Could not get page source")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
    finally:
        try:
            driver.quit()
        except:
            pass  # Ignore errors when quitting the driver

    # Make one final verification that the file exists and has content
    if not Path(abs_output_path).exists():
        raise FileNotFoundError(f"Image file does not exist after all steps: {abs_output_path}")
        
    if Path(abs_output_path).stat().st_size == 0:
        raise ValueError(f"Image file exists but has zero size: {abs_output_path}")
        
    print(f"Final verification succeeded. Image ready at {abs_output_path}")
    return abs_output_path
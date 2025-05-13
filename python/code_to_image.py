# code_to_image.py
#
# This module automates the process of generating a code image from a code snippet using Carbon (https://carbon.now.sh).
# It uses Selenium to control a headless Firefox browser, paste code, and export the image.
#
# Usage: Call generate_code_image(code_text, output_path) to save a PNG image of the code.

import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def generate_code_image(code_text: str, output_path: str):
    """
    Generate a code image using Carbon and save it to output_path.
    Args:
        code_text (str): The code to render as an image.
        output_path (str): The file path to save the PNG image.
    Returns:
        str: The output path of the saved image.
    """
    # Setup Firefox options (headless optional)
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.path.dirname(output_path))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)

    # Start WebDriver (requires geckodriver and Firefox installed)
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)  # 20 second timeout
    
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
        time.sleep(1)

        # Paste code
        editor.send_keys(code_text)
        print("Code pasted")
        time.sleep(2)

        # Click the Export button (this will download PNG directly)
        export_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="export-button"]'))
        )
        export_btn.click()
        print("Export button clicked, waiting for download...")
        time.sleep(5)  # Wait for download to complete

    except TimeoutException as e:
        print(f"Timeout waiting for element: {str(e)}")
        print("Current page source:")
        print(driver.page_source)
        raise
    except NoSuchElementException as e:
        print(f"Element not found: {str(e)}")
        print("Current page source:")
        print(driver.page_source)
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
    finally:
        driver.quit()

    return output_path
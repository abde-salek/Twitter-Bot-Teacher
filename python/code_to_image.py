import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Target file save path
IMAGE_PATH = r"C:\Users\admin\Desktop\All\test\FlutterDailyTweet\images\carbon.png"

def generate_code_image(code_text: str):
    # Setup Firefox options (headless optional)
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.path.dirname(IMAGE_PATH))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/png")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)

    # Start WebDriver
    driver = webdriver.Firefox(options=options)
    driver.get("https://carbon.now.sh/?bg=rgba%28171%2C+184%2C+195%2C+1%29&t=night-owl&wt=none&l=auto&width=680&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&pv=56px&ph=56px&ln=false&fl=1&fm=Hack&fs=14px&lh=133%25&si=false&es=2x&wm=false&code=const%2520pluckDeep%2520%253D%2520key%2520%253D%253E%2520obj%2520%253D%253E%2520key.split%28%27.%27%29.reduce%28%28accum%252C%2520key%29%2520%253D%253E%2520accum%255Bkey%255D%252C%2520obj%29%250A%250Aconst%2520compose%2520%253D%2520%28...fns%29%2520%253D%253E%2520res%2520%253D%253E%2520fns.reduce%28%28accum%252C%2520next%29%2520%253D%253E%2520next%28accum%29%252C%2520res%29%250A%250Aconst%2520unfold%2520%253D%2520%28f%252C%2520seed%29%2520%253D%253E%2520%257B%250A%2520%2520const%2520go%2520%253D%2520%28f%252C%2520seed%252C%2520acc%29%2520%253D%253E%2520%257B%250A%2520%2520%2520%2520const%2520res%2520%253D%2520f%28seed%29%250A%2520%2520%2520%2520return%2520res%2520%253F%2520go%28f%252C%2520res%255B1%255D%252C%2520acc.concat%28%255Bres%255B0%255D%255D%29%29%2520%253A%2520acc%250A%2520%2520%257D%250A%2520%2520return%2520go%28f%252C%2520seed%252C%2520%255B%255D%29%250A")

    try:
        time.sleep(3)  # Let page load

        # Focus editor and clear default code
        editor = driver.find_element(By.CSS_SELECTOR, "div.CodeMirror textarea")
        editor.send_keys(Keys.CONTROL + "a")
        editor.send_keys(Keys.DELETE)
        time.sleep(0.5)

        # Paste your code
        editor.send_keys(code_text)
        time.sleep(1)

        # Click "Export" button
        export_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Export")]')
        export_btn.click()
        time.sleep(0.5)

        # Click PNG download option
        png_option = driver.find_element(By.XPATH, '//span[text()="PNG"]/ancestor::button')
        png_option.click()

        # Wait for download (adjust if needed)
        time.sleep(5)

    finally:
        driver.quit()

    return IMAGE_PATH
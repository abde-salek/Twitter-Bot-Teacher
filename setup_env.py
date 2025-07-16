#!/usr/bin/env python3
"""
Setup script to create .env file with Twitter API credentials.
This helps users create the required .env file with their API credentials.
"""

import os
from pathlib import Path
import argparse

def create_env_file():
    """Create a new .env file with user input for API credentials."""
    env_path = Path('.env')
    
    # Check if .env already exists
    if env_path.exists():
        overwrite = input(".env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n=== Flutter Daily Tweet Bot Setup ===")
    print("\nYou'll need to provide API credentials for both Groq and Twitter/X.")
    print("\n1. Get Groq API key from https://console.groq.com/keys")
    print("2. Get Twitter API credentials from https://developer.twitter.com/en/portal/dashboard")
    print("\nEnter your API credentials (or leave blank to skip):")
    
    groq_api_key = input("Groq API Key: ").strip()
    
    twitter_consumer_key = input("Twitter Consumer Key (API Key): ").strip()
    twitter_consumer_secret = input("Twitter Consumer Secret (API Secret): ").strip()
    twitter_access_token = input("Twitter Access Token: ").strip()
    twitter_access_token_secret = input("Twitter Access Token Secret: ").strip()
    
    # Write to .env file
    with open(env_path, 'w') as f:
        f.write("# Flutter Daily Tweet Bot - Environment Variables\n\n")
        
        # Groq API Key
        f.write("# Groq API Key\n")
        f.write(f"GROQ_API_KEY={groq_api_key}\n\n")
        
        # Twitter API Credentials
        f.write("# Twitter/X API Credentials\n")
        f.write(f"CONSUMER_KEY={twitter_consumer_key}\n")
        f.write(f"CONSUMER_SECRET={twitter_consumer_secret}\n")
        f.write(f"ACCESS_TOKEN={twitter_access_token}\n")
        f.write(f"ACCESS_TOKEN_SECRET={twitter_access_token_secret}\n")
    
    print("\n.env file created successfully!")
    print(f"File path: {env_path.absolute()}")
    
    # Check if any credentials are missing
    missing = []
    if not groq_api_key:
        missing.append("Groq API Key")
    if not twitter_consumer_key:
        missing.append("Twitter Consumer Key")
    if not twitter_consumer_secret:
        missing.append("Twitter Consumer Secret")
    if not twitter_access_token:
        missing.append("Twitter Access Token")
    if not twitter_access_token_secret:
        missing.append("Twitter Access Token Secret")
    
    if missing:
        print("\nWarning: The following credentials are missing:")
        for item in missing:
            print(f"  - {item}")
        print("\nYou will need to add these manually to the .env file before running the bot.")

def check_webdriver():
    """Check if necessary webdrivers are installed."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        print("\n=== Checking WebDrivers ===")
        
        # Try to initialize Chrome driver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            chrome_service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service)
            driver.quit()
            print("✅ Chrome WebDriver: Installed and working")
        except Exception as e:
            print(f"⚠️ Chrome WebDriver: Not working - {str(e)}")
            print("  - Try installing Chrome: https://www.google.com/chrome/")
        
        # Try to initialize Firefox driver
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            firefox_service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=firefox_service)
            driver.quit()
            print("✅ Firefox WebDriver (GeckoDriver): Installed and working")
        except Exception as e:
            print(f"⚠️ Firefox WebDriver: Not working - {str(e)}")
            print("  - Download latest GeckoDriver: https://github.com/mozilla/geckodriver/releases")
            
    except ImportError as e:
        print(f"Error checking webdrivers: {str(e)}")
        print("Make sure to install all requirements: pip install -r requirements.txt")

def main():
    """Main entry point for setup script."""
    parser = argparse.ArgumentParser(description="Setup Flutter Daily Tweet Bot")
    parser.add_argument("--env", action="store_true", help="Create .env file")
    parser.add_argument("--check-drivers", action="store_true", help="Check webdrivers")
    args = parser.parse_args()
    
    # If no arguments provided, run all setup steps
    if not args.env and not args.check_drivers:
        create_env_file()
        check_webdriver()
    else:
        if args.env:
            create_env_file()
        if args.check_drivers:
            check_webdriver()
            
    print("\nSetup complete! Run 'python main.py' to start the bot.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Remove incompatible geckodriver script.

This script checks for and removes incompatible geckodriver versions,
especially version 0.34.0 which is incompatible with Firefox 140.x.

Run this script with sudo/admin privileges if needed:
  Linux/macOS: sudo python remove_geckodriver.py
  Windows: Run command prompt as Administrator, then python remove_geckodriver.py
"""

import os
import sys
import stat
import platform
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:  # Linux/macOS
            return os.geteuid() == 0  # 0 is root user ID
    except:
        return False

def remove_incompatible_geckodriver():
    """Remove the incompatible geckodriver if detected"""
    
    logger.info("Checking for incompatible geckodriver versions...")
    
    # Define known geckodriver paths
    geckodriver_paths = [
        "/usr/local/bin/geckodriver",  # Linux/macOS common path
        "/usr/bin/geckodriver",        # Linux alternative
        "/opt/homebrew/bin/geckodriver",  # macOS homebrew
        os.path.expanduser("~/.local/bin/geckodriver"),  # User local path
    ]
    
    # Add Windows paths if on Windows
    if platform.system() == "Windows":
        geckodriver_paths = [
            "C:\\geckodriver.exe",
            os.path.join(os.getenv('APPDATA'), 'geckodriver.exe'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'geckodriver.exe')
        ]
        
        # Add paths from environment PATH
        if os.getenv('PATH'):
            for path_dir in os.getenv('PATH').split(os.pathsep):
                geckodriver_paths.append(os.path.join(path_dir, 'geckodriver.exe'))
    
    # Check Firefox version
    firefox_version = "unknown"
    try:
        firefox_cmd = "firefox" if platform.system() != "Windows" else "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        result = subprocess.run([firefox_cmd, "--version"], capture_output=True, text=True)
        firefox_version = result.stdout.strip()
        logger.info(f"Detected Firefox version: {firefox_version}")
    except:
        logger.warning("Could not detect Firefox version. Assuming Firefox 140.x is installed.")
        firefox_version = "Firefox 140"
    
    removed_count = 0
    for path in geckodriver_paths:
        if os.path.exists(path):
            try:
                # Check geckodriver version
                result = subprocess.run([path, "--version"], capture_output=True, text=True)
                version_info = result.stdout.strip()
                logger.info(f"Found geckodriver at {path}: {version_info}")
                
                # If it's version 0.34.0 (incompatible with Firefox 140), remove it
                if "0.34.0" in version_info and "140" in firefox_version:
                    logger.warning(f"Found incompatible geckodriver {version_info} at {path}")
                    
                    # Make file writable if needed
                    if not os.access(path, os.W_OK):
                        try:
                            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
                        except:
                            logger.warning(f"Could not change file permissions for {path}")
                    
                    # Try to remove the file
                    try:
                        os.remove(path)
                        logger.info(f"✓ Successfully removed incompatible geckodriver at {path}")
                        removed_count += 1
                    except PermissionError:
                        logger.error(f"✗ Permission denied when trying to remove {path}")
                        logger.error("  Please run this script with admin/sudo privileges")
                    except Exception as e:
                        logger.error(f"✗ Could not remove {path}: {str(e)}")
                else:
                    logger.info(f"Geckodriver at {path} is compatible. Keeping it.")
            except Exception as e:
                logger.warning(f"Error checking geckodriver at {path}: {str(e)}")
    
    if removed_count == 0:
        logger.info("No incompatible geckodriver versions found or removed.")
    else:
        logger.info(f"Removed {removed_count} incompatible geckodriver installation(s).")
        logger.info("The next time you run your script, webdriver-manager will download a compatible version.")
    
    return removed_count

def main():
    """Main function"""
    print("\n=== Incompatible GeckoDriver Removal Tool ===\n")
    
    if not is_admin() and platform.system() != "Windows":
        logger.warning("This script may need admin privileges to remove system-installed geckodrivers.")
        logger.warning("Consider running with 'sudo python remove_geckodriver.py'\n")
    
    try:
        removed = remove_incompatible_geckodriver()
        
        if removed > 0:
            print("\n✓ Success! Incompatible geckodriver(s) removed.")
            print("  When you run your script next, webdriver-manager will download the compatible version.")
        else:
            print("\n✓ No action needed. No incompatible geckodriver found.")
        
        # Installation instructions for webdriver-manager
        print("\nTo ensure automatic driver management, make sure to install webdriver-manager:")
        print("    pip install webdriver-manager")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
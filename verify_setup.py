#!/usr/bin/env python3
"""
Setup verification script for FFVB Volleyball Results Scraper

This script verifies that all required dependencies are installed
and that the system is ready to run the volleyball scraper.
"""

import sys
import importlib

def check_package(package_name, min_version=None):
    """Check if a package is installed and optionally verify version."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False

def check_chrome():
    """Check if Chrome is available."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(), options=options)
        driver.quit()
        print("✅ Google Chrome: Available")
        return True
    except Exception as e:
        print(f"❌ Google Chrome: Not available or misconfigured")
        print(f"   Error: {e}")
        return False

def main():
    """Main verification function."""
    print("🏐 FFVB Volleyball Scraper - Setup Verification")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    else:
        print("✅ Python version OK")
    
    print("\nChecking required packages:")
    print("-" * 30)
    
    # List of required packages
    required_packages = [
        'selenium',
        'pandas', 
        'numpy',
        'lxml',
        'openpyxl'
    ]
    
    all_packages_ok = True
    for package in required_packages:
        if not check_package(package):
            all_packages_ok = False
    
    print("\nChecking system dependencies:")
    print("-" * 30)
    
    chrome_ok = check_chrome()
    
    print("\n" + "=" * 50)
    if all_packages_ok and chrome_ok:
        print("🎉 Setup verification PASSED!")
        print("You can now run the volleyball scraper.")
    else:
        print("⚠️  Setup verification FAILED!")
        if not all_packages_ok:
            print("Please install missing packages with: pip install -r requirements.txt")
        if not chrome_ok:
            print("Please install Google Chrome browser.")
    
    return all_packages_ok and chrome_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
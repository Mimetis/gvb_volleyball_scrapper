#!/usr/bin/env python3
"""
FFVB Beach Volleyball Results Scraper

This script scrapes volleyball results/standings from the FFVB Beach website.
It extracts the league standings table and saves it to a CSV file.

Author: Creat        if volleyball_data is not None:
            # Clean and save the data
            filename = output_filename if output_filename else "ffvb_results.xlsx"
            cleaned_data = clean_and_save_data(volleyball_data, filename)
            print(f"\nScraping completed successfully!")
            print(f"Scraped {len(cleaned_data)} rows of data")
            print(f"Data saved to '{filename}'") volley-scraper project
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import tempfile
import shutil
from io import StringIO
import re
import csv
import os


def load_teams_config(config_file="teams.csv"):
    """Load team configurations from CSV file."""
    teams = []
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line_num, row in enumerate(reader, 1):
                # Skip empty lines and comments
                if not row or row[0].strip().startswith('#'):
                    continue
                
                if len(row) >= 2:
                    team_name = row[0].strip()
                    team_url = row[1].strip()
                    teams.append((team_name, team_url))
                else:
                    print(f"Warning: Invalid format in line {line_num}: {row}")
        
        print(f"Loaded {len(teams)} teams from {config_file}")
        return teams
    
    except FileNotFoundError:
        print(f"Config file {config_file} not found. Please create it with team information.")
        return []
    except Exception as e:
        print(f"Error reading config file: {e}")
        return []


def setup_chrome_driver():
    """Set up Chrome WebDriver with appropriate options for scraping."""
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Create a unique temporary directory for user data
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_dir}")
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        return driver, temp_dir
    except Exception as e:
        print(f"Failed to start Chrome WebDriver: {e}")
        print("Make sure Google Chrome and ChromeDriver are installed.")
        return None, temp_dir


def find_volleyball_table(driver):
    """Find and extract the volleyball results table from the page."""
    print("Analyzing tables on the page...")
    
    # Get all tables and analyze them
    tables = driver.find_elements(By.TAG_NAME, "table")
    print(f"Found {len(tables)} tables on the page")
    
    for i, table in enumerate(tables):
        try:
            html_table = table.get_attribute("outerHTML")
            if html_table:
                # Try to parse each table
                df_temp = pd.read_html(StringIO(html_table))[0]
                print(f"Table {i+1}: {df_temp.shape[0]} rows, {df_temp.shape[1]} columns")
                
                # Look for tables that might contain match data
                table_text = df_temp.to_string().lower()
                
                # Look for volleyball-specific patterns
                match_patterns = [
                    r'\d{2}[/\-]\d{2}',  # Date patterns
                    'vs',  # versus indicator
                    r'\d+\s*-\s*\d+',  # Score patterns  
                    'set',
                    'equipe',
                    'match',
                    'Pts.',
                    'volley'
                ]
                
                pattern_matches = sum(1 for pattern in match_patterns if re.search(pattern, table_text))
                print(f"  Pattern matches: {pattern_matches}/{len(match_patterns)}")
                
                # Select table with most pattern matches and reasonable size
                if (df_temp.shape[0] > 2 and 
                    df_temp.shape[1] >= 3 and 
                    pattern_matches >= 2):
                    print(f"*** Selected table {i+1} as volleyball results table ***")
                    return df_temp
                    
        except Exception as e:
            print(f"Error processing table {i+1}: {e}")
    
    return None


def clean_and_save_data(df, filename="ffvb_results.xlsx"):
    """Clean the data and save to CSV with proper column names."""
    # Remove empty rows and columns
    df_clean = df.dropna(how='all').dropna(axis=1, how='all')
    
    # Try to set proper column names if we can identify them
    if len(df_clean.columns) >= 19:
        # This appears to be a standings table based on the scraped data
        column_mapping = {
            0: 'Class.',
            1: 'Equipe',
            2: 'Pts.',
            3: 'Jou.',
            4: 'Gagn.',
            5: 'Perd.'
        }
        
        # Rename columns where we have mappings
        for old_col, new_col in column_mapping.items():
            if old_col in df_clean.columns:
                df_clean = df_clean.rename(columns={old_col: new_col})
        
        # Keep only the desired columns
        desired_columns = ['Class.', 'Equipe', 'Pts.', 'Jou.', 'Gagn.', 'Perd.']
        available_columns = [col for col in desired_columns if col in df_clean.columns]
        df_clean = df_clean[available_columns]
        
        # Remove header rows (rows where 'Class.' is NaN or contains header text)
        df_clean = df_clean[df_clean['Class.'].notna()]
        df_clean = df_clean[~df_clean['Class.'].astype(str).str.contains('Pts.|Class.', case=False, na=False)]
        
        # Convert numeric columns to integers (no decimals)
        integer_columns = ['Class.', 'Pts.', 'Jou.', 'Gagn.', 'Perd.']
        for col in integer_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)
        
        # Calculate win percentage
        if 'Gagn.' in df_clean.columns and 'Perd.' in df_clean.columns:
            # Calculate percentage (wins / total games * 100)
            total_games = df_clean['Gagn.'] + df_clean['Perd.']
            percentage_values = ((df_clean['Gagn.'] / total_games) * 100).round(1)
            
            # Handle division by zero (when total games = 0)
            percentage_values = percentage_values.fillna(0)
            
            # Format as text with French decimal separator and % symbol
            # Remove decimal part if it's zero (e.g., 100,0 % becomes 100 %)
            def format_percentage(x):
                if x == int(x):  # If it's a whole number
                    return f"{int(x)} %"
                else:
                    return f"{x:.1f}".replace('.', ',') + " %"
            
            df_clean['Pourcentage'] = percentage_values.apply(format_percentage)
    
    # Save to Excel
    df_clean.to_excel(filename, index=False, engine='openpyxl')
    return df_clean


def scrape_ffvb_volleyball_results(url, output_filename=None):
    """
    Main function to scrape volleyball results from FFVB Beach website.
    
    Args:
        url (str): URL of the FFVB Beach results page
        output_filename (str): Custom filename for output (optional)
        
    Returns:
        pandas.DataFrame: Scraped volleyball data, or None if scraping failed
    """
    print(f"Starting scrape of: {url}")
    
    # Set up Chrome driver
    driver, temp_dir = setup_chrome_driver()
    if driver is None:
        return None
    
    try:
        # Load the page
        driver.get(url)
        print("Page loaded, waiting for content to render...")
        time.sleep(5)
        
        # Wait for tables to be present
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            print("Tables found, proceeding with extraction...")
        except Exception as e:
            print(f"Warning: Could not wait for tables to load: {e}")
        
        # Get page info
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Find and extract volleyball table
        volleyball_data = find_volleyball_table(driver)
        
        if volleyball_data is not None:
            # Clean and save the data
            filename = output_filename if output_filename else "ffvb_results.xlsx"
            cleaned_data = clean_and_save_data(volleyball_data, filename)
            print(f"\nScraping completed successfully!")
            print(f"Scraped {len(cleaned_data)} rows of data")
            print(f"Data saved to '{filename}'")
            
            # Display summary
            print(f"\nData summary:")
            print(f"Columns: {list(cleaned_data.columns)}")
            print(f"\nAll rows:")
            print(cleaned_data.to_string(index=False))
            
            return cleaned_data
        else:
            print("No suitable volleyball results table found on the page.")
            return None
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
        
    finally:
        # Clean up
        driver.quit()
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def process_multiple_teams(config_file="teams.csv"):
    """
    Process multiple teams from configuration file.
    
    Args:
        config_file (str): Path to the CSV configuration file
    """
    print("🏐 Starting multi-team volleyball scraper...")
    print("=" * 50)
    
    # Load team configurations
    teams = load_teams_config(config_file)
    
    if not teams:
        print("No teams to process. Exiting.")
        return
    
    successful_scrapes = 0
    failed_scrapes = 0
    
    for i, (team_name, team_url) in enumerate(teams, 1):
        print(f"\n[{i}/{len(teams)}] Processing: {team_name}")
        print("-" * 40)
        
        # Clean team name for filename (remove special characters)
        safe_filename = "".join(c for c in team_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        output_file = f"{safe_filename}.xlsx"
        
        # Scrape the team data
        result = scrape_ffvb_volleyball_results(team_url, output_file)
        
        if result is not None:
            successful_scrapes += 1
            print(f"✅ {team_name} - Success! Data saved to '{output_file}'")
        else:
            failed_scrapes += 1
            print(f"❌ {team_name} - Failed to scrape data")
        
        # Add a small delay between requests to be respectful to the server
        if i < len(teams):
            print("⏳ Waiting 2 seconds before next team...")
            time.sleep(2)
    
    # Final summary
    print("\n" + "=" * 50)
    print("🏐 SCRAPING SUMMARY")
    print("=" * 50)
    print(f"✅ Successful: {successful_scrapes}")
    print(f"❌ Failed: {failed_scrapes}")
    print(f"📊 Total teams processed: {len(teams)}")
    
    if successful_scrapes > 0:
        print(f"\n🎉 {successful_scrapes} Excel files have been created!")
        print("Check the current directory for the generated files.")


def process_single_argument(arg, config_file="teams.csv"):
    """
    Process a single argument - either a team name or direct URL.
    
    Args:
        arg (str): Team name from config or direct URL
        config_file (str): Path to the CSV configuration file
    """
    # Load team configurations to check if arg is a team name
    teams = load_teams_config(config_file)
    team_dict = {team_name: team_url for team_name, team_url in teams}
    
    if arg in team_dict:
        # Argument is a team name from config
        team_name = arg
        team_url = team_dict[arg]
        print(f"🏐 Processing team from config: {team_name}")
        
        # Clean team name for filename
        safe_filename = "".join(c for c in team_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        output_file = f"{safe_filename}.xlsx"
        
        result = scrape_ffvb_volleyball_results(team_url, output_file)
        
        if result is not None:
            print(f"\n✅ Scraping completed! Check '{output_file}' for the results.")
        else:
            print(f"\n❌ Scraping failed. Please check the team configuration.")
            
    elif arg.startswith('http'):
        # Argument is a direct URL
        print(f"🏐 Processing direct URL")
        
        # Generate random filename
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        output_file = f"volleyball_results_{random_suffix}.xlsx"
        
        result = scrape_ffvb_volleyball_results(arg, output_file)
        
        if result is not None:
            print(f"\n✅ Scraping completed! Check '{output_file}' for the results.")
        else:
            print(f"\n❌ Scraping failed. Please check the URL and try again.")
    else:
        # Invalid argument
        print(f"❌ Invalid argument: '{arg}'")
        print("Expected:")
        print("  - Team name from teams.csv:", list(team_dict.keys()))
        print("  - Direct URL starting with 'http'")
        print("\nAvailable teams in teams.csv:")
        for team_name in team_dict.keys():
            print(f"  - {team_name}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # No arguments - process all teams from config (default behavior)
        print("🏐 No arguments provided - processing all teams from teams.csv")
        process_multiple_teams()
        
    elif len(sys.argv) == 2:
        # One argument - either team name or direct URL
        arg = sys.argv[1]
        process_single_argument(arg)
        
    else:
        # Too many arguments
        print("❌ Invalid number of arguments!")
        print("\nUsage:")
        print("  python volley_scraper_final.py                    # Process all teams from teams.csv")
        print("  python volley_scraper_final.py <team_name>        # Process specific team from teams.csv") 
        print("  python volley_scraper_final.py <direct_url>       # Process direct URL")
        print("\nExamples:")
        print("  python volley_scraper_final.py PreNat")
        print("  python volley_scraper_final.py https://www.ffvbbeach.org/ffvbapp/resu/...")
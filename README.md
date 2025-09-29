# FFVB Volleyball Results Scraper

This Python script scrapes volleyball standings/results from the FFVB Beach website (Fédération Française de Volley Ball).

## Features

- Scrapes volleyball league standings from FFVB Beach website
- Automatically identifies the correct data table among multiple tables on the page
- Extracts comprehensive team statistics including:
  - Team rankings and points
  - Games played, wins, losses
  - Set-by-set results (3-0, 3-1, 3-2, 2-3, 1-3, 0-3)
  - Points for/against and ratios
- Saves data to CSV with proper column names
- Robust error handling and Chrome driver management

## Requirements

### System Requirements
- Python 3.7+
- Google Chrome browser (latest version recommended)
- Internet connection

### Python Dependencies  
All required packages are listed in `requirements.txt`:
- **selenium**: Web browser automation
- **pandas**: Data manipulation and analysis
- **lxml**: HTML/XML parsing (required by pandas)
- **openpyxl**: Excel file creation and editing
- **numpy**: Numerical computing (pandas dependency)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Make sure Google Chrome is installed on your system
5. Verify your setup (optional):
   ```bash
   python verify_setup.py
   ```

## Usage

### Usage Modes

The scraper supports three modes based on command line arguments:

#### 1. **Multi-Team Mode (No Arguments)**
Process all teams from the configuration file:
```bash
python volley_scraper_final.py
```
- Reads all teams from `teams.csv`
- Processes each team sequentially
- Creates separate Excel files for each team (named after the team)
- Displays a progress summary

#### 2. **Single Team by Name (One Argument - Team Name)**
Process a specific team from the configuration:
```bash
python volley_scraper_final.py PreNat
python volley_scraper_final.py R2F
```
- Looks up the team name in `teams.csv`
- Uses the corresponding URL from the configuration
- Creates an Excel file named after the team

#### 3. **Direct URL Mode (One Argument - URL)**
Process a direct URL with random filename:
```bash
python volley_scraper_final.py "https://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier.php?saison=2025%2F2026&codent=LILR&poule=FPO&calend=COMPLET&equipe=3"
```
- Processes the provided URL directly
- Generates a random filename like `volleyball_results_abc123.xlsx`
- No need to add the URL to the configuration file

### Configuration File

Create a `teams.csv` file with your team information:
```csv
# Team_Name,URL
Equipe_A,https://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier.php?saison=2025%2F2026&codent=LILR&poule=FPO&calend=COMPLET&equipe=1
Equipe_B,https://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier.php?saison=2025%2F2026&codent=LILR&poule=FPO&calend=COMPLET&equipe=2
My_Team,https://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier.php?saison=2025%2F2026&codent=LILR&poule=FPO&calend=COMPLET&equipe=3
```

**Format:**
- Each line: `Team_Name,URL`
- Team name will be used as the Excel filename (special characters are cleaned)
- Lines starting with `#` are ignored (comments)
- Empty lines are ignored

### Custom Usage (Programming)

You can also use it as a module:

```python
from volley_scraper_final import scrape_ffvb_volleyball_results

# Scrape a specific competition
url = "https://www.ffvbbeach.org/ffvbapp/resu/vbspo_calendrier.php?saison=2025%2F2026&codent=LILR&poule=FPO&calend=COMPLET&equipe=3"
data = scrape_ffvb_volleyball_results(url, "my_team.xlsx")

if data is not None:
    print(f"Scraped {len(data)} teams")
    print(data.head())
```

### Modifying the URL

To scrape different competitions, modify the URL parameters:
- `saison`: Season (e.g., 2025%2F2026)
- `codent`: Region code (e.g., LILR)
- `poule`: Pool/division (e.g., FPO)
- `equipe`: Team number (e.g., 3)

## Output

The script creates a CSV file named `ffvb_results.csv` with the following columns:

| Column | Description |
|--------|-------------|
| Rank | Team ranking position |
| Team | Team name |
| Points | Total points |
| Games_Played | Number of games played |
| Wins | Number of wins |
| Losses | Number of losses |
| Forfeits | Number of forfeits |
| Wins_3-0 | Wins with 3-0 score |
| Wins_3-1 | Wins with 3-1 score |
| Wins_3-2 | Wins with 3-2 score |
| Losses_2-3 | Losses with 2-3 score |
| Losses_1-3 | Losses with 1-3 score |
| Losses_0-3 | Losses with 0-3 score |
| Sets_For | Total sets won |
| Sets_Against | Total sets lost |
| Sets_Ratio | Sets won/lost ratio |
| Points_For | Total points scored |
| Points_Against | Total points conceded |
| Points_Ratio | Points scored/conceded ratio |

## Example Output

```
Rank,Team,Points,Games_Played,Wins,Losses,Forfeits,Wins_3-0,Wins_3-1,Wins_3-2,Losses_2-3,Losses_1-3,Losses_0-3,Sets_For,Sets_Against,Sets_Ratio,Points_For,Points_Against,Points_Ratio
1.0,IBOS VOLLEY 1,6,2,2,,,2,,,,,,6,,MAX,152,113,1.345
2.0,GRENADE VOLLEY BALL 1,6,2,2,,,1,1,,,,,6,1,6.000,167,130,1.285
3.0,TOULOUSE ATHLETIC CLUB 1,5,2,2,,,1,,1,,,,6,2,3.000,192,174,1.103
```

## Troubleshooting

### Chrome Driver Issues
- Make sure Google Chrome is installed
- The script automatically manages ChromeDriver through Selenium

### No Data Found
- Check if the URL is correct and accessible
- The website might have changed its structure
- Increase the wait time if the page loads slowly

### Permission Errors
- Run with appropriate permissions
- Make sure the output directory is writable

## Technical Details

The scraper:
1. Uses Selenium WebDriver with headless Chrome
2. Waits for JavaScript to render the page content
3. Analyzes all tables on the page using pattern matching
4. Selects the most likely volleyball data table
5. Cleans and structures the data with meaningful column names
6. Handles errors gracefully and cleans up resources

## Files

- `volley_scraper_final.py` - Main scraper script with improved structure
- `scrapper.py` - Original working version
- `ffvb_results.csv` - Output CSV file (generated after running)

## License

This project is for educational and personal use. Please respect the FFVB website's terms of service and don't overload their servers with too frequent requests.
# Trails Database Scraper

A Python script to scrape game script dialogue from [trailsinthedatabase.com](https://trailsinthedatabase.com), process the text, and export to TXT or HTML formats.

## Features

- Scrape dialogue entries by ID range (e.g., entries 232-250)
- Choose between English or Japanese text
- Export to TXT, HTML, or both formats
- Automatic text processing (removes newlines, collapses whitespace)
- Formatted output: `{number}. "{text}", {character_name}`

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py <URL> <START_ID> <FINISH_ID> [--lang en|jp] [--format txt|html|both]
```

### Arguments

- `URL`: Base URL (without anchor) to the game scripts page
- `START_ID`: Starting entry ID number
- `FINISH_ID`: Ending entry ID number
- `--lang`: Language selection (default: `en`)
  - `en`: English text
  - `jp`: Japanese text
- `--format`: Export format (default: `both`)
  - `txt`: Plain text file only
  - `html`: HTML file with styling only
  - `both`: Both TXT and HTML files

### Examples

```bash
# Scrape English text, export to TXT only
python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 232 250 --lang en --format txt

# Scrape Japanese text, export to HTML only
python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 232 250 --lang jp --format html

# Scrape English text, export to both formats
python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 232 250 --lang en --format both
```

## Output Files

Output files are named in the format:
- `output_{fname}_{start}_{finish}_{lang}.txt` - Plain text format
- `output_{fname}_{start}_{finish}_{lang}.html` - HTML format with styling

Example: `output_t5520_232_250_en.txt`

## How It Works

1. Fetches the HTML page from the provided URL
2. Extracts dialogue entries by ID from the HTML table structure:
   - Cell 1: ID and number
   - Cell 2: Character icon (skipped)
   - Cell 3: English text
   - Cell 4: Japanese text
3. Processes text by:
   - Removing newlines and replacing with spaces
   - Collapsing multiple spaces to single space
   - Stripping leading/trailing whitespace
4. Formats entries as: `{number}. "{text}", {character_name}`
5. Exports to selected format(s)

## Error Handling

- Handles missing entries gracefully (skips if ID doesn't exist)
- Retries network requests on failure (3 attempts with 1 second delay)
- Validates URL format and number ranges
- Provides informative error messages

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- lxml >= 4.9.0

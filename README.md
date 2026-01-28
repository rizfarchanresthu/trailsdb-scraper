# Trails Database Scraper

A Python script to scrape game script dialogue from [trailsinthedatabase.com](https://trailsinthedatabase.com), process the text, and export to TXT or HTML formats.

## Features

- **Interactive CLI**: User-friendly prompts with examples (default mode)
- **Non-Interactive Mode**: Command-line arguments for automation/scripting
- Scrape dialogue entries by ID range (e.g., entries 1-250, or 200 to end)
- Scrape until end of entries (use "end" or "END" as finish parameter)
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

### Interactive Mode (Default)

Simply run the script without arguments to enter interactive mode:

```bash
python scraper.py
```

The script will prompt you for:
- **URL**: Base URL with example placeholder
- **Start ID**: Starting entry ID (default: 1)
- **Finish ID**: Ending entry ID or "end" to scrape until end (default: 250)
- **Language**: Select English (en) or Japanese (jp)
- **Export Format**: Select TXT only, HTML only, or Both

Example interactive session:
```
============================================================
  Trails Database Scraper - Interactive Mode
============================================================

Enter URL: https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6
Start ID: 1
Finish ID (or 'end' to scrape until end): end

Language options:
  [1] English (en)
  [2] Japanese (jp)
Select language [1]: 1

Export format options:
  [1] TXT only
  [2] HTML only
  [3] Both (TXT and HTML)
Select format [3]: 3
```

### Non-Interactive Mode

For automation or scripting, use the `--non-interactive` flag:

```bash
python scraper.py --non-interactive <URL> <START_ID> <FINISH_ID> [--lang en|jp] [--format txt|html|both]
```

**Arguments:**
- `URL`: Base URL (without anchor) to the game scripts page
- `START_ID`: Starting entry ID number (must be at least 1)
- `FINISH_ID`: Ending entry ID number, or `"end"`/`"END"` to scrape until no more entries are found
- `--lang`: Language selection (default: `en`)
  - `en`: English text
  - `jp`: Japanese text
- `--format`: Export format (default: `both`)
  - `txt`: Plain text file only
  - `html`: HTML file with styling only
  - `both`: Both TXT and HTML files

**Non-Interactive Examples:**

```bash
# Scrape from ID 1 to 250, English text, export to TXT only
python scraper.py --non-interactive "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 1 250 --lang en --format txt

# Scrape from ID 200 to end, Japanese text, export to HTML only
python scraper.py --non-interactive "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 200 end --lang jp --format html

# Scrape from ID 1 to end, English text, export to both formats
python scraper.py --non-interactive "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 1 END --lang en --format both
```

## Output Files

Output files are named in the format:
- `output_{fname}_{start}_{finish}_{lang}.txt` - Plain text format
- `output_{fname}_{start}_{finish}_{lang}.html` - HTML format with styling

Examples:
- `output_t5520_1_250_en.txt` (when finish is a number)
- `output_t5520_200_end_jp.html` (when finish is "end")

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
- When finish is "end"/"END", stops after 10 consecutive missing entries
- Retries network requests on failure (3 attempts with 1 second delay)
- Validates URL format, start number, and finish number/end option
- Provides informative error messages

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- lxml >= 4.9.0
- prompt_toolkit >= 3.0.0 (for interactive mode)

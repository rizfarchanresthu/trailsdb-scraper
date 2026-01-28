#!/usr/bin/env python3
"""
Trails Database Scraper
Scrapes game script dialogue from trailsinthedatabase.com
"""

import argparse
import re
import sys
import time
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup


def fetch_page(url, retries=3, delay=1):
    """
    Fetch HTML page with retry logic.
    
    Args:
        url: URL to fetch
        retries: Number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        BeautifulSoup object or None if failed
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"Error fetching {url}: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None
    
    return None


def process_text(text):
    """
    Process text by removing newlines and collapsing whitespace.
    
    Args:
        text: Raw text string
    
    Returns:
        Processed text with newlines replaced by spaces
    """
    if not text:
        return ""
    
    # Replace newlines and carriage returns with space
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Collapse multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_entry(soup, entry_id, language):
    """
    Extract dialogue entry from HTML.
    
    Args:
        soup: BeautifulSoup object of the page
        entry_id: ID number to extract (e.g., 232)
        language: 'en' for English or 'jp' for Japanese
    
    Returns:
        Tuple of (number, text, character_name) or None if not found
    """
    # Find the element with the specific ID
    entry_element = soup.find(id=str(entry_id))
    
    if not entry_element:
        return None
    
    # Find the parent table row
    row = entry_element.find_parent('tr')
    if not row:
        return None
    
    # Get all table cells
    cells = row.find_all('td')
    if len(cells) < 4:
        return None
    
    # Cell 1: ID and number
    number_cell = cells[0]
    number_text = number_cell.get_text(strip=True)
    # Extract just the number (might be in format like "242" or "ID: 242")
    number_match = re.search(r'(\d+)', number_text)
    if not number_match:
        return None
    number = number_match.group(1)
    
    # Cell 2: Character icon (skip)
    # Cell 3: English text (index 2)
    # Cell 4: Japanese text (index 3)
    
    # Select text cell based on language
    text_cell_index = 2 if language == 'en' else 3
    text_cell = cells[text_cell_index]
    
    # Extract character name (usually in a span or div with class containing "name" or "character")
    # Try to find character name in the text cell or nearby elements
    character_name = "Unknown"
    
    # Look for character name in various possible locations
    name_elements = text_cell.find_all(['span', 'div', 'strong', 'b'], class_=re.compile(r'name|character', re.I))
    if not name_elements:
        # Try finding in the first cell or look for bold text
        name_in_first = cells[0].find(['span', 'div', 'strong', 'b'])
        if name_in_first:
            character_name = name_in_first.get_text(strip=True)
        else:
            # Look for any bold text in the row
            bold_text = row.find(['strong', 'b'])
            if bold_text:
                character_name = bold_text.get_text(strip=True)
    else:
        character_name = name_elements[0].get_text(strip=True)
    
    # If character name is still not found, try to extract from the text cell structure
    # Sometimes the name is in a separate element before the dialogue
    if character_name == "Unknown":
        # Check if there's a structure like <div class="character-name"> or similar
        for elem in text_cell.find_all(['div', 'span', 'p']):
            classes = elem.get('class', [])
            if any('name' in str(c).lower() or 'char' in str(c).lower() for c in classes):
                character_name = elem.get_text(strip=True)
                break
    
    # Extract dialogue text (everything except the character name)
    dialogue_text = text_cell.get_text(separator=' ', strip=False)
    
    # Remove character name from dialogue if it appears at the start
    if character_name != "Unknown" and dialogue_text.startswith(character_name):
        dialogue_text = dialogue_text[len(character_name):].strip()
    
    # Process the text
    processed_text = process_text(dialogue_text)
    
    if not processed_text:
        return None
    
    return (number, processed_text, character_name)


def scrape_entries(base_url, start_id, finish_id, language):
    """
    Scrape multiple entries from the website.
    
    Args:
        base_url: Base URL without anchor
        start_id: Starting ID number
        finish_id: Ending ID number, or "end"/"END" to scrape until no more entries
        language: 'en' for English or 'jp' for Japanese
    
    Returns:
        List of tuples (number, text, character_name)
    """
    entries = []
    
    # Fetch the base page once (entries are likely all on the same page)
    soup = fetch_page(base_url)
    if not soup:
        return entries
    
    # Determine if we should scrape until end
    scrape_until_end = isinstance(finish_id, str) and finish_id.lower() == 'end'
    
    if scrape_until_end:
        print(f"Scraping entries from {start_id} to end...")
        consecutive_misses = 0
        max_consecutive_misses = 10
        entry_id = start_id
        
        while consecutive_misses < max_consecutive_misses:
            entry = extract_entry(soup, entry_id, language)
            if entry:
                entries.append(entry)
                consecutive_misses = 0  # Reset counter on success
                print(f"  Found entry {entry_id}: {entry[0]}. \"{entry[1][:50]}...\", {entry[2]}")
            else:
                consecutive_misses += 1
                if consecutive_misses < max_consecutive_misses:
                    print(f"  Entry {entry_id} not found ({consecutive_misses}/{max_consecutive_misses} consecutive misses)...")
            
            entry_id += 1
        
        print(f"  Stopped after {max_consecutive_misses} consecutive missing entries.")
    else:
        print(f"Scraping entries {start_id} to {finish_id}...")
        
        for entry_id in range(start_id, finish_id + 1):
            entry = extract_entry(soup, entry_id, language)
            if entry:
                entries.append(entry)
                print(f"  Found entry {entry_id}: {entry[0]}. \"{entry[1][:50]}...\", {entry[2]}")
            else:
                print(f"  Entry {entry_id} not found, skipping...")
    
    return entries


def format_entry(number, text, character_name):
    """
    Format entry as specified: {number}. "{text}", {character_name}
    
    Args:
        number: Entry number
        text: Processed dialogue text
        character_name: Character name
    
    Returns:
        Formatted string
    """
    return f'{number}. "{text}", {character_name}'


def export_txt(entries, filename):
    """
    Export entries to TXT file.
    
    Args:
        entries: List of (number, text, character_name) tuples
        filename: Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for number, text, character_name in entries:
            formatted = format_entry(number, text, character_name)
            f.write(formatted + '\n')
    
    print(f"Exported {len(entries)} entries to {filename}")


def export_html(entries, filename):
    """
    Export entries to HTML file with styling.
    
    Args:
        entries: List of (number, text, character_name) tuples
        filename: Output filename
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trails Database Script</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        .entry {
            margin: 15px 0;
            padding: 15px;
            background-color: #fafafa;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }
        .entry-number {
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }
        .entry-text {
            margin: 8px 0;
            color: #333;
            font-size: 1.05em;
        }
        .entry-character {
            font-style: italic;
            color: #888;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Trails Database Script</h1>
"""
    
    for number, text, character_name in entries:
        formatted_text = text.replace('"', '&quot;')
        html_content += f"""        <div class="entry">
            <div class="entry-number">Entry {number}</div>
            <div class="entry-text">"{formatted_text}"</div>
            <div class="entry-character">{character_name}</div>
        </div>
"""
    
    html_content += """    </div>
</body>
</html>"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Exported {len(entries)} entries to {filename}")


def extract_fname_from_url(url):
    """
    Extract fname parameter from URL for output filename.
    
    Args:
        url: URL string
    
    Returns:
        fname value or 'output'
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return params.get('fname', ['output'])[0]


def main():
    """Main function to handle command-line arguments and orchestrate scraping."""
    parser = argparse.ArgumentParser(
        description='Scrape game script dialogue from trailsinthedatabase.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 1 250 --lang en --format txt
  python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 200 end --lang jp --format html
  python scraper.py "https://trailsinthedatabase.com/game-scripts?fname=t5520&game_id=6" 1 END --lang en --format both
        """
    )
    
    parser.add_argument('url', help='Base URL (without anchor)')
    parser.add_argument('start', type=int, help='Starting ID number')
    parser.add_argument('finish', help='Ending ID number, or "end"/"END" to scrape until no more entries')
    parser.add_argument('--lang', choices=['en', 'jp'], default='en',
                       help='Language: en for English, jp for Japanese (default: en)')
    parser.add_argument('--format', choices=['txt', 'html', 'both'], default='both',
                       help='Export format: txt, html, or both (default: both)')
    
    args = parser.parse_args()
    
    # Validate start number
    if args.start < 1:
        print("Error: Start number must be at least 1")
        sys.exit(1)
    
    # Parse finish - can be number or "end"/"END"
    finish_is_end = isinstance(args.finish, str) and args.finish.lower() == 'end'
    
    if finish_is_end:
        finish_id = 'end'
    else:
        try:
            finish_id = int(args.finish)
            if finish_id < args.start:
                print("Error: Finish number must be greater than or equal to start number")
                sys.exit(1)
            if finish_id < 1:
                print("Error: Finish number must be at least 1")
                sys.exit(1)
        except ValueError:
            print(f"Error: Finish must be a number or 'end'/'END', got '{args.finish}'")
            sys.exit(1)
    
    # Remove anchor from URL if present
    base_url = args.url.split('#')[0]
    
    # Scrape entries
    entries = scrape_entries(base_url, args.start, args.finish, args.lang)
    
    if not entries:
        print("No entries found. Exiting.")
        sys.exit(1)
    
    # Generate output filename
    fname = extract_fname_from_url(base_url)
    lang_suffix = 'en' if args.lang == 'en' else 'jp'
    finish_str = 'end' if finish_is_end else str(finish_id)
    base_filename = f"output_{fname}_{args.start}_{finish_str}_{lang_suffix}"
    
    # Export based on format selection
    if args.format in ['txt', 'both']:
        txt_filename = f"{base_filename}.txt"
        export_txt(entries, txt_filename)
    
    if args.format in ['html', 'both']:
        html_filename = f"{base_filename}.html"
        export_html(entries, html_filename)
    
    print(f"\nScraping complete! Found {len(entries)} entries.")


if __name__ == '__main__':
    main()

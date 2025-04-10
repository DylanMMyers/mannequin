import os
import csv
import re
import time
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}
output_dir = 'size_charts'
progress_file = 'scraping_progress.json'
os.makedirs(output_dir, exist_ok=True)

# Rate limiting settings
REQUEST_DELAY = 2  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

def clean_text(text):
    """Convert fractions to decimals and clean special characters"""
    if not text:
        return ""
    replacements = {
        r'½': '.5', r'¼': '.25', r'¾': '.75',
        r'\s+': ' ', r'[^\w\s\.-]': '_'
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, str(text))
    return text.strip()

def load_progress():
    """Load progress from file"""
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading progress: {e}")
    return {'completed_brands': [], 'last_update': None}

def save_progress(progress):
    """Save progress to file"""
    progress['last_update'] = datetime.now().isoformat()
    try:
        with open(progress_file, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Error saving progress: {e}")

def make_request(session, url, retries=MAX_RETRIES):
    """Make a request with retry logic"""
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)  # Rate limiting
            return response
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            print(f"Request failed: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

def process_chart(chart, brand_name, output_dir, tab_name=None):
    """Process a single chart and save to CSV"""
    try:
        chart_title = chart.find(['h2', 'h3'])
        chart_name = clean_text(chart_title.text) if chart_title else "unnamed_chart"
        
        # Include tab name in filename if available
        tab_suffix = f"_{clean_text(tab_name)}" if tab_name else ""
        filename = f"{brand_name}{tab_suffix}_{chart_name}.csv"
        filepath = os.path.join(output_dir, filename)
        
        table = chart.find('table')
        if not table:
            print("  No table found in chart")
            return
            
        rows = table.find_all('tr')
        if not rows:
            print("  No rows in table")
            return
            
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Process headers - use table's own headers and add tab name
            headers = [clean_text(th.text) for th in rows[0].find_all(['th', 'td'])]
            writer.writerow(['Tab'] + headers)
            
            # Process data rows
            for row in rows[1:]:
                cells = [clean_text(cell.text) for cell in row.find_all(['td', 'th'])]
                if any(cells):  # Only write row if it contains any data
                    writer.writerow([tab_name or ""] + cells)
                    
        print(f"  Saved: {filename}")
        return True
        
    except Exception as e:
        print(f"  Chart error: {str(e)}")
        return False

def main():
    # Load progress
    progress = load_progress()
    completed_brands = set(progress['completed_brands'])
    
    # Create a session for connection pooling
    with requests.Session() as session:
        # Get brand URLs
        print("Fetching brand list...")
        response = make_request(session, "https://www.sizecharter.com/brands/")
        soup = BeautifulSoup(response.content, 'html.parser')
        brand_list = soup.find('ul', id='list')
        brand_urls = [urljoin("https://www.sizecharter.com/brands/", a['href']) 
                     for a in brand_list.find_all('a')] if brand_list else []
        
        total_brands = len(brand_urls)
        print(f"Found {total_brands} brands")
        
        for i, brand_url in enumerate(brand_urls, 1):
            brand_name = clean_text(brand_url.split('/')[-2].replace('-', ' '))
            
            if brand_name in completed_brands:
                print(f"Skipping completed brand: {brand_name}")
                continue
                
            try:
                print(f"\nProcessing brand {i}/{total_brands}: {brand_name}")
                response = make_request(session, brand_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find navigation tabs
                tabs_nav = soup.find('nav', {'role': 'navigation', 'class': 'tabs'}) or soup.find('ul', class_='tabs')
                if tabs_nav:
                    tab_links = []
                    for tab in tabs_nav.find_all('a'):
                        tab_links.append((tab.get('href'), clean_text(tab.text)))
                else:
                    tab_links = [(brand_url, None)]
                
                charts_processed = 0
                for tab_link, tab_name in tab_links:
                    try:
                        tab_url = urljoin(brand_url, tab_link)
                        print(f"  Visiting tab: {tab_url} ({tab_name or 'default'})")
                        
                        tab_response = make_request(session, tab_url)
                        tab_soup = BeautifulSoup(tab_response.text, 'html.parser')
                        
                        box_div = tab_soup.find('div', class_='box')
                        if not box_div:
                            print("  No box div found")
                            continue
                        
                        for chart in box_div.find_all(class_='chart'):
                            if process_chart(chart, brand_name, output_dir, tab_name):
                                charts_processed += 1
                                
                    except Exception as tab_error:
                        print(f"  Tab error: {str(tab_error)}")
                        continue
                
                if charts_processed > 0:
                    completed_brands.add(brand_name)
                    progress['completed_brands'] = list(completed_brands)
                    save_progress(progress)
                    print(f"  Completed brand {brand_name} with {charts_processed} charts")
                
            except Exception as brand_error:
                print(f"Brand error for {brand_name}: {str(brand_error)}")
                continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        print("\nScraping completed")

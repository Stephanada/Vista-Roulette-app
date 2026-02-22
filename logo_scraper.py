import json
import urllib.request
import ssl
from bs4 import BeautifulSoup
import time

def scrape_logos():
    print("Loading stations_db.json...")
    with open("stations_db.json", "r") as f:
        stations = json.load(f)

    # Disable SSL verification for simple scraping
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"Scraping {len(stations)} stations for MyTownNow logos...")
    
    # Track unique URLs we've already scraped to save time
    cache = {}

    for i, station in enumerate(stations):
        url = station.get("mytownnow_url")
        if not url:
            station["mytownnow_logo_url"] = ""
            continue
            
        if url in cache:
            station["mytownnow_logo_url"] = cache[url]
            continue
            
        print(f"[{i+1}/{len(stations)}] Fetching: {url}")
        
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            html = urllib.request.urlopen(req, context=ctx, timeout=10).read()
            soup = BeautifulSoup(html, 'html.parser')
            
            # The standard MyTownNow NewspaperWP theme uses the class .tdb-logo-img for the header logo
            logo_img = soup.find('img', class_='tdb-logo-img')
            
            logo_url = ""
            if logo_img and logo_img.get('src'):
                logo_url = logo_img['src']
            else:
                # Fallback: look for any img with 'logo' in the src
                imgs = soup.find_all('img')
                for img in imgs:
                    src = img.get('src', '')
                    if 'logo' in src.lower() and '.png' in src.lower():
                        logo_url = src
                        break

            print(f"  -> Found Logo: {logo_url}")
            station["mytownnow_logo_url"] = logo_url
            cache[url] = logo_url
            
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")
            station["mytownnow_logo_url"] = ""
            
        # polite delay
        time.sleep(0.5)
        
    print("Saving updated stations_db.json...")
    with open("stations_db.json", "w") as f:
        json.dump(stations, f, indent=4)
        
    print("Done!")

if __name__ == "__main__":
    scrape_logos()

#!/usr/bin/env python3
"""
Scrape actual stream URLs from Vista Radio's player pages.
Each station has a player at: https://radioplayer.vistaradio.ca/{slug}
"""

import json
import requests
import re
from time import sleep

def get_stream_url(slug):
    """
    Fetch the stream URL from Vista Radio's player page.
    """
    player_url = f"https://radioplayer.vistaradio.ca/{slug}"
    
    try:
        response = requests.get(player_url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Look for stream URL patterns in the HTML
        # Common patterns: .mp3, .pls, .m3u, ice servers, stream URLs
        patterns = [
            r'https?://[^\s"\'<>]+\.(?:mp3|m3u8?|pls|aac)',  # Direct stream files
            r'https?://(?:ice\d*|stream)\.securenetsystems\.net/[^\s"\'<>]+',  # Securenet streams
            r'https?://[^\s"\'<>]+/stream[^\s"\'<>]*',  # Generic /stream endpoints
            r'"stream":\s*"([^"]+)"',  # JSON stream field
            r'"url":\s*"([^"]+)"',  # JSON url field
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                # Return the first match
                stream = matches[0]
                if isinstance(stream, tuple):
                    stream = stream[0]
                print(f"  ✓ {slug}: {stream}")
                return stream
        
        print(f"  ✗ {slug}: No stream URL found")
        return None
        
    except Exception as e:
        print(f"  ✗ {slug}: Error - {e}")
        return None

def main():
    # Load existing stations
    with open('stations_db.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
    
    print(f"Scraping stream URLs for {len(stations)} stations...\n")
    
    updated_count = 0
    for station in stations:
        slug = station['slug']
        stream_url = get_stream_url(slug)
        
        if stream_url:
            station['stream_url'] = stream_url
            updated_count += 1
        
        # Be polite to the server
        sleep(0.5)
    
    # Save updated stations
    with open('stations_db.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4)
    
    print(f"\n✅ Updated {updated_count}/{len(stations)} stations with stream URLs")
    print(f"📝 Saved to stations_db.json")

if __name__ == "__main__":
    main()

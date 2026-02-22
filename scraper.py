import requests
from bs4 import BeautifulSoup
import re
import json
import time

def main():
    print("Fetching radioplayer.vistaradio.ca landing page...")
    resp = requests.get('https://radioplayer.vistaradio.ca/')
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    stations = []
    
    links = soup.find_all('a', class_='station')
    print(f"Found {len(links)} stations on landing page.")
    
    for link in links:
        slug = link.get('rel')
        if not slug:
            continue
            
        if isinstance(slug, list):
            slug = slug[0]
            
        img = link.find('img')
        name = slug.upper()
        format_name = "Mixed"
        logo_url = ""
        
        if img:
            logo_url = img.get('src', '')
            if img.get('alt'):
                alt_text = img.get('alt')
                parts = alt_text.split('-', 1)
                name = parts[0].strip()
                if len(parts) > 1:
                    format_name = parts[1].strip()
                
        stations.append({
            'name': name,
            'slug': slug,
            'format': format_name,
            'province': 'AB', # Default
            'logo_url': logo_url,
            'town': 'Local',
            'mytownnow_url': 'https://www.vistaradio.ca'
        })
        
    print(f"Scraped {len(stations)} basic stations. Fetching streams and town data...")
    
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for st in stations:
        try:
            # Get Stream ID
            player_url = f"https://radioplayer.vistaradio.ca/{st['slug']}"
            r = requests.get(player_url, timeout=5)
            match = re.search(r'SB\d{5}', r.text)
            if match:
                st['stream_url'] = f"https://vistaradio.streamb.live/{match.group(0)}?args=web_01"
                
                # Get Brand Data (Town, MyTownNow link)
                brand_url = f"https://www.vistaradio.ca/brands/{st['slug']}/"
                br = requests.get(brand_url, headers=headers, timeout=5)
                if br.status_code == 200:
                    bsoup = BeautifulSoup(br.text, 'html.parser')
                    h3s = bsoup.find_all('h3')
                    for h3 in h3s:
                        a_tag = h3.find('a')
                        if a_tag and a_tag.get('href') and ('now.com' in a_tag.get('href') or 'my' in a_tag.get('href')):
                            st['mytownnow_url'] = a_tag.get('href')
                            st['town'] = a_tag.text.strip()
                            break
                            
                results.append(st)
        except Exception as e:
            pass
            
    with open("stations_db.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Finished. Saved {len(results)} stations.")

if __name__ == '__main__':
    main()

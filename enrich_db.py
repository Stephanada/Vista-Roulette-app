import csv
import json
import os

def get_prov(town):
    t = str(town).lower()
    if any(k in t for k in ['ab', 'grande', 'lethbridge', 'olds', 'vegreville', 'lloydminster', 'bonnyville']): return 'AB'
    if any(k in t for k in ['on', 'north bay', 'timmins', 'stratford', 'kapuskasing', 'bracebridge', 'huntsville', 'elliot', 'parry', 'sturgeon', 'espanola', 'bancroft', 'haliburton', 'kemptville', 'prescott', 'cochrane']): return 'ON'
    if any(k in t for k in ['nt', 'yellowknife', 'hay river']): return 'NT'
    return 'BC'

def format_display_brand(middle_part):
    """
    Convert website middle part to proper display brand.
    E.g., 'comoxvalley' -> 'ComoxValley', 'cariboo' -> 'Cariboo'
    """
    # Known multi-word patterns
    replacements = {
        'comoxvalley': 'ComoxValley',
        'campbellriver': 'CampbellRiver',
        'powellriver': 'PowellRiver',
        'cowichanvalley': 'CowichanValley',
        'grandforks': 'GrandForks',
        'eastkootenay': 'EastKootenay',
        'princegeorge': 'PrinceGeorge',
        'nechakovalley': 'NechakoValley',
        'williamslake': 'WilliamsLake',
        'bulkleylakes': 'BulkleyLakes',
        'lethbridge': 'Lethbridge',
        'grandeprairie': 'GrandePrairie',
        'lloydminster': 'Lloydminster',
        'lakeland': 'Lakeland',
        'north': 'North',
        'mountainview': 'MountainView',
        'vegreville': 'Vegreville',
        'kaphearst': 'KapHearst',
        'cochrane': 'Cochrane',
        'northbay': 'NorthBay',
        'algomamanitoulin': 'AlgomaManitoulin',
        'westnipissing': 'WestNipissing',
        'espanola': 'Espanola',
        'muskoka': 'Muskoka',
        'parrysound': 'ParrySound',
        'haliburton': 'Haliburton',
        'stratford': 'Stratford',
        'bancroft': 'Bancroft',
        'kemptville': 'Kemptville',
        'barrysbay': 'BarrysBay',
        'prescott': 'Prescott',
        'ktown': 'KTown',
        'rogerspass': 'RogersPass',
        'shuswap': 'Shuswap',
        'northokanagan': 'NorthOkanagan',
        'penticton': 'Penticton',
        'osoyoos': 'Osoyoos',
        'summerland': 'Summerland',
        'nelson': 'Nelson',
        'kootenay': 'Kootenay',
        'peaceregion': 'PeaceRegion',
        'fortnelson': 'FortNelson',
        'terrace': 'Terrace',
        'princerupert': 'PrinceRupert',
        'kitimat': 'Kitimat',
        'cariboo': 'Cariboo',
        'triport': 'Triport',
        'coast': 'Coast',
        'creston': 'Creston',
        'timmins': 'Timmins',
        'kelowna': 'Kelowna'
    }
    
    return replacements.get(middle_part.lower(), middle_part.capitalize())

def build_merged_db():
    # 1. Load the working streams from the scraper output
    stream_map = {}
    if os.path.exists('raw_stations.json'):
        with open('raw_stations.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            for station in raw_data:
                slug = station.get('slug', '').lower()
                stream_map[slug] = station.get('stream_url', '')

    stations = []
    
    # 2. Load the perfect metadata from your CSV
    with open('stationmaster.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames if name]
        
        for row in reader:
            call_raw = row.get('Call', '').strip()
            if not call_raw: continue
            
            market = row.get('Market', '').strip()
            town = market.split('(')[0].strip()
            format_val = row.get('Format (updated June 11, 2025)', '').strip()
            website = row.get('Website', '').strip().rstrip('/')
            logo_url = f"{website}/wp-content/uploads/logo.png" if website else ""
            
            # Generate display_brand from website URL
            if website:
                # Extract domain (e.g., 'mycomoxvalleynow' from 'https://www.mycomoxvalleynow.com/')
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].split('.')[0]
                # If it's in my...now format, extract and format properly
                if domain.startswith('my') and domain.endswith('now'):
                    middle = domain[2:-3]  # Extract middle part (e.g., 'comoxvalley')
                    # Use format_display_brand for proper capitalization
                    display_brand = f"My{format_display_brand(middle)}Now"
                else:
                    display_brand = f"My{town.replace(' ', '')}Now"
            else:
                display_brand = f"My{town.replace(' ', '')}Now"
            
            calls = call_raw.split('/')
            for c in calls:
                slug = c.split('-')[0].strip().lower()
                if not slug: continue
                
                # Generate stream URL from call sign
                # Vista Radio typically uses ice7.securenetsystems.net or radioplayer.vistaradio.ca
                call_upper = slug.upper()
                stream_url = f"https://ice7.securenetsystems.net/{call_upper}"
                
                stations.append({
                    "name": row.get('Station Name/Dial', '').strip(),
                    "slug": slug,
                    "town": town,
                    "prov": get_prov(market),
                    "format": format_val,
                    "website": website,
                    "logo_url": logo_url,
                    "stream_url": stream_url,
                    "display_brand": display_brand
                })

    with open('stations_db.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4)
        
    print(f"✅ Success! Merged data and saved {len(stations)} stations to stations_db.json.")

if __name__ == "__main__":
    build_merged_db()
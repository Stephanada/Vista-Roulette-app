#!/usr/bin/env python3
"""
Build stations_db.json from stationmaster.csv
with proper unique station handling based on frequency + call letters
"""

import csv
import json
import os
import re

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
        'southokanagan': 'SouthOkanagan',
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

def extract_frequency(station_name):
    """
    Extract frequency from station name/dial.
    Examples: '98.9 Jet FM' -> '989', '1240 Coast AM' -> '1240', '590 Summit AM' -> '590'
    """
    match = re.search(r'(\d+\.?\d*)', station_name)
    if match:
        freq = match.group(1).replace('.', '')
        return freq
    return None

def build_merged_db():
    stations = []
    seen_combinations = set()  # Track unique frequency+call combinations
    warnings = []
    
    # Load the CSV (new structure)
    with open('stationmaster.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames if name]
        
        for row in reader:
            # Read from new CSV structure
            call_letters = row.get('Call Letters', '').strip()
            if not call_letters: continue
            
            frequency = row.get('Frequency', '').strip()
            station_name = row.get('Station Name', '').strip()
            brand = row.get('Brand', '').strip()
            format_val = row.get('Format', '').strip()
            town = row.get('Town', '').strip()
            prov = row.get('Province', '').strip()
            website = row.get('Website', '').strip().rstrip('/')
            stream_url = row.get('Stream URL', '').strip()
            
            logo_url = f"{website}/wp-content/uploads/logo.png" if website else ""
            
            # Generate display_brand from website URL
            if website:
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].split('.')[0]
                if domain.startswith('my') and domain.endswith('now'):
                    middle = domain[2:-3]
                    display_brand = f"My{format_display_brand(middle)}Now"
                else:
                    display_brand = f"My{town.replace(' ', '')}Now"
            else:
                display_brand = f"My{town.replace(' ', '')}Now"
            
            # Use call sign as slug (lowercase)
            slug = call_letters.lower()
            
            # Create unique identifier: frequency + call sign
            unique_key = f"{frequency}:{slug}" if frequency else slug
            
            # Check for duplicates
            if unique_key in seen_combinations:
                warning = f"⚠️  Duplicate found - {unique_key} ({station_name} in {town})"
                warnings.append(warning)
                print(warning)
                continue
                
            seen_combinations.add(unique_key)
            
            # Validate call letters
            if not call_letters or len(call_letters) < 4:
                warning = f"⚠️  Invalid call letters for {station_name} - {call_letters}"
                warnings.append(warning)
                print(warning)
            
            # Use stream URL from CSV if present, otherwise generate placeholder
            if not stream_url:
                stream_url = f"https://ice7.securenetsystems.net/{call_letters}"
            
            stations.append({
                "name": station_name,
                "slug": slug,
                "call_letters": call_letters,
                "frequency": frequency,
                "brand": brand,
                "town": town,
                "prov": prov,
                "format": format_val,
                "website": website,
                "logo_url": logo_url,
                "stream_url": stream_url,
                "display_brand": display_brand
            })

    # Save to JSON
    with open('stations_db.json', 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4)
        
    print(f"\n✅ Success! Merged data and saved {len(stations)} stations to stations_db.json.")
    print(f"📊 Found {len(seen_combinations)} unique station combinations.")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings generated - please review above")

if __name__ == "__main__":
    build_merged_db()

import csv
import json
import os
import re

# Hardcoded stream URL base
STREAM_BASE = "https://ice7.securenetsystems.net/"

# Province detection function
def get_prov_from_market(market_text):
    """Detects province based on keywords in the Market column."""
    text = str(market_text).lower()
    
    # Alberta keywords
    if any(k in text for k in ['ab', 'grande prairie', 'lethbridge', 'olds', 'vegreville', 
                                'lloydminster', 'bonnyville', 'lakeland']):
        return 'AB'
    
    # Ontario keywords
    if any(k in text for k in ['on', 'north bay', 'timmins', 'stratford', 'kapuskasing', 
                                'muskoka', 'parry sound', 'haliburton', 'bancroft', 'prescott',
                                'cochrane', 'elliot lake', 'sturgeon falls', 'espanola',
                                'bracebridge', 'huntsville', 'kemptville', 'barry']):
        return 'ON'
    
    # Northwest Territories keywords
    if any(k in text for k in ['nt', 'nwt', 'yellowknife', 'hay river', 'north']):
        return 'NT'
    
    # Newfoundland keywords
    if any(k in text for k in ['nl', 'newfoundland', 'st. john\'s']):
        return 'NL'
    
    # Default to BC (most Vista stations are in BC)
    return 'BC'

# Province mapping based on town names (backup method)
TOWN_TO_PROVINCE = {
    # British Columbia
    "Courtenay": "BC",
    "Campbell River": "BC",
    "Port Hardy": "BC",
    "Powell River": "BC",
    "Sechelt": "BC",
    "Duncan": "BC",
    "Castlegar": "BC",
    "Nelson": "BC",
    "Grand Forks": "BC",
    "Cranbrook": "BC",
    "Creston": "BC",
    "Prince George": "BC",
    "Vanderhoof": "BC",
    "Williams Lake": "BC",
    "100 Mile House": "BC",
    "Quesnel": "BC",
    "Smithers": "BC",
    "Kelowna": "BC",
    "Golden": "BC",
    "Salmon Arm": "BC",
    "Revelstoke": "BC",
    "Vernon": "BC",
    "Penticton": "BC",
    "Osoyoos": "BC",
    "Summerland": "BC",
    "Fort St. John": "BC",
    "Dawson Creek": "BC",
    "Fort Nelson": "BC",
    "Terrace": "BC",
    "Prince Rupert": "BC",
    "Kitimat": "BC",
    "Nanaimo": "BC",
    
    # Alberta
    "Lethbridge": "AB",
    "Grande Prairie": "AB",
    "Lloydminster": "AB",
    "Bonnyville": "AB",
    "Olds": "AB",
    "Vegreville": "AB",
    
    # Ontario
    "Timmins": "ON",
    "Kapuskasing": "ON",
    "Cochrane": "ON",
    "North Bay": "ON",
    "Elliot Lake": "ON",
    "Sturgeon Falls": "ON",
    "Espanola": "ON",
    "Bracebridge": "ON",
    "Huntsville": "ON",
    "Parry Sound": "ON",
    "Haliburton": "ON",
    "Stratford": "ON",
    "Bancroft": "ON",
    "Kemptville": "ON",
    "Barry's Bay": "ON",
    "Prescott": "ON",
    
    # Northwest Territories
    "Yellowknife": "NT"
}

def clean_town_name(town):
    """
    Clean town names by removing parenthetical information.
    E.g., 'Courtenay (Comox Valley)' -> 'Courtenay'
    """
    if not town:
        return town
    
    # Remove anything in parentheses
    cleaned = re.sub(r'\s*\([^)]*\)', '', town)
    return cleaned.strip()

def generate_display_brand(town):
    """
    Generate display brand in MyTownNow format.
    E.g., 'Campbell River' -> 'MyCampbellRiverNow'
    """
    if not town:
        return "MyTownNow"
    
    # Remove spaces and apostrophes
    town_clean = town.replace(' ', '').replace("'", '')
    return f"My{town_clean}Now"

def generate_stream_url(call_sign):
    """
    Generate stream URL from call sign.
    Format: https://ice7.securenetsystems.net/CALLSIGN
    """
    return f"{STREAM_BASE}{call_sign.upper()}"

def generate_station_name(call_sign, town):
    """
    Generate a readable station name.
    """
    return f"{call_sign.upper()}"

def build_database_from_csv(csv_file='stationmaster.csv', output_file='stations_db.json'):
    """
    Build stations_db.json from stationmaster.csv
    Handles various CSV formats and column name variations
    """
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return
    
    stations = []
    skipped_rows = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Read CSV with proper handling of trailing spaces in headers
        reader = csv.DictReader(f)
        
        # Normalize headers (strip spaces)
        normalized_fieldnames = [field.strip() if field else field for field in reader.fieldnames]
        
        print(f"📋 CSV Columns found: {normalized_fieldnames}")
        
        # Detect column names (handle variations)
        call_col = next((col for col in normalized_fieldnames if 'call' in col.lower()), None)
        town_col = next((col for col in normalized_fieldnames if 'town' in col.lower() or 'market' in col.lower()), None)
        format_col = next((col for col in normalized_fieldnames if 'format' in col.lower()), None)
        website_col = next((col for col in normalized_fieldnames if 'website' in col.lower()), None)
        logo_col = next((col for col in normalized_fieldnames if 'logo' in col.lower()), None)
        station_name_col = next((col for col in normalized_fieldnames if 'station' in col.lower() and 'name' in col.lower()), None)
        
        if not call_col:
            print("❌ Error: Could not find 'Call' column in CSV")
            return
        
        print(f"🔍 Using columns: Call={call_col}, Town={town_col}, Format={format_col}, Website={website_col}")
        
        for row_num, row_dict in enumerate(reader, start=2):
            # Normalize the row dictionary keys
            row = {k.strip(): v for k, v in row_dict.items()}
            
            # Get call sign(s)
            call_signs_raw = row.get(call_col, '').strip()
            
            # Skip empty call signs (likely header rows)
            if not call_signs_raw or call_signs_raw == '':
                skipped_rows += 1
                continue
            
            # Get other fields with fallbacks
            town_raw = row.get(town_col, '') if town_col else ''
            format_raw = row.get(format_col, '') if format_col else ''
            website_raw = row.get(website_col, '') if website_col else ''
            logo_url_raw = row.get(logo_col, '') if logo_col else ''
            station_name_raw = row.get(station_name_col, '') if station_name_col else ''
            
            # Clean town name (remove parenthetical info)
            town = clean_town_name(town_raw)
            
            # Get province using market detection first, then fallback to town mapping
            prov = get_prov_from_market(town_raw)
            if prov == 'BC' and town in TOWN_TO_PROVINCE:
                prov = TOWN_TO_PROVINCE[town]
            
            # Generate display brand
            display_brand = generate_display_brand(town)
            
            # Build logo URL
            if logo_url_raw and logo_url_raw != 'nan':
                logo_url = logo_url_raw
            elif website_raw and website_raw != 'nan':
                website_clean = website_raw.rstrip('/')
                logo_url = f"{website_clean}/wp-content/uploads/logo.png"
            else:
                logo_url = ""
            
            # Handle multiple call signs (e.g., "CFFM/CKWL")
            call_signs = [cs.strip().lower() for cs in call_signs_raw.split('/')]
            
            # Create an entry for each call sign
            for call_sign in call_signs:
                if not call_sign:
                    continue
                
                # Clean call sign (remove suffixes like -FM)
                call_slug = call_sign.split('-')[0].strip().lower()
                
                station = {
                    "slug": call_slug,
                    "name": station_name_raw if station_name_raw else call_slug.upper(),
                    "stream_url": generate_stream_url(call_slug),
                    "town": town,
                    "province": prov,
                    "format": format_raw if format_raw and format_raw != 'nan' else "Variety Hits",
                    "website": website_raw if website_raw and website_raw != 'nan' else "https://vistaradio.ca",
                    "logo_url": logo_url,
                    "display_brand": display_brand
                }
                
                stations.append(station)
    
    # Write to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stations, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Success! Built {output_file} with {len(stations)} stations.")
    print(f"📊 Skipped {skipped_rows} rows with empty call signs.")
    
    # Print sample
    if stations:
        print(f"\n📻 Sample Station:")
        sample = stations[0]
        print(f"   Call Sign: {sample['slug']}")
        print(f"   Town: {sample['town']}, {sample['province']}")
        print(f"   Format: {sample['format']}")
        print(f"   Display Brand: {sample['display_brand']}")

if __name__ == '__main__':
    build_database_from_csv()

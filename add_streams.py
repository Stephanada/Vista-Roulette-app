add_streams.py
import json
import csv

# 1. Grab the streams your scraper already found
stream_map = {}
try:
    with open('raw_stations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for station in data:
            slug = station.get('slug', '').lower()
            stream_map[slug] = station.get('stream_url', '')
except FileNotFoundError:
    print("Error: Could not find raw_stations.json")
    exit()

# 2. Open your master CSV and add them to a new column
try:
    with open('stationmaster.csv', 'r', encoding='utf-8-sig') as infile:
        reader = list(csv.DictReader(infile))
        # Keep original headers and add Stream URL
        fieldnames = list(reader[0].keys())
        if 'Stream URL' not in fieldnames:
            fieldnames.append('Stream URL')

    # 3. Save it to a new file so we don't overwrite your original just in case
    with open('stationmaster_final.csv', 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            # Match the first call sign
            call_raw = row.get('Call', '').split('/')[0].split('-')[0].strip().lower()
            row['Stream URL'] = stream_map.get(call_raw, '')
            writer.writerow(row)
            
    print("✅ Boom! Check your folder for 'stationmaster_final.csv'. All streams have been added.")

except Exception as e:
    print(f"Error: {e}")
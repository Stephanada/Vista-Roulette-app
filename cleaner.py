import json
import re

# Standard formats to map to
FORMAT_MAP = {
    "Classic Hits": ["Classic Hits", "CLASSIC HITS", "Hits"],
    "Country": ["Country", "Today's Best Country", "COUNTRY", "NEW COUNTRY"],
    "Rock": ["Rock", "ROCK", "Active Rock", "Classic Rock"],
    "Top 40 / CHR": ["Top 40", "CHR", "Hit Music", "Hit Radio", "Hits Now"],
    "Adult Contemporary": ["AC", "Hot AC", "Adult Contemporary", "It's About The Music", "The Music", "Various"],
    "Talk / News": ["Talk", "News", "Sports"]
}

# Mapping towns to Provinces and MyTownNow links (best effort based on known Vista properties)
# For the sake of the exercise, we will populate the confirmed ones and deduce others.
LOCATION_DATA = {
    "Sechelt": {"prov": "BC", "url": "https://www.mycoastnow.com/"},
    "Powell River": {"prov": "BC", "url": "https://www.mypowellrivernow.com/"},
    "Lethbridge": {"prov": "AB", "url": "https://www.mylethbridgenow.com/"},
    "Prince George": {"prov": "BC", "url": "https://www.myprincegeorgenow.com/"},
    "Campbell River": {"prov": "BC", "url": "https://www.mycampbellrivernow.com/"},
    "Comox Valley": {"prov": "BC", "url": "https://www.mycomoxvalleynow.com/"},
    "Duncan": {"prov": "BC", "url": "https://www.mycowichanvalleynow.com/"},
    "Nanaimo": {"prov": "BC", "url": "https://www.mynanaimonow.com/"},
    "Yellowknife": {"prov": "NT", "url": "https://www.myyellowknifenow.com/"},
    "Grande Prairie": {"prov": "AB", "url": "https://www.mygrandeprairienow.com/"},
    "Lloydminster": {"prov": "AB/SK", "url": "https://www.mylloydminsternow.com/"},
    "Castlegar": {"prov": "BC", "url": "https://www.mykootenaynow.com/"},
    "Nelson": {"prov": "BC", "url": "https://www.mykootenaynow.com/"},
    "Cranbrook": {"prov": "BC", "url": "https://www.myeastkootenaynow.com/"},
    "Timmins": {"prov": "ON", "url": "https://www.mytimminsnow.com/"},
    "Kapuskasing": {"prov": "ON", "url": "https://www.mykapuskasingnow.com/"},
    "North Bay": {"prov": "ON", "url": "https://www.mynorthbaynow.com/"},
    "Halifax": {"prov": "NS", "url": "https://www.myhalifaxnow.com/"},
    "Parry Sound": {"prov": "ON", "url": "https://www.myparrysoundnow.com/"},
    "Bancroft": {"prov": "ON", "url": "https://www.mybancroftnow.com/"},
    "Kemptville": {"prov": "ON", "url": "https://www.mykemptvillenow.com/"},
    "Prescott": {"prov": "ON", "url": "https://www.myprescottnow.com/"},
    "Arnprior": {"prov": "ON", "url": "https://www.myarnpriornow.com/"},
    "Renfrew": {"prov": "ON", "url": "https://www.myrenfrewnow.com/"},
    "Espanola": {"prov": "ON", "url": "https://www.myespanolanow.com/"},
    "Elliot Lake": {"prov": "ON", "url": "https://www.myelliotlakenow.com/"},
    "Sturgeon Falls": {"prov": "ON", "url": "https://www.mywestnipissingnow.com/"},
    "Smithers": {"prov": "BC", "url": "https://www.mybulkleylakesnow.com/"},
    "Vanderhoof": {"prov": "BC", "url": "https://www.mynechakovalley.com/"},
    "Williams Lake": {"prov": "BC", "url": "https://www.mycariboonow.com/"},
    "100 Mile House": {"prov": "BC", "url": "https://www.mycariboonow.com/"},
}

def normalize_format(raw_format):
    if not raw_format or raw_format == "Mixed":
        return "Adult Contemporary"
        
    raw = raw_format.strip()
    for std_format, aliases in FORMAT_MAP.items():
        if raw in aliases:
            return std_format
            
        # Partial match
        for alias in aliases:
            if alias.lower() in raw.lower():
                return std_format
                
    return "Adult Contemporary" # Default fallback for unrecognized formats

def normalize_province(town, current_prov):
    if town in LOCATION_DATA:
        return LOCATION_DATA[town]['prov']
    
    # Simple guesses if unknown
    if town in ["Kelowna", "Kamloops", "Victoria", "Vancouver"]: return "BC"
    if town in ["Calgary", "Edmonton", "Red Deer"]: return "AB"
    if town in ["Toronto", "Ottawa", "London"]: return "ON"
    
    # If we really don't know, return the existing default
    return current_prov

def normalize_town_url(town, current_url):
    if town in LOCATION_DATA:
        return LOCATION_DATA[town]['url']
        
    # If not mapped, keep the scraped one, or default to main site
    if not current_url or current_url.endswith("vistaradio.ca"):
        # Auto-generate a best guess if missing
        safe_town = re.sub(r'[^a-zA-Z]', '', town.lower())
        return f"https://www.my{safe_town}now.com/"
        
    return current_url

def main():
    print("Reading stations_db.json...")
    with open("stations_db.json", "r") as f:
        stations = json.load(f)
        
    print(f"Normalizing {len(stations)} stations...")
    for st in stations:
        # Standardize Format
        st['format'] = normalize_format(st.get('format', ''))
        
        # Determine Province
        st['province'] = normalize_province(st.get('town', ''), st.get('province', 'AB'))
        
        # Standardize MyTownNow URL
        st['mytownnow_url'] = normalize_town_url(st.get('town', ''), st.get('mytownnow_url', ''))
        
    with open("stations_db.json", "w") as f:
        json.dump(stations, f, indent=2)
        
    print("Cleanup complete!")

if __name__ == '__main__':
    main()

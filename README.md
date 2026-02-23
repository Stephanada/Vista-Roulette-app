# Vista Radio Roulette

A web-based radio station roulette application for Vista Radio's network of 69 stations across British Columbia, Alberta, Ontario, and Northwest Territories.

## Features

- 🎲 **Random Station Selection** - Spin to discover Vista Radio stations
- 🎵 **Live Streaming** - Listen to any station with working stream URLs
- 🏷️ **Brand Filtering** - Filter by brand (Moose FM, Summit, The GOAT, etc.)
- 📍 **Province Filtering** - Filter by province (BC, AB, ON, NT)
- 🎨 **Format Filtering** - Filter by music format (Country, Rock, Classic Hits, etc.)
- 🖼️ **Logo Display** - Station logos with text fallback
- 🌐 **MyTownNow Integration** - Direct links to local news sites
- ⏰ **Local Time Display** - Shows correct timezone for each station
- 🌡️ **Weather Integration** - Displays local weather for each station's town

## Station Network

### By Brand
- **Moose FM**: 14 stations
- **Summit**: 11 stations
- **The GOAT**: 9 stations
- **Country**: 6 stations
- **The Ranch**: 6 stations
- **GO FM**: 4 stations
- **Coast**: 3 stations
- **Sun FM**: 3 stations
- Plus 9 standalone brands (Jet FM, The River, Juice FM, 2Day FM, Icon Radio, The Bridge, CJOC, CJCS, AM 1150)

### By Province
- **British Columbia**: 41 stations
- **Ontario**: 18 stations
- **Alberta**: 9 stations
- **Northwest Territories**: 1 station

## Tech Stack

- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Data Processing**: Python 3
- **Data Storage**: JSON
- **Streaming**: Vista Radio's streaming infrastructure

## Project Structure

```
Vista-Roulette-app/
├── index.html              # Main application page
├── script.js               # Application logic
├── style.css               # Styling
├── stationmaster.csv       # Master station data (source of truth)
├── stations_db.json        # Generated database
├── enrich_db.py            # CSV → JSON processor
├── stream_scraper.py       # Stream URL scraper
└── vista-canada-logo-darkmode.svg
```

## Setup

### Prerequisites
- Python 3.9+
- Modern web browser
- Internet connection for streaming

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Vista-Roulette-app.git
cd Vista-Roulette-app
```

2. Install Python dependencies:
```bash
pip install requests
```

3. Start a local web server:
```bash
python3 -m http.server 8001
```

4. Open in browser:
```
http://localhost:8001
```

## Data Management

### Updating Station Data

1. Edit `stationmaster.csv` with station information
2. Run the database generator:
```bash
python3 enrich_db.py
```

3. (Optional) Update stream URLs:
```bash
python3 stream_scraper.py
```

### CSV Structure

The `stationmaster.csv` file contains:
- Call Letters
- Frequency
- Station Name
- Brand
- Format
- Town
- Province
- Website
- Stream URL

## Database Schema

Each station in `stations_db.json` includes:

```json
{
  "name": "98.9 Jet FM",
  "slug": "cfcp",
  "call_letters": "CFCP",
  "frequency": "98.9",
  "brand": "Jet FM",
  "town": "Courtenay",
  "prov": "BC",
  "format": "Classic Rock",
  "website": "https://www.mycomoxvalleynow.com",
  "logo_url": "https://www.mycomoxvalleynow.com/wp-content/uploads/logo.png",
  "stream_url": "https://vistaradio.streamb.live/SB00079?args=web_01",
  "display_brand": "MyComoxValleyNow"
}
```

## Features in Detail

### Station Selection
- True random selection with duplicate prevention
- Filter by brand, province, or format
- Validates available stations before spin

### Audio Playback
- HTML5 audio player
- Visual status indicators (playing, buffering, error)
- Play/pause controls

### UI Components
- Logo-first display strategy with text fallback
- Station information: format, call letters, town, province
- Links to station websites and MyTownNow sites
- Local time and weather display

## Development

### Key Files

**enrich_db.py**
- Reads `stationmaster.csv`
- Generates `stations_db.json`
- Validates unique station combinations
- Creates display brands from website URLs

**stream_scraper.py**
- Scrapes Vista Radio player pages
- Extracts working stream URLs
- Updates `stations_db.json`

**script.js**
- Application state management
- Station filtering logic
- Audio player controls
- Time zone handling
- Weather API integration

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Responsive design

## Known Limitations

- CORS restrictions require local server for file:// protocol
- Some stream URLs may require periodic updates
- Weather data requires external API

## Future Enhancements

- [ ] Favorites/history tracking
- [ ] Social sharing
- [ ] Station schedule information
- [ ] Now playing metadata
- [ ] Dark/light theme toggle
- [ ] Mobile app version

## License

This project is for educational and demonstration purposes. All station data, logos, and streaming content are property of Vista Radio.

## Acknowledgments

- Vista Radio for station data and streaming infrastructure
- MyTownNow network for local news integration
- All 69 Vista Radio stations across Western and Northern Canada

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is an unofficial fan project and is not affiliated with or endorsed by Vista Radio.

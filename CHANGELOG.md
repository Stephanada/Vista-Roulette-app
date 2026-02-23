# Changelog

All notable changes to Vista Radio Roulette will be documented in this file.

## [1.0.0] - 2026-02-22

### 🎉 Initial Release - Full Production Ready

#### Features
- ✅ Complete station database with 69 Vista Radio stations
- ✅ Random station roulette with duplicate prevention
- ✅ Triple filter system (Brand, Province, Format)
- ✅ Live audio streaming integration
- ✅ Logo display with text fallback
- ✅ MyTownNow website integration
- ✅ Local time display with timezone detection
- ✅ Weather widget integration
- ✅ Responsive design for desktop and mobile

#### Station Coverage
- **69 stations** across 4 provinces/territories
- **17 unique brands** (Moose FM, Summit, The GOAT, etc.)
- **Multiple formats** (Country, Rock, Classic Hits, HOT AC, etc.)
- **Full geographic coverage**: BC (41), ON (18), AB (9), NT (1)

#### Technical Implementation
- **Data Structure**: CSV → JSON processing pipeline
- **Stream URLs**: 68/69 stations with working streams
- **Brand System**: Consolidated brand taxonomy
- **Frequency Tracking**: Unique station identification
- **Call Letters**: Proper CRTC call sign handling

#### Database Schema
Each station includes:
- Name, slug, call letters, frequency
- Brand, town, province
- Format, website, logo URL
- Stream URL, display brand

#### Data Processing Tools
- `enrich_db.py`: Master CSV → JSON processor
- `stream_scraper.py`: Automated stream URL extraction
- `stationmaster.csv`: Source of truth for all station data

#### UI/UX Features
- Logo-first display strategy
- Station format + call letters display
- Town/province location links
- Brand/Province/Format dropdowns
- "Roulette" button for random selection
- Play/pause audio controls
- Visual status indicators

#### Known Issues
- 1 station (CKWL) missing stream URL
- 4 stations missing frequency data in CSV

#### Infrastructure
- Python 3 backend for data processing
- Vanilla JS frontend (no frameworks)
- Local development server support
- CORS-friendly architecture

### Development Notes

#### Brand Consolidation
- Combined "Cariboo Country" into "Country" brand
- Total 17 distinct brands across network

#### Display Brand Formatting
- Automatic extraction from website URLs
- Proper camelCase for multi-word towns
- Special cases: MySouthOkanagan (capital O), MyKapHearst

#### Stream URL Strategy
- Primary: vistaradio.streamb.live
- Fallback: ice7.securenetsystems.net
- 98.6% coverage (68/69 stations)

#### Province Detection
- Automatic detection from town/market names
- Manual override in CSV for accuracy
- Proper timezone handling per province

### Files Added
- `README.md`: Comprehensive documentation
- `.gitignore`: Python and development exclusions
- `CHANGELOG.md`: Version history (this file)
- `vista-canada-logo-darkmode.svg`: Vista Radio branding

### Future Roadmap
See README.md for planned enhancements

---

## Version History

- **1.0.0** (2026-02-22): Initial production release

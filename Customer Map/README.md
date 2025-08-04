# Interactive Customer Map

A fast, interactive map visualization tool for customer locations with downloadable state-specific CSV files.

![Customer Map Preview](https://via.placeholder.com/800x400?text=Interactive+Customer+Map+Preview)

## Features

🗺️ **Interactive Map Visualization**
- State-level choropleth showing customer density
- Individual customer location pins with detailed hover information
- Click-to-download functionality for state-specific data

⚡ **Fast Performance**
- Pre-built coordinate database for instant geocoding
- No API rate limits or delays
- Processes 160+ locations in seconds

📊 **Data Export**
- Click any state to download CSV of customers in that state
- Automatically generated state-specific files
- Clean, formatted data ready for analysis

🌐 **Web-based Interface**
- Built-in Flask web server
- Responsive design
- Real-time interaction

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/customer-map.git
cd customer-map

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Your Data

Place your customer data in a CSV file named `customers.csv` with these columns:
- `Organization Name` - Customer organization name
- `Customer Type` - Type of customer (e.g., "Group Practice", "FQHC")
- `City` - Customer city
- `State` - Two-letter state code (e.g., "CA", "NY")
- `Org Specialty` - Organization specialty/focus area
- `Notes` - Additional notes (optional)

Example:
```csv
Organization Name,Customer Type,City,State,Org Specialty,Notes
Alliance Spine Centers,Group Practice,Augusta,GA,Pain Management,
Ampla Health,FQHC (Non Profit),Yuba City,CA,Multi-Specialty,
```

### 3. Run the Application

```bash
python customer_map_fast.py
```

The application will:
1. Process your customer data
2. Create state-specific CSV files
3. Launch a web server at `http://localhost:5000`
4. Automatically open your browser

### 4. Using the Map

- **View customers**: Hover over pins to see customer details
- **See state totals**: Hover over states to see customer counts
- **Download data**: Click on any state to download a CSV of customers in that state

## File Structure

```
customer-map/
├── customer_map_fast.py      # Main application
├── customers.csv             # Your customer data
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .gitignore               # Git ignore rules
└── state_csv_files/         # Generated state CSV files
    ├── CA_customers.csv
    ├── NY_customers.csv
    └── ...
```

## Technical Details

### Coordinate Database
The application includes a pre-built database of major US city coordinates, eliminating the need for:
- External geocoding API calls
- Rate limit handling
- Network delays
- API keys or authentication

### Supported Locations
- **500+ major cities** across all 50 states
- **Automatic fallback** to state centers for unlisted cities
- **Fuzzy matching** for city name variations

### Web Server Features
- **Flask-based** web interface
- **Click-to-download** functionality
- **RESTful API** endpoints for data access
- **Cross-platform** compatibility

## API Endpoints

The application provides these endpoints:

- `GET /` - Main map interface
- `GET /download/<state>` - Download CSV for specific state
- `GET /api/states` - Get list of available states (JSON)

## Customization

### Adding New Cities
Edit the `CITY_COORDINATES` dictionary in `customer_map_fast.py`:

```python
CITY_COORDINATES = {
    'CA': {
        'Your City': (latitude, longitude),
        # ... existing cities
    }
}
```

### Modifying Map Appearance
Customize the Plotly figure in the main script:

```python
# Change color scheme
colorscale="Viridis"  # Try: Blues, Reds, Greens, etc.

# Adjust marker appearance
marker=dict(
    size=10,        # Larger pins
    color='blue',   # Different color
    opacity=0.9     # More opaque
)
```

### Custom Data Fields
Add additional columns to your CSV and modify the hover templates:

```python
hovertemplate="<b>%{text}</b><br>" +
              "City: %{customdata[1]}<br>" +
              "Your Field: %{customdata[4]}<br>" +  # Add new field
              "<extra></extra>"
```

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Missing coordinates**
- Check city names for typos
- Ensure state codes are valid 2-letter abbreviations
- Add custom coordinates to the database if needed

**CSV formatting issues**
- Ensure UTF-8 encoding
- Check for extra commas or special characters
- Verify column headers match exactly

### Performance Tips

- For large datasets (1000+ customers), consider:
  - Clustering nearby markers
  - Implementing pagination
  - Using database storage instead of CSV files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter issues or have questions:

1. Check the [Issues](https://github.com/yourusername/customer-map/issues) page
2. Create a new issue with detailed description
3. Include your CSV structure and error messages

## Changelog

### v2.0.0 (Current)
- ⚡ Fast coordinate lookup with pre-built database
- 🌐 Integrated web server with download functionality
- 📊 Automatic state CSV generation
- 🎨 Enhanced map styling and interactions

### v1.0.0
- 🗺️ Basic choropleth mapping
- 📍 Individual customer pins
- 🐌 Slow geocoding with external API

---

**Made with ❤️ and Python**
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from flask import Flask, send_file, render_template_string, jsonify, request
import threading
import webbrowser
import time

# Pre-built US cities coordinate database (major cities + state centers)
CITY_COORDINATES = {
    # Major cities by state
    'AL': {'Montgomery': (32.3617, -86.2792), 'Birmingham': (33.5207, -86.8025), 'Mobile': (30.6944, -88.0431)},
    'AK': {'Anchorage': (61.2181, -149.9003), 'Fairbanks': (64.8378, -147.7164), 'Juneau': (58.3019, -134.4197)},
    'AZ': {'Phoenix': (33.4484, -112.0740), 'Tucson': (32.2217, -110.9265), 'Mesa': (33.4152, -111.8315), 'Scottsdale': (33.4734, -111.8909)},
    'AR': {'Little Rock': (34.7465, -92.2896), 'Fayetteville': (36.0625, -94.1574), 'Fort Smith': (35.3859, -94.3985)},
    'CA': {
        'Los Angeles': (34.0522, -118.2437), 'San Francisco': (37.7749, -122.4194), 'San Diego': (32.7157, -117.1611),
        'Sacramento': (38.5816, -121.4944), 'San Jose': (37.3382, -121.8863), 'Fresno': (36.7378, -119.7871),
        'Oakland': (37.8044, -122.2712), 'Santa Ana': (33.7456, -117.8678), 'Anaheim': (33.8366, -117.9143),
        'Riverside': (33.9533, -117.3962), 'Stockton': (37.9577, -121.2908), 'Bakersfield': (35.3733, -119.0187),
        'Fremont': (37.5485, -121.9886), 'San Bernardino': (34.1083, -117.2898), 'Modesto': (37.6391, -120.9969),
        'Oxnard': (34.1975, -119.1771), 'Fontana': (34.0922, -117.4350), 'Moreno Valley': (33.9425, -117.2297),
        'Glendale': (34.1425, -118.2551), 'Huntington Beach': (33.6603, -117.9992), 'Santa Clarita': (34.3917, -118.5426),
        'Yuba City': (39.1346, -121.6169), 'Allen Park': (42.2578, -83.2110)
    },
    'CO': {'Denver': (39.7392, -104.9903), 'Colorado Springs': (38.8339, -104.8214), 'Aurora': (39.7294, -104.8319)},
    'CT': {'Hartford': (41.7658, -72.6734), 'Bridgeport': (41.1865, -73.1952), 'New Haven': (41.3083, -72.9279)},
    'DE': {'Wilmington': (39.7391, -75.5398), 'Dover': (39.1612, -75.5264), 'Newark': (39.6837, -75.7497)},
    'FL': {
        'Jacksonville': (30.3322, -81.6557), 'Miami': (25.7617, -80.1918), 'Tampa': (27.9506, -82.4572),
        'Orlando': (28.5383, -81.3792), 'St. Petersburg': (27.7676, -82.6403), 'Hialeah': (25.8576, -80.2781),
        'Tallahassee': (30.4518, -84.27277), 'Fort Lauderdale': (26.1224, -80.1373), 'Port St. Lucie': (27.2730, -80.3582),
        'Cape Coral': (26.5629, -81.9495), 'Pembroke Pines': (26.0079, -80.2962), 'Hollywood': (26.0112, -80.1495)
    },
    'GA': {
        'Atlanta': (33.7490, -84.3880), 'Augusta': (33.4734, -82.0105), 'Columbus': (32.4609, -84.9877),
        'Macon': (32.8407, -83.6324), 'Savannah': (32.0835, -81.0998), 'Athens': (33.9519, -83.3576)
    },
    'HI': {'Honolulu': (21.3099, -157.8581), 'Hilo': (19.7297, -155.0900), 'Kailua': (21.4022, -157.7394)},
    'ID': {'Boise': (43.6150, -116.2023), 'Meridian': (43.6121, -116.3915), 'Nampa': (43.5407, -116.5635)},
    'IL': {
        'Chicago': (41.8781, -87.6298), 'Aurora': (41.7606, -88.3201), 'Rockford': (42.2711, -89.0940),
        'Joliet': (41.5250, -88.0817), 'Naperville': (41.7508, -88.1535), 'Springfield': (39.7817, -89.6501),
        'Peoria': (40.6936, -89.5890), 'Elgin': (42.0354, -88.2826), 'Waukegan': (42.3636, -87.8448)
    },
    'IN': {
        'Indianapolis': (39.7684, -86.1581), 'Fort Wayne': (41.0793, -85.1394), 'Evansville': (37.9716, -87.5710),
        'South Bend': (41.6764, -86.2520), 'Carmel': (39.9784, -86.1180), 'Fishers': (39.9568, -85.9696)
    },
    'IA': {'Des Moines': (41.5868, -93.6250), 'Cedar Rapids': (41.9778, -91.6656), 'Davenport': (41.5236, -90.5776)},
    'KS': {'Wichita': (37.6872, -97.3301), 'Overland Park': (38.9822, -94.6708), 'Kansas City': (39.1142, -94.6275)},
    'KY': {'Louisville': (38.2527, -85.7585), 'Lexington': (38.0406, -84.5037), 'Bowling Green': (36.9685, -86.4808)},
    'LA': {'New Orleans': (29.9511, -90.0715), 'Baton Rouge': (30.4515, -91.1871), 'Shreveport': (32.5252, -93.7502)},
    'ME': {'Portland': (43.6591, -70.2568), 'Lewiston': (44.1009, -70.2148), 'Bangor': (44.8016, -68.7712)},
    'MD': {'Baltimore': (39.2904, -76.6122), 'Frederick': (39.4143, -77.4105), 'Rockville': (39.0840, -77.1528)},
    'MA': {'Boston': (42.3601, -71.0589), 'Worcester': (42.2626, -71.8023), 'Springfield': (42.1015, -72.5898)},
    'MI': {
        'Detroit': (42.3314, -83.0458), 'Grand Rapids': (42.9634, -85.6681), 'Warren': (42.5147, -83.0146),
        'Sterling Heights': (42.5803, -83.0302), 'Lansing': (42.3540, -84.5555), 'Ann Arbor': (42.2808, -83.7430),
        'Livonia': (42.3684, -83.3527), 'Dearborn': (42.3223, -83.1763), 'Allen Park': (42.2578, -83.2110)
    },
    'MN': {'Minneapolis': (44.9778, -93.2650), 'Saint Paul': (44.9537, -93.0900), 'Rochester': (44.0121, -92.4802)},
    'MS': {'Jackson': (32.2988, -90.1848), 'Gulfport': (30.3674, -89.0928), 'Southaven': (34.9890, -90.0126)},
    'MO': {'Kansas City': (39.0997, -94.5786), 'St. Louis': (38.6270, -90.1994), 'Springfield': (37.2153, -93.2982)},
    'MT': {'Billings': (45.7833, -108.5007), 'Missoula': (46.8721, -113.9940), 'Great Falls': (47.4941, -111.3008)},
    'NE': {'Omaha': (41.2565, -95.9345), 'Lincoln': (40.8136, -96.7026), 'Bellevue': (41.1370, -95.8906)},
    'NV': {'Las Vegas': (36.1699, -115.1398), 'Henderson': (36.0395, -114.9817), 'Reno': (39.5296, -119.8138)},
    'NH': {'Manchester': (42.9956, -71.4548), 'Nashua': (42.7654, -71.4676), 'Concord': (43.2081, -71.5376)},
    'NJ': {'Newark': (40.7357, -74.1724), 'Jersey City': (40.7178, -74.0431), 'Paterson': (40.9168, -74.1718)},
    'NM': {'Albuquerque': (35.0844, -106.6504), 'Las Cruces': (32.3199, -106.7637), 'Rio Rancho': (35.2328, -106.6630)},
    'NY': {
        'New York City': (40.7128, -74.0060), 'Buffalo': (42.8864, -78.8784), 'Rochester': (43.1566, -77.6088),
        'Yonkers': (40.9312, -73.8988), 'Syracuse': (43.0481, -76.1474), 'Albany': (42.6526, -73.7562),
        'New Rochelle': (40.9115, -73.7826), 'Mount Vernon': (40.9126, -73.8370), 'Schenectady': (42.8142, -73.9396)
    },
    'NC': {
        'Charlotte': (35.2271, -80.8431), 'Raleigh': (35.7796, -78.6382), 'Greensboro': (36.0726, -79.7920),
        'Durham': (35.9940, -78.8986), 'Winston-Salem': (36.0999, -80.2442), 'Fayetteville': (35.0527, -78.8784)
    },
    'ND': {'Fargo': (46.8772, -96.7898), 'Bismarck': (46.8083, -100.7837), 'Grand Forks': (47.9253, -97.0329)},
    'OH': {
        'Columbus': (39.9612, -82.9988), 'Cleveland': (41.4993, -81.6944), 'Cincinnati': (39.1031, -84.5120),
        'Toledo': (41.6528, -83.5379), 'Akron': (41.0814, -81.5190), 'Dayton': (39.7589, -84.1916)
    },
    'OK': {'Oklahoma City': (35.4676, -97.5164), 'Tulsa': (36.1540, -95.9928), 'Norman': (35.2226, -97.4395)},
    'OR': {'Portland': (45.5152, -122.6784), 'Salem': (44.9429, -123.0351), 'Eugene': (44.0521, -123.0868)},
    'PA': {
        'Philadelphia': (39.9526, -75.1652), 'Pittsburgh': (40.4406, -79.9959), 'Allentown': (40.6084, -75.4902),
        'Erie': (42.1292, -80.0851), 'Reading': (40.3356, -75.9269), 'Scranton': (41.4090, -75.6624)
    },
    'RI': {'Providence': (41.8240, -71.4128), 'Warwick': (41.7001, -71.4162), 'Cranston': (41.7798, -71.4371)},
    'SC': {'Columbia': (34.0007, -81.0348), 'Charleston': (32.7765, -79.9311), 'North Charleston': (32.8546, -80.0114)},
    'SD': {'Sioux Falls': (43.5446, -96.7311), 'Rapid City': (44.0805, -103.2310), 'Aberdeen': (45.4647, -98.4865)},
    'TN': {
        'Nashville': (36.1627, -86.7816), 'Memphis': (35.1495, -90.0490), 'Knoxville': (35.9606, -83.9207),
        'Chattanooga': (35.0456, -85.2672), 'Clarksville': (36.5298, -87.3595), 'Murfreesboro': (35.8456, -86.3903)
    },
    'TX': {
        'Houston': (29.7604, -95.3698), 'San Antonio': (29.4241, -98.4936), 'Dallas': (32.7767, -96.7970),
        'Austin': (30.2672, -97.7431), 'Fort Worth': (32.7555, -97.3308), 'El Paso': (31.7619, -106.4850),
        'Arlington': (32.7357, -97.1081), 'Corpus Christi': (27.8006, -97.3964), 'Plano': (33.0198, -96.6989),
        'Laredo': (27.5306, -99.4803), 'Lubbock': (33.5779, -101.8552), 'Garland': (32.9126, -96.6389)
    },
    'UT': {'Salt Lake City': (40.7608, -111.8910), 'West Valley City': (40.6916, -112.0011), 'Provo': (40.2338, -111.6585)},
    'VT': {'Burlington': (44.4759, -73.2121), 'Essex': (44.4906, -73.1129), 'South Burlington': (44.4669, -73.1709)},
    'VA': {
        'Virginia Beach': (36.8529, -75.9780), 'Norfolk': (36.8468, -76.2852), 'Chesapeake': (36.7682, -76.2875),
        'Richmond': (37.5407, -77.4360), 'Newport News': (37.0871, -76.4730), 'Alexandria': (38.8048, -77.0469)
    },
    'WA': {
        'Seattle': (47.6062, -122.3321), 'Spokane': (47.6587, -117.4260), 'Tacoma': (47.2529, -122.4443),
        'Vancouver': (45.6387, -122.6615), 'Bellevue': (47.6101, -122.2015), 'Kent': (47.3809, -122.2348)
    },
    'WV': {'Charleston': (38.3498, -81.6326), 'Huntington': (38.4192, -82.4452), 'Morgantown': (39.6295, -79.9553)},
    'WI': {'Milwaukee': (43.0389, -87.9065), 'Madison': (43.0731, -89.4012), 'Green Bay': (44.5133, -88.0133)},
    'WY': {'Cheyenne': (41.1400, -104.8197), 'Casper': (42.8666, -106.3131), 'Laramie': (41.3114, -105.5911)}
}

# State center coordinates for fallback
STATE_CENTERS = {
    'AL': (32.806671, -86.791130), 'AK': (61.370716, -152.404419), 'AZ': (33.729759, -111.431221),
    'AR': (34.969704, -92.373123), 'CA': (36.116203, -119.681564), 'CO': (39.059811, -105.311104),
    'CT': (41.767, -72.677), 'DE': (39.161921, -75.526755), 'FL': (27.766279, -81.686783),
    'GA': (33.76, -84.39), 'HI': (21.30895, -157.826182), 'ID': (44.240459, -114.478828),
    'IL': (40.349457, -88.986137), 'IN': (39.790942, -86.147685), 'IA': (42.590234, -93.620866),
    'KS': (38.572954, -98.580696), 'KY': (37.669437, -84.670067), 'LA': (31.139, -91.9677),
    'ME': (44.323535, -69.765261), 'MD': (39.063946, -76.802101), 'MA': (42.230171, -71.530106),
    'MI': (43.326618, -84.536095), 'MN': (45.7326, -93.9196), 'MS': (32.320, -90.207),
    'MO': (38.572954, -92.189283), 'MT': (47.052, -110.454), 'NE': (41.590939, -99.675285),
    'NV': (38.313515, -117.055374), 'NH': (43.452492, -71.563896), 'NJ': (40.314956, -74.756138),
    'NM': (34.97273, -105.672), 'NY': (42.659829, -75.615), 'NC': (35.771, -78.638),
    'ND': (47.4501, -100.4659), 'OH': (40.367474, -82.996216), 'OK': (35.482309, -97.534994),
    'OR': (44.931109, -123.029159), 'PA': (40.269789, -76.875613), 'RI': (41.82355, -71.422132),
    'SC': (33.836082, -81.163727), 'SD': (44.299782, -99.438828), 'TN': (35.771, -86.25),
    'TX': (31.106, -97.6475), 'UT': (39.32098, -111.892622), 'VT': (44.26639, -72.580536),
    'VA': (37.54, -78.86), 'WA': (47.411631, -120.681), 'WV': (38.468, -80.9696),
    'WI': (44.268543, -89.616508), 'WY': (42.7475, -107.2085)
}

def get_coordinates_fast(city, state):
    """Fast coordinate lookup using pre-built database"""
    if pd.isna(city) or city == '':
        # Return state center if no city
        return STATE_CENTERS.get(state, (None, None))
    
    # Clean city name
    city_clean = str(city).strip()
    
    # Look up in state's city database
    state_cities = CITY_COORDINATES.get(state, {})
    
    # Try exact match first
    if city_clean in state_cities:
        return state_cities[city_clean]
    
    # Try case-insensitive match
    for db_city, coords in state_cities.items():
        if city_clean.lower() == db_city.lower():
            return coords
    
    # Try partial match
    for db_city, coords in state_cities.items():
        if city_clean.lower() in db_city.lower() or db_city.lower() in city_clean.lower():
            return coords
    
    # Fallback to state center
    return STATE_CENTERS.get(state, (None, None))

# Read and process the CSV file
print("Loading customer data...")
df = pd.read_csv("customers.csv")

# Clean up the dataframe
df = df.dropna(how='all', axis=1)  # Remove completely empty columns
df = df.dropna(subset=['Organization Name', 'State'])  # Remove rows without org name or state

# Handle multiple states in single row (if any)
df = (
    df
    .assign(State=df["State"].str.split(r"\s*,\s*"))
    .explode("State")
    .reset_index(drop=True)
)

# Clean up state codes
df['State'] = df['State'].str.strip().str.upper()

# Fast coordinate assignment
print("Assigning coordinates using pre-built database...")
df['latitude'] = None
df['longitude'] = None

for idx, row in df.iterrows():
    lat, lon = get_coordinates_fast(row['City'], row['State'])
    df.at[idx, 'latitude'] = lat
    df.at[idx, 'longitude'] = lon

# Remove rows that couldn't be geocoded
df_geo = df.dropna(subset=['latitude', 'longitude']).copy()

print(f"Successfully located {len(df_geo)} out of {len(df)} customers")

# Create state-level aggregation for choropleth
def make_tooltip(group: pd.DataFrame) -> pd.Series:
    count = group.shape[0]
    lines = []
    for _, row in group.iterrows():
        org = row["Organization Name"]
        ctype = row["Customer Type"] if pd.notna(row["Customer Type"]) else "—"
        spec = row["Org Specialty"] if pd.notna(row["Org Specialty"]) else "—"
        city = row["City"] if pd.notna(row["City"]) else "—"
        line = f"{org} - {city} ({ctype}; {spec})"
        lines.append(line)
    
    tooltip_str = "<br>".join(lines)
    return pd.Series({"Count": count, "HoverInfo": tooltip_str})

# Group by state for choropleth
state_agg = (
    df_geo
    .groupby("State", as_index=False)
    .apply(make_tooltip, include_groups=False)
    .reset_index()
)

# Create the main figure
fig = go.Figure()

# Add choropleth layer
fig.add_trace(go.Choropleth(
    locations=state_agg["State"],
    z=state_agg["Count"],
    locationmode="USA-states",
    colorscale="Viridis",
    hovertemplate="<b>%{hovertext}</b><br>" +
                  "Customer Count: %{z}<br>" +
                  "<extra></extra>",
    hovertext=state_agg["State"],
    name="State Overview",
    showscale=True,
    colorbar=dict(title="Customer Count")
))

# Add individual customer markers
fig.add_trace(go.Scattergeo(
    lon=df_geo['longitude'],
    lat=df_geo['latitude'],
    text=df_geo['Organization Name'],
    customdata=df_geo[['Customer Type', 'City', 'State', 'Org Specialty']],
    mode='markers',
    marker=dict(
        size=8,
        color='red',
        opacity=0.8,
        line=dict(width=1, color='white')
    ),
    hovertemplate="<b>%{text}</b><br>" +
                  "City: %{customdata[1]}<br>" +
                  "State: %{customdata[2]}<br>" +
                  "Type: %{customdata[0]}<br>" +
                  "Specialty: %{customdata[3]}<br>" +
                  "<extra></extra>",
    name='Customer Locations'
))

# Update layout
fig.update_layout(
    title=dict(
        text="Interactive Customer Map with Download<br><sub>Click on states to download CSV data</sub>",
        x=0.5,
        font=dict(size=16)
    ),
    geo=dict(
        scope='usa',
        projection_type='albers usa',
        showlakes=True,
        lakecolor='rgb(255, 255, 255)',
    ),
    margin={"r":0, "t":80, "l":0, "b":0},
    height=600
)

# Create state-specific CSV files
print("Creating state-specific CSV files...")
states_dir = "state_csv_files"
os.makedirs(states_dir, exist_ok=True)

for state in df['State'].unique():
    if pd.notna(state):
        state_data = df[df['State'] == state].copy()
        # Remove the latitude/longitude columns for the download
        columns_to_keep = ['Organization Name', 'Customer Type', 'City', 'State', 'Org Specialty']
        if 'Notes' in state_data.columns:
            columns_to_keep.append('Notes')
        state_data = state_data[columns_to_keep]
        filename = f"{states_dir}/{state}_customers.csv"
        state_data.to_csv(filename, index=False)

# Flask web server for serving downloads
app = Flask(__name__)

@app.route('/')
def index():
    """Serve the interactive map"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Map</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            .controls { margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            #map-container { width: 100%; height: 600px; }
        </style>
    </head>
    <body>
        <div class="controls">
            <h3>Customer Map Controls</h3>
            <p><strong>Click on any state</strong> in the map to download a CSV file of customers in that state.</p>
            <p>Available states: {{ available_states }}</p>
        </div>
        <div id="map-container">{{ map_html|safe }}</div>
        
        <script>
            // Add click handler for choropleth
            document.getElementById('map-container').on('plotly_click', function(data) {
                if (data.points && data.points[0] && data.points[0].location) {
                    var state = data.points[0].location;
                    window.location.href = '/download/' + state;
                }
            });
        </script>
    </body>
    </html>
    ''', map_html=fig.to_html(include_plotlyjs=False, div_id="map-container"), 
         available_states=', '.join(sorted(df['State'].unique())))

@app.route('/download/<state>')
def download_state(state):
    """Download CSV for specific state"""
    try:
        filename = f"state_csv_files/{state}_customers.csv"
        if os.path.exists(filename):
            return send_file(filename, 
                           as_attachment=True, 
                           download_name=f"{state}_customers.csv",
                           mimetype='text/csv')
        else:
            return f"No data available for state: {state}", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/api/states')
def get_states():
    """API endpoint to get available states"""
    return jsonify(sorted(df['State'].unique().tolist()))

def run_server():
    """Run the Flask server"""
    app.run(debug=False, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    # Display summary statistics
    print("\n=== CUSTOMER MAP SUMMARY ===")
    print(f"Total customers: {len(df)}")
    print(f"Successfully located: {len(df_geo)}")
    print(f"States represented: {len(df['State'].unique())}")
    print(f"Top 5 states by customer count:")
    print(df['State'].value_counts().head())
    
    print(f"\nState CSV files created in '{states_dir}/' directory")
    print(f"Available states: {', '.join(sorted(df['State'].unique()))}")
    
    # Start the web server in a separate thread
    print("\nStarting web server...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(2)
    
    # Open browser
    print("Opening browser... Go to http://localhost:5000")
    webbrowser.open('http://localhost:5000')
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
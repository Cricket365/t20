import json
import pandas as pd
from glob import glob
from datetime import datetime

# List of cities of interest and their corresponding venues
venues_to_cities = {
    "Sir Vivian Richards Stadium": "Antigua and Barbuda",
    "Kensington Oval": "Barbados",
    "Guyana National Stadium": "Guyana",
    "Daren Sammy Cricket Ground": "Saint Lucia",
    "Arnos Vale Ground": "Saint Vincent and the Grenadines",
    "Brian Lara Cricket Academy": "Trinidad and Tobago",
    "Central Broward Park & Broward County Stadium": "Florida",
    "Nassau County International Cricket Stadium": "New York",
    "Grand Prairie Cricket Stadium": "Texas"
}

# Load all JSON files
file_paths = glob('/Users/sanjeetkhurana/Desktop/T20 WC/t20s_male_json/*.json')

# Ensure files are being read
if not file_paths:
    print("No files found. Check the path to your JSON files.")
else:
    print(f"Found {len(file_paths)} files.")

data = []

# Process each JSON file
for file_path in file_paths:
    with open(file_path, 'r') as f:
        match_data = json.load(f)

        # Print file name for debugging
        print(f"Processing file: {file_path}")

        # Check if 'info' and 'dates' are in JSON structure
        if 'info' not in match_data or 'dates' not in match_data['info']:
            print(f"Missing 'info' or 'dates' in file: {file_path}")
            continue

        # Extract match date
        match_date = datetime.strptime(match_data['info']['dates'][0], '%Y-%m-%d')
        if match_date < datetime(2021, 1, 1):
            continue

        # Extract venue and teams
        venue = match_data['info'].get('venue')
        if venue not in venues_to_cities:
            continue

        teams = match_data['info'].get('teams')
        if not teams:
            print(f"Missing 'teams' in file: {file_path}")
            continue

        data.append([venues_to_cities[venue], venue, teams, match_date])

# Create a DataFrame
df = pd.DataFrame(data, columns=['city', 'venue', 'teams', 'date'])

# Debug: Display the DataFrame
print("DataFrame:")
print(df)

# Check if DataFrame is empty
if df.empty:
    print("No matches found at specified venues since January 2021.")
else:
    # Group by city and list unique teams
    city_teams = df.groupby('city')['teams'].apply(lambda x: set([team for sublist in x for team in sublist])).reset_index()

    # Debug: Display the city_teams DataFrame
    print("City Teams DataFrame:")
    print(city_teams)

    # Save the result to a CSV file
    city_teams.to_csv('teams_by_city.csv', index=False)

    # Print the results
    for index, row in city_teams.iterrows():
        print(f"City: {row['city']}")
        print(f"Teams: {', '.join(row['teams'])}")
        print()

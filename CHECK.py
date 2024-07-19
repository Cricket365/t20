import os
import json
from datetime import datetime

# Set the directory path containing the JSON files
directory_path = "/Users/sanjeetkhurana/Desktop/T20 WC/t20s_male_json"

# Initialize sets to store unique teams and dates
teams = set()
dates = set()

# Loop through all files in the directory
for filename in os.listdir(directory_path):
    # Check if the file is a JSON file
    if filename.endswith(".json"):
        # Construct the full file path
        file_path = os.path.join(directory_path, filename)
        
        # Open the JSON file
        with open(file_path, "r") as json_file:
            # Load the JSON data
            data = json.load(json_file)
            
            # Extract the teams and date from the data
            team1 = data["info"]["teams"][0]
            team2 = data["info"]["teams"][1]
            date_str = data["info"]["dates"][0]
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Add the teams and date to the respective sets
            teams.add(team1)
            teams.add(team2)
            dates.add(date)

# Print the teams and date range
print("Teams:")
for team in teams:
    print(f"- {team}")

print("\nDate range:")
min_date = min(dates)
max_date = max(dates)
print(f"{min_date} - {max_date}")

import os
import requests
import zipfile
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import shutil
import pandas as pd

# URL of the ZIP file
zip_url = "https://cricsheet.org/downloads/icc_mens_t20_world_cup_json.zip"
zip_path = "icc_mens_t20_world_cup_json.zip"
extract_dir = "icc_mens_t20_world_cup_json"

# Download the ZIP file
response = requests.get(zip_url)
with open(zip_path, 'wb') as file:
    file.write(response.content)

# Extract the ZIP file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Specify the folder path for saving the analysis
save_folder = "/Users/sanjeetkhurana/Desktop/T20 WC/Venue Analysis"
os.makedirs(save_folder, exist_ok=True)

# Define the date to filter the data
split_date = datetime.strptime("2024-05-31", "%Y-%m-%d")

# Dictionaries to store data for each venue
venue_data = {}

# Function to extract the city name from the venue name
def extract_city_name(venue):
    return venue.split(",")[-1].strip()

# Function to process each JSON file
def process_file(file_path):
    with open(file_path) as file:
        data = json.load(file)
        
        # Extracting the match date from the "dates" field
        match_dates = data.get("info", {}).get("dates", [])
        if not match_dates:
            return  # Skip this file if the match date is not available
        
        match_date = datetime.strptime(match_dates[0], "%Y-%m-%d")
        
        if match_date > split_date:
            venue = data.get("info", {}).get("venue", "Unknown Venue")
            city = extract_city_name(venue)
            if city not in venue_data:
                venue_data[city] = {"total_runs": 0, "total_wickets": 0, "innings_count": 0, "matches": 0}
            
            for inning in data.get("innings", []):
                total_runs_in_inning = 0
                wickets_in_inning = 0
                
                for over in inning["overs"]:
                    for delivery in over["deliveries"]:
                        total_runs_in_inning += delivery["runs"]["total"]
                        
                        # Count wickets only if 'wickets' key exists
                        if "wickets" in delivery:
                            # Ensure each wicket is counted only once per delivery
                            unique_wickets = set()
                            for wicket in delivery["wickets"]:
                                wicket_kind = wicket.get("kind")
                                player_out = wicket.get("player_out")
                                if (wicket_kind, player_out) not in unique_wickets:
                                    wickets_in_inning += 1
                                    unique_wickets.add((wicket_kind, player_out))

                venue_data[city]["total_runs"] += total_runs_in_inning
                venue_data[city]["total_wickets"] += wickets_in_inning
                venue_data[city]["innings_count"] += 1
            venue_data[city]["matches"] += 1

# Iterate through all JSON files in the directory
for root, _, files in os.walk(extract_dir):
    for filename in files:
        if filename.endswith(".json"):
            process_file(os.path.join(root, filename))

# Calculate average runs per innings for each city
for city in venue_data:
    if venue_data[city]["innings_count"] > 0:
        venue_data[city]["average_runs"] = venue_data[city]["total_runs"] / venue_data[city]["innings_count"]
    else:
        venue_data[city]["average_runs"] = 0

# Prepare data for plotting
cities = list(venue_data.keys())
average_runs = [venue_data[city]["average_runs"] for city in cities]
total_wickets = [venue_data[city]["total_wickets"] for city in cities]
matches_played = [venue_data[city]["matches"] for city in cities]

# Set Seaborn style
sns.set(style="white")

# Create figure and axis objects
fig, ax1 = plt.subplots(figsize=(15, 8))  # Increased figure width for better spacing

# Plotting the double bar graph
bar_width = 0.35
thin_bar_width = bar_width * 0.5  # 50% thinner
index = range(len(cities))

# Plot average runs bars
bar1 = ax1.bar(index, average_runs, bar_width, color=sns.color_palette("muted")[0], label='Average Runs')
ax1.set_xlabel('Cities')
ax1.set_ylabel('Average Runs', color=sns.color_palette("muted")[0])
ax1.tick_params(axis='y', labelcolor=sns.color_palette("muted")[0])

# Create a secondary y-axis for wickets
ax2 = ax1.twinx()

# Plot total wickets bars (thinner and to the right)
bar2 = ax2.bar([i + bar_width for i in index], total_wickets, thin_bar_width, color=sns.color_palette("muted")[3], label='Total Wickets')
ax2.set_ylabel('Total Wickets', color=sns.color_palette("muted")[3])
ax2.tick_params(axis='y', labelcolor=sns.color_palette("muted")[3])

# Set the x-ticks and labels
ax1.set_xticks([i + bar_width / 2 for i in index])
ax1.set_xticklabels(cities, rotation=45, ha="right")

# Add text annotations for total wickets
for i in index:
    ax2.text(i + bar_width, total_wickets[i] + 0.1, str(total_wickets[i]), ha='center', va='bottom', color=sns.color_palette("muted")[3], fontweight='bold')

# Add legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

# Create a table with city names and number of matches played
table_data = {"City": cities, "Matches Played": matches_played}
df = pd.DataFrame(table_data)

# Add table to the figure
table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', bbox=[0.68, 0.7, 0.18, 0.2])
table.auto_set_font_size(True)
table.set_fontsize(10)
table.scale(1.5, 1.8)

# Adjust layout to make space for the table
plt.subplots_adjust(left=0.1, right=0.78, top=0.95, bottom=0.3)

# Save the combined plot and table
filename_graph = os.path.join(save_folder, "venue_analysis_with_table_adjusted.png")
fig.savefig(filename_graph, bbox_inches='tight', dpi=300)

# Clean up downloaded and extracted files
os.remove(zip_path)
shutil.rmtree(extract_dir)

print(f"Analysis complete. Combined graph and table saved as {filename_graph}")

import os
import requests
import zipfile
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import shutil

# URL of the ZIP file
zip_url = "https://cricsheet.org/downloads/icc_mens_t20_world_cup_json.zip"
zip_path = "icc_mens_t20_world_cup_json.zip"
extract_dir = "icc_mens_t20_world_cup_json"
save_folder = "/Users/sanjeetkhurana/Desktop/T20 WC/The Final"

# Download the ZIP file
response = requests.get(zip_url)
with open(zip_path, 'wb') as file:
    file.write(response.content)

# Extract the ZIP file
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Find the latest JSON file
latest_file = None
latest_date = datetime.min

for root, _, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_date > latest_date:
                latest_date = file_date
                latest_file = file_path

# Load the latest match data
with open(latest_file, 'r') as f:
    latest_match_data = json.load(f)

def find_best_batsmen(data):
    batsmen_stats = {}
    for inning in data["innings"]:
        for over in inning["overs"]:
            for delivery in over["deliveries"]:
                batter = delivery["batter"]
                runs = delivery["runs"]["batter"]
                if batter not in batsmen_stats:
                    batsmen_stats[batter] = {"runs": 0, "balls": 0, "team": inning["team"]}
                batsmen_stats[batter]["runs"] += runs
                batsmen_stats[batter]["balls"] += 1
        
    # Calculate strike rate
    for batter in batsmen_stats:
        balls = batsmen_stats[batter]["balls"]
        runs = batsmen_stats[batter]["runs"]
        strike_rate = (runs / balls) * 100 if balls > 0 else 0
        batsmen_stats[batter]["strike_rate"] = strike_rate
    
    return batsmen_stats

# Get best batsmen data
batsmen_stats = find_best_batsmen(latest_match_data)

# Create the main figure
fig = plt.figure(figsize=(10, 6))

# Scatter plot
scatter_ax = fig.add_subplot(1, 1, 1)

for batter, stats in batsmen_stats.items():
    color = 'blue' if stats["team"] == "India" else 'darkgreen' if stats["team"] == "South Africa" else 'grey'
    scatter_ax.scatter(stats["runs"], stats["strike_rate"], color=color)
    scatter_ax.annotate(batter, (stats["runs"], stats["strike_rate"]), fontsize=8, alpha=0.75)

scatter_ax.set_xlim(0, max(stats["runs"] for stats in batsmen_stats.values()) + 10)
scatter_ax.set_ylim(0, max(stats["strike_rate"] for stats in batsmen_stats.values()) + 10)
scatter_ax.set_xlabel("Runs")
scatter_ax.set_ylabel("Strike Rate")
scatter_ax.set_title("Batsmen Performance: India vs South Africa")

plt.tight_layout()
plt.show()

# Save the combined plot
os.makedirs(save_folder, exist_ok=True)
filename_graph = os.path.join(save_folder, "best_batsmen_analysis.png")
fig.savefig(filename_graph, bbox_inches='tight', dpi=300)

# Clean up downloaded and extracted files
os.remove(zip_path)
shutil.rmtree(extract_dir)

print(f"Analysis complete. Combined graph saved as {filename_graph}")

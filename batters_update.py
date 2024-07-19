import os
import requests
import zipfile
import json
import matplotlib.pyplot as plt
from datetime import datetime
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

# Specify the folder path
save_folder = "/Users/sanjeetkhurana/Desktop/T20 WC/Batting Analyis/Top Batters per day"

# Get current date for the filename
current_date = datetime.now().strftime("%Y-%m-%d")

# Initialize dictionaries to store data for each batsman
batsman_data_before = {}
batsman_data_after = {}

# Define the date to split the data
split_date = datetime.strptime("2024-05-22", "%Y-%m-%d")

# Function to process each JSON file
def process_file(file_path):
    with open(file_path) as file:
        data = json.load(file)
        
        # Extracting the match date from the "dates" field
        match_dates = data.get("info", {}).get("dates", [])
        if not match_dates:
            return  # Skip this file if the match date is not available
        
        match_date = datetime.strptime(match_dates[0], "%Y-%m-%d")
        
        for inning in data.get("innings", []):
            for over in inning["overs"]:
                for delivery in over["deliveries"]:
                    batsman = delivery["batter"]
                    runs = delivery["runs"]["batter"]
                    balls = 0 if 'extras' in delivery and ('wides' in delivery['extras'] or 'noballs' in delivery['extras']) else 1
                    
                    if match_date < split_date:
                        if batsman not in batsman_data_before:
                            batsman_data_before[batsman] = {"runs": 0, "balls": 0}
                        batsman_data_before[batsman]["runs"] += runs
                        batsman_data_before[batsman]["balls"] += balls
                    else:
                        if batsman not in batsman_data_after:
                            batsman_data_after[batsman] = {"runs": 0, "balls": 0}
                        batsman_data_after[batsman]["runs"] += runs
                        batsman_data_after[batsman]["balls"] += balls

# Iterate through all JSON files in the directory
for root, _, files in os.walk(extract_dir):
    for filename in files:
        if filename.endswith(".json"):
            process_file(os.path.join(root, filename))

# Calculate strike rate for each batsman
def calculate_strike_rate(data):
    for batsman in data:
        data[batsman]["strike_rate"] = (data[batsman]["runs"] / data[batsman]["balls"]) * 100 if data[batsman]["balls"] > 0 else 0
    return data

batsman_data_before = calculate_strike_rate(batsman_data_before)
batsman_data_after = calculate_strike_rate(batsman_data_after)

# Get top 15 batsmen based on runs
top_15_before = sorted(batsman_data_before.items(), key=lambda x: x[1]["runs"], reverse=True)[:15]
top_15_after = sorted(batsman_data_after.items(), key=lambda x: x[1]["runs"], reverse=True)[:15]

# Prepare data for plotting
def prepare_plot_data(top_15):
    runs = [item[1]["runs"] for item in top_15]
    strike_rates = [item[1]["strike_rate"] for item in top_15]
    names = [item[0] for item in top_15]
    return runs, strike_rates, names

runs_before, strike_rates_before, names_before = prepare_plot_data(top_15_before)
runs_after, strike_rates_after, names_after = prepare_plot_data(top_15_after)

# Plot settings
def plot_scatter(runs, strike_rates, names, title, subplot_index):
    plt.subplot(1, 2, subplot_index)
    plt.scatter(runs, strike_rates)
    for i, name in enumerate(names):
        plt.text(runs[i], strike_rates[i], name, fontsize=8)
    plt.xlabel("Total Runs")
    plt.ylabel("Strike Rate")
    plt.title(title)
    plt.grid(True)

# Plotting the scatter plots
plt.figure(figsize=(18, 9))

# Before May 22, 2024
plot_scatter(runs_before, strike_rates_before, names_before, "Top 15 Batsmen T20 WC Before 2024", 1)

# After May 22, 2024
plot_scatter(runs_after, strike_rates_after, names_after, "Top 15 Batsmen T20 WC 2024", 2)

plt.tight_layout()

# Save the plot with the current date in the filename
filename = f"t20_world_cup_batsmen_comparison_{current_date}.png"
plt.savefig(os.path.join(save_folder, filename))

# Clean up downloaded and extracted files
os.remove(zip_path)
import shutil
shutil.rmtree(extract_dir)


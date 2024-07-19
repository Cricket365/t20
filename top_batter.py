import os
import json
from collections import defaultdict

# Set the directory path containing the JSON files
directory_path = "/Users/sanjeetkhurana/Desktop/T20 WC/t20s_male_json"

# List of teams to consider
teams_to_consider = ["Canada", "Ireland", "USA", "Namibia", "Oman", "Scotland", "Papua New Guinea", "Uganda", "Afghanistan", "Nepal", "Netherlands"]

# Initialize a dictionary to store batting statistics
batting_stats = defaultdict(lambda: {"runs": 0, "balls_faced": 0})

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
            
            # Check if the teams in the match are in the list of teams to consider
            team1 = data["info"]["teams"][0]
            team2 = data["info"]["teams"][1]
            if team1 in teams_to_consider or team2 in teams_to_consider:
                # Process the batting data for both innings
                for innings in data["innings"]:
                    batting_team = innings["team"]
                    for over in innings["overs"]:
                        for delivery in over["deliveries"]:
                            batter = delivery["batter"]
                            runs_scored = delivery["runs"]["batter"]
                            batting_stats[batter]["runs"] += runs_scored
                            batting_stats[batter]["balls_faced"] += 1

# Calculate the strike rate for each batter
for batter, stats in batting_stats.items():
    runs = stats["runs"]
    balls_faced = stats["balls_faced"]
    if balls_faced > 0:
        strike_rate = runs * 100 / balls_faced
        batting_stats[batter]["strike_rate"] = strike_rate
    else:
        batting_stats[batter]["strike_rate"] = 0

# Sort the batters by runs in descending order
sorted_batters = sorted(batting_stats.items(), key=lambda x: x[1]["runs"], reverse=True)

# Create the scatterplot for the top 30 batters
import matplotlib.pyplot as plt

x = [stats["runs"] for batter, stats in sorted_batters[:30]]
y = [stats["strike_rate"] for batter, stats in sorted_batters[:30]]
labels = [batter for batter, stats in sorted_batters[:30]]

plt.scatter(x, y)
plt.xlabel("Runs")
plt.ylabel("Strike Rate")
plt.title("Top 30 Batters (Runs vs Strike Rate)")

# Rotate the x-axis labels for better visibility
plt.xticks(rotation=90)

# Add labels to the data points
for i, label in enumerate(labels):
    plt.annotate(label, (x[i], y[i]))

plt.show()

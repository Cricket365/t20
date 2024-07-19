import json
import pandas as pd
from glob import glob
import os

# Get the full directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
file_paths = glob(os.path.join(script_dir, 't20s_male_json/*.json'))

data = []

# Process each JSON file
for file_path in file_paths:
    with open(file_path, 'r') as f:
        match_data = json.load(f)
        
        # Extract deliveries information
        for inning in match_data['innings']:
            for over in inning['overs']:
                for delivery in over['deliveries']:
                    batter = delivery['batter']
                    runs = delivery['runs']['batter']
                    data.append([batter, runs])

# Create a DataFrame
df = pd.DataFrame(data, columns=['batter', 'runs'])

# Calculate total runs and balls faced by each batter
batter_stats = df.groupby('batter', as_index=False).agg({'runs': 'sum', 'batter': 'count'}).rename(columns={'batter': 'balls'})

# Calculate strike rate
batter_stats['strike_rate'] = (batter_stats['runs'] / batter_stats['balls']) * 100

# Filter batters who have played more than 10 games
batter_stats = batter_stats[batter_stats['balls'] > 10]

# Get top 10 batters based on strike rate
top_batters = batter_stats.sort_values(by='strike_rate', ascending=False).head(10)

# Check if the expected column names exist
expected_columns = ['batter', 'runs', 'balls', 'strike_rate']
if all(col in top_batters.columns for col in expected_columns):
    # Print the top 10 batters
    print("Top 10 Batters with Highest Strike Rate (Minimum 10 Games):")
    print(top_batters[expected_columns])
else:
    print("Error: Expected columns not found in the DataFrame.")

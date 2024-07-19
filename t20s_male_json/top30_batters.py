import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from datetime import datetime

# Function to calculate the strike rate
def calculate_strike_rate(runs, balls):
    if balls == 0:
        return 0
    return (runs / balls) * 100

# Load all JSON files
file_paths = glob('path_to_your_json_files/*.json')
data = []

# Process each JSON file
for file_path in file_paths:
    with open(file_path, 'r') as f:
        match_data = json.load(f)
        
        # Extract match date
        match_date = datetime.strptime(match_data['info']['dates'][0], '%Y-%m-%d')
        if match_date < datetime(2022, 9, 1):
            continue
        
        # Extract deliveries information
        for inning in match_data['innings']:
            for over in inning['overs']:
                for delivery in over['deliveries']:
                    batter = delivery['batter']
                    runs = delivery['runs']['batter']
                    data.append([match_date, batter, runs])

# Create a DataFrame
df = pd.DataFrame(data, columns=['date', 'batter', 'runs'])

# Calculate total runs and balls faced by each batter
batter_stats = df.groupby('batter').agg({'runs': 'sum', 'date': 'count'}).reset_index()
batter_stats.columns = ['batter', 'runs', 'balls']

# Calculate strike rate
batter_stats['strike_rate'] = batter_stats.apply(lambda row: calculate_strike_rate(row['runs'], row['balls']), axis=1)

# Get top 30 batters based on runs scored
top_batters = batter_stats.sort_values(by='runs', ascending=False).head(30)

# Plotting
plt.figure(figsize=(12, 8))
sns.scatterplot(data=top_batters, x='runs', y='strike_rate', hue='batter', s=100)
plt.title('Top 30 Batters since September 2022: Runs vs Strike Rate')
plt.xlabel('Runs Scored')
plt.ylabel('Strike Rate')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

import os
import requests
import zipfile
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import shutil

def create_wicket_hover_text(wicket_info):
    text = f"Player out: {wicket_info[0]['player_out']}<br>"
    text += f"Dismissal: {wicket_info[0]['kind']}<br>"
    text += f"Bowler: {wicket_info[0]['bowler']}<br>"
    
    if wicket_info[0]['kind'] == 'caught':
        fielders = [f['name'] for f in wicket_info[0]['fielders']]
        if fielders:
            text += f"Caught by: {fielders[0]}"
    elif wicket_info[0]['kind'] == 'run out':
        fielders = [f['name'] for f in wicket_info[0]['fielders']]
        if fielders:
            text += f"Run out by: {', '.join(fielders)}"
    
    return text

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

def create_manhattan_data(data):
    innings_data = []
    for inning in data["innings"]:
        over_data = []
        cumulative_runs = 0
        cumulative_balls = 0
        for over in inning["overs"]:
            over_runs = 0
            over_wickets = 0
            bowler = over["deliveries"][0]["bowler"]
            batters = set()
            wicket_info = []
            for delivery in over["deliveries"]:
                over_runs += delivery["runs"]["total"]
                batters.add(delivery["batter"])
                cumulative_balls += 1
                if "wickets" in delivery:
                    over_wickets += len(delivery["wickets"])
                    for wicket in delivery["wickets"]:
                        wicket_info.append({
                            "player_out": wicket["player_out"],
                            "kind": wicket["kind"],
                            "bowler": delivery["bowler"],
                            "fielders": wicket.get("fielders", [])
                        })
            cumulative_runs += over_runs
            over_data.append({
                "over": over["over"],
                "runs": over_runs,
                "cumulative_runs": cumulative_runs,
                "cumulative_balls": cumulative_balls,
                "wickets": over_wickets,
                "bowler": bowler,
                "batters": list(batters),
                "wicket_info": wicket_info
            })
        innings_data.append(over_data)
    return innings_data

# Create Manhattan data
manhattan_data = create_manhattan_data(latest_match_data)

# Create the interactive Manhattan graph
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=(f"{latest_match_data['info']['teams'][0]} Innings", 
                                    f"{latest_match_data['info']['teams'][1]} Innings"))

for i, inning in enumerate(manhattan_data, start=1):
    overs = [d["over"] for d in inning]
    runs = [d["runs"] for d in inning]
    cumulative_runs = [d["cumulative_runs"] for d in inning]
    
    # Add bar trace for runs
    fig.add_trace(
        go.Bar(
            x=overs,
            y=runs,
            name=f"Inning {i} Runs",
            hovertemplate="Over: %{x}<br>Runs: %{y}<br>Cumulative Runs: %{customdata[2]}<br>Bowler: %{customdata[0]}<br>Batters: %{customdata[1]}",
            customdata=[[d["bowler"], ", ".join(d["batters"]), d["cumulative_runs"]] for d in inning]
        ),
        row=i, col=1
    )
    
    # Add scatter trace for wickets
    wicket_overs = [d["over"] for d in inning if d["wickets"] > 0]
    wicket_runs = [d["runs"] + 2 for d in inning if d["wickets"] > 0]  # Add 2 to place wickets higher
    wicket_info = [d["wicket_info"] for d in inning if d["wickets"] > 0]
    
    if wicket_overs:  # Only add the trace if there are wickets
        fig.add_trace(
            go.Scatter(
                x=wicket_overs,
                y=wicket_runs,
                mode="markers",
                marker=dict(symbol="star", size=12, color="red"),
                name="Wickets",
                hovertemplate="Over: %{x}<br>Runs: %{y}<br>%{customdata}",
                customdata=[create_wicket_hover_text(w) for w in wicket_info]
            ),
            row=i, col=1
        )

fig.update_layout(
    title_text="Manhattan Graph: Over-wise Runs and Wickets",
    height=800,
    showlegend=True
)

fig.update_xaxes(title_text="Overs", row=2, col=1)
fig.update_yaxes(title_text="Runs", row=1, col=1)
fig.update_yaxes(title_text="Runs", row=2, col=1)

# Save the interactive plot
os.makedirs(save_folder, exist_ok=True)
filename_graph = os.path.join(save_folder, "manhattan_graph.html")
fig.write_html(filename_graph)

# Clean up downloaded and extracted files
os.remove(zip_path)
shutil.rmtree(extract_dir)

print(f"Analysis complete. Interactive Manhattan graph saved as {filename_graph}")

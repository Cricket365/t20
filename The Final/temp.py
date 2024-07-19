import matplotlib.pyplot as plt
import mpld3

# Simplified data for testing
overs = [1, 2, 3, 4, 5, 6]
runs = [10, 20, 15, 25, 10, 5]
cumulative_runs = [10, 30, 45, 70, 80, 85]

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(overs, runs, color='blue', edgecolor='white')

# Adding hover text
tooltip = mpld3.plugins.PointLabelTooltip(bars, labels=[
    f"Over: {o}<br>Runs: {r}<br>Cumulative Runs: {c}" 
    for o, r, c in zip(overs, runs, cumulative_runs)
])
mpld3.plugins.connect(fig, tooltip)

ax.set_title("Simplified Manhattan Graph")
ax.set_xlabel("Overs")
ax.set_ylabel("Runs")

# Save the interactive plot
mpld3.save_html(fig, "simplified_manhattan_graph.html")

print("Simplified Manhattan graph saved as simplified_manhattan_graph.html")

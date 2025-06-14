import pandas as pd
import matplotlib.pyplot as plt

# List of UC campuses
uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

# Load and extract TRANSFERABLE AVERAGE row from each order CSV
order_dfs = []
for i in range(1, 4):
    df = pd.read_csv(f"order_{i}_averages.csv")
    transferable_row = df[df["Community College"] == "TRANSFERABLE AVERAGE"]
    if not transferable_row.empty:
        transferable_row["Order"] = f"Order {i}"
        order_dfs.append(transferable_row)

# Reformat into long-form for plotting
records = []
for df in order_dfs:
    order = df["Order"].values[0]
    for uc in uc_schools:
        art_col = f"{uc} Articulated"
        if art_col in df.columns:
            records.append({
                "UC": uc,
                "Order": order,
                "Average Courses": df[art_col].values[0]
            })

plot_df = pd.DataFrame(records)

# Pivot to get each UC with average per order
pivot_df = plot_df.pivot(index="UC", columns="Order", values="Average Courses")

# Plot grouped bar chart
ax = pivot_df.plot(kind="bar", figsize=(12, 6), colormap="tab10")
plt.title("Transferable Average Articulated Courses by UC and Order")
plt.ylabel("Average Articulated Courses")
plt.xlabel("University of California")
plt.xticks(rotation=0)
plt.tight_layout()
plt.legend(title="Order")

# Annotate values above bars
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", label_type="edge", padding=3, fontsize=8)

# Save the figure
plt.savefig("transferable_averages_by_uc.png", dpi=300, bbox_inches='tight')

plt.show()
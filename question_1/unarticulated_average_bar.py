import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_uc_unarticulated_from_average_row(order_1_path):
    # Load the CSV
    df = pd.read_csv(order_1_path)

    # Extract the 'AVERAGE' row
    avg_row = df[df["Community College"].str.upper() == "AVERAGE"]

    if avg_row.empty:
        print("No 'AVERAGE' row found.")
        return

    # Get UCs from column names
    uc_list = sorted(set(col.split()[0] for col in df.columns if col.endswith("Unarticulated")))

    # Extract data from 'AVERAGE' row
    unart_data = {'UC': [], 'Avg Unarticulated Courses': []}
    for uc in uc_list:
        col_name = f"{uc} Unarticulated"
        if col_name in avg_row.columns:
            unart_data['UC'].append(uc)
            unart_data['Avg Unarticulated Courses'].append(float(avg_row.iloc[0][col_name]))

    # Create DataFrame for plotting
    unart_df = pd.DataFrame(unart_data)

    # Plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=unart_df, x='UC', y='Avg Unarticulated Courses')
    plt.title("Average Unarticulated Courses per UC (From 'AVERAGE' Row of Order 1)")
    plt.ylabel("Average Unarticulated Courses")
    plt.xlabel("UC")

    # Annotate each bar with its value
    for i, bar in enumerate(ax.patches):
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",  # Format to 2 decimal places
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset text slightly above bar
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig("unarticulated_simple_bar.png")
    plt.show()

if __name__ == "__main__":
    plot_uc_unarticulated_from_average_row(
        "/workspaces/assist_web_scraping/question_1/order_csvs_averages/order_1_averages.csv"
    )

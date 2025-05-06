import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_grouped_bar_charts(order_1_path, order_2_path, order_3_path):
    # Load all three CSVs, excluding the 'AVERAGE' row
    def load_and_clean_csv(path):
        df = pd.read_csv(path)
        return df[df["Community College"].str.upper() != "AVERAGE"].reset_index(drop=True)

    order_1_df = load_and_clean_csv(order_1_path)
    order_2_df = load_and_clean_csv(order_2_path)
    order_3_df = load_and_clean_csv(order_3_path)

    # Identify all UC names
    uc_list = sorted(set(col.split()[0] for col in order_1_df.columns if col != "Community College"))
    roles = ['1st', '2nd', '3rd']
    dfs = [order_1_df, order_2_df, order_3_df]

    # Track excluded (CC, UC) paths and store included articulated data
    excluded_paths = []
    included_data = {uc: {role: [] for role in roles} for uc in uc_list}

    cc_names = order_1_df["Community College"]

    for i, cc in enumerate(cc_names):
        for uc in uc_list:
            exclude_pair = False
            for df in dfs:
                unart_col = f"{uc} Unarticulated"
                if unart_col in df.columns and df.iloc[i][unart_col] > 0:
                    exclude_pair = True
                    break
            if exclude_pair:
                excluded_paths.append(f"{cc} --> {uc}")
            else:
                for df, role in zip(dfs, roles):
                    art_col = f"{uc} Articulated"
                    if art_col in df.columns:
                        included_data[uc][role].append(df.iloc[i][art_col])

    # Save excluded paths to a .txt file
    with open("excluded_cc_uc_paths.txt", "w") as f:
        f.write(f"Total Excluded CC → UC Paths: {len(excluded_paths)}\n\n")
        for path in excluded_paths:
            f.write(path + "\n")

    # Prepare data for plotting
    art_data = {'UC': [], 'Role': [], 'Avg Articulated Courses': []}
    for uc in uc_list:
        for role in roles:
            values = included_data[uc][role]
            if values:
                avg = sum(values) / len(values)
                art_data['UC'].append(uc)
                art_data['Role'].append(role)
                art_data['Avg Articulated Courses'].append(avg)

    art_df = pd.DataFrame(art_data)

    # Plot with annotated values
    plt.figure(figsize=(14, 6))
    ax = sns.barplot(data=art_df, x='UC', y='Avg Articulated Courses', hue='Role')
    plt.title("Average Articulated Courses per UC by Role (Only Articulated CC→UC Pathways)")
    plt.ylabel("Average Articulated Courses")
    plt.xlabel("UC")
    plt.legend(title="Role")

    # Annotate bars using grouped data so that we avoid any misalignment
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            if not pd.isna(height):
                offset = 3 if height > 0 else 6
                ax.annotate(f"{height:.2f}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, offset),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig("articulated_grouped_by_role_filtered.png")
    plt.show()


if __name__ == "__main__":
    plot_grouped_bar_charts(
        "/workspaces/assist_web_scraping/question_1/order_csvs_averages/order_1_averages.csv",
        "/workspaces/assist_web_scraping/question_1/order_csvs_averages/order_2_averages.csv",
        "/workspaces/assist_web_scraping/question_1/order_csvs_averages/order_3_averages.csv"
    )

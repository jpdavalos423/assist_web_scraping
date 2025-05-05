import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_grouped_bar_charts(order_1_path, order_2_path, order_3_path):
    # Load all three CSVs
    order_1_df = pd.read_csv(order_1_path)
    order_2_df = pd.read_csv(order_2_path)
    order_3_df = pd.read_csv(order_3_path)

    # Get list of UCs by splitting columns
    uc_list = sorted(set(col.split()[0] for col in order_1_df.columns if col != "Community College"))
    roles = ['1st', '2nd', '3rd']
    dfs = [order_1_df, order_2_df, order_3_df]

    # Prepare long-form data
    art_data = {'UC': [], 'Role': [], 'Avg Articulated Courses': []}
    unart_data = {'UC': [], 'Role': [], 'Avg Unarticulated Courses': []}

    for uc in uc_list:
        for df, role in zip(dfs, roles):
            art_col = f"{uc} Articulated"
            unart_col = f"{uc} Unarticulated"

            if art_col in df.columns and unart_col in df.columns:
                art_data['UC'].append(uc)
                art_data['Role'].append(role)
                art_data['Avg Articulated Courses'].append(df[art_col].mean())

                unart_data['UC'].append(uc)
                unart_data['Role'].append(role)
                unart_data['Avg Unarticulated Courses'].append(df[unart_col].mean())

    art_df = pd.DataFrame(art_data)
    unart_df = pd.DataFrame(unart_data)

    # Plot Articulated
    plt.figure(figsize=(14, 6))
    sns.barplot(data=art_df, x='UC', y='Avg Articulated Courses', hue='Role')
    plt.title("Average Articulated Courses per UC by Role")
    plt.ylabel("Average Articulated Courses")
    plt.xlabel("UC")
    plt.legend(title="Role")
    plt.tight_layout()
    plt.savefig("articulated_grouped_by_role.png")
    plt.show()

    # Plot Unarticulated
    plt.figure(figsize=(14, 6))
    sns.barplot(data=unart_df, x='UC', y='Avg Unarticulated Courses', hue='Role')
    plt.title("Average Unarticulated Courses per UC by Role")
    plt.ylabel("Average Unarticulated Courses")
    plt.xlabel("UC")
    plt.legend(title="Role")
    plt.tight_layout()
    plt.savefig("unarticulated_grouped_by_role.png")
    plt.show()

if __name__ == "__main__":
    # Replace with actual paths or use command-line arguments
    plot_grouped_bar_charts(
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_1_averages.csv",
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_1_averages.csv",
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_1_averages.csv"
    )

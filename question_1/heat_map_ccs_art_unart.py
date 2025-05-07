import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def plot_heatmaps_for_file(csv_path):
    df = pd.read_csv(csv_path, index_col=0)
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    order_number = base_name.split("_")[1] if "_" in base_name else "X"

    # Articulated
    art_cols = [col for col in df.columns if 'Art' in col and 'Unart' not in col]
    art_df = df[art_cols].copy()
    art_df.columns = [col.replace(" Art", "") for col in art_df.columns]
    art_df.index.name = "Community College"

    # Articulated - With Labels
    plt.figure(figsize=(12, 10))
    sns.heatmap(art_df, cmap="YlGnBu", annot=True, fmt=".1f")
    plt.title(f"Articulated Courses (Order {order_number})")
    plt.xlabel("UC Campus")
    plt.ylabel("Community College")
    plt.tight_layout()
    plt.savefig(f"articulated_order_{order_number}_with_labels.png")
    plt.close()

    # Articulated - No Labels
    plt.figure(figsize=(12, 10))
    sns.heatmap(art_df, cmap="YlGnBu", annot=False)
    plt.title(f"Articulated Courses (Order {order_number})")
    plt.xlabel("UC Campus")
    plt.ylabel("Community College")
    plt.tight_layout()
    plt.savefig(f"articulated_order_{order_number}_no_labels.png")
    plt.close()

    # Unarticulated
    unart_cols = [col for col in df.columns if 'Unart' in col]
    unart_df = df[unart_cols].copy()
    unart_df.columns = [col.replace(" Unart", "") for col in unart_df.columns]
    unart_df.index.name = "Community College"

    # Unarticulated - With Labels
    plt.figure(figsize=(12, 10))
    sns.heatmap(unart_df, cmap="Reds", annot=True, fmt=".1f")
    plt.title(f"Unarticulated Courses (Order {order_number})")
    plt.xlabel("UC Campus")
    plt.ylabel("Community College")
    plt.tight_layout()
    plt.savefig(f"unarticulated_order_{order_number}_with_labels.png")
    plt.close()

    # Unarticulated - No Labels
    plt.figure(figsize=(12, 10))
    sns.heatmap(unart_df, cmap="Reds", annot=False)
    plt.title(f"Unarticulated Courses (Order {order_number})")
    plt.xlabel("UC Campus")
    plt.ylabel("Community College")
    plt.tight_layout()
    plt.savefig(f"unarticulated_order_{order_number}_no_labels.png")
    plt.close()

    print(f"✅ Finished heatmaps for Order {order_number}")

if __name__ == "__main__":
    filenames = [
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_1_averages.csv",
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_2_averages.csv",
        "/Users/yasminkabir/assist_web_scraping-1/question_1/order_csvs_averages/order_3_averages.csv"
    ]

    for file_path in filenames:
        if os.path.exists(file_path):
            plot_heatmaps_for_file(file_path)
        else:
            print(f"⚠️ File not found: {file_path}")

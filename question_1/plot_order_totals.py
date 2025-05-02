import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_uc_articulation(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Identify columns for articulated and unarticulated data
    art_cols = [col for col in df.columns if 'Art' in col and 'Unart' not in col]
    unart_cols = [col for col in df.columns if 'Unart' in col]

    # Sum and average values
    total_articulated = df[art_cols].sum()
    total_unarticulated = df[unart_cols].sum()
    order_number = os.path.basename(file_path).split("_")[1]
    average_articulated = total_articulated / len(df)
    average_unarticulated = total_unarticulated / len(df)

    # Articulated courses plot
    plt.figure(figsize=(10, 6))
    average_articulated.sort_values().plot(
        kind='barh',
        title=f'Articulated Courses for Order #{order_number}',
        xlabel='Average Courses',
        ylabel='UC'
    )
    plt.tight_layout()
    plt.savefig(f'articulated_order_{order_number}.png')
    plt.show()

    # Unarticulated courses plot
    plt.figure(figsize=(10, 6))
    average_unarticulated.sort_values().plot(
        kind='barh',
        color='orange',
        title=f'Unarticulated Courses for Order #{order_number}',
        xlabel='Average Courses',
        ylabel='UC'
    )
    plt.tight_layout()
    plt.savefig(f'unarticulated_order_{order_number}.png')
    plt.show()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python plot_uc_articulation.py <path_to_csv>")
    else:
        plot_uc_articulation(sys.argv[1])

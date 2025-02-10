import pandas as pd
import csv
import os
import matplotlib.pyplot as plt
import json


with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)


def display_computations(
                    data_dir="performance_data", # Directory containing raw data
                    output_dir="performance_graphs" # Directory for saving metric graphs
                ):
    output_dir = os.path.join(os.path.dirname(__file__), output_dir)
    data_dir = os.path.join(os.path.dirname(__file__), data_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Combining computations over time and saving as graph
    naive_df = pd.read_csv(os.path.join(data_dir, "naive_real_vs_necessary_computations.csv"))
    naive_df.columns = ['naive_necessary_processes', 'naive_real_processes']
    x_naive = naive_df['naive_necessary_processes']
    y_naive = naive_df['naive_real_processes']

    optimised_df = pd.read_csv(os.path.join(data_dir, "optimised_real_vs_necessary_computations.csv"))
    optimised_df.columns = ['optimised_necessary_processes', 'optimised_real_processes']
    x_optimised = optimised_df['optimised_necessary_processes']
    y_optimised = optimised_df['optimised_real_processes']

    # Ploting combined computations
    plt.plot(x_naive, y_naive, marker="o", linestyle="-", label="Naive pipeline")
    plt.plot(x_optimised, y_optimised, marker="s", linestyle="--", label="Optimised pipeline")

    # Adding labels and legend
    plt.xlabel("Necessary computations")
    plt.ylabel("Real computations")
    plt.title("Number of real compared to necessary computations for the naive vs. optimised pipeline")
    plt.legend()
    plt.grid(True)

    # Saving the combined graph
    plt.savefig(os.path.join(output_dir, 'real_vs_necessary_computations.png'), bbox_inches='tight')
    print("Computations over time saved as: real_vs_necessary_computations.png")


    # Combining other metric data and saving as a dataframe image
    naive_df = pd.read_csv(os.path.join(data_dir, "naive_outputs.csv"))
    naive_df['process'] = ['naive']

    optimised_df = pd.read_csv(os.path.join(data_dir, "optimised_outputs.csv"))
    optimised_df['process'] = ['optimised']

    df_outputs = pd.concat([naive_df, optimised_df], ignore_index=True)
    df_outputs = df_outputs[['process', 'inference_function_totals', 'total_processing_time', 'total_processes']]

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.axis("tight")
    ax.axis("off")
    ax.table(cellText=df_outputs.values, colLabels=df_outputs.columns, cellLoc="center", loc="center")

    # Saving the dataframe
    plt.savefig(os.path.join(output_dir, "pipeline_metrics.png"), dpi=300, bbox_inches="tight")
    print("Overall pipeline metrics saved as: pipeline_metrics.png")


if __name__ == "__main__":
    display_computations(
                    data_dir=config["METRIC_DATA_DIR"],
                    output_dir=config["METRIC_GRAPHS_DIR"]
                )
    







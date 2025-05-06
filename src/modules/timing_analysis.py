import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def analyze_timing_log(log_path='detailed_timing.log'):
    # Load the timing log CSV
    df = pd.read_csv(log_path)

    # Basic line plots of timing components over simulation steps
    plt.figure(figsize=(14, 7))
    plt.plot(df['step'], df['update_time'], label='Update Time (s)', color='blue')
    plt.plot(df['step'], df['visualize_time'], label='Visualize Time (s)', color='green')
    plt.plot(df['step'], df['capture_frame_time'], label='Capture Frame Time (s)', color='red')
    plt.xlabel('Simulation Step')
    plt.ylabel('Time (seconds)')
    plt.title('Simulation Timing per Step')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('simulation_timing_overview.png')
    plt.show()

    # Histogram of update times to identify bottlenecks
    plt.figure(figsize=(10, 6))
    plt.hist(df['update_time'], bins=30, color='skyblue', edgecolor='black')
    plt.xlabel('Update Time (s)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Update Times')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('update_time_histogram.png')
    plt.show()

    # Boxplot to show distribution and outliers of timing components
    plt.figure(figsize=(10, 6))
    plt.boxplot([df['update_time'], df['visualize_time'], df['capture_frame_time']],
                labels=['Update Time', 'Visualize Time', 'Capture Frame Time'])
    plt.title('Boxplot of Timing Components')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('timing_components_boxplot.png')
    plt.show()

    # Calculate rolling average to smooth timing data and highlight trends
    window_size = 10
    df['update_time_smooth'] = df['update_time'].rolling(window=window_size).mean()
    df['visualize_time_smooth'] = df['visualize_time'].rolling(window=window_size).mean()
    df['capture_frame_time_smooth'] = df['capture_frame_time'].rolling(window=window_size).mean()

    plt.figure(figsize=(14, 7))
    plt.plot(df['step'], df['update_time_smooth'], label='Smoothed Update Time', color='blue')
    plt.plot(df['step'], df['visualize_time_smooth'], label='Smoothed Visualize Time', color='green')
    plt.plot(df['step'], df['capture_frame_time_smooth'], label='Smoothed Capture Frame Time', color='red')
    plt.xlabel('Simulation Step')
    plt.ylabel('Time (seconds)')
    plt.title(f'Smoothed Timing per Step (Window Size = {window_size})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('smoothed_timing_overview.png')
    plt.show()

    # Annotate potential bottlenecks: steps where update_time exceeds mean + 2*std
    mean_update = df['update_time'].mean()
    std_update = df['update_time'].std()
    threshold = mean_update + 2 * std_update
    bottlenecks = df[df['update_time'] > threshold]

    plt.figure(figsize=(14, 7))
    plt.plot(df['step'], df['update_time'], label='Update Time (s)', color='blue')
    plt.axhline(y=threshold, color='red', linestyle='--', label='Bottleneck Threshold')
    for _, row in bottlenecks.iterrows():
        plt.annotate(f"Step {int(row['step'])}", (row['step'], row['update_time']),
                     textcoords="offset points", xytext=(0,10), ha='center', color='red')
    plt.xlabel('Simulation Step')
    plt.ylabel('Update Time (seconds)')
    plt.title('Update Time with Bottleneck Annotations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('update_time_bottlenecks.png')
    plt.show()

    # Summary statistics with explanations
    summary = df.describe()
    print("Timing Summary Statistics:")
    print(summary)
    print("\nExplanation:")
    print("- Mean and median show typical timing values.")
    print("- Std deviation indicates variability; high values suggest inconsistent performance.")
    print("- Bottlenecks are steps where update time significantly exceeds normal range (mean + 2*std).")
    print("- Use the graphs to identify when and how often bottlenecks occur.")

if __name__ == "__main__":
    analyze_timing_log()

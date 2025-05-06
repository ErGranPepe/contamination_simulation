import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def analyze_timing_log(log_path='detailed_timing.log'):
    # Load the timing log CSV
    df = pd.read_csv(log_path)

    # Calculate total time per step as sum of main components
    df['total_time'] = df['update_time'] + df['visualize_time'] + df['capture_frame_time']

    # Calculate percentage of total time for each component
    df['update_pct'] = 100 * df['update_time'] / df['total_time']
    df['visualize_pct'] = 100 * df['visualize_time'] / df['total_time']
    df['capture_pct'] = 100 * df['capture_frame_time'] / df['total_time']

    # Plot absolute timing components over simulation steps
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

    # Plot percentage of total time per component over steps
    plt.figure(figsize=(14, 7))
    plt.plot(df['step'], df['update_pct'], label='Update Time (%)', color='blue')
    plt.plot(df['step'], df['visualize_pct'], label='Visualize Time (%)', color='green')
    plt.plot(df['step'], df['capture_pct'], label='Capture Frame Time (%)', color='red')
    plt.xlabel('Simulation Step')
    plt.ylabel('Percentage of Total Time (%)')
    plt.title('Percentage of Total Time per Component per Step')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('simulation_timing_percentage_overview.png')
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
    components = ['update_time', 'visualize_time', 'capture_frame_time']
    plt.figure(figsize=(10, 6))
    plt.boxplot([df[comp] for comp in components],
                labels=[comp.replace('_', ' ').title() for comp in components])
    plt.title('Boxplot of Timing Components')
    plt.ylabel('Time (seconds)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('timing_components_boxplot.png')
    plt.show()

    # Calculate rolling average to smooth timing data and highlight trends
    window_size = 10
    for comp in components:
        df[f'{comp}_smooth'] = df[comp].rolling(window=window_size).mean()

    plt.figure(figsize=(14, 7))
    for comp in components:
        plt.plot(df['step'], df[f'{comp}_smooth'], label=f'Smoothed {comp.replace("_", " ").title()}')
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
    plt.ylabel('Time (seconds)')
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
    print("- The new percentage plots show how much each component contributes to total time per step.")

if __name__ == "__main__":
    analyze_timing_log()

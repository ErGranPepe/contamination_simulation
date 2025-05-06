import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

class ControlPanel(tk.Frame):
    def __init__(self, parent, log_path='detailed_timing.log'):
        super().__init__(parent)
        self.log_path = log_path
        self.df = pd.read_csv(self.log_path)
        self.create_widgets()

    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Create frames for each tab
        self.tab_overview = ttk.Frame(self.notebook)
        self.tab_histogram = ttk.Frame(self.notebook)
        self.tab_boxplot = ttk.Frame(self.notebook)
        self.tab_bottlenecks = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_overview, text='Timing Overview')
        self.notebook.add(self.tab_histogram, text='Update Time Histogram')
        self.notebook.add(self.tab_boxplot, text='Timing Boxplot')
        self.notebook.add(self.tab_bottlenecks, text='Bottleneck Analysis')

        # Plot each graph in respective tab
        self.plot_timing_overview()
        self.plot_histogram()
        self.plot_boxplot()
        self.plot_bottlenecks()

    def plot_timing_overview(self):
        start = time.perf_counter()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(self.df['step'], self.df['update_time'], label='Update Time (s)', color='blue')
        ax.plot(self.df['step'], self.df['visualize_time'], label='Visualize Time (s)', color='green')
        ax.plot(self.df['step'], self.df['capture_frame_time'], label='Capture Frame Time (s)', color='red')
        ax.set_xlabel('Simulation Step')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Simulation Timing per Step')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.tab_overview)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        end = time.perf_counter()
        print(f"plot_timing_overview took {end - start:.4f} seconds")

    def plot_histogram(self):
        start = time.perf_counter()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(self.df['update_time'], bins=30, color='skyblue', edgecolor='black')
        ax.set_xlabel('Update Time (s)')
        ax.set_ylabel('Frequency')
        ax.set_title('Histogram of Update Times')
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.tab_histogram)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        end = time.perf_counter()
        print(f"plot_histogram took {end - start:.4f} seconds")

    def plot_boxplot(self):
        start = time.perf_counter()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.boxplot([self.df['update_time'], self.df['visualize_time'], self.df['capture_frame_time']],
                   labels=['Update Time', 'Visualize Time', 'Capture Frame Time'])
        ax.set_title('Boxplot of Timing Components')
        ax.set_ylabel('Time (seconds)')
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.tab_boxplot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        end = time.perf_counter()
        print(f"plot_boxplot took {end - start:.4f} seconds")

    def plot_bottlenecks(self):
        start = time.perf_counter()
        mean_update = self.df['update_time'].mean()
        std_update = self.df['update_time'].std()
        threshold = mean_update + 2 * std_update
        bottlenecks = self.df[self.df['update_time'] > threshold]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(self.df['step'], self.df['update_time'], label='Update Time (s)', color='blue')
        ax.axhline(y=threshold, color='red', linestyle='--', label='Bottleneck Threshold')
        for _, row in bottlenecks.iterrows():
            ax.annotate(f"Step {int(row['step'])}", (row['step'], row['update_time']),
                        textcoords="offset points", xytext=(0,10), ha='center', color='red')
        ax.set_xlabel('Simulation Step')
        ax.set_ylabel('Update Time (seconds)')
        ax.set_title('Update Time with Bottleneck Annotations')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.tab_bottlenecks)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        end = time.perf_counter()
        print(f"plot_bottlenecks took {end - start:.4f} seconds")

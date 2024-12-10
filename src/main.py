import tkinter as tk
from src.modules.toolTip import ToolTip
from src.modules.contaminationSimulation import ContaminationSimulation
from src.modules.recorder import SimulationRecorder
import traci
import threading

# Código principal que incluye la clase ContaminationConfigPlugin y sus métodos.

if __name__ == "__main__":
    root = tk.Tk()
    app = ContaminationConfigPlugin(root, start_simulation_thread)
    root.mainloop()

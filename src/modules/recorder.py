import os
import cv2
import traci
from datetime import datetime
import logging

logging.basicConfig(filename='simulation_recorder.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SimulationRecorder:
    def __init__(self, sumo_config, parameters, fps=30):
        self.sumo_config = sumo_config
        self.parameters = parameters
        self.fps = fps
        self.frames = []
        self.temp_frame_path = "temp_frame.png"
        self.output_file = self.generate_output_filename()

    def generate_output_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.sumo_config}_{timestamp}.mp4"
        output_dir = os.path.abspath("recordings")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return os.path.join(output_dir, filename)

    def capture_frame(self):
        try:
            traci.gui.screenshot("View #0", self.temp_frame_path, width=1920, height=1080)
            frame = cv2.imread(self.temp_frame_path)
            if frame is not None:
                self.frames.append(frame)
        except Exception as e:
            logging.error(f"Error capturing frame: {e}")
        finally:
            if os.path.exists(self.temp_frame_path):
                try:
                    os.remove(self.temp_frame_path)
                except Exception as e:
                    logging.error(f"Error removing temp frame: {e}")

    def overlay_text(self, frame):
        parameters_text = "\n".join([f"{key}: {value}" for key, value in self.parameters.items()])
        text = f"Config: {self.sumo_config}\nParameters:\n{parameters_text}"
        y0, dy = 30, 30
        for i, line in enumerate(text.split('\n')):
            y = y0 + i * dy
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        return frame

    def save_video(self):
        if not self.frames:
            return
        height, width, _ = self.frames[0].shape
        video = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (width, height))
        for frame in self.frames:
            frame = self.overlay_text(frame)
            video.write(frame)
        video.release()

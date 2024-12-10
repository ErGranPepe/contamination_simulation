import os
import time
import cv2
import traci

class SimulationRecorder:
    def __init__(self, output_file, fps=30):
        self.output_file = output_file
        self.fps = fps
        self.frames = []
        self.temp_frame_path = os.path.abspath("temp_frame.png")

    def capture_frame(self):
        try:
            traci.gui.screenshot("View #0", self.temp_frame_path, width=1920, height=1080)
            if not os.path.exists(self.temp_frame_path):
                print(f"Screenshot not created at {self.temp_frame_path}")
                return

            frame = cv2.imread(self.temp_frame_path)
            if frame is None:
                print(f"Failed to read image from {self.temp_frame_path}")
                return

            # Agregar el frame a la lista
            self.frames.append(frame)

        except Exception as e:
            print(f"Error capturing frame: {str(e)}")

        finally:
            if os.path.exists(self.temp_frame_path):
                try:
                    os.remove(self.temp_frame_path)
                except Exception as e:
                    print(f"Error removing temporary file: {str(e)}")

    def save_video(self):
        if not self.frames:
            print("No frames to save")
            return

        height, width, layers = self.frames[0].shape
        video = cv2.VideoWriter(self.output_file, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (width, height))

        for frame in self.frames:
            video.write(frame)

        video.release()
        print(f"Video saved to {self.output_file}")

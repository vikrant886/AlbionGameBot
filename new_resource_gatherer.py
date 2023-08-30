import threading
from object_detector import perform_object_detection , stop
import pyautogui
# from ui_logic import is_performing_object_detection
class ObjectDetectionThread(threading.Thread):
    def __init__(self):
        super(ObjectDetectionThread, self).__init__()
        self.running = False

    def run(self):
        self.running = True
        if self.running:
            perform_object_detection()

    def stop(self):
        stop()
        print("stopping")
        self.running = False

is_running=0

def stop():
    print("resource gatherer stop called")

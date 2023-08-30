import cv2 as cv
import numpy as np
import os
import time
from window_cap import WindowCapture
from ultralytics import YOLO
import random
import pyautogui
import threading
import sys
from ui_logic import MyApp

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ui=MyApp()

def call_ui():
    ui.run()
# Create and start the thread

ui_thread=threading.Thread(target=call_ui)

ui_thread.start()

ui_thread.join()



print('Done.')

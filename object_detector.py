from window_cap import WindowCapture
import  cv2 as cv
from ultralytics import YOLO
import torch
import  time
import queue


print('cuda' if torch.cuda.is_available() else 'cpu')
model = YOLO('./YOLOmodel/dungeon_edit.pt')
wincap = WindowCapture(None)
# initialize the position variable
pos = 0
change=1
def stop():
    global change
    change=-1;

fps_start_time = time.time()
fps_counter = 0

def perform_object_detection():
    screenshot_queue = queue.Queue()
    global fps_counter
    global fps_start_time
    while True:
        # get an updated image of the game
        screenshot = wincap.get_screenshot()

        results = model(screenshot,device="cuda")
        aa = None
        for result in results:
            for box in result.boxes.xyxy:
                left, top, right, bottom = box
                aa = cv.rectangle(screenshot, (int(left + 2), int(top + 2)), (int(right + 2), int(bottom + 2)),
                                   (0, 255, 0), 2)
        if results[0].keypoints is None:
            aa = screenshot
        cv.resize(aa, (800, 600))

        aa = cv.resize(aa, (800, 600))

        cv.imshow("record", aa)
        screenshot_queue.put(aa)
        fps_counter += 1
        fps_end_time = time.time()
        fps_duration = fps_end_time - fps_start_time

        if fps_duration >= 1:
            fps = fps_counter / fps_duration
            print(f"FPS: {fps:.2f}")
            fps_counter = 0
            fps_start_time = fps_end_time


        global change
        if change==-1:
            print("inside")
            cv.destroyAllWindows()
            change=1
            break
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break


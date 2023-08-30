import math
import threading
import time
import pyautogui
from time import sleep
import paperclip
import pyperclip
import pandas as pd
import re
from pynput import keyboard
from window_cap import WindowCapture
# import keyboard
import cv2 as cv
# from new_resource_gatherer import  perform_gathering , stop


is_running = True
stop_key = keyboard.Key.esc
path = pd.read_csv('path.csv')
window = WindowCapture(None)
# class Pather:
#
#     def __init__(self):


def create_vector(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    vx = x2 - x1
    vy = y2 - y1

    return vx, vy

def angle_with_x_axis(vector):
    # Extract the x-component and y-component of the vector
    vx, vy = vector

    # Calculate the magnitude of the vector
    magnitude = math.sqrt(vx ** 2 + vy ** 2)

    # Calculate the angle with the x-axis using the arccos function
    if magnitude == 0:
        return 0
    if vy >= 0:
        angle_radians = math.acos(vx / magnitude)
    else:
        angle_radians = -math.acos(vx / magnitude)

    return angle_radians - math.pi / 4
    # + math.pi - math.pi/4

def extract_numbers(input_string):
    # Define the regular expression pattern to find two floating-point numbers
    pattern = r"-?\d+\.\d+"

    # Find all occurrences of the pattern in the input string
    numbers = re.findall(pattern, input_string)

    # Convert the found strings to floating-point numbers
    numbers = [float(num) for num in numbers]

    return numbers

def move_player(angle, radius, monitor):
    # Calculate X and Y offsets using trigonometry
    x_offset = radius * math.cos(angle)
    y_offset = -radius * math.sin(angle)

    # Get the current mouse position
    player_x, player_y = monitor['left'] + monitor['width'] / 2, monitor['top'] + monitor['height'] / 2

    # Calculate the new position around the player
    new_x = player_x + x_offset
    new_y = player_y + y_offset

    # Move the mouse to the new position
    pyautogui.moveTo(new_x, new_y)

def on_press(key):
    global is_running
    if key == stop_key:
        pyautogui.mouseUp(button='right')
        is_running=False
        return False


def gather_surrounding():
    gatherer_thread=resource_thread()
    print("gatherer called")
    time.sleep(3)
    gatherer_thread.start()


def movement_logic_main():
    global is_running
    is_running=True
    sleep(2)
    pyautogui.press('enter')
    sleep(0.1)
    pyautogui.press('#')
    pyautogui.press('w')
    pyautogui.press('h')
    pyautogui.press('e')
    pyautogui.press('r')
    pyautogui.press('e')
    pyautogui.press('enter')
    sleep(2)
    with keyboard.Listener(on_press=on_press) as listener:
        index = 0
        print(index)
        count = 0
        pre_x = 0
        pre_y = 0
        try:
            while is_running:
                # pyautogui.mouseUp(button='right')
                print("working in a while")
                pyautogui.press('enter')
                pyautogui.press('up')
                pyautogui.press('enter')
                my_pos = pyperclip.paste()
                my_pos = extract_numbers(my_pos)
                first = my_pos[0]
                second = my_pos[1];
                monitor = window.monitor
                if count == 0:
                    pre_x = first
                    pre_y = second
                    count += 1
                else:
                    print(str(first) + " " + str(pre_x) + " " + str(second) + " " + str(pre_y))
                    if math.sqrt((first - pre_x) ** 2 + (second - pre_y) ** 2) <= 0.004:
                        print("rerouting")
                    else:
                        pre_x = first
                        pre_y = second
                row = path.iloc[index]
                x, y, station = row['x'], row['y'], row['station']
                distance = math.sqrt((first - x) ** 2 + (second - y) ** 2)
                print(distance)
                destination = (x, y)
                print("destination: " + str(destination))
                vector = create_vector(my_pos, destination)
                vx, vy = vector
                magnitude = math.sqrt(vx ** 2 + vy ** 2)
                angle = angle_with_x_axis(vector)
                print("magnitude: " + str(magnitude))

                print("angle: " + str(math.degrees(angle)))

                monitor = window.monitor
                print(monitor)
                move_player(angle, 100, monitor)

                if magnitude >= 5:
                    pyautogui.mouseDown(button='right')
                    continue
                elif magnitude < 5:
                    if station == 1:
                        pyautogui.rightClick()
                        gather_surrounding()
                    index += 1
                    pass

        except Exception as e:
            pyautogui.rightClick()
            print(e)
            print("stopping")
        # index += 1

# t 3209 208.9543 386.1061

import cv2 as cv
import numpy as np
import math
import pyautogui

# from screeninfo import get_monitors

dpi_scaling = 2
ENEMIES = ['low mob', 'high mob', 'golem']
MOB_RADIUS = 210


class Location:
    def __init__(self, name, coordinate, monitor):
        self.name = name
        self.coordinates = coordinate
        self.monitor = monitor
        my_pos = ((monitor['left'] * 2 + monitor['width']) / 2, (monitor['top'] * 2 + monitor['height']) / 2)
        self.dist_from_center = self.distance_from_center(my_pos[0], my_pos[1])

    def distance_from_center(self, x, y):
        return math.sqrt((self.coordinates[0] - x) ** 2 + (self.coordinates[1] - y) ** 2)


class Vision:

    # given a list of [x, y, w, h] rectangles returned by find(), convert those into a list of
    # [x, y] positions in the center of those rectangles where we can click on those found items
    def get_click_points(self, rectangles, names, monitor):
        points = []


        for box, name in zip(rectangles, names):
            x1, y1, x2, y2 = box
            coordinates = [(x1 + x2) / (2 * dpi_scaling), (y1 + y2) / (2 * dpi_scaling)]

            x_c, y_c = coordinates
            x_c += monitor['left']
            y_c += monitor['top']

            points.append(Location(name, (x_c, y_c), monitor))

        return points

    # given a list of [x, y, w, h] rectangles and a canvas image to draw on, return an image with
    # all of those rectangles drawn
    def draw_rectangles(self, screenshot, results, monitor):
        if results is None:
            return screenshot
        for result in results:
            bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
            classes = np.array(result.boxes.cls.cpu(), dtype="int")
            for label, box in zip(classes, bboxes):
                # for box, label in zip(result.boxes.xyxy, result.boxes.cls):
                left, top, right, bottom = box

                x = int(left)
                y = int(top)
                w = (int(right) - int(left))
                h = int(bottom) - int(top)

                cv.rectangle(screenshot, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0),
                                     2)

                # Add label above the bounding box
                label = str(result.names[label.item()])
                font = cv.FONT_HERSHEY_SIMPLEX
                font_scale = 2
                font_thickness = 2
                label_size, _ = cv.getTextSize(label, font, font_scale, font_thickness)
                label_x = int(x + (w - label_size[0]) // 2)  # Convert to integer
                label_y = int(y - 10)  # Convert to integer and adjust this value as needed

                coordinate = ((x*2 + w)//2, (y*2 + h)//2)
                center = (((monitor['width']) * dpi_scaling) // 2, ((monitor['height']) * dpi_scaling) // 2)

                cv.line(screenshot, (int(center[0]), int(center[1])), (int(coordinate[0]), int(coordinate[1])), (0, 0, 255), 2)

                if label in ENEMIES:
                    cv.circle(screenshot, (int(coordinate[0]), int(coordinate[1])), MOB_RADIUS, (0, 0, 255), 2)

                cv.putText(screenshot, label, (label_x, label_y), font, font_scale, (0, 255, 0), font_thickness)

        return screenshot


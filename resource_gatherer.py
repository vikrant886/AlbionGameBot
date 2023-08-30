import random
import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt
import math

dpi_scale = 2
RADIUS = 210
ENEMIES = ['low mob', 'high mob', 'golem']


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    MINING = 3
    BACKTRACKING = 4


class AlbionBot:
    # constants
    INITIALIZING_SECONDS = 6
    MINING_SECONDS = 2
    MOVEMENT_STOPPED_THRESHOLD = 0.60
    IGNORE_RADIUS = 0
    TOOLTIP_MATCH_THRESHOLD = 0.80
    BACKTIP_MATCH_THRESHOLD = 0.73

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    click_history = []

    def __init__(self, window_offset, window_size, monitor):
        # create a thread lock object
        self.lock = Lock()

        self.monitor = monitor

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        # pre-load the needle image used to confirm our object detection
        self.tooltip = cv.imread('cursor/tooltip.png', cv.IMREAD_UNCHANGED)
        self.tooltip = cv.cvtColor(self.tooltip, cv.COLOR_RGBA2RGB)
        self.mask = cv.imread('cursor/mask.png', cv.IMREAD_UNCHANGED)
        self.mask = cv.cvtColor(self.mask, cv.COLOR_RGBA2RGB)

        self.back_tip = cv.imread('cursor/back_tip.png', cv.IMREAD_UNCHANGED)
        self.back_tip = cv.cvtColor(self.back_tip, cv.COLOR_RGBA2RGB)
        self.back_tip_mask = cv.imread('cursor/back_tip_mask.png', cv.IMREAD_UNCHANGED)
        self.back_tip_mask = cv.cvtColor(self.back_tip_mask, cv.COLOR_RGBA2RGB)

        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()

    def click_next_target(self):
        self.lock.acquire()
        targets = self.targets_ordered(self.targets)
        self.lock.release()
        print([t.name for t in targets])
        target_i = 0
        found_resource = False
        while not found_resource and target_i < len(targets):
            # if we stopped our script, exit this loop
            if self.stopped:
                break

            # load up the next target in the list and convert those coordinates
            # that are relative to the game screenshot to a position on our
            # screen
            target_pos = targets[target_i].coordinates
            screen_x, screen_y = target_pos
            # print('Moving mouse to x:{} y:{}'.format(screen_x, screen_y))

            # move the mouse
            self.lock.acquire()
            pyautogui.moveTo(x=screen_x, y=screen_y, duration=0.1)
            self.lock.release()
            # short pause to let the mouse movement complete and allow
            # time for the tooltip to appear
            sleep(.5)
            # confirm limestone tooltip
            # self.lock.acquire()
            if self.confirm_tooltip():
                # print('Click on confirmed target at x:{} y:{}'.format(screen_x, screen_y))
                found_resource = True
                # pyautogui.click()
                # save this position to the click history
                self.click_history.append(target_pos)
            target_i += 1
        # self.lock.release()
        return found_resource

    def have_stopped_moving(self):
        # if we haven't stored a screenshot to compare to, do that first
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False

        # compare the old screenshot to the new screenshot
        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        similarity = result[0][0]
        # print('Movement detection similarity: {}'.format(similarity))

        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            # pictures look similar, so we've probably stopped moving
            print('Movement detected stop')
            return True

        # looks like we're still moving.
        # use this new screenshot to compare to the next one
        self.movement_screenshot = self.screenshot.copy()
        return False

    def targets_ordered(self, targets):
        # our character is always in the center of the screen
        # print('target_ordering')

        center = (((self.monitor['width']) * dpi_scale) // 2, ((self.monitor['height']) * dpi_scale) // 2)

        targets.sort(key=lambda loc: loc.dist_from_center)

        def circle_line_segment_collision(circle_center, circle_radius, center_, line_end):
            line_vec = [line_end[0] - center_[0], line_end[1] - center_[1]]
            circle_to_line_vec = [circle_center[0] - center_[0], circle_center[1] - center_[1]]
            line_mag = math.sqrt(line_vec[0] ** 2 + line_vec[1] ** 2)
            line_unit = [line_vec[0] / line_mag, line_vec[1] / line_mag]
            dot_product = circle_to_line_vec[0] * line_unit[0] + circle_to_line_vec[1] * line_unit[1]

            # Find the closest point on the line segment to the circle center
            closest_point = [0, 0]
            if dot_product < 0:
                closest_point = center_
            elif dot_product > line_mag:
                closest_point = line_end
            else:
                closest_point = [center_[0] + line_unit[0] * dot_product,
                                 center_[1] + line_unit[1] * dot_product]
            # print("screenshot widht:" + str(self.screenshot.shape))
            # print("monitor width: " + str(self.monitor['width']))
            # print("circle center: " + str(circle_center))
            # print("closest point: " + str(closest_point))

            distance_to_line = math.sqrt(
                (circle_center[0] - closest_point[0]) ** 2 + (circle_center[1] - closest_point[1]) ** 2)

            # print("distance: " + str(distance_to_line))

            if distance_to_line <= circle_radius:
                return True
            else:
                return False

        def convert_to_screenshot_scale(coordinates):
            return ((coordinates[0] - self.monitor['left']) * dpi_scale,
                    (coordinates[1] - self.monitor['top']) * dpi_scale)

        # Filter out targets whose lines are colliding with the circle
        # print('first_filtering')
        filtered_targets = []

        mob_targets = []
        for target in targets:
            if target.name in ENEMIES:
                mob_targets.append(target)

        for target in targets:
            sleep(0.001)
            if target.name not in ENEMIES:

                line_end = convert_to_screenshot_scale(target.coordinates)

                append_required = True
                for mob in mob_targets:
                    print(mob.name)
                    print(target.name)
                    # print("line end in click: " + str(target.coordinates))
                    # print("line end in pixel: " + str(line_end))
                    mob_center = convert_to_screenshot_scale(mob.coordinates)
                    if not circle_line_segment_collision(mob_center, RADIUS, center, line_end):
                        filtered_targets.append(target)
                        append_required = False
                        break
                    else:
                        append_required = False
                        break
                if append_required:
                    filtered_targets.append(target)
        # print('second_filtering')
        # Filter out targets that are in the ENEMIES list
        # filtered_targets = [t for t in filtered_targets if t.name not in ENEMIES]

        return filtered_targets

    def confirm_tooltip(self):
        result = cv.matchTemplate(self.screenshot, self.tooltip, cv.TM_CCOEFF_NORMED, mask=self.mask)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        print(max_val)
        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            return True

        screenshot_data = self.screenshot
        cv.imwrite("/Users/premkumarsinha/Desktop/test/s.png", screenshot_data)
        # print('Tooltip not found.')
        return False

    def confirm_back_tip(self):
        result = cv.matchTemplate(self.screenshot, self.back_tip, method=cv.TM_CCORR_NORMED, mask=self.back_tip_mask)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        print(max_val)
        if max_val >= self.BACKTIP_MATCH_THRESHOLD:
            return True
        screenshot_data = self.screenshot
        cv.imwrite("/Users/premkumarsinha/Desktop/test/b.png", screenshot_data)
        # print('Tooltip not found.')
        return False

    def click_backtrack(self, targets):
        last_click = self.click_history.pop()
        my_pos = ((self.window_offset[0] * 2 + self.window_w) / 2, (self.window_offset[1] * 2 + self.window_h) / 2)
        back_x = (my_pos[0] + (my_pos[0] - last_click[0])*0.6)
        back_y = (my_pos[1] + (my_pos[1] - last_click[1])*0.6)


        # print("my pos: ",my_pos)

        def random_coordinates_around_base(X, Y, r):
            # Generate a random angle in radians (0 to 2*pi)
            angle = random.uniform(0, 2 * math.pi)

            # Generate a random distance from 0 to the radius r
            distance = random.uniform(0, RADIUS / dpi_scale)

            # Convert polar coordinates to Cartesian coordinates (x, y)
            x = X + distance * math.cos(angle)
            y = Y + distance * math.sin(angle)

            return x, y

        print('Backtracking to x:{} y:{}'.format(back_x, back_y))
        self.lock.acquire()
        # pyautogui.moveTo(x=back_x, y=back_y, duration=0.1)
        self.lock.release()
        # while not self.confirm_back_tip():
        #     x_, y_ = random_coordinates_around_base(back_x, back_y, 30)
        #     pyautogui.moveTo(x_, y_, duration=0.2)
        #     sleep(0.2)

        # pyautogui.click()

        # short pause to let the mouse movement complete
        sleep(3.5)

    def update_targets(self, targets, monitor):
        self.lock.acquire()
        self.monitor = monitor
        self.targets = targets
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run, daemon=True)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def resource_gatherer_main(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # print('initialitaion')
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    print('searching')
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                print('searching')
                # check the given click point targets, confirm a limestone deposit,
                # then click it.
                success = self.click_next_target()
                # if not successful, try one more time
                if not success:
                    success = self.click_next_target()

                # if successful, switch state to moving
                # if not, backtrack or hold the current position
                if success:
                    self.lock.acquire()
                    print('moving')
                    self.state = BotState.MOVING
                    self.lock.release()
                else:
                    # stay in place and keep searching
                    pass

            elif self.state == BotState.MOVING or self.state == BotState.BACKTRACKING:
                # print('moving')
                # see if we've stopped moving yet by comparing the current pixel mesh
                # to the previously observed mesh
                if not self.have_stopped_moving():
                    # wait a short time to allow for the character position to change
                    sleep(0.500)
                else:
                    # reset the timestamp marker to the current time. switch state
                    # to mining if we clicked on a deposit, or search again if we
                    # backtracked
                    if self.state == BotState.MOVING:
                        self.lock.acquire()
                        self.timestamp = time()
                        print('mining')
                        self.state = BotState.MINING
                        self.lock.release()
                    elif self.state == BotState.BACKTRACKING:

                        print('bactracking')
                        # print(self.click_history)
                        # print(len(self.click_history))
                        if len(self.click_history) > 0:
                            # self.lock.acquire()
                            self.click_backtrack(self.targets)
                        self.state = BotState.SEARCHING
                        # self.lock.release()

            elif self.state == BotState.MINING:
                # print('mining')
                # see if we're done mining. just wait some amount of time
                if time() > self.timestamp + self.MINING_SECONDS:
                    self.lock.acquire()
                    print('backtracking')
                    self.state = BotState.BACKTRACKING
                    self.lock.release()

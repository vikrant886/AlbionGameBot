from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.switch import Switch
from kivy.uix.label import Label
from kivy.uix.button import Button
import threading
from object_detector import perform_object_detection
from object_detector import stop
from movement_logic import movement_logic_main
from movement_logic import on_press
from pynput import keyboard


is_pre_alive=False
class ObjectDetectionThread(threading.Thread):
    def __init__(self):
        global  is_performing_object_detection
        super(ObjectDetectionThread, self).__init__()
        self.running = False
        # is_performing_object_detection=1

    def run(self):
        self.running = True
        if self.running:
            perform_object_detection()

    def stop(self):
        global  is_performing_object_detection
        stop()
        print("stopping")
        self.running = False
        # is_performing_object_detection=0

class MovementThread(threading.Thread):
    def __init__(self):
        super(MovementThread, self).__init__()
        self.move_run = False

    def run(self):
        self.move_run = True
        if self.move_run:
            movement_logic_main()
    def stop_move(self):
        self.move_run=False
        on_press(keyboard.Key.esc)



class SimpleSwitch(GridLayout):

    def __init__(self, **kwargs):
        super(SimpleSwitch, self).__init__(**kwargs)

        self.cols = 2

        # Adding labels and switches
        self.add_widget(Label(text="Bot Vision"))
        self.switch1 = Switch(active=False)
        self.add_widget(self.switch1)

        self.add_widget(Label(text="Bot movement"))
        self.switch2 = Switch(active=False)
        self.add_widget(self.switch2)


        # Adding Save button
        self.save_button = Button(text="Save", size_hint=(None, None), size=(100, 50))
        self.add_widget(self.save_button)

        # Bind the button to a callback function
        self.save_button.bind(on_press=self.save_status)

    def save_status(self, instance):
        first = self.switch1.active
        second = self.switch2.active
        object_detection_thread = ObjectDetectionThread()
        movement_thread=MovementThread()
        global is_pre_alive
        if first:
            if not is_pre_alive:
                object_detection_thread.start()
                is_pre_alive = True
        elif not first:
            if is_pre_alive:
                object_detection_thread.stop()
                is_pre_alive=False
        if second:
            movement_thread.start()
        elif not second:
            movement_thread.stop_move()





class MyApp(App):

    def build(self):
        return SimpleSwitch()


if __name__ == '__main__':
    MyApp().run()

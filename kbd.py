import os
from queue import Queue
import sys

from pynput import keyboard

from utils import Intervals
from base import BaseInputHandler


class InputHandler(BaseInputHandler):

    DOUBLE_TAP_INTERVAL = 0.10   # seconds
    LONG_PRESS_INTERVAL = 0.5    # seconds


    def __init__(self, command_set):
        super().__init__(command_set)
        self.timer = Intervals()
        self.q = Queue()

    def start(self):
        """
        Enter event loop, waiting for and acting upon key presses.
        This will block for ever.
        """
        keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release).start()

        self.set_echo(False)
        # enter event loop to handle keypresses as received.
        while True:
            ch = self.q.get()
            self.command_set.handle(ch)


    def flush_keys(self):
        """
        The buffer will have loads of presses in it. Terminate in 'enter',
        read the line and discard.
        """
        this_keyboard = keyboard.Controller()
        this_keyboard.press(keyboard.Key.enter)
        this_keyboard.release(keyboard.Key.enter)
        sys.stdin.readline()


    def set_echo(self, on=False):
        """
        Disable/enable echoing of input to screen
        """
        if on:
            os.system("stty > /dev/null")
        else:
            os.system("stty -echo")


    def on_press(self, key):
        ##
        ## BUG:
        ## This will start time, and put is in frame, when <SHIFT> (or other
        ## modifier) pressed. That will then ensure we ignore another keypress
        ## such as the actual character.

        delta = self.timer.start()
        if delta is None:
            return

        if delta < self.DOUBLE_TAP_INTERVAL:
            prefix = "double_"
        else:
            prefix = ""

        try:
            ch = key.char
            if key.char == '+':
                ch = "PLUS"
            elif key.char == '-':
                ch = "MINUS"

            self.q.put_nowait("{}{}".format(prefix, ch))

        except AttributeError:
            ch = None

            if key == keyboard.Key.space:
                ch = "SPACE"
            elif key == keyboard.Key.up:
                ch = "UP"
            elif key == keyboard.Key.down:
                ch = "DOWN"
            elif key == keyboard.Key.left:
                ch = "LEFT"
            elif key == keyboard.Key.right:
                ch = "RIGHT"

            elif key in [keyboard.Key.ctrl,
                         keyboard.Key.ctrl_r,
                         keyboard.Key.shift,
                         keyboard.Key.shift_r,
                         keyboard.Key.alt_gr,
                         keyboard.Key.alt,
                         keyboard.Key.alt_r]:
                self.timer.ignore_next()
                return

            if ch is not None:
                self.q.put_nowait("{}{}".format(prefix, ch))


    def on_release(self, key):
        delta = self.timer.stop()
        ch = None
        try:
            ch = key.char
            if ch == 'q':
                # Stop listener
                return False
        except AttributeError:
            if key == keyboard.Key.space:
                ch = "SPACE"
            elif key == keyboard.Key.up:
                ch = "UP"
            elif key == keyboard.Key.down:
                ch = "DOWN"
            elif key == keyboard.Key.left:
                ch = "LEFT"
            elif key == keyboard.Key.right:
                ch = "RIGHT"

        if delta is not None and delta >= self.LONG_PRESS_INTERVAL and ch is not None:
            self.q.put_nowait("long_{}".format(ch))




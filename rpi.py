"""
Input handler for Raspberry Pi with external switches (stomp box foot
switches)

Issues and features to consider:

    * de-bouncing is a problem. On my test momentary switch, the release
    * generates GPIO.RISING events even with a 0.1uF capacitor. Maybe
      try bigger capacitor? Different mix of capacitor and software
      debounce?
    * implement timer, as per keyboard input handler, for:
      - double tap
      - long press
    * may need to implement handler for latching switches, but not until
      the need arises
"""
from queue import Queue

import RPi.GPIO as GPIO

from looper import BaseInputHandler
import settings


GPIO.setmode(GPIO.BOARD)


class InputHandler(BaseInputHandler):
    def __init__(self, command_set):
        super().__init__(command_set)
        self.q = Queue()
        self.channel_map = {}

    def start(self):
        """
        Setup event handlers for switch input.

        Currently only coded for momentary switches; latching switches
        to come.

        Can't yet do double taps.
        """
        idx = 0
        for channel in settings.SWITCH_CHANNELS:
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(channel,
                                  GPIO.RISING,
                                  callback=self.handle_press,
                                  bouncetime=200)
            self.channel_map[channel] = idx
            idx += 1

        # process requests in the main thread, not on the event thread
        while True:
            ch = self.q.get()
            self.command_set.handle(ch)

    def handle_press(self, channel):
        """
        Handle button press events.
        """
        # convert channel to logical switch number (zero indexed)
        switch = self.channel_map[channel]

        # call appropriate command
        self.q.put(switch)

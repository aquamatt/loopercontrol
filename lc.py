#!/usr/bin/env python3
import optfn

from kbd import InputHandler
from looper import *
import settings
from utils import get_class_from_string


def run_controller(host, port, setup, nloops, channels_per_loop):
    """
    Initialise and run the SooperLooper controller
    """
    channel = Channel(host, port)

    looper = Looper(channel)
    # setup loops in SooperLooper
    # don't call this if you want to bind to already setup instance

    if setup:
        channel.clear_loops()

    for i in range(nloops):
        loop = Loop()
        looper.add_loop(loop, channels=channels_per_loop, master=True if i == 0 else False, create=setup)
        time.sleep(0.1)

    command_set = get_class_from_string(settings.COMMAND_SET)(looper)
    handler = get_class_from_string(settings.INPUT_HANDLER)(command_set)

    handler.start()


def cli_handler(host="localhost", port=9951, stereo=False,
                loops=2, nosetup=False):
    """
    Use:

    > ./lc.py [options]

    --host=<host>            - host running SooperLooper (default: localhost)
    --port=<port>            - SooperLooper port (default: 9951)
    --loops=<n>              - Number of loops to start (default: 2)
    --stero                  - Set if stereo is to be selected
    --nosetup                - Do not re-configure the looper
    --help -h                - Show this help
    """

    # ensure type is correct here
    port = int(port)
    loops = int(loops)
    setup = not nosetup
    run_controller(host, port, setup, loops, 2 if stereo else 1)


if __name__ == '__main__':
    optfn.run(cli_handler)

#!/usr/bin/env python3
import optfn

from kbd import InputHandler
from looper import *
import settings
from utils import get_class_from_string


def run_controller(host, port, nloops):
    """
    Initialise and run the SooperLooper controller
    """
    channel = Channel(host, port)

    # setup loops in SooperLooper
    # don't call this if you want to bind to already setup instance
    channel.clear_loops()
    looper = Looper(channel)
    for i in range(nloops):
        loop = Loop()
        looper.add_loop(loop, True if i == 0 else False)
        time.sleep(0.1)

    command_set = get_class_from_string(settings.COMMAND_SET)(looper)
    handler = get_class_from_string(settings.INPUT_HANDLER)(command_set)

    handler.start()


def cli_handler(host="localhost", port=9951,
                loops=2):
    """
    Use:

    > ./lc.py [options]

    --host=<host>            - host running SooperLooper (default: localhost)
    --port=<port>            - SooperLooper port (default: 9951)
    --loops=<n>              - Number of loops to start (default: 2)
    --help -h                - Show this help
    """

    # ensure type is correct here
    port = int(port)
    loops = int(loops)

    run_controller(host, port, loops)


if __name__ == '__main__':
    optfn.run(cli_handler)

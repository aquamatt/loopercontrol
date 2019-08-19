#!/usr/bin/env python3
import optfn

from commands import CommandSet
from kbd import InputHandler
from looper import *


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

    command_set = CommandSet(looper)
    handler = InputHandler(command_set)

    handler.start()


def cli_handler(host="localhost", port=9951,
                loops=2):

    """
    Use:

    > ./lc.py [options]

    --host=<host>            - host running SooperLooper (default: localhost)
    --port=<port>            - SooperLooper port (default: 9951)
    --loops=<n>              - Number of loops to start (default: 2)

    Output is sent to /tmp/ptrh.[out|err]
    """

    # ensure type is correct here
    port = int(port)
    loops = int(loops)

    run_controller(host, port, loops)


if __name__ == '__main__':
    optfn.run(cli_handler)

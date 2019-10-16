#!/usr/bin/env python3
import optfn
import sys

from looper import *
import settings
from utils import get_class_from_string


def run_controller(host, port, setup, nloops, channels_per_loop):
    """
    Initialise and run the SooperLooper controller
    """

    # @todo: this is a hangover from early days when this only controlled
    # SooperLooper and only via OSC. Could refactor this elsewhere.
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


def set_config(config):
    """
    From settings.CONFIG_SETS pull the config referenced by `config` and copy
    keys into the main space.
    """
    try:
        cfg = settings.CONFIG_SETS[config]
    except KeyError:
        print("Config {} is not defined in settings".format(config))
        sys.exit(1)

    for k, v in cfg.items():
        setattr(settings, k, v)


def show_configs():
    print("\nAvailable configurations are:\n")
    for name, config in settings.CONFIG_SETS.items():
        print("{}: \t{}".format(name, config['doc']))
    print()


def cli_handler(host="localhost", port=9951, stereo=False,
                loops=2, nosetup=False, config="default",
                udp_host=None, show_config=False):
    """
    Use:

    > ./lc.py [options]

    --host=<host>            - host running SooperLooper (default: localhost)
    --port=<port>            - SooperLooper port (default: 9951)
    --loops=<n>              - Number of loops to start (default: 2)
    --udp_host=<host>        - UDP host address to connect/bind to (default
                               in settings)
    --stero                  - Set if stereo is to be selected
    --nosetup                - Do not re-configure the looper
    --config=<config>        - Config set defined in settings (default: default)
    --show_config            - Show configurations available
    --help -h                - Show this help
    """

    if show_config is True:
        show_configs()
        sys.exit(0)

    # ensure type is correct here
    port = int(port)
    loops = int(loops)
    if udp_host is not None:
        settings.UDP_HOST = udp_host
    setup = not nosetup
    set_config(config)
    run_controller(host, port, setup, loops, 2 if stereo else 1)


if __name__ == '__main__':
    optfn.run(cli_handler)

import argparse

from . import configuration
from . import constants
from . import utils

def main(argv=None):
    """
    Run commands from configuration.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
        prog = constants.APPNAME,
    )
    parser.add_argument('config', nargs='+')
    parser.add_argument('--dry', action='store_true')
    args = parser.parse_args(argv)

    utils.raise_for_missing(args.config)

    commands = configuration.parse(args.config)
    if not commands:
        parser.error('No commands.')

    for command in commands:
        print(command.preview())
        if not args.dry:
            completed = command.run()

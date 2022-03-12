import argparse
import configparser
import subprocess

from pathlib import Path

APPNAME = 'simple_supervisor'

class SimpleSupervisorError(Exception):
    """
    Base for all explicitly raise errors here.
    """


class NoResultError(SimpleSupervisorError):
    """
    No results from iterable.
    """


class MultipleResultsError(SimpleSupervisorError):
    """
    More than one result from iterable.
    """


def one(iterable):
    """
    Iterable yields one and only one result.
    """
    try:
        item = next(iterable)
    except StopIteration:
        raise NoResultError
    try:
        next(iterable)
    except StopIteration:
        return item
    else:
        raise MultipleResultsError

def hasonlyone(iterable, items):
    """
    `iterable` has one and only one, item from `items` `in` it; if true, return
    the item.
    """
    filtered = (item for item in iterable if item in items)
    return one(filtered)

def main(argv=None):
    """
    Run commands from configuration.
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
        prog = APPNAME,
    )
    parser.add_argument('--config', nargs='+')
    parser.add_argument('--dry', action='store_true')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    if APPNAME not in cp:
        parser.error('Nothing configured to do.')

    appconfig = cp[APPNAME]

    for key in (key for key in appconfig if key.startswith('keys')):
        section = cp[appconfig[key]]

        command_key = hasonlyone(section, ('command', 'safer_command'))
        if command_key == 'safer_command':
            command = eval(section['safer_command'])
            run_kwargs = dict(
                capture_output = True,
                check = True, # raise for exit code
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
            )
            # TODO: do not permit overriding these kwargs?
        elif command_key == 'command':
            command = eval(section['command'])
            run_kwargs = dict()

        cwd = section.get('cwd')
        if cwd:
            cwd_path = Path(cwd)
        else:
            cwd_path = Path.cwd()
        if args.dry:
            preview = cwd_path / subprocess.list2cmdline(command)
            print(preview, run_kwargs)
        else:
            print(cwd_path)
            print(command)
            result = subprocess.run(command, cwd=cwd_path)
            print(result)

if __name__ == '__main__':
    main()

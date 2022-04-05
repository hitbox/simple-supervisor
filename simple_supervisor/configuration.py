import configparser

from itertools import tee

from . import constants
from . import exceptions
from . import models
from . import query
from . import utils

SIMPLE_GIT_PULL = f'{constants.APPNAME}.git_pull'

def parse_numbered_list(section, prefix, silent=False):
    """
    """
    keys1, keys2 = tee(query.prefixedkeys(section, prefix))

    # raise for invalid key name
    for key in keys1:
        if utils.is_numbered_key(key, prefix):
            continue
        if not silent:
            raise exceptions.ConfigError(
                f'Expected key name "{prefix}" followed only by digits. %r'
                % key)

    return ((key, section[key]) for key in keys2)

def has_simple_git_pull(cp):
    return SIMPLE_GIT_PULL in cp

def simple_git_pull(cp):
    """
    simplified git pull
    """
    git_pull_config = cp[SIMPLE_GIT_PULL]

    items = parse_numbered_list(git_pull_config, 'path')
    paths1, paths2 = tee(path for key, path in items)

    # raise for paths
    utils.raise_for_missing(paths1)

    # git pull on all paths
    for cwd_path in paths2:
        command = models.Command(['git', 'pull'], cwd = cwd_path)
        yield command


def parse(path):
    """
    """
    commands = []

    cp = configparser.ConfigParser()
    cp.read(path)

    if constants.APPNAME not in cp:
        raise exceptions.ConfigError('Missing section %r.' % constants.APPNAME)

    appconfig = cp[constants.APPNAME]

    if has_simple_git_pull(cp):
        for command in simple_git_pull(cp):
            commands.append(command)

    return commands

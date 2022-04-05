import os

from . import exceptions

def is_numbered_key(key, prefix):
    """
    """
    return key[len(prefix):].isdigit()

def raise_for_missing(paths):
    """
    Raise for missing files.
    """
    for path in paths:
        if not os.path.exists(path):
            raise exceptions.MissingFileError(
                'File does not exist. %r', path)

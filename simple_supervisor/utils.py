import os

from . import exceptions

def is_numbered_key(key, prefix):
    """
    String `key` is prefixed by `prefix` and immediately followed by a number.
    """
    return key.startswith(prefix) and key[len(prefix):].isdigit()

def raise_for_missing(paths):
    """
    Raise for missing files.
    """
    for path in paths:
        if not os.path.exists(path):
            raise exceptions.MissingFileError(
                'File does not exist. %r', path)

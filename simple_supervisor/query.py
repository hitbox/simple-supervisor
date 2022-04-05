from .exceptions import MultipleResultsError
from .exceptions import NoResultError

def hasonlyone(iterable, items):
    """
    `iterable` has exactly one item from `items` `in` it; if true, return the item.
    """
    filtered = (item for item in iterable if item in items)
    return one(filtered)

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
        # good, one and only one item next-ed from iterable
        return item
    else:
        raise MultipleResultsError

def prefixedkeys(iterable, prefix):
    """
    """
    return (key for key in iterable if key.startswith(prefix))

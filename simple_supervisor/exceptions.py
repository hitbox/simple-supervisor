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


class ConfigError(SimpleSupervisorError):
    """
    Config error.
    """


class MissingFileError(SimpleSupervisorError):
    """
    Missing file error.
    """

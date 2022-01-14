# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class NotYetBookable(Error):
    """Raised when the curse is not bookable yet, due to the 24h timeframe"""
    pass


class WrongProgram(Error):
    """Raised when the wrong program was selected"""
    pass


class WrongDatetime(Error):
    """Raised when the wrong date time was selected"""
    pass


class KnowElementError(Error):
    """Raised when we saw a know element error and want to exit gracefully"""
    pass

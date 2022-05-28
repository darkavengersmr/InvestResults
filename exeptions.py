class DBNoConnection(Exception):
    """Error connection to DB"""


class TooShortPassword(Exception):
    """Password is too short"""


class UserPasswordIsInvalid(Exception):
    """User password is invalid"""


class CategoryInUse(Exception):
    """Error deletion - category in use"""


class CategoryNotFound(Exception):
    """Error - category not found"""


class InvestmentNotFound(Exception):
    """Error - investment not found"""

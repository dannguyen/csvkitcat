
from csvkit.exceptions import ColumnIdentifierError, CustomException, RequiredHeaderError
from agate import DataTypeError



class ArgumentErrorTK(CustomException):
    """
    Exception raised when the user supplies an invalid column identifier.
    """
    pass


class InvalidAggregation(CustomException):
    pass

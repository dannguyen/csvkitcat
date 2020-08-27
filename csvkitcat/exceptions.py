
from csvkit.exceptions import CustomException
from agate import DataTypeError



class ArgumentErrorTK(CustomException):
    """
    Exception raised when the user supplies an invalid column identifier.
    """
    pass


from agate.aggregations import Count, Min, Max, MaxLength, Mean, Median, Mode, StDev, Sum
from csvkitcat import CSVKitcatUtil
from csvkitcat.exceptions import *

from collections import namedtuple
import csv
from io import StringIO

class AgatableUtil(CSVKitcatUtil):
    """
    This is just a placeholder class, meant to be subclassed by utils like
    csvpivot that rely specifically on agate.Table. Ideally, if we need features beyond
    agate.Table, the AgatableUtil placeholder provides a scaffold to substitute pandas or whatever
    """
    pass


Aggregates = (Count, Max, MaxLength, Min, Mean, Median, Mode, StDev, Sum)


AggArg = namedtuple('AggArg', ['foo', 'args', 'colname'], defaults=(None, None, None))


def get_agg(name: str) -> [type, bool]:
    try:
        x = next((a for a in Aggregates if a.__name__.lower() == name.lower()))
    except StopIteration as err:
        raise InvalidAggregation(f'Invalid aggregation: "{name}". Call `-a/--agg list` to get a list of available aggregations')
    else:
        return x

def parse_aggregate_string_arg(line:str, valid_columns:list = []) -> AggArg:
    """
    line looks like:
        - 'count'
        - 'count:col_name,other_arg'
        - 'Name of AggCount|count:col_name'
    """

    # first we parse out the name, if specified
    src = StringIO(line)
    *_cname, _x = next(csv.reader(src, delimiter='|'))  # _cname is either [] or ['Column Name']
    colname = _cname[0] if _cname else None

    _foo, *_y = next(csv.reader(StringIO(_x), delimiter=':'))
    foo = get_agg(_foo)

    args = next(csv.reader(StringIO(_y[0]))) if _y else []

    # if args[0] exists, assume it is a column identifier and
    # validate it
    if args and valid_columns:
        if args[0] not in valid_columns:
            raise ColumnIdentifierError(f"Expected column name '{args[0]}' to refer to a column for {foo.__name__} aggregation, but did not find it in table's list of column names: {valid_columns}")

    return AggArg(foo=foo, args=args, colname=colname)


def print_available_aggregates(outs):
    outs.write(f"List of aggregate functions:\n")
    for a in Aggregates:
        outs.write(f"- {a.__name__.lower()}\n")

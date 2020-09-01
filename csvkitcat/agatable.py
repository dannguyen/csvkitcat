from agate.aggregations import Count, Min, Max, MaxLength, Mean, Median, Mode, StDev, Sum
from csvkitcat import CSVKitcatUtil


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
    return next((a for a in Aggregates if a.__name__.lower() == name.lower()), False)

def parse_aggregate_string_arg(line:str) -> AggArg:
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

    return AggArg(foo=foo, args=args, colname=colname)



def print_available_aggregates(outs):
    outs.write(f"List of aggregate functions:\n")
    for a in Aggregates:
        outs.write(f"- {a.__name__.lower()}\n")

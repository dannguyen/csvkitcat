from csvkit.grep import FilteringCSVReader, pattern_as_function
from collections import defaultdict
from typing import List as typeList, Dict as typeDict, Tuple as typeTuple, Callable as typeCallable

class FilterMoreCSVReader(FilteringCSVReader):

    """just like FilteringCSVReader, just with patternlists instead of just patterns"""
    def __init__(self, reader, patternlists, all_column_names=[], header=True, any_match=False, inverse=False):
        super(FilteringCSVReader, self).__init__()

        self.reader = reader
        self.header = header

        if self.header:
            self.column_names = next(reader)

        self.all_column_names = all_column_names if all_column_names else self.column_names
        # if all_column_names:
        #     self.column_names = all_column_names

        self.any_match = any_match
        self.inverse = inverse
        self.patternlists = standardize_stuff(self.all_column_names, patternlists)

    def test_row(self, row):
        # for idx, test in self.patterns.items():
        for idx, tests in self.patternlists.items():
            for test in tests:
                try:
                    value = row[idx]
                except IndexError:
                    value = ''
                result = test(value)
                if self.any_match:
                    if result:
                        return not self.inverse  # True
                else:
                    if not result:
                        return self.inverse  # False

        if self.any_match:
            return self.inverse  # False
        else:
            return not self.inverse  # True


def standardize_stuff(all_column_names:typeList[str], patternlists:typeList[typeTuple[typeList[int], str]]) -> typeDict[typeList[int], typeList[typeCallable]]:
    r"""
    all_column_names example:
        ['name', 'surname', 'phone']

    patternlists example:

        [
            (['name', 'surname', 'phone'], r'\w+'),
            (['phone'], r'\d+'),
        ]

    Returns:
        {
            1: ['\w+'],
            2: ['\w+'],
            3: ['\w+', '\d+'],

        }

    where each pattern is a callable not a string
    """
    df = defaultdict(list)
    for colnames, pattern in patternlists:
        for k in colnames:
            idx = all_column_names.index(k)
            pfoo = pattern_as_function(pattern)
            df[idx].append(pfoo)
            # TODO: optimize by having patterns as functions
    return df



class regex_callable(object):

    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, arg):
        return self.pattern.search(arg)

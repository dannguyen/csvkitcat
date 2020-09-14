from csvkitcat import CSVKitUtility


class CSVKitcatUtil(CSVKitUtility):
    """
    slightly adjusted version of standard CSVKitUtility
    """


    def get_column_offset(self):
        if getattr(self.args, 'zero_based', None):
            if self.args.zero_based:
                return 0
            else:
                return 1
        else:
            return 1
    # dumb hack

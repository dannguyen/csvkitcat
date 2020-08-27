from csvkitcat import CSVKitcatUtil


class AgatableUtil(CSVKitcatUtil):
    """
    This is just a placeholder class, meant to be subclassed by utils like
    csvpivot that rely specifically on agate.Table. Ideally, if we need features beyond
    agate.Table, the AgatableUtil placeholder provides a scaffold to substitute pandas or whatever
    """
    pass



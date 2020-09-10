#!/usr/bin/env python3
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Test if we can make arguments optional"
    )

    parser.add_argument(
        "-E", "--expression", dest="expressions_list", action="append", nargs="*",
    )

    # parser.add_argument(
    #     "pattern",
    #     metavar="pattern",
    #     type=str,
    #     nargs="?",
    #     # default='hello',
    #     help="just a pattern",
    # )

    # parser.add_argument(
    #     "repl",
    #     metavar="repl",
    #     type=str,
    #     nargs="?",
    #     # default='world',
    #     help="and a repl",
    # )

    parser.add_argument(
        "file", metavar="input_file", type=str, nargs="?", help="and a file"
    )

    parser.add_argument("-l", "--love", type=str, default="LOVE")

    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    args = parser.parse_args()
    vargs = vars(args)

    if exes := vargs.pop("expressions_list", []):
        print("In expressions mode!")
        for e in exes:
            print(e)
    #            print(f"\t pattern: {p}   repl: {r}   columns: {c}")

    # if args.pattern and not args.file:
    #     args.file = args.pattern
    #     delattr(args, "pattern")
    #     delattr(args, "repl")

    # elif args.pattern and args.file:
    #     # this is bad!
    #     parser.error(
    #         f"""Got an unexpected positional argument; either:
    #         - More than 3 arguments for -E/--expr {exes[-1]}
    #         - Or, a PATTERN argument, which is invalid when using -E/--expr
    #     """
    #     )
    else:
        # print(f"No expressions: {args.expressions_list}")
        # the above will error out
        # AttributeError: 'Namespace' object has no attribute 'expressions_list'
        pass
    print("--------------------\n")

    print("Other arguments and options")
    for k, v in vargs.items():
        print(f"{k}: {v}")

    print("\n\n")
    print("and here are argv:")
    for i, arg in enumerate(sys.argv):
        print(f"{i}: {arg}")


if __name__ == "__main__":
    main()

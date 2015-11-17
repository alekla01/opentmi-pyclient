#!/usr/bin/env python

"""
MIT
"""

import sys
import optparse


def cmd_parser_setup():
    """! Configure CLI (Command Line OPtions) options
    @return Returns OptionParser's tuple of (options, arguments)
    @details Add new command line options
    """
    parser = optparse.OptionParser()

    parser.add_option('', '--version',
                      dest='version',
                      default=False,
                      action="store_true",
                      help='Prints package version and exits')

    (opts, args) = parser.parse_args()
    return (opts, args)


def mbedutf_main():
    """! Function used to drive CLI (command line interface) application
    @return Function exits with success-code
    @details Function exits back to command line with ERRORLEVEL
    """
    retcode = 0

    (opts, args) = cmd_parser_setup()

    if opts.version:
        import pkg_resources  # part of setuptools
        version = pkg_resources.require("tmt-client")[0].version
        print version
    else:
        # @todo something
        retcode = 1
        pass

    sys.exit(retcode)
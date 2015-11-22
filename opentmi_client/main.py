#!/usr/bin/env python

"""
MIT
"""

import sys
import json
import argparse
from opentmi_client import OpenTmiClient

def cmd_parser_setup():
    """! Configure CLI (Command Line Options) options
    @return Returns OptionParser's tuple of (options, arguments)
    @details Add new command line options
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--version',
                      dest='version',
                      default=False,
                      type=bool,
                      help='Prints package version and exits')

    parser.add_argument('--host',
                      dest='host',
                      default='localhost',
                      help='OpenTMI host, default: localhost')

    parser.add_argument('-p', '--port',
                      dest='port',
                      type=int,
                      default=3000,
                      help='OpenTMI port')

    parser.add_argument('--list',
                      dest='list',
                      type=bool,
                      default=False,
                      help='List something')
    parser.add_argument('--testcases',
                      dest='testcases',
                      default='',
                      help='Testcases')

    args = parser.parse_args()
    return args


def opentmi_client_main():
    """! Function used to drive CLI (command line interface) application
    @return Function exits with success-code
    @details Function exits back to command line with ERRORLEVEL
    """
    retcode = 0

    args = cmd_parser_setup()

    if args.version:
        import pkg_resources  # part of setuptools
        version = pkg_resources.require("opentmi-client")[0].version
        print version
    else:
        client = OpenTmiClient(host=args.host, port=args.port)
        if args.list:
            if args.testcases:
                print(json.dumps(client.get_testcases()))
        retcode = 1
        pass

    sys.exit(retcode)
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
                      action='store_true',
                      help='Prints package version and exits')

    parser.add_argument('--host',
                      dest='host',
                      default='localhost',
                      help='OpenTMI host, default: localhost')

    parser.add_argument('--json',
                        dest='json',
                        default=False,
                        action='store_true',
                        help='results as json')
    parser.add_argument('-p', '--port',
                      dest='port',
                      type=int,
                      default=3000,
                      help='OpenTMI port')

    parser.add_argument('--list',
                      dest='list',
                      action='store_true',
                      default=False,
                      help='List something')
    parser.add_argument('--testcases',
                      dest='testcases',
                      default='',
                      help='Testcases')
    parser.add_argument('--campaigns',
                      dest='campaigns',
                      default='',
                      help='Campaigns')

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
        print(version)
    else:
        client = OpenTmiClient(host=args.host, port=args.port)
        if args.list:
            if args.testcases:
                testcases = client.get_testcases()
                if args.json:
                    print(json.dumps(testcases))    
                for tc in testcases:
                    print(tc['tcid'])
            elif args.campaigns:
                campaigns = client.get_campaign_names()
                if args.json:
                    print(campaigns)
                else:
                    for campaign in campaigns:
                        print(campaign)

    sys.exit(retcode)
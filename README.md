# Python Client library for OpenTMI

This library purpose is to provide simple interface for OpenTMI -backend.
For example this can fetch existing test case meta information from OpenTMI and upload results to it.

## installation

`python setup.py install`

## Command Line Interface

Purpose is to provide simple Command line Interface to communicate with OpenTMI -backend

```
/> opentmi --help
usage: opentmi [-h] [--version VERSION] [--host HOST] [-p PORT] [--list LIST]
               [--testcases TESTCASES]

optional arguments:
  -h, --help            show this help message and exit
  --version VERSION     Prints package version and exits
  --host HOST           OpenTMI host, default: localhost
  -p PORT, --port PORT  OpenTMI port
  --list LIST           List something
  --testcases TESTCASES
```

## Python API

```
from opentmi_client import OpenTmiClient
client = OpenTmiClient()
campaigns = client.get_campaigns()
testcases = client.get_testcases()
client.sendResult()
```


LICENSE: GPLv3
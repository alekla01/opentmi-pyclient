# Python Client library for OpenTMI

This library purpose is to provide simple interface for OpenTMI -backend.
For example this can fetch existing test case meta information from OpenTMI and upload results to it.

## installation

`python setup.py install`

## Command Line Interface

Purpose is to provide simple Command line Interface to communicate with OpenTMI -backend
..Work in Progress..

## Python API

```
from opentmi_client import OpenTmiClient
client = OpenTmiClient()
campaigns = client.get_campaigns()
testcases = client.get_testcases()
client.sendResult()
```


LICENSE: GPLv3
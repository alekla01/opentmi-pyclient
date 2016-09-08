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

example:
```
opentmi --host localhost --port 3000 --list --testcases 1
```

## Python API

```
from opentmi_client.opentmi_client import OpenTmiClient
client = OpenTmiClient(host='127.0.0.1', port=3000) # defaults
campaigns = client.get_campaigns()
testcases = client.get_testcases()
result = {
  "tcid": "test-case",
  "campaign": "my-campaign",
  "exec": { 
    "verdict": "pass",
    "duration": "8",
  },
  "sut": {
    "gitUrl": "github.com/opentmi/opentmi",
    "commitId": "123",
  },
  "dut": {
    "type": "hw",
    "vendor": "ABC",
    "model": "platform#1",
    "sn": "123"
  }
}
client.upload_results(result) # require valid result json object or converter function
```

Alternative you can set `result_converter` and `testcase_converter` for OpenTmiClient constructor.
Converter functions will be used to convert application specific result object for opentmi suitable format. 

Suitable result schema is described [here](https://github.com/OpenTMI/opentmi/blob/master/app/models/results.js#L15).

Test case document schema is available [here](https://github.com/OpenTMI/opentmi/blob/master/app/models/testcase.js).

**notes**

* `tcid` -field have to be unique for each test cases. 
* There is couple mandatory fields by default: `tcid` and `exec.verdict`. Allowed values for result verdict is: `pass`, `fail`, `inconclusive`, `blocked` and `error`. `upload_results()` -function also create test case document if it doesn't exists in database. 


LICENSE: GPLv3

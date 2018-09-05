# Python Client library for OpenTMI

[![CircleCI](https://circleci.com/gh/OpenTMI/opentmi-pyclient/tree/master.svg?style=svg)](https://circleci.com/gh/OpenTMI/opentmi-pyclient/tree/master)
[![Coverage Status](https://coveralls.io/repos/github/OpenTMI/opentmi-pyclient/badge.svg)](https://coveralls.io/github/OpenTMI/opentmi-pyclient)

This is the Python client library for [OpenTMI](https://github.com/opentmi/opentmi).

## installation

To install, simply use `pip`:

`$ pip install --upgrade opentmi-client`

See the [Developers Guide](development.md) if you want to develop this library.

## Command Line Interface

Library provides Command line Interface to communicate with OpenTMI -backend

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
from opentmi_client import Client
client = Client('https://127.0.0.1')
print(client.get_campaigns())
print(client.get_testcases())
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

Alternative you can set `result_converter()` and `testcase_converter()` -functions in Client constructor.
Converter functions will be used to convert application specific result object for opentmi suitable format.

Suitable result schema is described [here](https://github.com/OpenTMI/opentmi/blob/master/app/models/results.js#L15).

Test case document schema is available [here](https://github.com/OpenTMI/opentmi/blob/master/app/models/testcase.js).

**notes**

* `tcid` -field have to be unique for each test cases.
* There is couple mandatory fields by default: `tcid` and `exec.verdict`. Allowed values for result verdict is: `pass`, `fail`, `inconclusive`, `blocked` and `error`. `upload_results()` -function also create test case document if it doesn't exists in database.


## LICENSE

[MIT](LICENSE)

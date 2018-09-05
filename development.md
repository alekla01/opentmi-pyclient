## Test

`python setup.py test`

## Compile documentation

```
sphinx-apidoc -o docs/_static opentmi_client
make -C docs html
```

## Releasing

CircleCI is configured to build release and publish automatically to pypi when release tag is added

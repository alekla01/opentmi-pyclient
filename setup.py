import os
from distutils.core import setup
from setuptools import find_packages

DESCRIPTION = "opentmi-client"
OWNER_NAMES = 'Jussi Vatjus-Anttila'
OWNER_EMAILS = 'jussiva@gmail.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='opentmi_client',
      version='0.2.0',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/OpenTMI/opentmi-client-python.git',
      packages=find_packages(exclude=['test', 'log', 'htmlcov']),
      package_data={'': ['tc_schema.json']},
      include_package_data=True,
      license="GPLv3",
      tests_require=["coverage"],
      test_suite = 'test',
      entry_points={
          "console_scripts": [
              "opentmi=opentmi_client:opentmiclient_main",
          ]
      },
      install_requires=[
          "requests",
          "jsonmerge"
      ]
    )

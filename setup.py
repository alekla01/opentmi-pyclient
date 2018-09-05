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
      version='0.3.2',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      url='https://github.com/OpenTMI/opentmi-pyclient.git',
      packages=find_packages(exclude=['test', 'log', 'htmlcov', 'docs']),
      include_package_data=True,
      license="MIT",
      tests_require=read('dev_requirements.txt').splitlines(),
      test_suite = 'test',
      entry_points={
          "console_scripts": [
              "opentmi=opentmi_client:opentmiclient_main",
          ]
      },
      install_requires=read('requirements.txt').splitlines(),
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ]
    )

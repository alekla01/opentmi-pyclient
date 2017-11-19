import os
import unittest
from logging import Logger
from opentmi_client.utils import get_logger

class TestLogger(unittest.TestCase):
    def test_default_logger(self):
        logger = get_logger()
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 1)

    def test_null_logger(self):
        logger = get_logger(name="new", level=None)
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 1)

if __name__ == '__main__':
    unittest.main()
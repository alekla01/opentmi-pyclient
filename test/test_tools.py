import os
import unittest
from opentmi_client.utils import is_object_id, resolve_host, archive_files


class TestTools(unittest.TestCase):
    def test_is_object_id(self):
        self.assertEqual(is_object_id(""), False)
        self.assertEqual(is_object_id("asd"), False)
        self.assertEqual(is_object_id(None), False)
        self.assertEqual(is_object_id(1), False)
        self.assertEqual(is_object_id("1234567890abcdef78901234"), True)

    def test_resolve_host(self):
        self.assertEqual(resolve_host("1.2.3.4"), "http://1.2.3.4")
        self.assertEqual(resolve_host("1.2.3.4", 80), "http://1.2.3.4")
        self.assertEqual(resolve_host("1.2.3.4", 8000), "http://1.2.3.4:8000")
        self.assertEqual(resolve_host("1.2.3.4:3000"), "http://1.2.3.4:3000")
        self.assertEqual(resolve_host("http://1.2.3.4"), "http://1.2.3.4")
        self.assertEqual(resolve_host("https://1.2.3.4"), "https://1.2.3.4")
        self.assertEqual(resolve_host("https://mydomain"), "https://mydomain")
        self.assertEqual(resolve_host("https://1.2.3.4:3000"), "https://1.2.3.4:3000")
        self.assertEqual(resolve_host("https://1.2.3.4", 3000), "https://1.2.3.4:3000")

    def test_archive(self):
        zip = 'temp.zip'
        archive_files(['test_tools.py'], zip, os.path.dirname(__file__))
        self.assertTrue(os.path.exists(zip))
        os.remove(zip)

if __name__ == '__main__':
    unittest.main()

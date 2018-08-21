import unittest
from mock import MagicMock, patch, call
from opentmi_client.api import Client, create
from opentmi_client.utils import TransportException, OpentmiException
from opentmi_client.transport.transport import Transport


def mocked_post(*args, **kwargs):
    if args[1].get("exception") == "TransportException":
        raise TransportException("")
    elif args[1].get("exception") == 'OpentmiException':
        raise OpentmiException("")
    elif args[1].get("status_code") == 404:
        return None
    return args[1]

def mocked_put(*args, **kwargs):
    if args[1].get("exception") == "TransportException":
        raise TransportException("")
    elif args[1].get("exception") == 'OpentmiException':
        raise OpentmiException("")
    elif args[1].get("status_code") == 404:
        return None
    return args[1]

def mocked_get(*args, **kwargs):
    if kwargs.get('params', {}).get('tcid') == "notfound":
        return []
    return [{"tcid": "abc"}]

def mock_transport(transport):
    transport.set_token =  MagicMock()
    transport.set_host =  MagicMock()
    transport.get_json = MagicMock()
    transport.post_json = MagicMock()
    transport.put_json = MagicMock()


class TestClient(unittest.TestCase):

    def test_create(self):
        client = create()
        self.assertIsInstance(client, Client)

    def test_token(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.set_token('test')
        tr_mock.set_token.assert_called_once_with("test")

    def test_login(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.login("user", "passwd")
        tr_mock.post_json.assert_called_once_with("http://127.0.0.1/login",
                                                  {"username": "user", "password": "passwd"})

    def test_logout(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.logout()
        tr_mock.set_token.assert_called_once_with(None)

    def test_version(self):
        client = Client()
        self.assertEqual(client.get_version(), 0)

    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_build(self, mock_post):
        client = Client()
        self.assertDictEqual(client.upload_build({}), {})
        mock_post.assert_called_once_with("http://127.0.0.1/api/v0/duts/builds", {})

    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_build_exceptions(self, mock_post):
        client = Client()
        self.assertEqual(client.upload_build({"exception": "TransportException"}), None)
        self.assertEqual(client.upload_build({"exception": "OpentmiException"}), None)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_results_new_test(self, mock_post, mock_get):
        client = Client()
        tc_data = {"tcid": "notfound"}
        client.upload_results(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "notfound"})
        mock_post.assert_has_calls([
            call("http://127.0.0.1/api/v0/testcases", tc_data),
            call("http://127.0.0.1/api/v0/results", tc_data, files=None)])

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_results_update_test(self, mock_post, mock_get):
        client = Client()
        tc_data = {"tcid": "abc"}
        client.upload_results(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "abc"})
        mock_post.assert_called_once_with("http://127.0.0.1/api/v0/results", tc_data, files=None)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    def test_get_test(self, mock_get):
        client = Client()
        tc_data = {"tcid": "abc %s"}
        client.get_testcases(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "abc %s"})



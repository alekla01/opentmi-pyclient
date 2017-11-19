import sys
import unittest
from mock import MagicMock, patch, call, Mock
from opentmi_client.cli.main import opentmiclient_main, OpentTMIClientCLI


def mocked_get_list(*args, **kwargs):
    return [{"tcid": "b", "name": "c"}]


class TestCli(unittest.TestCase):
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_help(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "--help"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_version(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "version"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_version_verbose(self, mock_exit, mock_stdout):
        fake_args = ["opentmi", "-v", "version"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_verbose_levels(self, mock_exit, mock_stdout):

        fake_args = ["opentmi", "-v", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vvv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

        fake_args = ["opentmi", "-vvvv", "version"]
        with patch('sys.argv', fake_args):
            cli = OpentTMIClientCLI()

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get_list)
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_testcases(self, mock_exit, _mock_stdout, mock_list):
        fake_args = ["opentmi", "list", "--testcases"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get_list)
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_results(self, mock_exit, _mock_stdout, mock_list):
        fake_args = ["opentmi", "list", "--campaigns"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get_list)
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_testcases_json(self, mock_exit, _mock_stdout, mock_list):
        fake_args = ["opentmi", "list", "--testcases", "--json"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get_list)
    @patch('sys.stdout', new_callable=Mock())
    @patch("sys.exit")
    def test_list_results_json(self, mock_exit, _mock_stdout, mock_list):
        fake_args = ["opentmi", "list", "--campaigns", "--json"]
        with patch('sys.argv', fake_args):
            opentmiclient_main()
        mock_exit.assert_called_with(0)

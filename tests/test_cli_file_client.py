"""
test_cli_file_client.py - Unit tests for the `file_client.py` CLI application.
                          These tests verify the functionality of the `stat`
                          and `read` commands for both REST and gRPC backends,
                          including error handling and non-zero exit codes on failure.

@author: Kristijan <kristijan.sarin@gmail.com>
"""

import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from file_client import file_client

class TestFileClient(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('file_client.requests.get')
    def test_rest_stat_success(self, mock_get):
        # Simulate a successful REST response for metadata
        mock_get.return_value.json.return_value = {
            'name': 'example.txt',
            'size': 1234,
            'mimetype': 'text/plain',
            'create_datetime': '2024-01-01T12:00:00'
        }
        mock_get.return_value.status_code = 200
        result = self.runner.invoke(file_client, ['stat', '123', '--backend', 'rest'])
        self.assertIn("File Metadata:", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch('file_client.requests.get')
    def test_rest_stat_not_found(self, mock_get):
        # Simulate a 404 error for missing file
        mock_get.return_value.status_code = 404
        result = self.runner.invoke(file_client, ['stat', '123', '--backend', 'rest'])
        self.assertIn("File not found", result.output)
        self.assertNotEqual(result.exit_code, 0)  # Expect non-zero exit code

    @patch('file_client.grpc.insecure_channel')
    def test_grpc_stat_success(self, mock_channel):
        # Simulate a successful gRPC response for metadata
        mock_stub = MagicMock()
        mock_channel.return_value.__enter__.return_value = mock_stub
        mock_stub.Stat.return_value = MagicMock(
            name="example.txt", size=1234, mimetype="text/plain", create_datetime="2024-01-01T12:00:00"
        )
        result = self.runner.invoke(file_client, ['stat', '123', '--backend', 'grpc'])
        self.assertIn("File Metadata:", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch('file_client.grpc.insecure_channel')
    def test_grpc_stat_not_found(self, mock_channel):
        # Simulate a gRPC NOT_FOUND error
        mock_channel.side_effect = grpc.RpcError("NOT_FOUND")
        result = self.runner.invoke(file_client, ['stat', '123', '--backend', 'grpc'])
        self.assertIn("File not found", result.output)
        self.assertNotEqual(result.exit_code, 0)  # Expect non-zero exit code

    def test_stat_output_to_file(self):
        # Test `stat` command output to a file
        with patch('file_client.requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                'name': 'example.txt',
                'size': 1234,
                'mimetype': 'text/plain',
                'create_datetime': '2024-01-01T12:00:00'
            }
            mock_get.return_value.status_code = 200
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(file_client, ['stat', '123', '--backend', 'rest', '--output', 'output.txt'])
                with open('output.txt', 'r') as f:
                    content = f.read()
                self.assertIn("File Metadata:", content)
                self.assertEqual(result.exit_code, 0)

if __name__ == '__main__':
    unittest.main()

import unittest
import json
import tempfile
import datetime
import logging
from requests import Session
from requests.exceptions import Timeout, RequestException
from unittest.mock import patch, MagicMock
from speed_test_nokia_gateway import SpeedTestNokiaGateway, SpeedTestNokiaGatewayCsvWriter, requests


class TestTmobileNokiaGatewayAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.endpoint_url: str = 'http://localhost:8080'
        self.test_username: str = 'admin'
        self.test_password: str = 'super_secure_password'

    def setUp(self) -> None:
        self.test_agent: SpeedTestNokiaGateway = SpeedTestNokiaGateway(
            self.endpoint_url, self.test_username, self.test_password)

    @patch.object(Session, 'get')
    @patch.object(Session, 'post')
    def test_get_cell_status_success(self, mock_post, mock_get) -> None:
        five_g_metrics, four_g_metrics = \
            self._run_get_cell_status(mock_get, mock_post, 'cell_status_app-response.json')

        self.assertEqual('B71', four_g_metrics['band'])
        self.assertEqual('61', four_g_metrics['cell_id'])
        self.assertEqual('879386', four_g_metrics['enbid'])
        self.assertEqual('310260225122877', four_g_metrics['ecgi'])

        self.assertEqual('', five_g_metrics['band'])
        self.assertEqual('', five_g_metrics['cell_id'])
        self.assertEqual('', five_g_metrics['enbid'])
        self.assertEqual('', five_g_metrics['ecgi'])

    @patch.object(Session, 'get')
    @patch.object(Session, 'post')
    def test_get_cell_status_success_with_5g(self, mock_post: MagicMock, mock_get: MagicMock) -> None:
        five_g_metrics, four_g_metrics = \
            self._run_get_cell_status(mock_get, mock_post, 'cell_status_app-response-with-5g.json')

        # Additional assertions.
        self.assertEqual('B2', four_g_metrics['band'])
        self.assertEqual('11', four_g_metrics['cell_id'])
        self.assertEqual('879386', four_g_metrics['enbid'])
        self.assertEqual('310260225122827', four_g_metrics['ecgi'])

        self.assertEqual('n71', five_g_metrics['band'])
        self.assertEqual('11', five_g_metrics['cell_id'])
        self.assertEqual('879386', four_g_metrics['enbid'])
        self.assertEqual('310260225122827', five_g_metrics['ecgi'])

    def _run_get_cell_status(self, mock_get: MagicMock, mock_post: MagicMock, return_data: str):
        # log in
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # download
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        with open(return_data, 'r') as json_file:
            # Prepare the mocked json object to return to the caller.
            mock_get_response.json.return_value = json.load(json_file)

            four_g_metrics, five_g_metrics = self.test_agent.get_cell_status()

        # Assertions
        mock_post.assert_called_once()
        mock_get.assert_called_once()
        mock_get_response.json.assert_called_once()

        return five_g_metrics, four_g_metrics

    @patch.object(Session, 'post')
    def test_cell_status_app_wrong_username_password(self, mock_post: MagicMock):
        # log in
        mock_post_response = MagicMock()
        mock_post_response.status_code = 401
        mock_post.return_value = mock_post_response

        self.test_agent.username = 'i_am_admin'
        self.test_agent.password = 'wrong password'

        with self.assertRaises(RequestException):
            self.test_agent.get_cell_status()

    @patch.object(Session, 'get')
    @patch.object(Session, 'post')
    def test_get_cell_status_exception_happened(self, mock_post: MagicMock, mock_get: MagicMock) -> None:
        # log in
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        # Force a Timeout exception internally..
        mock_get.side_effect = Timeout

        four_g_metrics, five_g_metrics = self.test_agent.get_cell_status()

        # Assertions
        for metrics in [four_g_metrics, five_g_metrics]:
            self.assertEqual('', metrics['band'])
            self.assertEqual('', metrics['cell_id'])
            self.assertEqual('', metrics['rsrp'])
            self.assertEqual('', metrics['rsrq'])
            self.assertEqual('', metrics['rssi'])
            self.assertEqual('', metrics['snr'])
            self.assertEqual('', metrics['ecgi'])
            self.assertEqual('', metrics['enbid'])

    @patch('speed_test_nokia_gateway.speedtest.Speedtest.upload')
    @patch('speed_test_nokia_gateway.speedtest.Speedtest.download')
    @patch('speed_test_nokia_gateway.speedtest.Speedtest.get_best_server')
    def test_speed_test_success(self, mock_speedtest_get_best_server: MagicMock, mock_speedtest_download: MagicMock,
                                mock_speedtest_upload: MagicMock):
        mock_speedtest_get_best_server.return_value = {'latency': 12.0}
        mock_speedtest_download.return_value = 8.0 * 1000000
        mock_speedtest_upload.return_value = 1.9 * 1000000

        ping_ms, download_mbps, upload_mbps, timestamp = self.test_agent.perform_internet_speed_test()

        # Assertions
        mock_speedtest_get_best_server.assert_called_once()
        mock_speedtest_download.assert_called_once()
        mock_speedtest_upload.assert_called_once()

        # Cannot return real values because Speedtest.results is an instance variable and not a method.
        self.assertEqual(12.0, ping_ms)
        self.assertEqual(8.0, download_mbps)
        self.assertEqual(1.9, upload_mbps)
        self.assertIsNotNone(timestamp)

    def test_csv_output(self):
        with tempfile.NamedTemporaryFile(mode='w') as tmp_file:
            csv_writer: SpeedTestNokiaGatewayCsvWriter = SpeedTestNokiaGatewayCsvWriter(tmp_file.name)
            csv_writer.add_run_output(
                52.0,
                10.0,
                2.0,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %z'),
                SpeedTestNokiaGateway.BASE_TOWER_METRICS,
                SpeedTestNokiaGateway.BASE_TOWER_METRICS
            )

            logging.debug(tmp_file.name)

        # TODO add assertions.




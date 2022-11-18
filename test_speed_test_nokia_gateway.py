import unittest
import json
import tempfile
import datetime
import logging
from requests.exceptions import Timeout
from unittest.mock import patch, MagicMock
from speed_test_nokia_gateway import SpeedTestNokiaGateway, SpeedTestNokiaGatewayCsvWriter, requests


class TestTmobileNokiaGatewayAPI(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.endpoint_url = 'http://localhost:8080'

    def setUp(self) -> None:
        self.test_agent = SpeedTestNokiaGateway(self.endpoint_url)

    @patch('speed_test_nokia_gateway.requests')
    def test_radio_status_success(self, mock_requests) -> None:
        # Prepare the mocked json object to return to the caller.
        mock_response = MagicMock()
        mock_response.status_code = 200
        with open('fastmile_radio_status_web_app-response.json', 'r') as json_file:
            mock_response.json.return_value = json.load(json_file)
            mock_requests.get.return_value = mock_response

            four_g_metrics, five_g_metrics = self.test_agent.get_radio_status()

        # Assertions
        mock_response.json.asset_called_once()
        mock_response.get.asset_called_once()

        self.assertEqual('B71', four_g_metrics['band'])
        self.assertEqual('285', four_g_metrics['cell_id'])

        self.assertEqual('', five_g_metrics['band'])
        self.assertEqual('', five_g_metrics['cell_id'])

    @patch.object(requests, 'get')
    def test_radio_status_exception_happened(self, mock_get) -> None:
        # Force a Timeout exception internally..
        mock_get.side_effect = Timeout

        four_g_metrics, five_g_metrics = self.test_agent.get_radio_status()

        # Assertions
        for metrics in [four_g_metrics, five_g_metrics]:
            self.assertEqual('', metrics['band'])
            self.assertEqual('', metrics['cell_id'])
            self.assertEqual('', metrics['rsrp'])
            self.assertEqual('', metrics['rsrq'])
            self.assertEqual('', metrics['rssi'])
            self.assertEqual('', metrics['snr'])

    @patch('speed_test_nokia_gateway.speedtest.Speedtest.upload')
    @patch('speed_test_nokia_gateway.speedtest.Speedtest.download')
    @patch('speed_test_nokia_gateway.speedtest.Speedtest.get_best_server')
    def test_speed_test_success(self, mock_speedtest_get_best_server, mock_speedtest_download, mock_speedtest_upload):
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





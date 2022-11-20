import requests
from requests.exceptions import RequestException
import speedtest
import tzlocal
import logging
import datetime
import csv
from typing import Any, Optional, Dict, Tuple, List


class SpeedTestNokiaGateway:
    """
    Performs a speed test using the Speedtest module. The information logged includes tower metrics
    from the T-mobile Nokia Gateway for contextual debugging of the service's throughput.
    """

    DEFAULT_HTTP_REQUEST_TIMEOUT: int = 5

    THROUGHPUT_METRIC_NAMES: List[str] = [
        'timestamp',
        'ping',
        'download',
        'upload'
    ]

    BASE_TOWER_METRIC_NAMES: List[str] = [
        'rsrp',
        'rsrq',
        'rssi',
        'snr',
        'band',
        'cell_id',
        'ecgi',
        'enbid'
    ]

    BASE_TOWER_METRICS: Dict[str, str] = {key: '' for key in BASE_TOWER_METRIC_NAMES}

    def __init__(self, root_endpoint_url: str, username: str, password: str):
        self.root_endpoint_url: str = root_endpoint_url
        self.radio_status_endpoint_url: str = self.root_endpoint_url + '/fastmile_radio_status_web_app.cgi'
        self.login_url = self.root_endpoint_url + '/login_app.cgi'
        self.cell_status_url = self.root_endpoint_url + '/cell_status_app.cgi'

        self.username = username
        self.password = password

    def get_cell_status(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        with requests.session() as t_session:
            # Log in to the trashcan.
            login_response: requests.Response = t_session.post(self.login_url, data={
                'name': self.username,
                'pswd': self.password
            })

            # Wrong username and/or password?
            if login_response.status_code != 200:
                raise RequestException(login_response.text)

            else:
                # Let's get the data from the admin-only page.
                return self._get_radio_status(t_session)
                # No log out? We're relying on the trashcan to clean up the session.

    def perform_speed_test_with_tower_metrics(self) -> \
            Tuple[Optional[float], Optional[float], Optional[float], str, Dict[str, str], Dict[str, str]]:
        """
        Query the T-mobile gateway for the tower metrics, then immediately do a speed test.
        :return: the throughput stats and tower metrics.
        """

        four_g_metrics, five_g_metrics = self.get_cell_status()
        ping_ms, download_mbps, upload_mbps, timestamp = self.perform_internet_speed_test()

        return ping_ms, download_mbps, upload_mbps, timestamp, four_g_metrics, five_g_metrics

    def perform_internet_speed_test(self) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
        """
        Performs a speed test of the internet connection.

        :return: Tuple with the following information. None is returned if the speed test failed.
            float: Download speed in Mbps.
            float: Upload speed in Mbps.
            float: Ping time in ms.
        """
        ping_ms: Optional[float] = None
        download_mbps: Optional[float] = None
        upload_mbps: Optional[float] = None

        try:
            # TODO use UTC.
            exec_timestamp: str = datetime.datetime.now(tzlocal.get_localzone()).strftime('%Y-%m-%d %H:%M:%S %Z')

            # Run speedtest: ping, download, upload.
            transfer_agent: speedtest.Speedtest = speedtest.Speedtest(secure=True)

            best_server: Dict[str, Any] = transfer_agent.get_best_server()
            ping_ms = float(best_server['latency'])

            download_mbps: float = transfer_agent.download()
            download_mbps = round(download_mbps / 1000000, 2)

            upload_mbps: float = transfer_agent.upload()
            upload_mbps = round(upload_mbps / 1000000, 2)

        except Exception as e:
            logging.exception(e)

        return ping_ms, download_mbps, upload_mbps, exec_timestamp

    def _get_radio_status(self, t_session: requests.Session) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Gets the tower metrics from the Nokia Gateway's RESTful API.

        :return: The metrics for 4G LTE and 5G. The attributes per tower are listed in BASE_TOWER_METRICS.
        """

        four_g_metrics: Dict[str, str]
        five_g_metrics: Dict[str, str]
        response_json: Any = None

        try:
            response: requests.Response = t_session.get(
                self.cell_status_url, timeout=SpeedTestNokiaGateway.DEFAULT_HTTP_REQUEST_TIMEOUT)

            response_json: Any = response.json()

            # Make sure there is data in request_json
            if response_json:
                four_g_metrics, five_g_metrics = SpeedTestNokiaGateway._extract_tower_stats(response_json)

        except Exception as e:
            logging.exception(e)

        finally:
            if response_json is None:
                four_g_metrics, five_g_metrics = SpeedTestNokiaGateway._extract_tower_stats(None)

        # Return all signal metrics
        return four_g_metrics, five_g_metrics

    @staticmethod
    def _extract_tower_stats(response_json: Optional[dict]) -> Tuple[Dict[str, str], Dict[str, str]]:
        four_g_metrics: Dict[str, str] = SpeedTestNokiaGateway.BASE_TOWER_METRICS.copy()
        five_g_metrics: Dict[str, str] = SpeedTestNokiaGateway.BASE_TOWER_METRICS.copy()

        # Extract 4G data - bands, tower, rsrp, rsrq, rssi, sinr
        if response_json and 'cell_stat_lte' in response_json:
            four_g_metrics = {
                'rsrp':     str(response_json['cell_stat_lte'][0].get('RSRPCurrent', '')),
                'rsrq':     str(response_json['cell_stat_lte'][0].get('RSRQCurrent', '')),
                'rssi':     str(response_json['cell_stat_lte'][0].get('RSSICurrent', '')),
                'snr':      str(response_json['cell_stat_lte'][0].get('SNRCurrent', '')),
                'band':     str(response_json['cell_stat_lte'][0].get('Band', '')),
                'cell_id':  str(response_json['cell_stat_lte'][0].get('Cellid', '')),
                'ecgi':     str(response_json['cell_stat_lte'][0].get('ECGI', '')),
                'enbid':    str(response_json['cell_stat_lte'][0].get('eNBID', ''))
            }

        # Extract 5G data - bands, tower, rsrp, rsrq, rssi, sinr
        if response_json and 'cell_stat_5G' in response_json:
            five_g_metrics = {
                'rsrp':     str(response_json['cell_stat_5G'][0].get('RSRPCurrent', '')),
                'rsrq':     str(response_json['cell_stat_5G'][0].get('RSRQCurrent', '')),
                'rssi':     str(response_json['cell_stat_5G'][0].get('RSSICurrent', '')),
                'snr':      str(response_json['cell_stat_5G'][0].get('SNRCurrent', '')),
                'band':     str(response_json['cell_stat_5G'][0].get('Band', '')),
                'cell_id':  str(response_json['cell_stat_5G'][0].get('Cellid', '')),
                'ecgi':     str(response_json['cell_stat_5G'][0].get('ECGI', '')),
                'enbid':    str(response_json['cell_stat_5G'][0].get('eNBID', ''))
            }

        return four_g_metrics, five_g_metrics


class SpeedTestNokiaGatewayCsvWriter:
    """
    Writes the output of the SpeedTestNokiaGateway into a CSV.
    """

    FOUR_G_METRIC_NAMES: List[str] = ['4g_' + col for col in SpeedTestNokiaGateway.BASE_TOWER_METRIC_NAMES]

    FIVE_G_METRIC_NAMES: List[str] = ['5g_' + col for col in SpeedTestNokiaGateway.BASE_TOWER_METRIC_NAMES]

    ORDERED_COLUMN_NAMES = \
        SpeedTestNokiaGateway.THROUGHPUT_METRIC_NAMES + \
        FOUR_G_METRIC_NAMES + \
        FIVE_G_METRIC_NAMES

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path

    def add_run_output(self, ping_ms: Optional[float], download_mbps: Optional[float], upload_mbps: Optional[float],
                       timestamp: str, four_g_metrics: Dict[str, str], five_g_metrics: Dict[str, str]) -> None:
        """
        Writes a row to the output file.

        :param ping_ms: ping time in milliseconds.
        :param download_mbps: download throughput in Mbps.
        :param upload_mbps: upload throughput in Mbps.
        :param timestamp: time when the speed test was started.
        :param four_g_metrics: tower metrics for 4G LTE.
        :param five_g_metrics: tower metrics for 5G.
        :return: None
        """

        with open(self.log_file_path, 'a', newline='') as output_csv:
            csv_writer: csv.DictWriter = \
                csv.DictWriter(output_csv, fieldnames=SpeedTestNokiaGatewayCsvWriter.ORDERED_COLUMN_NAMES)

            if output_csv.tell() == 0:
                csv_writer.writeheader()

            # Assemble the row.
            row: Dict[str] = {
                'timestamp': timestamp,
                'ping': ping_ms,
                'download': download_mbps,
                'upload': upload_mbps,
            }
            row.update({'4g_' + key: value for key, value in four_g_metrics.items()})
            row.update({'5g_' + key: value for key, value in five_g_metrics.items()})

            csv_writer.writerow(row)

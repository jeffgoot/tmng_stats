import argparse
from typing import Dict
from speed_test_nokia_gateway import SpeedTestNokiaGateway, SpeedTestNokiaGatewayCsvWriter


def main():
    default_endpoint_url: str = 'http://192.168.12.1:80/'
    default_log_file_path: str = './speed_test_nokia_gateway.csv'

    # Gather the CLI arguments.
    args: Dict[str, str] = parse_arguments(default_endpoint_url, default_log_file_path)
    endpoint_url: str = args['endpoint']
    log_file_path: str = args['logfile']
    username: str = args['username']
    password: str = args['password']

    tool: SpeedTestNokiaGateway = \
        SpeedTestNokiaGateway(root_endpoint_url=endpoint_url, username=username, password=password)

    # Let's do it!
    ping_ms, download_mbps, upload_mbps, timestamp, four_g_metrics, five_g_metrics = \
        tool.perform_speed_test_with_tower_metrics()

    SpeedTestNokiaGatewayCsvWriter(log_file_path).add_run_output(
        ping_ms, download_mbps, upload_mbps, timestamp, four_g_metrics, five_g_metrics)


def parse_arguments(default_endpoint_url, default_log_file_path) -> Dict[str, str]:
    arg_parser = argparse.ArgumentParser()

    # Add the arguments to the parser
    arg_parser.add_argument('-e', '--endpoint', required=False, default=default_endpoint_url,
                            help='The root endpoint URL of the T-mobile Nokia Gateway. Default: %(default)s.')
    arg_parser.add_argument('-f', '--logfile', required=False, default=default_log_file_path,
                            help='The log file path. Default: %(default)s.')
    arg_parser.add_argument('-u', '--username', required=True, help='The admin username to use.')
    # XXX This is a security issue; the password will show up in `ps`. This will have to do for now.
    arg_parser.add_argument('-p', '--password', required=True, help='The admin password to use.')

    args: Dict[str, str] = vars(arg_parser.parse_args())

    return args


if __name__ == "__main__":
    main()


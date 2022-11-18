from speed_test_nokia_gateway import SpeedTestNokiaGateway


if __name__ == '__main__':
    SpeedTestNokiaGateway(root_endpoint_url='http://localhost:8080').get_radio_status()


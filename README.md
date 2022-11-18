# Speed Test: T-mobile Nokia Gateway
## Overview
This tool is used to speed test an internet connection using the [speedtest-cli API](https://github.com/sivel/speedtest-cli), and include the tower metrics from the T-mobile Nokia Gateway as part of the logged CSV output. It is assumed that the internet connection of the host device is through the T-mobile Nokia Gateway.

The information is being used as part of an ongoing effort to improve our T-mobile Home Internet setup (antenna, direction, etc.)

## Versions
``ng_speedtest-cli`` is used and was tested only with Python 3.9.

## Usage
Under the covers, the [speedtest-cli API](https://github.com/sivel/speedtest-cli) library is used in performing the speed test. However, this tool logs the throughput results and the tower metrics in a CSV file directly. It deviates from [speedtest-cli API](https://github.com/sivel/speedtest-cli), which outputs the results to ``stdout``.

``ng_speedtest-cli.py`` can be executed without any parameters with assumptions on the URL of the of the T-mobile Nokia Gateway and on the location of the output file.
```shell
python ng_speedtest-cli.py 
```
The full description of the parameters and the default value of each parameter are described below.
```shell
$ python ng_speedtest-cli.py -h
usage: ng_speedtest-cli.py [-h] [-u ENDPOINT] [-f LOGFILE]

optional arguments:
  -h, --help            show this help message and exit
  -u ENDPOINT, --endpoint ENDPOINT
                        The root endpoint URL of the T-mobile Nokia Gateway. Default: http://192.168.12.1:80/.
  -f LOGFILE, --logfile LOGFILE
                        The log file path. Default: ./speed_test_nokia_gateway.csv.

```

# Disclaimer
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
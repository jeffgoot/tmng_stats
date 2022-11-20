# Speed Test: T-mobile Nokia Gateway
## Overview
This tool is used to speed test an internet connection using the [speedtest-cli API](https://github.com/sivel/speedtest-cli), and include the tower metrics from the T-mobile Nokia Gateway as part of the logged CSV output. It is assumed that the internet connection of the host device is through the T-mobile Nokia Gateway.

The information is being used as part of an ongoing effort to improve our T-mobile Home Internet setup (antenna, direction, etc.)

### Output Example
```shell
timestamp,ping,download,upload,4g_rsrp,4g_rsrq,4g_rssi,4g_snr,4g_band,4g_cell_id,5g_rsrp,5g_rsrq,5g_rssi,5g_snr,5g_band,5g_cell_id
2022-11-18 22:29:30 ,97.956,14.55,2.41,-108,-17,-77,0,B71,285,-32768,-32768,,-32768,,
```
Using ``csvkit`` to display the row in json format:
```shell
[
    {
        "timestamp": "2022-11-18T22:29:30",
        "ping": 97.956,
        "download": 14.55,
        "upload": 2.41,
        "4g_rsrp": -108.0,
        "4g_rsrq": -17.0,
        "4g_rssi": -77.0,
        "4g_snr": false,
        "4g_band": "B71",
        "4g_cell_id": 285.0,
        "5g_rsrp": -32768.0,
        "5g_rsrq": -32768.0,
        "5g_rssi": null,
        "5g_snr": -32768.0,
        "5g_band": null,
        "5g_cell_id": null
    }
]
```

## Versions
``ng_speedtest-cli`` is used and was tested only with Python 3.9.

## Installation
1. Clone the repo.
2. Create the virtual environment and install the requirements.
   ```shell
   # Download the code.
   cd ~
   git clone https://github.com/jeffgoot/tmng_stats
   cd ~/tmng_stats/
   
   # Set up the environment.
   python3 -m venv .venv
   source .venv/bin/activate   
   pip install -r requirements.txt
   ```
3. To install the script as a cron job, use the following in your crontab file:
   ```
   SHELL=/bin/bash
   5,20,35,50 * * * * cd ~/tmng_stats/ && source ~/tmng_stats/.venv/bin/activate && python ng_speedtest-cli.py -f ~/tmng_stats/speed_test_nokia_gateway.csv
   ```

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
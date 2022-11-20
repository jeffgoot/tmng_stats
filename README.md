# Speed Test: T-mobile Nokia Gateway
## Overview
This tool is used to speed test an internet connection using the [speedtest-cli API](https://github.com/sivel/speedtest-cli), and include the tower metrics from the T-mobile Nokia Gateway as part of the logged CSV output. It is assumed that the internet connection of the host device is through the T-mobile Nokia Gateway.

The information is being used as part of an ongoing effort to improve our T-mobile Home Internet setup (antenna, direction, etc.)

### Output Example
```shell
timestamp,ping,download,upload,4g_rsrp,4g_rsrq,4g_rssi,4g_snr,4g_band,4g_cell_id,4g_ecgi,4g_enbid,5g_rsrp,5g_rsrq,5g_rssi,5g_snr,5g_band,5g_cell_id,5g_ecgi,5g_enbid
2022-11-19 23:03:17 EST,50.64,14.06,2.92,-107,-14,-80,4,B71,61,310260225122877,879386,-32768,-32768,,-32768,,,,
```
Using ``csvkit`` to display the row in json format:
```shell
[
    {
        "timestamp": "2022-11-19 23:03:17 EST",
        "ping": 50.64,
        "download": 14.06,
        "upload": 2.92,
        "4g_rsrp": -107.0,
        "4g_rsrq": -14.0,
        "4g_rssi": -80.0,
        "4g_snr": 4.0,
        "4g_band": "B71",
        "4g_cell_id": 61.0,
        "4g_ecgi": 310260225122877.0,
        "4g_enbid": 879386.0,
        "5g_rsrp": -32768.0,
        "5g_rsrq": -32768.0,
        "5g_rssi": null,
        "5g_snr": -32768.0,
        "5g_band": null,
        "5g_cell_id": null,
        "5g_ecgi": null,
        "5g_enbid": null
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
3. To install the script as a cron job and run it every 15 minutes, use the following in your crontab file. 
   ```
   SHELL=/bin/bash
   5,20,35,50 * * * * (cd ~/tmng_stats/ && source ~/tmng_stats/.venv/bin/activate && python ng_speedtest-cli.py -f ~/tmng_stats/speed_test_nokia_gateway.csv) >> /tmp/ng_speedtest-cli.cron.log 2>&1
   ```

## Usage
Under the covers, the [speedtest-cli API](https://github.com/sivel/speedtest-cli) library is used in performing the speed test. However, this tool logs the throughput results and the tower metrics in a CSV file directly. It deviates from [speedtest-cli API](https://github.com/sivel/speedtest-cli), which outputs the results to ``stdout``.

``ng_speedtest-cli.py`` requires the T-mobile Nokia Gateway admin ``username`` and ``password``, but can make assumptions on the URL of the gateway and on the location of the output file. **Note that the password will show up in `ps`.** This will have to do for now. 
```shell
python ng_speedtest-cli.py -u youradminusername -p yourpassword
```
The full description of the parameters are below.
```shell
usage: ng_speedtest-cli.py [-h] [-e ENDPOINT] [-f LOGFILE] -u USERNAME -p PASSWORD

optional arguments:
  -h, --help            show this help message and exit
  -e ENDPOINT, --endpoint ENDPOINT
                        The root endpoint URL of the T-mobile Nokia Gateway. Default: http://192.168.12.1:80/.
  -f LOGFILE, --logfile LOGFILE
                        The log file path. Default: ./speed_test_nokia_gateway.csv.
  -u USERNAME, --username USERNAME
                        The admin username to use.
  -p PASSWORD, --password PASSWORD
                        The admin password to use.
```

# Disclaimer
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
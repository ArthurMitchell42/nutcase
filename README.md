<h1>NUTCase</h1>
<h2>A Network UPS Tools (NUT) exporter to pass data to Prometheus and any JSON compatible application.</h2>
<h3><b>Key features:</b>
<ul>
  <li>Supports pulling data from a NUT server and formatting the UPS status for the <a href="https://prometheus.io/">Prometheus</a> logging system</li>
  <li>Supports formatting the UPS status as JSON for use with the beautiful <a href="https://gethomepage.dev">HomePage</a> app.</li>
  <li>The JSON output can be used with <a href="https://github.com/louislam/uptime-kuma">Uptime Kuma</a> and other reporting, alarming and monitoring apps.</li>
  <li>Provides diagnostic information and usage information.</li>
</ul>
</h3>
Please see:

The docker container:
> https://hub.docker.com/repository/docker/kronos443/nutcase

Source code:
> https://github.com/ArthurMitchell42/nutcase

<h2>Supported Architectures</h2>
<p>
Currently supports AMD64,ARM64 (ARM64V8) (suitable for running on docker under Raspberry PI with a 64-bit OS such as Raspberry PI OS 64-bit and Ubuntu 64-bit) & ARM32 V7 (armhf) (suitable for running on docker under Raspberry PI 32-bit OS)    
<br>

<table>
<thead>
<tr bgcolor="lightblue"><th align="center">Architecture</th>
<th>Tag</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center">AMD64</td>
<td>latest-amd64 For PC and Synology DSM</td>
</tr>
<tr>
<td align="center">ARM32V7 (armhf 32-bit)</td>
<td>latest-arm32v7 For Raspberry PI with a 32-bit OS</td>
</tr>
<tr>
<td align="center">ARM64V8 (ARM64)</td>
<td>arm64v8-latest. For Raspberry PI with a 64-bit OS (RaspberryPI OS 64-bit or Ubuntu 64-bit</td>
</tr>
</tbody></table>

> [!WARNING]
> For security reasons, going forward I'll be focusing on 64-bit containers only.

<h2>History</h2>
<table>
<thead>
<tr bgcolor="lightblue"><th align="center">Date</th>
<th>Version</th>
<th>Notes</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left">01/12/2023</td>
<td align="left">0.1.0</td>
<td align="left">Initial release.</td>
</tr>
</tbody></table>

<h2>Preparation and Application Setup</h2>
<p>
<h3>Your UPS system should be set up</h3>
<ol>
  <li>Your UPS should be connected to the machine you intend to have as the NUT server.</li>
  <li>The NUT server software should be installed and the UPS should be configured correctly.</li>
</ol>
<p>You can verify if this is correctly setup by using:</p>

<code>    telnet server-ip server-port</code><br>

and typing <code>VER</code> at the command line followed by <code>LIST UPS</code>. If the server is correctly configured you should get the version information of the server followed by a list of UPS's served by the machine. The result should that look something like this:<br>
```
  VER
    DSM7-1-1-42930-workplus-version2-repack-42930-220712
  LIST UPS
    BEGIN LIST UPS
    UPS ups "Description unavailable"
    END LIST UPS
```
This example output is from a Synology DSM 7.1 NAS. The name `ups` is not configurable and neither is the decsription [^1]

> [^1]: <i>without SSH'ing into the system and editing config files.</i>

> [!IMPORTANT]
> Your NUT server must be functioning before trying to run NUTCase or you will only recieve errors.

<h3>Setup the NUTCase docker container</h3>
<ol start="3">
  <li>Create the logging directory on the mapped docker share directory.</li>
  <li>Add the container to your system and start.</li>
</ol>
</p>

<h2>Usage</h2>
<p>
Create you container locally by either:
<br>
<h3>Docker CLI</h3>

```
docker run -d \
        --name NUTCase \
        -v /path/to/config:/config \
        -e TZ=Europe/London  \
        -p 9995:9995 \
        --restart always \
        kronos443/nutcase:latest
```

<h3>Docker Compose</h3>
The minimal configuration:<br>

> [!TIP]
> This assumes you have set the appropriate variables for docker compose

```
---
version: '3.9'
services:
  nutcase:
    image: kronos443/nutcase:latest
    container_name: NUTCase
    restart: always  # always or unless-stopped    
    user: "$PUID:$PGID"
    ports:
      - "$NUTEXPORT_PORT:9995"
    volumes:
      - '$DOCKER_DIR/nutcase:/config'
    environment:
      TZ: $TZ
```

> [!TIP]
> To help disgnostics and see what information the server is returning about the UPS you can use optional variables such as LOG_LEVEL.

```
---
version: '3.9'
services:
  nutcase:
    image: kronos443/nutcase:latest
    container_name: NUTCase
    restart: always  # always or unless-stopped    
    user: "$PUID:$PGID"
    ports:
      - "$NUTEXPORT_PORT:9995"
    volumes:
      - '$DOCKER_DIR/nutcase:/config'
    environment:
      TZ: $TZ
      # LOG_LEVEL - DEBUG INFO WARNING ERROR CRITICAL & FATAL are the options
      LOG_LEVEL: INFO  
      LOG_REQUESTS_DEBUG: False
      LOG_FILE=your-file-name.log
      ENV LOG_REQUESTS: True
      LOG_REQUESTS_DEBUG: False
      ORDER_METRICS: True
    healthcheck:
      test: wget --spider -q  http://localhost:$NUTEXPORT_PORT/help
      interval: 3m30s
      timeout: 10s
      retries: 2
      start_period: 30s
```

> [!NOTE]
> The log files will rotate when the reach **250KB** and up to 5 versions will be kept with the extensions <i>.log.1, .log.2, .log.3, .log.4, .log.5</i>

<h2>Parameters</h2>
<p>
The parameters available are as follows:

> [!IMPORTANT]
> When setting the LOG_LEVEL to DEBUG you may find that the log fills up quite quickly. I suggest to only use this level during set up diagnosing connectivity issues

<br>
<table>
<thead>
<tr><th align="center">Parameter</th>
<th>Function</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><b>Volume mapping</b><br>/path/to/config:/config</td>
<td>The directory on your host that is shared with the container. The log file will be generated here.<br><i><b>Required</b></i></td>
</tr>
<tr>
<td align="left"><b>Environment variable</b><br>LOG_FILE</td>
<td>Changes the name of the logfile.<br><i><b>Optional</b></i> <i>Default: NUTCase.log</i></td>
</tr>
<tr>
<td align="left"><b>Environment variable</b><br>LOG_REQUESTS</td>
<td>Controls whether each HTTP request to NUTCase is recorded in the logfile.<br><i><b>Optional</b></i> <i>Options: true false - Default: true</i></td>
</tr>
<tr>
<td align="left"><b>Environment variable</b><br>LOG_REQUESTS_DEBUG</td>
<td>Controls whether details of each HTTP request to NUTCase is recorded in the logfile. This can be verbose and is intended for detailed investigations only.<br><i><b>Optional</b></i> <i>Options: true false - Default: false</i></td>
</tr>
<tr>
<td align="left"><b>Environment variable</b><br>ORDER_METRICS</td>
<td>Controls whether the metrics are reported in the same order as the HON95 container send them to Prometheus. Otherwise the variables are reported in the order the server sends them.<br><i><b>Optional</b></i> <i>Options: true false - Default: true</i></td>
</tr>
<tr>
<td align="left"><b>Environment variable</b><br>PORT</td>
<td>Sets the port that NUTCase binds to. This is generally only required if you set the container network mode to ***host*** since in bridge mode the port mapping controls which port is mapped.<br><i><b>Optional</b></i> <i>Default: 9995</i></td>
</tr>
</tr>
<td align="left"><b>Environment variable</b><br>TZ</td>
<td>Time zone, e.g. Europe/London.<br><i><b>Optional</b></i> but specifying this means the log times will be in the local timezone rather than UT</td>
</tr>
</tbody></table>
</p>

<p><b>If you find this container useful then please consider</b> <a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8">buying me a coffee by following this link or scanning the QR below.</a> :)</p>

<a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8"> <img src="http://www.ajwm.uk/dockerdonate.jpg" alt="Please consider donating" width="120" height="120"> </a>

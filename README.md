<h1>NUTCase</h1>

[<img src="https://img.shields.io/badge/paypal-donate-blue.svg?logo=paypal&style=for-the-badge">](https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8)
[![Release](https://img.shields.io/github/release/ArthurMitchell42/nutcase.svg?logo=github&style=for-the-badge)](https://github.com/ArthurMitchell42/nutcase/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/kronos443/nutcase/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/kronos443/nutcase?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)
[![Docker Stars](https://img.shields.io/docker/stars/kronos443/nutcase?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)
[![Docker Build](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml)
[![Docker build and push](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-buildpush.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-buildpush.yml)

### V0.2.0 Beta is ready for download with [new features](https://github.com/ArthurMitchell42/nutcase/discussions/5)

<h2 id="introduction">A Network UPS Tools (NUT) and APC daemon exporter to pass data to Prometheus and any JSON compatible applications</h2>
<h3 id="key-features">Key features</h3>
<h4>
<ul>
  <li>Supports pulling data from a NUT server and formatting the UPS status for the <a href="https://prometheus.io/">Prometheus</a> logging system</li> as text
  <li>Supports pulling data from both <b>NUT and APC daemon servers</b> and formatting the UPS status to JSON</li>
  <li>JSON formatting is compatible with the beautiful <a href="https://gethomepage.dev">HomePage</a> app.</li>
  <li>The JSON output can be used with <a href="https://github.com/louislam/uptime-kuma">Uptime Kuma</a> and other reporting, alarming and monitoring apps.</li>
  <li>Provides diagnostic information and usage information.</li>
</ul>
</h4>
<h3 id="contents">Contents</h3>
  
- [Introduction](#introduction)
  - [Key features](#key-features)
  - [Contents](#contents)
  - [Links & References](#links-refs)
- [Supported Architectures](#architectures)
- [History & Versions](#history)
- [Preparation and Application Setup](#preparation)
  - [Your UPS system](#preparation-system)
  - [The NUTCase docker container](#preparation-docker)
- [NUTCase Usage](#nutcase-useage)
  - [Docker CLI](#nutcase-useage-docker-cli)
  - [Docker Compose](#nutcase-useage-docker-comp)
- [End-points to Access NUTCase](#endpoints)
  - [Metrics & Text](#endpoints-metrics)
  - [The JSON End-point](#endpoints-json)
  - [Diagnosics](#endpoints-diag)
    - [The log End-point](#endpoints-log)
    - [The help End-point](#endpoints-help)
    - [The raw End-point](#endpoints-raw)
- [Using NUTCase](#using-nutcase)
  - [Prometheus](#using-nutcase-prometheus)
  - [HomePage](#using-nutcase-homepage)
- [Parameters](#parameters)
- [Credits](#credits)
- [Support](#support)

<h3 id="links-refs">Links & References</h3>

The docker container:
> https://hub.docker.com/repository/docker/kronos443/nutcase

Source code:
> https://github.com/ArthurMitchell42/nutcase

The Wiki for usage information and advice:
> https://github.com/ArthurMitchell42/nutcase/wiki

<h3 id="architectures">Supported Architectures</h3>
<p>
Currently supports 'AMD64', 'ARM64 (ARM64V8)' (suitable for running on docker under Raspberry PI with a 64-bit OS such as Raspberry PI OS 64-bit and Ubuntu 64-bit) & 'ARM32 V7 (armhf)' (suitable for running on docker under Raspberry PI 32-bit OS)    
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
<td>latest-arm32v7 For Raspberry PI with a 32-bit OS :warning:</td>
</tr>
<tr>
<td align="center">ARM64V8 (ARM64)</td>
<td>arm64v8-latest. For Raspberry PI with a 64-bit OS (RaspberryPI OS 64-bit or Ubuntu 64-bit</td>
</tr>
</tbody></table>

> [!WARNING]
> For security reasons, going forward I'll be focusing on 64-bit containers only.

[Contents](#contents)

<h3 id="history">History & Versions</h3>
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

[Contents](#contents)

<h3 id="preparation">Preparation and Application Setup</h3>
<p>
<h4 id="preparation-system">Your UPS system</h3>
Your UPS system should be set up and working.
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

<h4 id="preparation-docker">The NUTCase docker container</h3>
To setup the NUTCase docker container:
<ol start="3">
  <li>Create the logging directory on the mapped docker share directory.</li>
  <li>Add the container to your system and start.</li>
</ol>
</p>

[Contents](#contents)

<h3 id="nutcase-useage">NUTCase Usage</h3>

For details on useage please see [Running the NUTCase container](https://github.com/ArthurMitchell42/nutcase/wiki/Running-the-NUTCase-container). 

Create you container locally by either:

<h4 id="nutcase-useage-docker-cli">Docker CLI</h4>

```shell
docker run -d \
        --name NUTCase \
        -v /path/to/config:/config \
        -e TZ=Europe/London  \
        -p 9995:9995 \
        --restart always \
        kronos443/nutcase:latest
```

<h4 id="nutcase-useage-docker-comp">Docker Compose</h4>
The minimal configuration:<br>

> [!TIP]
> This assumes you have set the appropriate variables for docker compose

```yaml
---
version: '3.9'
services:
  nutcase:
    image: kronos443/nutcase:latest
    container_name: NUTCase
    restart: always  # always or unless-stopped    
    ports:
      - "$NUTEXPORT_PORT:9995"
    volumes:
      - '$DOCKER_DIR/nutcase:/config'
    environment:
      TZ: $TZ
```

> [!TIP]
> To help disgnostics and see what information the server is returning about the UPS you can use optional variables such as LOG_LEVEL.

[Contents](#contents)

<h3 id="parameters">Parameters</h3>
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

[Contents](#contents)

<h3 id="endpoints">End-points to Access NUTCase</h3>
<h4 id="endpoints-metrics">Metrics & Text</h4>
The metrics end point returns data suitable for Prometheus. If called from a browser then plain text is returned.
Calling this end-point usually uses the _target_ parameter as this is the usual method used by Prometheus. However it can also be called with _addr_ and _port_.
Examples are:

```
http://<nutcase-ip>:<port>/metrics?target=A.B.C.D      Specifying the address of the server, assuming the default port, 3493.
http://<nutcase-ip>:<port>/metrics?target=A.B.C.D:P    Specifying the address of the server and the port.
http://<nutcase-ip>:<port>/metrics?addr=A.B.C.D&port=P Specifying the address of the server and the port (P).
```

<h4 id="endpoints-json">The JSON End-point</h4>
The JSON end point returns JSON data suitable for HomePage or any app that can use the formatted JSON data.
Calling this end-point can use the _target_ parameter or the _addr_ and _port_ parameters.
Examples are:

```
http://<nutcase-ip>:<port>/json?target=A.B.C.D      Specifying the address of the server, assuming the default port, 3493.
http://<nutcase-ip>:<port>/json?target=A.B.C.D:P    Specifying the address of the server and the port.
http://<nutcase-ip>:<port>/json?addr=A.B.C.D&port=P Specifying the address of the server and the port (P).
```
[Contents](#contents)

<h3 id="endpoints-diag">Diagnostics</h3>
<h4 id="endpoints-log">The log End-point</h4>
The log end point returns a list of the last 20, or other requested number, of lines from the log file to speed diagnostics.

```
http://<nutcase-ip>:<port>/log           View the last 20 lines of the log file.
http://<nutcase-ip>:<port>/log?lines=30  Optionally view a given number of last lines of the log file.
```

<h4 id="endpoints-help">The help End-point</h4>
The help end point returns basic usage information and advice.

```
http://<nutcase-ip>:<port>/help
```

<h4 id="endpoints-raw">The raw End-point</h4>
The raw end point returns JSON data with extra diagnostic information and is intended for support and debugging.

```
http://<nutcase-ip>:<port>/raw?target=A.B.C.D      Specifying the address of the server, assuming the default port, 3493.
http://<nutcase-ip>:<port>/raw?target=A.B.C.D:P    Specifying the address of the server and the port.
http://<nutcase-ip>:<port>/raw?addr=A.B.C.D&port=P Specifying the address of the server and the port (P).
```

[Contents](#contents)

<h3 id="using-nutcase">Using NUTCase</h3>
<h4 id="using-nutcase-prometheus">Prometheus</h4>
To configure Prometheus to scrape NUTCase for metrics set up the following in your prometheus.yml file

```yaml
# prometheus.yml
global:
    scrape_interval: 10s
scrape_configs:
    - job_name: 'nut'
      scrape_interval: 30s
      scrape_timeout: 10s
      static_configs:
      # Insert NUT server address here
      - targets: ['10.0.10.9:3493']
      metrics_path: /metrics
      relabel_configs:
        - source_labels: [__address__]
          target_label: __param_target
        - source_labels: [__param_target]
          target_label: instance
        - target_label: __address__
          # Insert NUT exporter address here
          replacement: 10.0.10.9:9995
```

This example makes the assumption that the UPS server is running on 10.0.10.9, port 3493 and that NUTCase is hosted on 10.0.10.9 port 9995. Change as appropriate for your system.

<h4 id="using-nutcase-homepage">HomePage</h4>
To configure HomePage to display information from NUTCase up the following in your services.yaml file

![Screenshot of code](https://github.com/ArthurMitchell42/nutcase/blob/1211bd35a422d9c3e6bcf10cdf3be337acb43927/resources/homepage-code.jpg)

```yaml
- UPS-Other:
    - DS9 UPS:
        href: http://10.0.10.9:9995/log?lines=40
        description: DS9 UPS
        icon: ups.png
        widget:
            type: customapi
            url: http://10.0.10.9:9995/json?target=10.0.10.9:3493
            refreshInterval: 60000 # In milliseconds, set to ~60s
            method: GET
            mappings:
                - field: 
                    ups:
                      input.voltage
                  label: Input
                  format: text
                  suffix: V
                - field: 
                    ups: battery.runtime
                  label: Runtime
                  format: float
                  scale: 1/60
                  suffix: Min
                - field: 
                    ups:
                      ups.load
                  label: Power
                  format: text
                  suffix: "%"
                - field: 
                    ups:
                      ups.status
                  label: Status
                  format: text
                  remap:
                    - value: "OL"
                      to: On-Line
                    - value: "OB"
                      to: Discharge
```

This will give a display as follows

![Screenshot of HomePage](https://github.com/ArthurMitchell42/nutcase/blob/1211bd35a422d9c3e6bcf10cdf3be337acb43927/resources/homepage-image.jpg)

You can customise which parameters of the UPS appear by selecting them from the JSON data supplied by the JSON end point, see above.

[Contents](#contents)

<h3 id="credits">Credits</h3>
<p>
Credit goes to the HON95 container upon which this is heavily based on.
</p>

[Contents](#contents)

<h3 id="support">Support</h3>
<p><b>If you find this container useful then please consider</b> <a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8">buying me a coffee by following this link or scanning the QR below.</a> :smiley: :coffee:</p>

<a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8"> <img src="http://www.ajwm.uk/dockerdonate.jpg" alt="Please consider donating" width="120" height="120"> </a>

[Contents](#contents)


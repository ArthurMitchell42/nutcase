<h1>NUTCase</h1>

[<img src="https://img.shields.io/badge/paypal-donate-blue.svg?logo=paypal&style=for-the-badge">](https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8)
[![Release](https://img.shields.io/github/release/ArthurMitchell42/nutcase.svg?logo=github&style=for-the-badge)](https://github.com/ArthurMitchell42/nutcase/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/kronos443/nutcase/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/kronos443/nutcase?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)
[![Docker Stars](https://img.shields.io/docker/stars/kronos443/nutcase?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)
[![Docker Build](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml)
[![Docker build and push](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-buildpush.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-buildpush.yml)

> [!TIP]
> ### News: [Beta 2 of V0.3.0](https://github.com/ArthurMitchell42/nutcase/discussions/19) is released with lots of new features and a GUI - 18/1/2024

<h2 id="introduction">A Network UPS Tools (NUT) and APC daemon exporter to pass data to Prometheus and any JSON compatible applications</h2>
<h3 id="key-features">Key features</h3>

* A graphic interface showing key data over time with diagnostic information. <img src="https://img.shields.io/badge/New_in_V0.3.0_Beta_1-8A2BE2">
* Supports pulling data from NUT and APC servers and formatting the UPS status for the [Prometheus](https://prometheus.io/) logging system
* Supports formatting the UPS status as JSON for use with the beautiful [HomePage](https://gethomepage.dev/) app.
* The JSON output can be used with [Uptime Kuma](https://github.com/louislam/uptime-kuma) and other reporting, alarming and monitoring apps.
* Provides diagnostic information and usage information.
* Supports APC apcupsd servers for graphic display **and** metric scraping - **Use one Prometheus and Grafana dashboard for all servers.**
* Supports filtering of JSON elements to support simple monitoring apps. See [Filtering the JSON](https://github.com/ArthurMitchell42/nutcase/wiki/Using-the-JSON-returned-by-NUTCase#filtering-the-json-) <img src="https://img.shields.io/badge/New_in_V0.3.0_Beta_4-8A2BE2">

### How It Works

![Structure](https://github.com/ArthurMitchell42/nutcase/blob/6e7b52aa5cd89663476fa5558ab05a15233967aa/resources/structure_v2.png)

NUTCase sits between any nuber of UPS servers, either NUT or APC, and converts the UPS parameters in to either text metrics suitable for use with data caputre systems like Prometheus or JSON.
The JSON is ideal for monitoring or display on dashboard systems such as HomePage.

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
<td align="left">12/1/2024</td>
<td align="left">0.2.2</td>
<td align="left">Corrected potential crash re rework->ratio.</td>
</tr>
<tr>
<td align="left">22/12/2023</td>
<td align="left">0.2.1</td>
<td align="left">Corrected error relating to the query port command.</td>
</tr>
<tr>
<td align="left">16/12/2023</td>
<td align="left">0.2.0</td>
<td align="left">APC Support with other features, See GitHub notes.</td>
</tr>
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

See [Diagnosing Connection Issues](https://github.com/ArthurMitchell42/nutcase/wiki/Diagnosing-Connection-Issues) to set up an diagnose connection issues.

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

[Contents](#contents)

<h3 id="parameters">Parameters</h3>
<p>
The parameters available are documented in [Running the NUTCase container](https://github.com/ArthurMitchell42/nutcase/wiki/Running-the-NUTCase-container)

[Contents](#contents)

<h3 id="endpoints">End-points to Access NUTCase</h3>

Please see [Accessing and Using NUTCase](https://github.com/ArthurMitchell42/nutcase/wiki/Accessing-and-Using-NUTCase)

[Contents](#contents)

<h3 id="using-nutcase">Using NUTCase</h3>
<h4 id="using-nutcase-prometheus">Prometeus & Grafana</h4>

See [Using with Prometheus and Grafana](https://github.com/ArthurMitchell42/nutcase/wiki/Using-with-Prometheus-and-Grafana)

<h4 id="using-nutcase-homepage">HomePage</h4>

To configure HomePage to display information from NUTCase see [Customising the Data Displayed on the HomePage App](https://github.com/ArthurMitchell42/nutcase/wiki/Customising-the-Data-Displayed-on-the-HomePage-App)


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


<h1>NUTCase</h1>

[<img src="https://img.shields.io/badge/paypal-donate-blue.svg?logo=paypal&style=for-the-badge">](https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8)
[![Release](https://img.shields.io/github/release/ArthurMitchell42/nutcase.svg?logo=github&style=for-the-badge)](https://github.com/ArthurMitchell42/nutcase/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/kronos443/nutcase/latest?logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/kronos443/nutcase?label=Pulls&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)
[![Docker Stars](https://img.shields.io/docker/stars/kronos443/nutcase?label=Stars&logo=docker&style=for-the-badge)](https://hub.docker.com/r/kronos443/nutcase)

[![Docker Build](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-image.yml)
[![Docker build and push release tag & latest](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-build-release.yml/badge.svg)](https://github.com/ArthurMitchell42/nutcase/actions/workflows/docker-build-release.yml)

s
> [!TIP]
> ### News: [V0.3.3](https://github.com/ArthurMitchell42/nutcase/releases) is released today. - 7/3/2024

## A **Network UPS Tools (NUT)** and **APC daemon** exporter working with Prometheus and any JSON compatible application and GUI

### Key features
* Acts as a **drop in replacement** for other NUT scrapers such as HON95 prometheus nut exporter
* A [graphic interface](https://github.com/ArthurMitchell42/nutcase/wiki/The-GUI) showing key data over time with diagnostic information. <a href="https://github.com/ArthurMitchell42/nutcase/wiki/The-GUI"><img src="https://img.shields.io/badge/New_in_V0.3.0-8A2BE2"></a>
* Supports pulling data from NUT and APC servers, formatting the UPS metrics for the [Prometheus](https://prometheus.io/) logging system
* Supports formatting the UPS data as JSON for use with the beautiful [HomePage](https://gethomepage.dev/) app.
* The JSON output can be used with [Uptime Kuma](https://github.com/louislam/uptime-kuma) and other reporting, alerting and monitoring apps.
* Provides diagnostic and usage information.
* Supports APC apcupsd servers for graphic display **and** metric scraping - **Use one Prometheus and Grafana dashboard for all servers.**
* Supports filtering of JSON elements to support simple monitoring apps. See [Filtering the JSON](https://github.com/ArthurMitchell42/nutcase/wiki/Using-the-JSON-returned-by-NUTCase#filtering-the-json-) <a href="https://github.com/ArthurMitchell42/nutcase/wiki/Using-the-JSON-returned-by-NUTCase#filtering-the-json-"><img src="https://img.shields.io/badge/New_in_V0.3.0-8A2BE2"></a>

![image](https://github.com/ArthurMitchell42/nutcase/assets/82239494/6fbfa4d8-7cbc-4882-9e8e-ac3907e70d9a)

### What it does for you

![Structure](https://github.com/ArthurMitchell42/nutcase/blob/6e7b52aa5cd89663476fa5558ab05a15233967aa/resources/structure_v2.png)

NUTCase sits between any nuber of UPS servers, either NUT or APC, and converts the UPS parameters in to either text metrics suitable for use with data caputre systems like Prometheus or JSON.
The JSON is ideal for monitoring or display on dashboard systems such as HomePage.

<h3 id="links-refs">Links & References</h3>

The docker container:
> https://hub.docker.com/repository/docker/kronos443/nutcase

Source code:
> https://github.com/ArthurMitchell42/nutcase

The Wiki for usage information and advice:
> https://github.com/ArthurMitchell42/nutcase/wiki

<h3 id="architectures">Supported Architectures</h3>
<p>
Currently supports 'AMD64', 'ARM64 (ARM64V8)' (suitable for running on docker under Raspberry PI with a 64-bit OS such as Raspberry PI OS 64-bit and Ubuntu 64-bit)'
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
<td align="center">ARM64V8 (ARM64)</td>
<td>arm64v8-latest. For Raspberry PI with a 64-bit OS (RaspberryPI OS 64-bit or Ubuntu 64-bit</td>
</tr>
</tbody></table>

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
<td align="left">7/3/2024</td>
<td align="left">0.3.3</td>
<td align="left">Add a check for release updates on the GUI, prep-work for next major release.</td>
</tr>
<tr>
<td align="left">22/2/2024</td>
<td align="left">0.3.2</td>
<td align="left">Correct re-work of cl-count miss reading data</td>
</tr>
<tr>
<td align="left">19/2/2024</td>
<td align="left">0.3.1</td>
<td align="left">Fix for start crash Re missing config file</td>
</tr>
<tr>
<td align="left">3/2/2024</td>
<td align="left">0.3.0</td>
<td align="left">New GUI and many more features.</td>
</tr>
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

<h3 id="contents">Contents</h3>

Getting started
  * [Instalation](https://github.com/ArthurMitchell42/nutcase/wiki/Running-the-NUTCase-container)
  * [Accessing Nutcase](https://github.com/ArthurMitchell42/nutcase/wiki/Accessing-and-Using-NUTCase)
  * [Configuring NUTCase](https://github.com/ArthurMitchell42/nutcase/wiki/The-Configuration-File)

Using NUTCase
  * [Working with the GUI](https://github.com/ArthurMitchell42/nutcase/wiki/The-GUI)
  * [Working with HomePage](https://github.com/ArthurMitchell42/nutcase/wiki/Customising-the-data-displayed-on-the-HomePage-app)
  * [Working with other JSON consumers](https://github.com/ArthurMitchell42/nutcase/wiki/Using-the-JSON-returned-by-NUTCase)
  * [Interfacing to Prometheus & Grafana](https://github.com/ArthurMitchell42/nutcase/wiki/Using-with-Prometheus-and-Grafana)

Advanced useage
  * [Customising data for HomePage and UptimeKuma](https://github.com/ArthurMitchell42/nutcase/wiki/Customising-the-Data-Displayed-on-the-HomePage-App)
  * [With APC devices](https://github.com/ArthurMitchell42/nutcase/wiki/NUTCase-and-APC's-apcupsd)
  * [Custom variables](https://github.com/ArthurMitchell42/nutcase/wiki/Reworking-variables-using-the-configuration-file)
  * [WebHooks](https://github.com/ArthurMitchell42/nutcase/wiki/WebHooks)

[Contents](#contents)

<h3 id="credits">Credits</h3>
<p>
Credit goes to the HON95 container which gave inspiration to the metrics function.
</p>

[Contents](#contents)

<h3 id="support">Support</h3>
<p><b>If you find this container useful then please consider</b> <a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8">buying me a coffee by following this link or scanning the QR below.</a> :smiley: :coffee:</p>

<a href="https://www.paypal.com/donate?hosted_button_id=N6F4E9YCD5VC8"> <img src="http://www.ajwm.uk/dockerdonate.jpg" alt="Please consider donating" width="120" height="120"> </a>

[Contents](#contents)


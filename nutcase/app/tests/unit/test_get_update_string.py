import unittest
import flask
import unittest.mock as mock
from unittest.mock import call

from http import HTTPStatus
from urllib.error import URLError, HTTPError

from .mock_types import Urlopen

from app.api.api_utils import Get_Update_String
from app.utils.app_log_config import Add_Logging_Levels

BASE_CONFIG = {
    "APP_VERSION": '0.3.2',
    "GITHUB_API_URL": "https://api.github.com/repos/ArthurMitchell42/nutcase/"
    }

Full_JSON = b'[{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/144328522","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/144328522/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/144328522/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/v0.3.2_release","id":144328522,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84ImkdK","tag_name":"v0.3.2_release","target_commitish":"main","name":"V0.3.2 release","draft":false,"prerelease":false,"created_at":"2024-03-01T08:20:57Z","published_at":"2024-03-01T08:33:00Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/v0.3.2_release","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/v0.3.2_release","body":"## V0.3.2 Release\\r\\n### Bug fixes\\r\\nCorrect re-work of cl-count style: miss-reporting data \\r\\nAssorted minor fixes thrown up by automatic testing\\r\\n\\r\\n### Background\\r\\nIntroduced unit testing\\r\\nVarious minor tweaks raised by testing to aid robustness\\r\\n\\r\\n### UI\\r\\nAdd countdown bar\\r\\nChange X axis on charts to clarify scale\\r\\nCorrect HTML update rate"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/143996309","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/143996309/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/143996309/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.3.2a_pre_release","id":143996309,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84IlTWV","tag_name":"V0.3.2a_pre_release","target_commitish":"V0.3.2","name":"V0.3.2a Pre Release","draft":false,"prerelease":true,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.3.2a_pre_release","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.3.2a_pre_release","body":"Add countdown bar\\r\\nChange X axis on charts to clarify scale\\r\\nCorrect HTML update rate\\r\\n"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/143776227","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/143776227/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/143776227/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.3.2_pre_release","id":143776227,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84Ikdnj","tag_name":"V0.3.2_pre_release","target_commitish":"V0.3.2","name":"V0.3.2_pre_release","draft":false,"prerelease":true,"created_at":"2024-02-26T20:59:43Z","published_at":"2024-02-27T10:21:05Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.3.2_pre_release","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.3.2_pre_release","body":"## V0.3.2 Pre-Release\\r\\n### Bug fixes\\r\\nCorrect re-work of cl-count style: miss-reporting data \\r\\nAssorted minor fixes thrown up by automatic testing\\r\\n\\r\\n### Background\\r\\nIntroduced unit testing\\r\\nVarious minor tweaks raised by testing to aid robustness\\r\\n"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/142581599","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/142581599/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/142581599/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.3.1","id":142581599,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84If59f","tag_name":"V0.3.1","target_commitish":"main","name":"V0.3.1","draft":false,"prerelease":false,"created_at":"2024-02-19T11:53:30Z","published_at":"2024-02-19T12:15:39Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.3.1","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.3.1","body":"Bug fix:\\r\\nCrash on startup if the `nutcase.yaml` configuration file is missing\\r\\n"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/139768022","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/139768022/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/139768022/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.3.0-Release","id":139768022,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84IVLDW","tag_name":"V0.3.0-Release","target_commitish":"main","name":"V0.3.0","draft":false,"prerelease":false,"created_at":"2024-02-03T12:27:14Z","published_at":"2024-02-03T13:17:15Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.3.0-Release","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.3.0-Release","body":"# V0.3.0 Release \\r\\n## New Features \\r\\n### A new GUI \\r\\nThe big change in this release is the inclusion of a GUI to directly display UPS device data as a web page. \\r\\nKey items: \\r\\n* Support for displaying data from both NUT and APC daemon hosted devices  \\r\\n* Status summary of line power and battery \\r\\n* Detail pull-downs for server and variable information \\r\\n* Gauges for current data \\r\\n* Charts for up to 30 minutes of history on key values \\r\\n* Tool-tips to provide quick information \\r\\n* Light & dark UI themes \\r\\n* Better log file display with the option to download logs directly \\r\\n* Download the metrics, JSON or raw JSON from the tool bar for diagnostics \\r\\n* Added tool tips to the menu icons \\r\\n\\r\\n### Other New Features \\r\\nThe metrics end point now supports serving data from both NUT and APC daemon served devices \\r\\nThis allows all UPS devices to have data gathered to the same database (Prometheus) and be displayed on the same Grafana dashboard \\r\\nAdded a URL option to filter and deliver only the requested variable values to simplify operation with tools such as Uptime Kuma \\r\\nSupport for web hooks to report successful and failed actions \\r\\nCaching of server data has been added to control the access rate when multiple requests are made \\r\\nLogging in to a NUT server using stored credentials is now supported \\r\\nAdd The ability to rework APC variables \\r\\nAdded translation of APC variables to NUT format to simplify usage  \\r\\nA friendly name has been added to the servers section to be used on the devices menu \\r\\n\\r\\n### Configuration Options & Settings \\r\\nA list of servers can be set in the configuration file to give server specific settings and quick access through the GUI \\r\\nThe option to strip units from APC variable values which can improve visual results with APC data and HomePage \\r\\nThe configuration file now supports a range settings for the app \\r\\nA power setting in the servers section of the configuration file can override or mitigates the absence of the  `ups.realpower.nominal` variable to allow real power figures in the JSON and GUI \\r\\nNew `elem` URL parameter to filter the delivered JSON \\r\\n\\r\\n### Refined Features \\r\\nThe configuration file name now supports either  `.yaml` or`. yml` extensions \\r\\nNew log levels supported, `DEBUGV` & `DEBUGVV`  to control extra verbosity  \\r\\nThe NUTCase version has been added to the output JSON data \\r\\nThe JSON download now formats the sent file with indents to make parsing easier \\r\\nViewing Metrics, JSON or raw data now opens in a new tab \\r\\nAdded a representation of the last modification time on log->file menu \\r\\n"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/136792591","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/136792591/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/136792591/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.2.2","id":136792591,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84IJ0oP","tag_name":"V0.2.2","target_commitish":"main","name":"V0.2.2","draft":false,"prerelease":false,"created_at":"2024-01-12T09:09:10Z","published_at":"2024-01-12T09:13:22Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.2.2","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.2.2","body":"Correct a potential crash re rework->ratio"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/134901613","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/134901613/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/134901613/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.2.1","id":134901613,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84ICm9t","tag_name":"V0.2.1","target_commitish":"main","name":"Corrected issue with \'port\' query directive","draft":false,"prerelease":false,"created_at":"2023-12-22T12:43:42Z","published_at":"2023-12-22T12:52:33Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.2.1","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.2.1","body":"Corrected an error where by the `port` directive of the URL query did not work."},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/134189195","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/134189195/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/134189195/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.2.0","id":134189195,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84H_5CL","tag_name":"V0.2.0","target_commitish":"main","name":"V0.2.0","draft":false,"prerelease":false,"created_at":"2023-12-16T14:39:51Z","published_at":"2023-12-16T14:52:05Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.2.0","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.2.0","body":"* Added support for APC servers running apcupsd \\r\\n* Added listing the APC log events with the end point /apclog \\r\\n* Added support for variable reworking to make virtual variables with changed text or numeric values \\r\\n* Added support for a health check end point /health which returns the JSON { \xe2\x80\x9cOK\xe2\x80\x9d: \xe2\x80\x9dTrue\xe2\x80\x9d }\\r\\n* Added NUT client machines to JSON under  \\r\\n    `<ups-name> \\\\ clients \\\\ list `\\r\\n  And a count of clients under \\r\\n    `<ups-name> \\\\ clients \\\\ count `\\r\\n* Added environment variable support for DEFAULT_LOG_LINES\\r\\n"},{"url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/133164171","assets_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/releases/133164171/assets","upload_url":"https://uploads.github.com/repos/ArthurMitchell42/nutcase/releases/133164171/assets{?name,label}","html_url":"https://github.com/ArthurMitchell42/nutcase/releases/tag/V0.1.0","id":133164171,"author":{"login":"ArthurMitchell42","id":82239494,"node_id":"MDQ6VXNlcjgyMjM5NDk0","avatar_url":"https://avatars.githubusercontent.com/u/82239494?v=4","gravatar_id":"","url":"https://api.github.com/users/ArthurMitchell42","html_url":"https://github.com/ArthurMitchell42","followers_url":"https://api.github.com/users/ArthurMitchell42/followers","following_url":"https://api.github.com/users/ArthurMitchell42/following{/other_user}","gists_url":"https://api.github.com/users/ArthurMitchell42/gists{/gist_id}","starred_url":"https://api.github.com/users/ArthurMitchell42/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/ArthurMitchell42/subscriptions","organizations_url":"https://api.github.com/users/ArthurMitchell42/orgs","repos_url":"https://api.github.com/users/ArthurMitchell42/repos","events_url":"https://api.github.com/users/ArthurMitchell42/events{/privacy}","received_events_url":"https://api.github.com/users/ArthurMitchell42/received_events","type":"User","site_admin":false},"node_id":"RE_kwDOK0NoT84H7-yL","tag_name":"V0.1.0","target_commitish":"main","name":"V0.1.0","draft":false,"prerelease":false,"created_at":"2023-12-02T14:02:15Z","published_at":"2023-12-08T11:45:28Z","assets":[],"tarball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/tarball/V0.1.0","zipball_url":"https://api.github.com/repos/ArthurMitchell42/nutcase/zipball/V0.1.0","body":"First public release"}]'

Test_prerel_JSON = b'[{"html_url":"https://github/v0.3.3_draft","node_id":"RE_kwDOK0NoT84ImkdK","tag_name":"v0.3.3_draft","name":"V0.3.3 draft","draft":true,"prerelease":false,"created_at":"2024-03-01T08:20:57Z","published_at":"2024-03-01T08:33:00Z","body":"## V0.3.2 Release"},{"html_url":"https://github/V0.3.2a_pre_release","tag_name":"V0.3.2a_pre_release","name":"V0.3.2a Pre Release","draft":false,"prerelease":true,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"pre release\\r\\n"},{"html_url":"https://github/V0.3.1_release","tag_name":"V0.3.1_release","name":"V0.3.1 Release","draft":false,"prerelease":false,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"release\\r\\n"},{"html_url":"https://github/V0.3.0_release","tag_name":"V0.3.0_release","name":"V0.3.0 Release","draft":false,"prerelease":false,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"release\\r\\n"}]'

Test_urgent_JSON = b'[{"html_url":"https://github/v0.3.3_draft","node_id":"RE_kwDOK0NoT84ImkdK","tag_name":"v0.3.3_draft","name":"V0.3.3 draft","draft":true,"prerelease":false,"created_at":"2024-03-01T08:20:57Z","published_at":"2024-03-01T08:33:00Z","body":"## V0.3.2 Release"},{"html_url":"https://github/V0.3.2a_pre_release","tag_name":"V0.3.2a_pre_release","name":"V0.3.2a Pre Release","draft":false,"prerelease":true,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"pre release Urgent\\r\\n"},{"html_url":"https://github/V0.3.1_release","tag_name":"V0.3.1_release","name":"V0.3.1 Release","draft":false,"prerelease":false,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"release secuRity\\r\\n"},{"html_url":"https://github/V0.3.0_release","tag_name":"V0.3.0_release","name":"V0.3.0 Release","draft":false,"prerelease":false,"created_at":"2024-02-28T13:05:21Z","published_at":"2024-02-28T13:08:00Z","body":"release\\r\\n"}]'

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)
        app.config.update(BASE_CONFIG)
        self.app = app
        self.app.app_context().push()
        Add_Logging_Levels()
        # app.logger.setLevel("CRITICAL")
        # app.logger.setLevel("WARNING")
        app.logger.setLevel("DEBUG")

@mock.patch("urllib.request.urlopen", autospec=True)
class Test_get_update_string(BaseTestCase):
    # HTTPError
    def test_gus_http_error(self, mock_urlopen):
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj
        mock_urlopen.side_effect = HTTPError(url=url, code=HTTPStatus.BAD_REQUEST,
                                             msg="Bad request", hdrs=None, fp=None)

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_get_update_string:Failed to call Github API. "
                                                        "Reason: Bad request",
                "WARNING:tests.unit.test_get_update_string:Github couldn't fulfill request Error: 400"
                ])

        self.assertEqual(Rtn, "")

    # URLError
    def test_gus_url_error(self, mock_urlopen):
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url)
        mock_urlopen.return_value = rtn_obj
        mock_urlopen.side_effect = URLError(reason="The reason")

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_get_update_string:Failed to call Github API. Reason: The reason"
                ])

        self.assertEqual(Rtn, "")

    # Return 404
    def test_gus_return_404(self, mock_urlopen):
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.NOT_FOUND, read_data='')
        mock_urlopen.return_value = rtn_obj

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_get_update_string:Github returned 404: NOT_FOUND",
                ])

        self.assertEqual(Rtn, "")
        self.assertEqual(mock_urlopen.call_count, 1)

    # Return malformed JSON
    def test_gus_malformed_json(self, mock_urlopen):
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data='xxx')
        mock_urlopen.return_value = rtn_obj

        with self.assertLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
            self.assertEqual(cm.output, [
                "WARNING:tests.unit.test_get_update_string:JSON Returned by Github could not be "
                                    "parsed Expecting value: line 1 column 1 (char 0)",
                ])

        self.assertEqual(Rtn, "")
        self.assertEqual(mock_urlopen.call_count, 1)

    # Return zero array JSON
    def test_gus_zero_array_json(self, mock_urlopen):
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data='[]')
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
            # self.assertEqual(cm.output, [])

        self.assertEqual(Rtn, "")
        self.assertEqual(mock_urlopen.call_count, 1)

    # Normal up to date
    def test_gus_normal_current(self, mock_urlopen):
        self.app.config.update(APP_VERSION = '0.3.3')
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data=Test_prerel_JSON)
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()

        self.assertEqual(Rtn, "")
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

    # Pre-rel available
    def test_gus_prerel_avail(self, mock_urlopen):
        self.maxDiff = None
        self.app.config.update(APP_VERSION = '0.3.1')
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data=Test_prerel_JSON)
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
        # print("Rtn: {}".format(Rtn))
        self.assertEqual(Rtn, '<a href="https://github/V0.3.2a_pre_release" target="_blank" class="text-decoration-none text-small badge rounded-pill bg-success text-light">V0.3.2a_pre_release</a>')
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

    # Pre-rel and release available
    def test_gus_release_avail(self, mock_urlopen):
        self.maxDiff = None
        self.app.config.update(APP_VERSION = '0.3.0')
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data=Test_prerel_JSON)
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
        # print("Rtn: {}".format(Rtn))
        self.assertEqual(Rtn, '<a href="https://github/V0.3.1_release" target="_blank" class="text-decoration-none text-small badge rounded-pill bg-warning text-dark">V0.3.1_release</a>')
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

    # Pre-rel urgent
    def test_gus_prerel_urgent(self, mock_urlopen):
        self.maxDiff = None
        self.app.config.update(APP_VERSION = '0.3.1')
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data=Test_urgent_JSON)
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
        print("Rtn: {}".format(Rtn))
        self.assertEqual(Rtn, '<a href="https://github/V0.3.2a_pre_release" target="_blank" class="text-decoration-none text-small badge rounded-pill bg-danger text-light">V0.3.2a_pre_release</a>')
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

    # Pre-rel urgent
    def test_gus_rel_urgent(self, mock_urlopen):
        self.maxDiff = None
        self.app.config.update(APP_VERSION = '0.3.0')
        url = self.app.config['GITHUB_API_URL'] + "releases"
        rtn_obj = Urlopen(url, code=HTTPStatus.OK, read_data=Test_urgent_JSON)
        mock_urlopen.return_value = rtn_obj

        with self.assertNoLogs('tests', level='DEBUG') as cm:
            Rtn = Get_Update_String()
        print("Rtn: {}".format(Rtn))
        self.assertEqual(Rtn, '<a href="https://github/V0.3.1_release" target="_blank" class="text-decoration-none text-small badge rounded-pill bg-danger text-light">V0.3.1_release</a>')
        self.assertEqual(mock_urlopen.call_count, 1)
        self.assertEqual(rtn_obj.geturl(), url)

if __name__ == '__main__':
    unittest.main()  # pragma: no cover

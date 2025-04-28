# pypinfo: View PyPI download statistics with ease.

[![PyPI version](https://img.shields.io/pypi/v/pypinfo.svg?style=flat-square)](https://pypi.org/project/pypinfo)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pypinfo.svg?style=flat-square)](https://pypi.org/project/pypinfo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

pypinfo is a simple CLI to access [PyPI](https://pypi.org/) download statistics via Google's BigQuery.

## Table of contents

1. [Usage](#usage)
2. [Installation](#installation)
3. [Credits](#credits)

## Usage

<details>
  <summary>
  Click to unfold usage
  </summary>

```console
$ pypinfo
Usage: pypinfo [OPTIONS] [PROJECT] [FIELDS]... COMMAND [ARGS]...

  Valid fields are:

  project | version | file | pyversion | percent3 | percent2 | impl | impl-version |

  openssl | date | month | year | country | installer | installer-version |

  setuptools-version | system | system-release | distro | distro-version | ci | cpu |

  libc | libc-version

Options:
  -a, --auth TEXT         Path to Google credentials JSON file.
  --run / --test          --test simply prints the query.
  -n, --dry-run           Don't run query but display how much data would be processed.
  -j, --json              Print data as JSON, with keys `rows` and `query`.
  -i, --indent INTEGER    JSON indentation level.
  -t, --timeout INTEGER   Milliseconds. Default: 120000 (2 minutes)
  -l, --limit INTEGER     Maximum number of query results. Default: 10
  -d, --days INTEGER      Number of days in the past to include. Default: 30
  -sd, --start-date TEXT  Must be negative or YYYY-MM[-DD]. Default: -31
  -ed, --end-date TEXT    Must be negative or YYYY-MM[-DD]. Default: -1
  -m, --month TEXT        Shortcut for -sd & -ed for a single YYYY-MM month.
  -w, --where TEXT        WHERE conditional. Default: file.project = "project"
  -o, --order TEXT        Field to order by. Default: download_count
  --all                   Show downloads by all installers, not only pip.
  -pc, --percent          Print percentages.
  -md, --markdown         Output as Markdown.
  -v, --verbose           Print debug messages to stderr.
  --version               Show the version and exit.
  -h, --help              Show this message and exit.
```

pypinfo accepts 0 or more options, followed by exactly 1 project, followed by
0 or more fields. By default only the last 30 days are queried. Let's take a
look at some examples!

_Tip_: If queries are resulting in NoneType errors, increase timeout.

### Downloads for a project

```console
$ pypinfo requests
Served from cache: False
Data processed: 2.83 GiB
Data billed: 2.83 GiB
Estimated cost: $0.02

| download_count |
| -------------- |
|    116,353,535 |
```

### All downloads

```console
$ pypinfo ""
Served from cache: False
Data processed: 116.15 GiB
Data billed: 116.15 GiB
Estimated cost: $0.57

| download_count |
| -------------- |
|  8,642,447,168 |
```

### Downloads for a project by Python version

```console
$ pypinfo django pyversion
Served from cache: False
Data processed: 967.33 MiB
Data billed: 968.00 MiB
Estimated cost: $0.01

| python_version | download_count |
| -------------- | -------------- |
| 3.8            |      1,735,967 |
| 3.6            |      1,654,871 |
| 3.7            |      1,326,423 |
| 2.7            |        876,621 |
| 3.9            |        524,570 |
| 3.5            |        258,609 |
| 3.4            |         12,769 |
| 3.10           |          3,050 |
| 3.3            |            225 |
| 2.6            |            158 |
| Total          |      6,393,263 |
```

### All downloads by country code

```console
$ pypinfo "" country
Served from cache: False
Data processed: 150.40 GiB
Data billed: 150.40 GiB
Estimated cost: $0.74

| country | download_count |
| ------- | -------------- |
| US      |  6,614,473,568 |
| IE      |    336,037,059 |
| IN      |    192,914,402 |
| DE      |    186,968,946 |
| NL      |    182,691,755 |
| None    |    141,753,357 |
| BE      |    111,234,463 |
| GB      |    109,539,219 |
| SG      |    106,375,274 |
| FR      |     86,036,896 |
| Total   |  8,068,024,939 |
```

### Downloads for a project by system and distribution

```console
$ pypinfo cryptography system distro
Served from cache: False
Data processed: 2.52 GiB
Data billed: 2.52 GiB
Estimated cost: $0.02

| system_name | distro_name                     | download_count |
| ----------- | ------------------------------- | -------------- |
| Linux       | Ubuntu                          |     19,524,538 |
| Linux       | Debian GNU/Linux                |     11,662,104 |
| Linux       | Alpine Linux                    |      3,105,553 |
| Linux       | Amazon Linux AMI                |      2,427,975 |
| Linux       | Amazon Linux                    |      2,374,869 |
| Linux       | CentOS Linux                    |      1,955,181 |
| Windows     | None                            |      1,522,069 |
| Linux       | CentOS                          |        568,370 |
| Darwin      | macOS                           |        489,859 |
| Linux       | Red Hat Enterprise Linux Server |        296,858 |
| Total       |                                 |     43,927,376 |
```

### Most popular projects in the past year

```console
$ pypinfo --days 365 "" project
Served from cache: False
Data processed: 1.69 TiB
Data billed: 1.69 TiB
Estimated cost: $8.45

| project         | download_count |
| --------------- | -------------- |
| urllib3         |  1,382,528,406 |
| six             |  1,172,798,441 |
| botocore        |  1,053,169,690 |
| requests        |    995,387,353 |
| setuptools      |    992,794,567 |
| certifi         |    948,518,394 |
| python-dateutil |    934,709,454 |
| idna            |    929,781,443 |
| s3transfer      |    877,565,186 |
| chardet         |    854,744,674 |
| Total           | 10,141,997,608 |
```

### Downloads between two YYYY-MM-DD dates


```console
$ pypinfo --start-date 2018-04-01 --end-date 2018-04-30 setuptools
Served from cache: False
Data processed: 571.37 MiB
Data billed: 572.00 MiB
Estimated cost: $0.01

| download_count |
| -------------- |
|      8,972,826 |
```

### Downloads between two YYYY-MM dates

- A yyyy-mm ``--start-date`` defaults to the first day of the month
- A yyyy-mm ``--end-date`` defaults to the last day of the month

```console
$ pypinfo --start-date 2018-04 --end-date 2018-04 setuptools
Served from cache: False
Data processed: 571.37 MiB
Data billed: 572.00 MiB
Estimated cost: $0.01

| download_count |
| -------------- |
|      8,972,826 |
```

### Downloads for a single YYYY-MM month

```console
$ pypinfo --month 2018-04 setuptools
Served from cache: False
Data processed: 571.37 MiB
Data billed: 572.00 MiB
Estimated cost: $0.01

| download_count |
| -------------- |
|      8,972,826 |
```

### Percentage of Python 3 downloads of the top 100 projects in the past year

Let's use ``--test`` to only see the query instead of sending it.

```console
$ pypinfo --test --days 365 --limit 100 "" project percent3
SELECT
    file.project as project,
    ROUND(100 * SUM(CASE WHEN REGEXP_EXTRACT(details.python, r"^([^\.]+)") = "3" THEN 1 ELSE 0 END) / COUNT(*), 1) as percent_3,
    COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -366 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
    AND details.installer.name = "pip"
GROUP BY
    project
ORDER BY
    download_count DESC
LIMIT 100
```

### Downloads for a given version

pypinfo supports [PEP 440 version matching](https://peps.python.org/pep-0440/#version-matching).

We can use it to query stats on a given major version.

```console
$ pypinfo -pc 'pip==21.*' pyversion version
Served from cache: False
Data processed: 34.45 MiB
Data billed: 35.00 MiB
Estimated cost: $0.01

| python_version | version | percent | download_count |
| -------------- | ------- | ------- | -------------- |
| 3.6            | 21.3.1  |  78.74% |         10,430 |
| 3.8            | 21.3.1  |   7.81% |          1,034 |
| 3.7            | 21.2.1  |   3.59% |            476 |
| 3.7            | 21.3.1  |   2.60% |            345 |
| 3.7            | 21.0.1  |   2.25% |            298 |
| 3.8            | 21.0.1  |   1.58% |            209 |
| 3.8            | 21.2.1  |   1.42% |            188 |
| 3.7            | 21.1.2  |   0.81% |            107 |
| 3.9            | 21.3.1  |   0.69% |             92 |
| 3.8            | 21.1.1  |   0.51% |             67 |
| Total          |         |         |         13,246 |
```

We can also use it to query stats on an exact version:

```console
$ pypinfo -pc 'numpy==1.23rc3' pyversion version
Served from cache: False
Data processed: 34.01 MiB
Data billed: 35.00 MiB
Estimated cost: $0.01

| python_version | version   | percent | download_count |
| -------------- | --------- | ------- | -------------- |
| 3.9            | 1.23.0rc3 |  63.33% |             38 |
| 3.8            | 1.23.0rc3 |  28.33% |             17 |
| 3.10           | 1.23.0rc3 |   8.33% |              5 |
| Total          |           |         |             60 |
```

Check how many downloads came from continuous integration servers:

```console
❯ pypinfo --percent --days 5 pillow ci
Served from cache: False
Data processed: 384.22 MiB
Data billed: 385.00 MiB
Estimated cost: $0.01

| ci    | percent | download_count |
| ----- | ------- | -------------- |
| None  |  79.37% |     11,963,127 |
| True  |  20.63% |      3,109,931 |
| Total |         |     15,073,058 |
```

</details>

## Installation

<details>
  <summary>
  Click to unfold installation
  </summary>

pypinfo is distributed on **PyPI** as a universal wheel and is available on Linux, macOS and Windows.

This is relatively painless, I swear.

### Create project

1. Go to https://bigquery.cloud.google.com.
2. Sign up if you haven't already. The first TB of queried data each month is free. Each additional TB is $5.

3. Sign in on your account if you are not already;

4. Go to https://console.developers.google.com/cloud-resource-manager and click CREATE PROJECT if you don't already have one:

![create](https://user-images.githubusercontent.com/1324225/47172949-6f4ea880-d315-11e8-8587-8b8117efeae9.png "CREATE PROJECT")

5. This takes you to [https://console.developers.google.com/projectcreate](https://console.developers.google.com/projectcreate). Fill out the form and click CREATE. Any name is fine, but I recommend you choose something to do with PyPI like pypinfo. This way you know what the project is designated for:

![click](https://user-images.githubusercontent.com/1324225/47173020-986f3900-d315-11e8-90ab-4b2ecd85b88e.png) 

6. A while after creation, at the left-top corner, select the project name of your choice on dropdown component AND at the left-top corner "Navigation Menu", select option "Cloud Overview > Dashboard":

![show](https://user-images.githubusercontent.com/1324225/47173170-0b78af80-d316-11e8-879e-01f34e139b80.png)

### Enable BigQuery API

7. Click on top-left button "Navigation Menu" and click on option "API and services > Library":

![api_library](https://user-images.githubusercontent.com/13961685/224557997-6842161c-6589-4c2a-8974-6bb3c8dc0b0b.png)

8. Perform a search with keywords "big query api" on available text field: 

![big_query_api_search](https://user-images.githubusercontent.com/13961685/224558113-4f3a3006-3216-41e9-9554-3ce60da60fd1.png)

9. Enable Big Query API by button "Enable" press: 

![big_query_api](https://user-images.githubusercontent.com/13961685/224558381-4af65bf6-348b-4e48-bd14-d667c4a6e1c7.png)

10. After enabling, click CREATE CREDENTIALS:

![credentials](https://user-images.githubusercontent.com/1324225/47173432-bc7f4a00-d316-11e8-8152-6a0e6cfab70f.png)

**Note**: You will be requested to go back to Big Query panel. In this case, click on top-left button "Navigation Menu", option "API and services > Enabled APIs and services" and on consequent page, on item "Big Query API": 

![enabled_credentials](https://user-images.githubusercontent.com/13961685/224572489-402be9b3-a441-45f0-a469-df3a292b2d80.png)

11. On the page after clicking the "CREATE CREDENTIALS" button, choose "BigQuery API", "Application Data" and "No, I'm not using them":

![credentials_page_1](https://user-images.githubusercontent.com/13961685/224556508-e57d9ea0-564c-45db-b553-a53f60c307af.png)

12. Fill account details and press button "Create and Continue":

![credentials_page_2](https://user-images.githubusercontent.com/13961685/224557099-e0e4785d-5af8-41d8-b179-5df7c49fca79.png)

13. Select role "BigQuery User" (option path "BigQuery > Big Query User"), press button "Done":

![credentials_page_3](https://user-images.githubusercontent.com/13961685/224557170-73532a10-ad64-4e74-9018-8c5f8ad205d7.png)

14. On Big Query API panel (See **Note** on item *10*), click on tab "CREDENTIALS". On section "Service accounts", click on created credentials on items 11, 12 and 13.

![create_service_credential_key](https://user-images.githubusercontent.com/13961685/224572983-d005fef7-9490-429a-bd6b-58616dd6cc86.png)

15. On page from credential click, click on tab "KEYS". On dropdown menu "ADD KEY", click on option "Create new key":

![create_credential_key](https://user-images.githubusercontent.com/13961685/224573182-5d812f47-c1c5-4aaa-a774-6ae00ce8250d.png)

16. On appearing box, click on option "JSON" and press button "CREATE": This will start the download of credentials on a JSON file with name pattern `{name}-{credentials_hash}.json`:

![create_private_key](https://user-images.githubusercontent.com/13961685/224573235-70f35826-73bb-4dad-bcbf-e6267d105121.png)

### Installation and authentication

17. Run `python -m pip install pypinfo` in the terminal.
18. `pypinfo --auth path/to/your_credentials.json`, or set an environment variable `GOOGLE_APPLICATION_CREDENTIALS` that points to the file.

</details>


## Credits

- [Donald Stufft](https://github.com/dstufft) for maintaining [PyPI](https://pypi.org) all these years;
- [Google](https://github.com/google) for donating BigQuery capacity to [PyPI](https://pypi.org);
- [Paul Kehrer](https://github.com/reaperhulk) for his [awesome blog post](https://langui.sh/2016/12/09/data-driven-decisions).

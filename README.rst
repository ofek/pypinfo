pypinfo: View PyPI download statistics with ease.
=================================================

.. image:: https://img.shields.io/pypi/v/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/pypi/pyversions/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
    :target: https://github.com/psf/black

-----

pypinfo is a simple CLI to access `PyPI`_ download statistics via Google's BigQuery.

Installation
------------

pypinfo is distributed on `PyPI`_ as a universal wheel and is available on
Linux/macOS and Windows and supports Python 3.7+.

This is relatively painless, I swear.

**Create project**

1. Go to `<https://bigquery.cloud.google.com>`_.
2. Sign up if you haven't already. The first TB of queried data each month
   is free. Each additional TB is $5.

3. Go to `<https://console.developers.google.com/cloud-resource-manager>`_ and click
   CREATE PROJECT if you don't already have one:

   .. image:: https://user-images.githubusercontent.com/1324225/47172949-6f4ea880-d315-11e8-8587-8b8117efeae9.png

4. This takes you to `<https://console.developers.google.com/projectcreate>`_. Fill out
   the form and click CREATE. Any name is fine, but I recommend you choose something to
   do with PyPI like pypinfo. This way you know what the project is designated for:

   .. image:: https://user-images.githubusercontent.com/1324225/47173020-986f3900-d315-11e8-90ab-4b2ecd85b88e.png

5. The next page should show your new project. If not, reload the page and select from
   the top menu:

   .. image:: https://user-images.githubusercontent.com/1324225/47173170-0b78af80-d316-11e8-879e-01f34e139b80.png

**Enable BigQuery API**

6. Go to `<https://console.cloud.google.com/apis/api/bigquery-json.googleapis.com/overview>`_
   and make sure the correct project is chosen using the drop-down on top. Click
   the ENABLE button:

   .. image:: https://user-images.githubusercontent.com/1324225/47173408-a6718980-d316-11e8-94c2-a17ff54fc389.png

7. After enabling, click CREATE CREDENTIALS:

   .. image:: https://user-images.githubusercontent.com/1324225/47173432-bc7f4a00-d316-11e8-8152-6a0e6cfab70f.png

8. Choose the "BigQuery API" and "No, I'm not using them":

   .. image:: https://user-images.githubusercontent.com/1324225/47173510-ec2e5200-d316-11e8-8508-2bfbb8f6b02f.png

9. Fill in a name, and select role "BigQuery User" (if the "BigQuery" is not an option
   in the list, wait 15-20 minutes and try creating the credentials again), and select a
   JSON key:

   .. image:: https://user-images.githubusercontent.com/1324225/47173576-18e26980-d317-11e8-8bfe-e4775d965e32.png

10. Click continue and the JSON will download to your computer. Note the download
    location. Move the file wherever you want:

   .. image:: https://user-images.githubusercontent.com/1324225/47173614-331c4780-d317-11e8-9ed2-fc76557a2bf6.png

11. ``pip install pypinfo``
12. ``pypinfo --auth path/to/your_credentials.json``, or set an environment variable
    ``GOOGLE_APPLICATION_CREDENTIALS`` that points to the file.

Usage
-----

.. code-block:: console

    $ pypinfo
    Usage: pypinfo [OPTIONS] [PROJECT] [FIELDS]... COMMAND [ARGS]...

      Valid fields are:

      project | version | file | pyversion | percent3 | percent2 | impl | impl-version |

      openssl | date | month | year | country | installer | installer-version |

      setuptools-version | system | system-release | distro | distro-version | cpu |

      libc | libc-version

    Options:
      -a, --auth TEXT         Path to Google credentials JSON file.
      --run / --test          --test simply prints the query.
      -j, --json              Print data as JSON, with keys `rows` and `query`.
      -i, --indent INTEGER    JSON indentation level.
      -t, --timeout INTEGER   Milliseconds. Default: 120000 (2 minutes)
      -l, --limit TEXT        Maximum number of query results. Default: 10
      -d, --days TEXT         Number of days in the past to include. Default: 30
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

pypinfo accepts 0 or more options, followed by exactly 1 project, followed by
0 or more fields. By default only the last 30 days are queried. Let's take a
look at some examples!

Tip: If queries are resulting in NoneType errors, increase timeout.

Downloads for a project
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo requests
    Served from cache: False
    Data processed: 2.83 GiB
    Data billed: 2.83 GiB
    Estimated cost: $0.02

    | download_count |
    | -------------- |
    |    116,353,535 |

All downloads
^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo ""
    Served from cache: False
    Data processed: 116.15 GiB
    Data billed: 116.15 GiB
    Estimated cost: $0.57

    | download_count |
    | -------------- |
    |  8,642,447,168 |

Downloads for a project by Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

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

All downloads by country code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

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

Downloads for a project by system and distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

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

Most popular projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

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

Downloads between two YYYY-MM-DD dates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo --start-date 2018-04-01 --end-date 2018-04-30 setuptools
    Served from cache: False
    Data processed: 571.37 MiB
    Data billed: 572.00 MiB
    Estimated cost: $0.01

    | download_count |
    | -------------- |
    |      8,972,826 |

Downloads between two YYYY-MM dates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- A yyyy-mm ``--start-date`` defaults to the first day of the month
- A yyyy-mm ``--end-date`` defaults to the last day of the month

.. code-block:: console

    $ pypinfo --start-date 2018-04 --end-date 2018-04 setuptools
    Served from cache: False
    Data processed: 571.37 MiB
    Data billed: 572.00 MiB
    Estimated cost: $0.01

    | download_count |
    | -------------- |
    |      8,972,826 |

Downloads for a single YYYY-MM month
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo --month 2018-04 setuptools
    Served from cache: False
    Data processed: 571.37 MiB
    Data billed: 572.00 MiB
    Estimated cost: $0.01

    | download_count |
    | -------------- |
    |      8,972,826 |

Percentage of Python 3 downloads of the top 100 projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's use ``--test`` to only see the query instead of sending it.

.. code-block:: console

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

Downloads for a given version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pypinfo supports `PEP 440 version matching <https://peps.python.org/pep-0440/#version-matching>`_.

We can use it to query stats on a given major version.

.. code-block:: console

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

We can also use it to query stats on an exact version:

.. code-block:: console

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

Credits
-------

- `Donald Stufft <https://github.com/dstufft>`_ for maintaining `PyPI`_ all
  these years.
- `Google <https://github.com/google>`_ for donating BigQuery capacity to
  `PyPI`_.
- `Paul Kehrer <https://github.com/reaperhulk>`_ for his
  `awesome blog post <https://langui.sh/2016/12/09/data-driven-decisions>`_.

.. _PyPI: https://pypi.org

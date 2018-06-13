pypinfo: View PyPI download statistics with ease.
=================================================

.. image:: https://img.shields.io/pypi/v/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/pypi/pyversions/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
    :target: https://github.com/ambv/black

-----

pypinfo is a simple CLI to access `PyPI`_ download statistics via Google's BigQuery.

Installation
------------

pypinfo is distributed on `PyPI`_ as a universal wheel and is available on
Linux/macOS and Windows and supports Python 3.5+ and PyPy.

This is relatively painless, I swear.

1. Go to `<https://bigquery.cloud.google.com>`_.
2. Sign up if you haven't already. The first TB of queried data each month
   is free. Each additional TB is $5.
3. Go to `<https://console.developers.google.com/cloud-resource-manager>`_ and
   create a new project if you don't already have one. Any name is fine, but I
   recommend you choose something to do with PyPI like pypinfo. This way you
   know what the project is designated for.
4. Go to `<https://console.cloud.google.com/apis/api/bigquery-json.googleapis.com/overview>`_
   and make sure the correct project is chosen using the drop-down on top. Click
   the button on top to enable.
5. Follow `<https://cloud.google.com/storage/docs/authentication#generating-a-private-key>`_
   to create credentials in JSON format. During creation, choose ``BigQuery User`` as role.
   (If ``BigQuery`` is not an option in the list, wait 15-20 minutes and try creating
   the credentials again.) After creation, note the download location. Move the file
   wherever you want.
6. ``pip install pypinfo``
7. ``pypinfo --auth path/to/your_credentials.json``, or set an environment variable
   ``GOOGLE_APPLICATION_CREDENTIALS`` that points to the file.

Usage
-----

.. code-block:: console

    $ pypinfo
    Usage: pypinfo [OPTIONS] [PROJECT] [FIELDS]... COMMAND [ARGS]...

      Valid fields are:

      project | version | file | pyversion | percent3 | percent2 | impl | impl-version |

      openssl | date | month | year | country | installer | installer-version |

      setuptools-version | system | system-release | distro | distro-version | cpu

    Options:
      -a, --auth TEXT         Path to Google credentials JSON file.
      --run / --test          --test simply prints the query.
      -j, --json              Print data as JSON, with keys `rows` and `query`.
      -i, --indent INTEGER    JSON indentation level.
      -t, --timeout INTEGER   Milliseconds. Default: 120000 (2 minutes)
      -l, --limit TEXT        Maximum number of query results. Default: 10
      -d, --days TEXT         Number of days in the past to include. Default: 30
      -sd, --start-date TEXT  Must be negative. Default: -31
      -ed, --end-date TEXT    Must be negative. Default: -1
      -w, --where TEXT        WHERE conditional. Default: file.project = "project"
      -o, --order TEXT        Field to order by. Default: download_count
      -p, --pip               Only show installs by pip.
      -pc, --percent          Print percentages.
      -md, --markdown         Output as Markdown.
      --version               Show the version and exit.
      --help                  Show this message and exit.

pypinfo accepts 0 or more options, followed by exactly 1 project, followed by
0 or more fields. By default only the last 30 days are queried. Let's take a
look at some examples!

Tip: If queries are resulting in NoneType errors, increase timeout.

Downloads for a project
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo requests
    Served from cache: False
    Data processed: 6.87 GiB
    Data billed: 6.87 GiB
    Estimated cost: $0.04

    | download_count |
    | -------------- |
    |      9,316,415 |

All downloads
^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo ""
    Served from cache: False
    Data processed: 0.00 B
    Data billed: 0.00 B
    Estimated cost: $0.00

    | download_count |
    | -------------- |
    |    661,224,259 |

Downloads for a project by Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo django pyversion
    Served from cache: False
    Data processed: 10.81 GiB
    Data billed: 10.81 GiB
    Estimated cost: $0.06

    | python_version | download_count |
    | -------------- | -------------- |
    | 3.5            |        539,194 |
    | 2.7            |        495,207 |
    | 3.6            |        310,750 |
    | None           |         84,524 |
    | 3.4            |         64,621 |
    | 3.7            |          3,022 |
    | 2.6            |          2,966 |
    | 3.3            |          1,638 |
    | 1.17           |            285 |
    | 3.2            |            188 |
    | 3.1            |              4 |
    | 2.5            |              3 |

All downloads by country code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo "" country
    Served from cache: False
    Data processed: 2.40 GiB
    Data billed: 2.40 GiB
    Estimated cost: $0.02

    | country | download_count |
    | ------- | -------------- |
    | US      |    420,722,571 |
    | CN      |     27,235,750 |
    | IE      |     24,011,857 |
    | DE      |     19,112,463 |
    | GB      |     18,485,428 |
    | FR      |     17,394,541 |
    | None    |     15,867,055 |
    | JP      |     12,381,087 |
    | CA      |     11,666,733 |
    | KR      |     10,239,761 |
    | AU      |      9,573,248 |
    | SG      |      8,500,881 |
    | IN      |      8,467,755 |
    | RU      |      6,243,255 |
    | NL      |      6,096,337 |
    | BR      |      5,992,892 |
    | IL      |      4,924,533 |
    | PL      |      2,902,368 |
    | HK      |      2,873,318 |
    | SE      |      2,604,146 |

Downloads for a project by system and distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo cryptography system distro
    Served from cache: False
    Data processed: 14.75 GiB
    Data billed: 14.75 GiB
    Estimated cost: $0.08

    | system_name | distro_name                     | download_count |
    | ----------- | ------------------------------- | -------------- |
    | Linux       | Ubuntu                          |      1,314,938 |
    | Linux       | Debian GNU/Linux                |        381,857 |
    | Linux       | None                            |        359,993 |
    | Linux       | CentOS Linux                    |        210,950 |
    | Linux       | Amazon Linux AMI                |        198,807 |
    | None        | None                            |        179,950 |
    | Windows     | None                            |        176,495 |
    | Darwin      | macOS                           |         75,030 |
    | Linux       | Alpine Linux                    |         66,296 |
    | Linux       | CentOS                          |         62,812 |
    | Linux       | Red Hat Enterprise Linux Server |         47,030 |
    | Linux       | debian                          |         33,601 |
    | Linux       | Raspbian GNU/Linux              |         29,467 |
    | Linux       | Fedora                          |         20,112 |
    | Linux       | openSUSE Leap                   |         11,549 |
    | Darwin      | OS X                            |          6,970 |
    | Linux       | Linux                           |          6,894 |
    | Linux       | Virtuozzo                       |          6,611 |
    | FreeBSD     | None                            |          5,898 |
    | Linux       | RedHatEnterpriseServer          |          4,415 |

Most popular projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ pypinfo --days 365 "" project
    Served from cache: False
    Data processed: 87.84 GiB
    Data billed: 87.84 GiB
    Estimated cost: $0.43

    | project         | download_count |
    | --------------- | -------------- |
    | simplejson      |    267,459,163 |
    | six             |    213,697,561 |
    | setuptools      |    164,144,954 |
    | botocore        |    162,843,025 |
    | python-dateutil |    159,786,908 |
    | pip             |    155,164,096 |
    | pyasn1          |    142,647,378 |
    | requests        |    141,811,313 |
    | docutils        |    136,073,108 |
    | pyyaml          |    127,183,654 |
    | jmespath        |    126,997,657 |
    | s3transfer      |    123,275,444 |
    | futures         |    121,993,875 |
    | awscli          |    119,512,669 |
    | rsa             |    112,884,251 |
    | colorama        |    107,995,099 |
    | idna            |     79,363,400 |
    | wheel           |     79,098,241 |
    | selenium        |     72,291,821 |
    | awscli-cwlogs   |     69,708,863 |

Percentage of Python 3 downloads of the top 100 projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's use ``--test`` to only see the query instead of sending it.

.. code-block:: console

    $ pypinfo --test --days 365 --limit 100 "" project percent3
    SELECT
      file.project as project,
      ROUND(100 * SUM(CASE WHEN REGEXP_EXTRACT(details.python, r"^([^\.]+)") = "3" THEN 1 ELSE 0 END) / COUNT(*), 1) as percent_3,
      COUNT(*) as download_count,
    FROM
      TABLE_DATE_RANGE(
        [the-psf:pypi.downloads],
        DATE_ADD(CURRENT_TIMESTAMP(), -366, "day"),
        DATE_ADD(CURRENT_TIMESTAMP(), -1, "day")
      )
    GROUP BY
      project,
    ORDER BY
      download_count DESC
    LIMIT 100

Credits
-------

- `Donald Stufft <https://github.com/dstufft>`_ for maintaining `PyPI`_ all
  these years.
- `Google <https://github.com/google>`_ for donating BigQuery capacity to
  `PyPI`_.
- `Paul Kehrer <https://github.com/reaperhulk>`_ for his
  `awesome blog post <https://langui.sh/2016/12/09/data-driven-decisions>`_.

Changelog
---------

Important changes are emphasized.

14.0.0
^^^^^^

- Added new ``file`` field!

13.0.0
^^^^^^

- Added ``last_update`` JSON key, which is a UTC timestamp.

12.0.0
^^^^^^

- **Breaking:** JSON output is now a mapping with keys ``rows``, which is all the
  data that was previously outputted, and ``query``, which is relevant metadata.
- Increased the resolution of percentages.

11.0.0
^^^^^^

- Fixed JSON output.

10.0.0
^^^^^^

- Fixed custom field ordering.

9.0.0
^^^^^

- Added new BigQuery usage stats.
- Lowered the default number of results to ``10`` from ``20``.
- Updated examples.
- Fixed table formatting regression.

8.0.0
^^^^^

- Updated ``google-cloud-bigquery`` dependency.

7.0.0
^^^^^

- Output table is now in Markdown format for easy copying to GitHub issues and PRs.

6.0.0
^^^^^

- Updated ``google-cloud-bigquery`` dependency.

5.0.0
^^^^^

- Numeric output (non-json) is now prettier (thanks `hugovk <https://github.com/hugovk>`_)
- You can now filter results for only pip installs with the ``--pip`` flag
  (thanks `hugovk <https://github.com/hugovk>`_)

4.0.0
^^^^^

- ``--order`` now works with all fields (thanks `Brian Skinn <https://github.com/bskinn>`_)
- Updated installation docs (thanks `Brian Skinn <https://github.com/bskinn>`_)

3.0.1
^^^^^

- Fix: project names are now normalized to adhere to
  `PEP 503 <https://www.python.org/dev/peps/pep-0503>`_.

3.0.0
^^^^^

- **Breaking:** ``--json`` option is now just a flag and prints output as prettified JSON.

2.0.0
^^^^^

- Added ``--json`` path option.

1.0.0
^^^^^

- Initial release

.. _PyPI: https://pypi.org

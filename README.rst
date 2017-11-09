pypinfo: View PyPI download statistics with ease.
=================================================

.. image:: https://img.shields.io/pypi/v/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/pypi/pyversions/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

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

.. code-block:: bash

    $ pypinfo
    Usage: pypinfo [OPTIONS] [PROJECT] [FIELDS]... COMMAND [ARGS]...

      Valid fields are:

      project | version | pyversion | percent3 | percent2 | impl | impl-version |

      openssl | date | month | year | country | installer | installer-version |

      setuptools-version | system | system-release | distro | distro-version | cpu

    Options:
      -a, --auth TEXT         Path to Google credentials JSON file.
      --run / --test          --test simply prints the query.
      -j, --json              Print data as JSON.
      -t, --timeout INTEGER   Milliseconds. Default: 120000 (2 minutes)
      -l, --limit TEXT        Maximum number of query results. Default: 20
      -d, --days TEXT         Number of days in the past to include. Default: 30
      -sd, --start-date TEXT  Must be negative. Default: -31
      -ed, --end-date TEXT    Must be negative. Default: -1
      -w, --where TEXT        WHERE conditional. Default: file.project = "project"
      -o, --order TEXT        Field to order by. Default: download_count
      -p, --pip               Only show installs by pip.
      --version               Show the version and exit.
      --help                  Show this message and exit.

pypinfo accepts 0 or more options, followed by exactly 1 project, followed by
0 or more fields. By default only the last 30 days are queried. Let's take a
look at some examples!

Tip: If queries are resulting in NoneType errors, increase timeout.

Downloads for a project
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo requests
    download_count
    --------------
        13,149,515

All downloads
^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo ""
    download_count
    --------------
       765,826,772

Downloads for a project by Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo django pyversion
    python_version download_count
    -------------- --------------
    2.7                   611,777
    3.6                   259,357
    3.5                   200,749
    3.4                   104,585
    None                   97,813
    2.6                     6,318
    3.7                     2,342
    3.3                     2,106
    3.2                       365
    2.4                        11
    1.17                       10
    2.5                         8
    3.1                         1
    2.1                         1

All downloads by country code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo "" country
    country download_count
    ------- --------------
    US         501,337,782
    IE          29,547,697
    CN          22,198,589
    DE          21,641,064
    GB          18,946,922
    None        18,077,976
    FR          15,593,846
    BR          13,500,471
    CA          13,098,341
    AU          12,482,455
    JP          12,390,691
    RU          11,381,041
    SG          11,326,902
    IN          10,186,952
    KR           8,141,791
    NL           6,695,112
    IL           3,381,433
    ES           2,622,822
    PL           2,408,438
    NO           2,292,994

Downloads for a project by system and distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo cryptography system distro
    system_name distro_name                     download_count
    ----------- ------------------------------- --------------
    Linux       Ubuntu                               1,949,204
    Linux       Debian GNU/Linux                       407,626
    Linux       None                                   375,363
    Linux       CentOS Linux                           251,467
    None        None                                   204,007
    Windows     None                                   174,763
    Linux       debian                                 116,972
    Linux       Amazon Linux AMI                       106,790
    Linux       CentOS                                  99,851
    Darwin      macOS                                   81,554
    Linux       Raspbian GNU/Linux                      68,696
    Linux       Red Hat Enterprise Linux Server         54,737
    Linux       Alpine Linux                            46,135
    Linux       Fedora                                  27,746
    Darwin      OS X                                    16,918
    Linux       Linux                                    9,711
    Linux       openSUSE Leap                            8,636
    Linux       Virtuozzo                                7,978
    Linux       RedHatEnterpriseServer                   5,789
    FreeBSD     None                                     4,899

Most popular projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo --days 365 "" project
    project         download_count
    --------------- --------------
    simplejson         327,946,463
    six                214,930,152
    python-dateutil    152,089,489
    setuptools         149,294,971
    botocore           146,935,887
    pip                140,216,305
    requests           137,229,399
    pyasn1             134,867,638
    docutils           126,916,467
    jmespath           117,212,884
    awscli             112,539,772
    rsa                106,762,453
    colorama           101,860,595
    pyyaml             100,055,678
    selenium            98,418,802
    futures             92,938,638
    s3transfer          91,310,210
    awscli-cwlogs       66,183,214
    cffi                65,383,612
    pyparsing           63,603,014

Percentage of Python 3 downloads of the top 100 projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's use ``--test`` to only see the query instead of sending it.

.. code-block:: bash

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

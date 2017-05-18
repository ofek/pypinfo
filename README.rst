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

This is relatively painless, I swear.

1. Go to `<https://bigquery.cloud.google.com>`_.
2. Sign up if you haven't already. Querying PyPI's dataset is free (for you).
3. Go to `<https://console.developers.google.com/cloud-resource-manager>`_ and
   create a new project. Any name is fine, but I recommend you choose something
   to do with PyPI like pypinfo. This way you know the project is designated
   as free.
4. Follow `<https://cloud.google.com/storage/docs/authentication#generating-a-private-key>`_
   to create credentials in JSON format. During creation, choose ``BigQuery User`` as role.
   After creation, note the download location. Move the file wherever you want.
5. ``pip install pypinfo``
6. ``pypinfo --auth path/to/your_credentials.json``, or set an environment variable
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
      --run / --test          --test simply prints the query.
      -a, --auth TEXT         Path to Google credentials JSON file.
      -t, --timeout INTEGER   Milliseconds. Default: 120000 (2 minutes)
      -l, --limit TEXT        Maximum number of query results. Default: 20
      -d, --days TEXT         Number of days in the past to include. Default: 30
      -sd, --start-date TEXT  Must be negative. Default: -31
      -ed, --end-date TEXT    Must be negative. Default: -1
      -w, --where TEXT        WHERE conditional. Default: file.project = "project"
      -o, --order TEXT        Field to order by. Default: download_count
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
    11033343

Just see query
^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo --test requests

All downloads
^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo ""
    download_count
    --------------
    662834133

Downloads for a project by Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo django pyversion
    python_version download_count
    -------------- --------------
    2.7            788060
    3.5            400008
    3.6            169665
    3.4            134378
    None           59415
    2.6            8276
    3.3            4831
    3.7            2680
    3.2            1560
    1.17           41
    2.5            15
    2.4            15
    3.1            6

All downloads by country code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo "" country
    country download_count
    ------- --------------
    US      427837633
    None    26184466
    IE      25595967
    CN      19682726
    DE      17338740
    GB      16848703
    AU      12201849
    CA      9828255
    FR      9780133
    BR      9276365
    JP      9247794
    RU      8758959
    IL      7578813
    IN      7468363
    KR      6809831
    NL      6120287
    SG      5882292
    TW      3961899
    CZ      2352650
    PL      2270622

Downloads for a project by system and distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo cryptography system distro
    system_name distro_name                     download_count
    ----------- ------------------------------- --------------
    Linux       Ubuntu                          1226983
    Linux       None                            701829
    Linux       CentOS Linux                    254488
    Linux       Debian GNU/Linux                207352
    Linux       debian                          205485
    Linux       CentOS                          195178
    None        None                            179178
    Windows     None                            126962
    Darwin      macOS                           123389
    Darwin      OS X                            51606
    Linux       Amazon Linux AMI                43192
    Linux       Red Hat Enterprise Linux Server 39157
    Linux       Alpine Linux                    37721
    Linux       Fedora                          25036
    Linux       Virtuozzo                       10302
    Linux       Raspbian GNU/Linux              4261
    Linux       Linux                           4162
    Linux       Oracle Linux Server             3754
    FreeBSD     None                            3513
    Linux       Debian                          3479

Most popular projects in the past year
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo --days 365 "" project
    project         download_count
    --------------- --------------
    simplejson      315759419
    six             197395098
    setuptools      132878072
    python-dateutil 126256414
    pip             118786872
    botocore        115173253
    pyasn1          111974599
    requests        108922890
    selenium        104830580
    docutils        104397734
    jmespath        95403328
    awscli          94119214
    rsa             91575245
    colorama        85788062
    awscli-cwlogs   57035580
    futures         52305306
    cffi            51895901
    pyyaml          51475454
    pbr             50267849
    pyparsing       50155835

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

.. _PyPI: https://pypi.org

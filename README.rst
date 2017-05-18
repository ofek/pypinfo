pypinfo: View PyPI download statistics with ease.
=================================================

.. image:: https://img.shields.io/pypi/v/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/pypi/pyversions/pypinfo.svg?style=flat-square
    :target: https://pypi.org/project/pypinfo

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

-----

pypinfo is a simple CLI to access PyPI download statistics via Google's BigQuery.

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
6. ``pypinfo creds path/to/your_credentials.json``, or set an environment variable
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
      -t, --timeout INTEGER   Milliseconds. Default: 60000 (1 minute)
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

Downloads for a project
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    $ pypinfo requests
    download_count
    --------------
    11033343

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








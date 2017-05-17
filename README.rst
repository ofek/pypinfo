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

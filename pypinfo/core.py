import os

from google.cloud.bigquery import Client

DATE_RANGE = """\
  TABLE_DATE_RANGE(
    [the-psf:pypi.downloads],
    DATE_ADD(CURRENT_TIMESTAMP(), {}, "day"),
    DATE_ADD(CURRENT_TIMESTAMP(), {}, "day")
  )
"""
DEFAULT_START_DATE = '-31'
DEFAULT_END_DATE = '-1'


def create_client(creds_file=None):
    creds_file = creds_file or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if creds_file is None:
        raise SystemError('Credentials could not be found.')

    return Client.from_service_account_json(creds_file, project='the-psf')


class Query:
    def __init__(self):
        self._select = 'SELECT\n'
        self._from_table = 'FROM\n'



import contextlib
import os

from appdirs import user_data_dir
from tinydb import TinyDB, Query, where
from tinyrecord import transaction

DB_FILE = os.path.join(user_data_dir('pypinfo', appauthor=False), 'db.json')


@contextlib.contextmanager
def get_credentials_table(table=None):
    if table is None:
        with TinyDB(DB_FILE, create_dirs=True) as db:
            yield db.table('credentials')
    else:
        yield table


def get_credentials(table=None):
    with get_credentials_table(table) as table:
        query = table.search(Query().path.exists())
        return query[0]['path'] if query else None


def set_credentials(creds_file):
    with get_credentials_table() as table:
        exists = get_credentials(table)
        with transaction(table) as tr:
            if exists:
                tr.update({'path': creds_file}, where('path').exists())
            else:
                tr.insert({'path': creds_file})

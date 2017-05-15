import os

from appdirs import user_data_dir
from tinydb import TinyDB, Query, where
from tinyrecord import transaction

DB_FILE = os.path.join(user_data_dir('pypinfo', ''), 'db.json')


def get_credentials():
    table = TinyDB(DB_FILE, create_dirs=True).table('credentials')
    query = table.search(Query().path.exists())

    return query[0]['path'] if query else None


def set_credentials(creds_file):
    table = TinyDB(DB_FILE, create_dirs=True).table('credentials')
    exists = get_credentials()

    with transaction(table) as tr:
        if exists:
            tr.update({'path': creds_file}, where('path').exists())
        else:
            tr.insert({'path': creds_file})

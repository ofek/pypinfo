import json
import os

from google.cloud.bigquery import Client

from pypinfo.fields import Downloads

FROM = """\
FROM
  TABLE_DATE_RANGE(
    [the-psf:pypi.downloads],
    DATE_ADD(CURRENT_TIMESTAMP(), {}, "day"),
    DATE_ADD(CURRENT_TIMESTAMP(), {}, "day")
  )
"""
START_DATE = '-31'
END_DATE = '-1'
DEFAULT_LIMIT = '100'


def create_client(creds_file=None):
    creds_file = creds_file or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if creds_file is None:
        raise SystemError('Credentials could not be found.')

    project = json.load(open(creds_file))['project_id']
    return Client.from_service_account_json(creds_file, project=project)


def build_query(project, fields, start_date=START_DATE, end_date=END_DATE,
                days=None, limit=DEFAULT_LIMIT, where=None):
    start_date = start_date or START_DATE
    end_date = end_date or END_DATE
    limit = limit or DEFAULT_LIMIT

    if days:
        start_date = str(int(end_date) - int(days))

    if int(start_date) > 0 or int(end_date) > 0:
        raise ValueError('Dates must be in the past (negative).')

    if int(start_date) >= int(end_date):
        raise ValueError('End date must be greater than start date.')

    fields.append(Downloads)
    query = 'SELECT\n'

    for field in fields:
        query += '  {} as {},\n'.format(field.data, field.name)

    query += FROM.format(start_date, end_date)

    if where:
        query += 'WHERE\n  {}\n'.format(where)
    else:
        query += 'WHERE\n  file.project = "{}"\n'.format(project)

    if len(fields) > 1:
        query += 'GROUP BY\n'

        for field in fields[:-1]:
            query += '  {},\n'.format(field.name)

    query += 'ORDER BY\n  {} DESC\n'.format(Downloads.name)
    query += 'LIMIT {}'.format(limit)

    return query


def parse_query_result(query):
    rows = [[field.name for field in query.schema]]
    rows.extend([str(item) for item in row] for row in query.rows)
    return rows


def tabulate(rows):
    # This function assumes that a header will always be the longest element.
    column_index = 0
    column_width = 0

    for row in rows:
        for i, item in enumerate(row):
            length = len(item)
            if length > column_width:
                column_index = i
                column_width = length

    tabulated = ''

    headers = rows.pop(0)
    last_index = len(headers) - 1
    for i, item in enumerate(headers):
        tabulated += item
        if i != last_index:
            pad = 1 if i == column_index else 0
            tabulated += ' ' * (column_width - len(item) + pad)
    tabulated += '\n' + ''.join('-' if c != ' ' else ' ' for c in tabulated) + '\n'

    for row in rows:
        last_index = len(row) - 1
        for i, item in enumerate(row):
            tabulated += item
            if i != last_index:
                pad = 1 if i == column_index else 0
                tabulated += ' ' * (column_width - len(item) + pad)
        tabulated += '\n'

    return tabulated

import json
import os
import re

from google.cloud.bigquery import Client
from google.cloud.bigquery.job import QueryJobConfig

from pypinfo.fields import AGGREGATES, Downloads

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
DEFAULT_LIMIT = '20'


def create_config():
    config = QueryJobConfig()
    config.use_legacy_sql = True
    return config


def normalize(name):
    """https://www.python.org/dev/peps/pep-0503/#normalized-names"""
    return re.sub(r'[-_.]+', '-', name).lower()


def create_client(creds_file=None):
    creds_file = creds_file or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if creds_file is None:
        raise SystemError('Credentials could not be found.')

    project = json.load(open(creds_file))['project_id']
    return Client.from_service_account_json(creds_file, project=project)


def build_query(project, fields, start_date=None, end_date=None,
                days=None, limit=None, where=None, order=None, pip=None):
    project = normalize(project)

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
        conditions = []
        if project:
            conditions.append('file.project = "{}"\n'.format(project))
        if pip:
            conditions.append('details.installer.name = "pip"\n')
        if conditions:
            query += 'WHERE\n  ' + '  AND '.join(conditions)

    if len(fields) > 1:
        gb = 'GROUP BY\n'
        initial_length = len(gb)

        for field in fields[:-1]:
            if field not in AGGREGATES:
                gb += '  {},\n'.format(field.name)

        if len(gb) > initial_length:
            query += gb

    query += 'ORDER BY\n  {} DESC\n'.format(order or Downloads.name)
    query += 'LIMIT {}'.format(limit)

    return query


def parse_query_result(query_job, query_rows):
    rows = [[field.name for field in query_job.query_results().schema]]
    rows.extend([str(item) for item in row] for row in query_rows)
    return rows


def add_percentages(rows, include_sign=True):

    headers = rows.pop(0)
    index = headers.index('download_count')
    headers.insert(index, 'percent')
    total_downloads = sum(int(row[index]) for row in rows)
    percent_format = '{:.1%}' if include_sign else '{:.1}'

    for r, row in enumerate(rows):
        percent = percent_format.format(int(row[index]) / total_downloads)
        row.insert(index, percent)

    rows.insert(0, headers)
    return rows


def tabulate(rows):
    column_widths = [0] * len(rows[0])
    is_digits = [[False] * len(rows[0])] * len(rows)

    # Get max width of each column
    for r, row in enumerate(rows):
        for i, item in enumerate(row):
            if item.isdigit():
                # Separate the thousands
                rows[r][i] = "{:,}".format(int(item))
                is_digits[r][i] = True
            length = len(item)
            if length > column_widths[i]:
                column_widths[i] = length

    tabulated = ''

    headers = rows.pop(0)
    for i, item in enumerate(headers):
        tabulated += item + ' ' * (column_widths[i] - len(item) + 1)

    tabulated += '\n' + ''.join('-' * i + ' ' for i in column_widths) + '\n'

    for r, row in enumerate(rows):
        for i, item in enumerate(row):
            num_spaces = column_widths[i] - len(item)
            if is_digits[r][i] or item.endswith('%'):
                tabulated += ' ' * num_spaces + item + ' '
            else:
                tabulated += item + ' ' * (num_spaces + 1)
        tabulated += '\n'

    return tabulated


def format_json(rows):
    headers, *data = rows
    j = []

    for d in data:
        item = {}
        for i in range(len(headers)):
            if d[i].isdigit():
                d[i] = int(d[i])
            item[headers[i]] = d[i]
        j.append(item)

    return json.dumps(j, indent=2, sort_keys=True)

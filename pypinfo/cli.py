import click

from pypinfo.core import build_query, create_client, parse_query_result, tabulate
from pypinfo.db import get_credentials, set_credentials
from pypinfo.fields import (
    Project, Date, Country, Version, PythonVersion, Installer, InstallerVersion,
    System, SystemRelease, Implementation, ImplementationVersion, OpenSSLVersion
)

CONTEXT_SETTINGS = {
    'max_content_width': 300
}
COMMAND_MAP = {
    'project': Project,
    'version': Version,
    'pyversion': PythonVersion,
    'impl': Implementation,
    'impl-version': ImplementationVersion,
    'openssl': OpenSSLVersion,
    'date': Date,
    'country': Country,
    'installer': Installer,
    'installer-version': InstallerVersion,
    'system': System,
    'system-release': SystemRelease,
}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('project', required=False)
@click.argument('fields', nargs=-1, required=False)
@click.option('--run/--test', default=True, help='--test simply prints the query.')
@click.option('--auth', '-a', help='Path to Google credentials JSON file.')
@click.option('--timeout', '-t', type=int, default=60000,
              help='Milliseconds. Default: 60000 (1 minute)')
@click.option('--limit', '-l', help='Maximum number of query results.')
@click.option('--days', '-d', help='Number of days in the past to include. Default: 30')
@click.option('--start-date', '-sd', help='Must be negative. Default: -31')
@click.option('--end-date', '-ed', help='Must be negative. Default: -1')
@click.option('--where', '-w', help='Supply your own WHERE conditional.')
@click.pass_context
def pypinfo(ctx, project, fields, run, auth, timeout, limit, days,
            start_date, end_date, where):
    """Valid fields are:\n
    project | version | pyversion | impl | impl-version | openssl | date |\n
    country | installer | installer-version | system | system-release
    """
    if auth:
        set_credentials(auth)
        click.echo('Credentials location set to "{}".'.format(get_credentials()))
        return

    if project is None and not fields:
        click.echo(ctx.get_help())
        return

    parsed_fields = []
    for field in fields:
        parsed = COMMAND_MAP.get(field)
        if parsed is None:
            raise ValueError('"{}" is an unsupported field.'.format(field))
        parsed_fields.append(parsed)

    built_query = build_query(project, parsed_fields, limit=limit, days=days,
                              start_date=start_date, end_date=end_date, where=where)

    if run:
        client = create_client(get_credentials())
        query = client.run_sync_query(built_query)
        query.timeout_ms = timeout
        query.run()
        click.echo(tabulate(parse_query_result(query)))
    else:
        click.echo(built_query)

import click

from pypinfo.core import build_query, create_client, parse_query_result, tabulate
from pypinfo.db import get_credentials, set_credentials
from pypinfo.fields import Date, PythonVersion, Installer, InstallerVersion

CONTEXT_SETTINGS = {
    'max_content_width': 300
}
COMMAND_MAP = {
    'date': Date,
    'pyversion': PythonVersion,
    'installer': Installer,
    'installer_version': InstallerVersion,
}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('package', required=False)
@click.argument('fields', nargs=-1, required=False)
@click.option('--run/--test', default=True)
@click.option('--auth', '-a')
@click.option('--timeout', '-t', type=int, default=60000)
@click.option('--limit', '-l')
@click.option('--days', '-d')
@click.option('--start-date', '-sd')
@click.option('--end-date', '-ed')
@click.pass_context
def pypinfo(ctx, package, fields, run, auth, timeout, limit, days,
            start_date, end_date):
    if auth:
        set_credentials(auth)
        click.echo('Credentials location set to "{}".'.format(get_credentials()))
        return

    if package is None or not fields:
        click.echo(ctx.get_help())
        return

    parsed_fields = []
    for field in fields:
        parsed = COMMAND_MAP.get(field)
        if parsed is None:
            raise ValueError('"{}" is an unsupported field.'.format(field))
        parsed_fields.append(parsed)

    built_query = build_query(package, parsed_fields, limit=limit, days=days,
                              start_date=start_date, end_date=end_date)

    if run:
        client = create_client(get_credentials())
        query = client.run_sync_query(built_query)
        query.timeout_ms = timeout
        query.run()
        click.echo(tabulate(parse_query_result(query)))
    else:
        click.echo(built_query)

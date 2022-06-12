from decimal import ROUND_UP, Decimal
from typing import List

import click
from binary import TEBIBYTE, convert_units

from pypinfo.core import (
    add_percentages,
    add_download_total,
    build_query,
    create_client,
    create_config,
    format_json,
    month_ends,
    parse_query_result,
    tabulate,
)
from pypinfo.db import get_credentials, set_credentials
from pypinfo.fields import (
    Project,
    Date,
    Month,
    Year,
    Country,
    Version,
    File,
    PythonVersion,
    Percent3,
    Percent2,
    Installer,
    InstallerVersion,
    SetuptoolsVersion,
    System,
    SystemRelease,
    Implementation,
    ImplementationVersion,
    OpenSSLVersion,
    Distro,
    DistroVersion,
    CPU,
    Libc,
    LibcVersion,
)

CONTEXT_SETTINGS = {
    'help_option_names': ('-h', '--help'),
    'max_content_width': 300,
}
FIELD_MAP = {
    'project': Project,
    'version': Version,
    'file': File,
    'pyversion': PythonVersion,
    'percent3': Percent3,
    'percent2': Percent2,
    'impl': Implementation,
    'impl-version': ImplementationVersion,
    'openssl': OpenSSLVersion,
    'date': Date,
    'month': Month,
    'year': Year,
    'country': Country,
    'installer': Installer,
    'installer-version': InstallerVersion,
    'setuptools-version': SetuptoolsVersion,
    'system': System,
    'system-release': SystemRelease,
    'distro': Distro,
    'distro-version': DistroVersion,
    'cpu': CPU,
    'libc': Libc,
    'libc-version': LibcVersion,
}
TIER_COST = 5
TB = Decimal(TEBIBYTE)
TO_CENTS = Decimal('0.00')


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('project', required=False)
@click.argument('fields', nargs=-1, required=False)
@click.option('--auth', '-a', help='Path to Google credentials JSON file.')
@click.option('--run/--test', default=True, help='--test simply prints the query.')
@click.option('--json', '-j', is_flag=True, help='Print data as JSON, with keys `rows` and `query`.')
@click.option('--indent', '-i', type=int, help='JSON indentation level.')
@click.option('--timeout', '-t', type=int, default=120000, help='Milliseconds. Default: 120000 (2 minutes)')
@click.option('--limit', '-l', type=int, help='Maximum number of query results. Default: 10')
@click.option('--days', '-d', type=int, help='Number of days in the past to include. Default: 30')
@click.option('--start-date', '-sd', help='Must be negative or YYYY-MM[-DD]. Default: -31')
@click.option('--end-date', '-ed', help='Must be negative or YYYY-MM[-DD]. Default: -1')
@click.option('--month', '-m', help='Shortcut for -sd & -ed for a single YYYY-MM month.')
@click.option('--where', '-w', help='WHERE conditional. Default: file.project = "project"')
@click.option('--order', '-o', help='Field to order by. Default: download_count')
@click.option('--all', 'all_installers', is_flag=True, help='Show downloads by all installers, not only pip.')
@click.option('--percent', '-pc', is_flag=True, help='Print percentages.')
@click.option('--markdown', '-md', is_flag=True, help='Output as Markdown.')
@click.option('--verbose', '-v', is_flag=True, help='Print debug messages to stderr.')
@click.version_option()
@click.pass_context
def pypinfo(
    ctx: click.Context,
    project: str,
    fields: List[str],
    auth: str,
    run: bool,
    json: bool,
    indent: int,
    timeout: int,
    limit: int,
    days: int,
    start_date: str,
    end_date: str,
    month: str,
    where: str,
    order: str,
    all_installers: bool,
    percent: bool,
    markdown: bool,
    verbose: bool,
) -> None:
    """Valid fields are:\n
    project | version | file | pyversion | percent3 | percent2 | impl | impl-version |\n
    openssl | date | month | year | country | installer | installer-version |\n
    setuptools-version | system | system-release | distro | distro-version | cpu |\n
    libc | libc-version
    """
    if auth:
        set_credentials(auth)
        click.echo(f'Credentials location set to "{get_credentials()}".')
        return

    if verbose:
        click.echo(f'Credentials location set to "{get_credentials()}".', err=True)

    if project is None and not fields:
        click.echo(ctx.get_help())
        return

    parsed_fields = []
    for field in fields:
        parsed = FIELD_MAP.get(field)
        if parsed is None:
            raise ValueError(f'"{field}" is an unsupported field.')
        parsed_fields.append(parsed)

    order_name = order
    parsed_order = FIELD_MAP.get(order)
    if parsed_order:
        order_name = parsed_order.name
        parsed_fields.insert(0, parsed_order)

    if month:
        start_date, end_date = month_ends(month)

    built_query = build_query(
        project,
        parsed_fields,
        limit=limit,
        days=days,
        start_date=start_date,
        end_date=end_date,
        where=where,
        order=order_name,
        pip=not all_installers,
    )

    if run:
        with create_client(get_credentials()) as client:
            query_job = client.query(built_query, job_config=create_config())
            query_rows = query_job.result(timeout=timeout // 1000)
            rows = parse_query_result(query_rows)

        # Cached
        from_cache = not not query_job.cache_hit

        # Processed
        bytes_processed = query_job.total_bytes_processed or 0
        processed_amount, processed_unit = convert_units(bytes_processed)

        # Billed
        bytes_billed = query_job.total_bytes_billed or 0
        billed_amount, billed_unit = convert_units(bytes_billed)

        # Cost
        billing_tier = query_job.billing_tier or 1
        estimated_cost = Decimal(TIER_COST * billing_tier) / TB * Decimal(bytes_billed)
        estimated_cost_str = str(estimated_cost.quantize(TO_CENTS, rounding=ROUND_UP))

        if len(rows) == 1 and not json:
            # Only headers returned
            click.echo("No data returned, check project name")
            return

        if percent:
            rows = add_percentages(rows, include_sign=not json)

        # Only for tables, and if more than the header row + a single data row
        if len(rows) > 2 and not json:
            rows = add_download_total(rows)

        if not json:
            click.echo(f'Served from cache: {from_cache}')
            click.echo(f'Data processed: {processed_amount:.2f} {processed_unit}')
            click.echo(f'Data billed: {billed_amount:.2f} {billed_unit}')
            click.echo(f'Estimated cost: ${estimated_cost_str}')

            click.echo()
            click.echo(tabulate(rows, markdown))
        else:
            query_info = {
                'cached': from_cache,
                'bytes_processed': bytes_processed,
                'bytes_billed': bytes_billed,
                'estimated_cost': estimated_cost_str,
            }
            click.echo(format_json(rows, query_info, indent))
    else:
        click.echo(built_query)

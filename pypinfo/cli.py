from decimal import ROUND_UP, Decimal

import click
from binary import TEBIBYTE, convert_units

from pypinfo.core import (
    add_percentages,
    build_query,
    create_client,
    create_config,
    format_json,
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
)

CONTEXT_SETTINGS = {'max_content_width': 300}
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
@click.option('--limit', '-l', help='Maximum number of query results. Default: 10')
@click.option('--days', '-d', help='Number of days in the past to include. Default: 30')
@click.option('--start-date', '-sd', help='Must be negative. Default: -31')
@click.option('--end-date', '-ed', help='Must be negative. Default: -1')
@click.option('--where', '-w', help='WHERE conditional. Default: file.project = "project"')
@click.option('--order', '-o', help='Field to order by. Default: download_count')
@click.option('--all', 'all_installers', is_flag=True, help='Show downloads by all installers, not only pip.')
@click.option('--percent', '-pc', is_flag=True, help='Print percentages.')
@click.option('--markdown', '-md', is_flag=True, help='Output as Markdown.')
@click.version_option()
@click.pass_context
def pypinfo(
    ctx,
    project,
    fields,
    auth,
    run,
    json,
    indent,
    timeout,
    limit,
    days,
    start_date,
    end_date,
    where,
    order,
    all_installers,
    percent,
    markdown,
):
    """Valid fields are:\n
    project | version | file | pyversion | percent3 | percent2 | impl | impl-version |\n
    openssl | date | month | year | country | installer | installer-version |\n
    setuptools-version | system | system-release | distro | distro-version | cpu
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
        parsed = FIELD_MAP.get(field)
        if parsed is None:
            raise ValueError('"{}" is an unsupported field.'.format(field))
        parsed_fields.append(parsed)

    order_name = order
    order = FIELD_MAP.get(order)
    if order:
        order_name = order.name
        parsed_fields.insert(0, order)

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
        client = create_client(get_credentials())
        query_job = client.query(built_query, job_config=create_config())
        query_rows = query_job.result(timeout=timeout // 1000)

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
        estimated_cost = str(estimated_cost.quantize(TO_CENTS, rounding=ROUND_UP))

        rows = parse_query_result(query_job, query_rows)

        if percent:
            rows = add_percentages(rows, include_sign=not json)

        if not json:
            click.echo('Served from cache: {}'.format(from_cache))
            click.echo('Data processed: {:.2f} {}'.format(processed_amount, processed_unit))
            click.echo('Data billed: {:.2f} {}'.format(billed_amount, billed_unit))
            click.echo('Estimated cost: ${}'.format(estimated_cost))

            click.echo()
            click.echo(tabulate(rows, markdown))
        else:
            query_info = {
                'cached': from_cache,
                'bytes_processed': bytes_processed,
                'bytes_billed': bytes_billed,
                'estimated_cost': estimated_cost,
            }
            click.echo(format_json(rows, query_info, indent))
    else:
        click.echo(built_query)

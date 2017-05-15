import click

from pypinfo.core import Query, create_client
from pypinfo.db import get_credentials, set_credentials

CONTEXT_SETTINGS = {
    'max_content_width': 300
}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('--package', '-p')
@click.pass_context
def pypinfo(ctx, package):
    pass


@pypinfo.command(context_settings=CONTEXT_SETTINGS)
@click.argument('path')
def creds(path):
    set_credentials(path)
    click.echo('Credentials location set to {}.'.format(get_credentials()))

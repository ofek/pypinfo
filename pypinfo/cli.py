import click

CONTEXT_SETTINGS = {
    'max_content_width': 300
}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('package', required=False)
@click.pass_context
def pypinfo(ctx, package):
    if ctx.invoked_subcommand is None and package is None:
        click.echo(ctx.get_help())
        return

    click.echo(package)

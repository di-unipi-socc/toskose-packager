import click

# from . import __name__
# from . import __version__

from app.toskose import Toskose
from app.common.commons import Alerts
from app.gui.interactive_cli import InteractiveCLI
from app.gui.effects import print_notification_cli


def handling_failure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print_notification_cli(err, Alerts.Failure)
    return wrapper

@click.group(invoke_without_command=True)
#@click.version_option(version=__version__)
@click.option('--quiet', '-q', is_flag=True, help='Give less output.')
@click.option('--debug', is_flag=True, help='Enable debug mode.')
@click.option('--interactive-cli', is_flag=True, help='Enable the interactive CLI.')
@click.pass_context
def cli(ctx, quiet, debug, interactive_cli):
    """
    test
    """

    ctx.obj = Toskose(debug=debug, quiet=quiet)

    if ctx.invoked_subcommand is None:
        if interactive_cli:
            InteractiveCLI().run()   
        else:
            click.echo(ctx.get_help())

@cli.command(name='validate')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@handling_failure
def validate(ctx, file):
    """ 
    test
    """

    validated = ctx.obj.validate(file=file)
    
    print_notification_cli('\u2713 Validated.', Alerts.Success) if validated \
            else print_notification_cli('\u274C Not Validated.', Alerts.Failure)
    
@cli.command(name='generate')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@click.option(
    '--orchestrator', 
    help='the target orchestrator',
    default='compose',
    show_default=True
)
@click.option(
    '--docker-url', 
    help='the URL for connecting to the Docker Engine',
    default='unix:///var/run/docker.sock',
    show_default=True
)
@handling_failure
def generate(ctx, file, orchestrator, docker_url):
    """
    test
    """

    res = ctx.obj.generate(
        file=file, 
        orchestrator=orchestrator,
        docker_url=docker_url)


if __name__ == '__main__':
    cli()
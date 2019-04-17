import click

# from . import __name__
# from . import __version__

#from app.toskose import Toskose
from app.toskoserizator import Toskoserizator
from app.common.commons import Alerts
from app.gui.effects import print_notification_cli


def handling_failure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            print_notification_cli(err, Alerts.Failure)
    return wrapper

@click.group()
#@click.version_option(version=__version__)
@click.option('--quiet', '-q', is_flag=True, help='Give less output.')
@click.option('--debug', is_flag=True, help='Enable debug mode.')
@click.pass_context
def cli(ctx, quiet, debug):
    """
    Description Soon
    """

    ctx.obj = Toskoserizator(debug=debug, quiet=quiet)

@cli.command(name='validate')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
@handling_failure
def validate(ctx, file):
    """ 
    Soon
    """

    print_notification_cli('Not implemented yet', Alerts.Warning)

    # validated = ctx.obj.validate(file=file)
    
    # print_notification_cli('\u2713 Validated.', Alerts.Success) if validated \
    #         else print_notification_cli('\u274C Not Validated.', Alerts.Failure)
    
@cli.command(name='toskoserize')
@click.pass_context
@click.argument(
    'csar_path', 
    type=click.Path(exists=True),
)
@click.option(
    '--docker-url', 
    help='The URL for the Docker Engine.',
    default='unix:///var/run/docker.sock',
    show_default=True
)
@click.option(
    '--output-path', '-o', 
    help='The path for the output.'
)
@handling_failure
def toskose(ctx, csar_path, output_path, docker_url):
    """
    Description Soon
    """

    ctx.obj.csar_path = csar_path
    if output_path:
        ctx.obj.output_path = output_path
    if docker_url:
        ctx.obj.docker_url = docker_url

    ctx.obj.toskosed()


if __name__ == '__main__':
    cli()
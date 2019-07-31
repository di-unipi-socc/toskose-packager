import click
from app.toskose import Toskoserizator


@click.command()
@click.argument(
    'csar_path', 
    type=click.Path(exists=True),
)
@click.argument(
    'config_path',
    type=click.Path(exists=True),
    required=False
)
@click.option(
    '--output-path', '-o', 
    help='The path for the output.'
)
@click.option(
    '--enable-push', '-p',
    is_flag=True,
    help='Enable pushing of Docker images.',
)
@click.option(
    '--docker-url', 
    help='The URL for the Docker Engine.',
    show_default=True
)
@click.option('--quiet', '-q', is_flag=True, help='Give less output.')
@click.option('--debug', is_flag=True, help='Enable debug mode.')
def cli(csar_path, config_path, output_path, enable_push, docker_url, quiet, debug):
    """
    A tool for translating a TOSCA application into docker-compose.
    """

    tsk = Toskoserizator(debug=debug, quiet=quiet)
    
    if docker_url:
        tsk.docker_url = docker_url

    tsk.toskosed(
        csar_path,
        config_path=config_path,
        output_path=output_path,
        enable_push=enable_push
    )
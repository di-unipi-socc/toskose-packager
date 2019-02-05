import click
from effects import print_cli


@click.command()
@click.option(
    '-f', '--file', 
    help='the path of the TOSCA .CSAR or .yml')
def main():
    print_cli("Toskose", color="blue", figlet=True)
    print_cli("version 0.1.0\n", color="yellow")


if __name__ == "__main__":
    main()
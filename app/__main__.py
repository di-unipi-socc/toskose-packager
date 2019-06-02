#!/usr/bin/env python
"""The main entry point. Invoke as `toskose' or `python -m toskose'. """

import sys

def main():
    try:
        from .gui.cli import cli
        sys.exit(cli())
    except KeyboardInterrupt:
        from . import ExitStatus
        sys.exit(ExitStatus.ERROR_CTRL_C)


if __name__ == '__main__':
    main()
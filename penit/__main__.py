"""Entry point for `python -m penit` and the `penit` console script."""

import sys


def main():
    from penit.app import PenItApp
    app = PenItApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()

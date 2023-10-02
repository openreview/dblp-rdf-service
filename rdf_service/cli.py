# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false

import click

from pprint import pprint

@click.command()
@click.option("--env", type=click.Choice(["test", "dev", "prod"]), required=True, help="Check that config is valid")
def config(env: str):
    """Ensure config is valid"""
    print(f"Checking env {env}")


def go():
    print("go!")


if __name__ == "__main__":
    go()

import click
from click.core import Context
from lib.predef.config import setenv


@click.group()
@click.pass_context
@click.option("--env", type=click.Choice(["test", "dev", "prod"]), default="dev", help="Check that config is valid")
def cli(ctx: Context, env: str):
    print(f"Env = {env}")
    setenv(env)
    ctx.ensure_object(dict)

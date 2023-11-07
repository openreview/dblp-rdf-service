import click
from click.core import Context
from lib.predef.config import Config, load_config, setenv
import typing as t


@click.group()
@click.pass_context
@click.option("--env", type=click.Choice(["test", "dev", "prod"]), default="dev", help="Check that config is valid")
def cli(ctx: Context, env: str):
    print(f"Env = {env}")
    setenv(env)
    set_config(ctx)
    if not get_config(ctx):
        print("No config found; exiting...")
        return


def get_config(ctx: Context) -> t.Optional[Config]:
    obj: t.Any = ctx.find_object(dict)
    return obj['config'] if obj else None

def set_config(ctx: Context):
    config = load_config()
    if not config:
        return

    obj: t.Any = ctx.ensure_object(dict)
    obj['config'] = config

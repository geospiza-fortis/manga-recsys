import click

from .metadata import metadata
from .models.group_manga import group_manga
from .models.manga import manga
from .models.tag_rules import tag_rules
from .parquet import parquet
from .sync import sync


@click.group()
def models():
    """Various models for recommending manga."""
    pass


for cmd in [tag_rules, group_manga, manga]:
    models.add_command(cmd)


@click.group()
def cli():
    pass


for cmd in [sync, parquet, metadata, models]:
    cli.add_command(cmd)

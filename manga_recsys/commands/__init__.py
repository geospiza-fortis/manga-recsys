import click

from .metadata_listing import metadata_listing
from .models.group_manga import group_manga
from .models.tag_rules import tag_rules
from .parquet import parquet


@click.group()
def models():
    """Various models for recommending manga."""
    pass


for cmd in [tag_rules, group_manga]:
    models.add_command(cmd)


@click.group()
def cli():
    pass


for cmd in [parquet, metadata_listing, models]:
    cli.add_command(cmd)

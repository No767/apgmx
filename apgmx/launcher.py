import typer

import asyncpg

# from ..migration import Migrations
import asyncio
import traceback
# from apgmx.upgrade_utils import run_upgrade, run_upgrade_all
from typing_extensions import Annotated
from migration import Migrations
from utils import run_upgrade, run_upgrade_all, ensure_uri_can_run
from db_settings import database_uri

app = typer.Typer(add_completion=False, help="apgmx is a asyncpg migration utility based off of RDanny's migration system")
migrateApp = typer.Typer(help="Commands for managing migrations")

app.add_typer(migrateApp, name="migrate")

@app.command()
def current():
    """Shows the current active revision version"""
    migrations = Migrations()
    typer.echo(f"Version {migrations.version}")


@app.command()
def log(reverse: Annotated[bool, typer.Option("--reverse", help="Print in reverse order (oldest first).")] = True):
    """Displays the revision history"""
    migrations = Migrations()
    # Revisions is oldest first already
    revs = (
        reversed(migrations.ordered_revisions)
        if not reverse
        else migrations.ordered_revisions
    )
    for rev in revs:
        as_yellow = typer.style(f"V{rev.version:>03}", fg="yellow")
        typer.secho(f'{as_yellow} {rev.description.replace("_", " ")}')
        
@migrateApp.command()
def init(reason: Annotated[str, typer.Option(help="The reason for this revision")] = "Initial migration") -> None:
    """Initializes the database and creates the initial revision"""

    asyncio.run(ensure_uri_can_run())

    migrations = Migrations()
    migrations.database_uri = database_uri  # type: ignore
    # migrations.database_uri = ""
    revision = migrations.create_revision(reason)
    typer.echo(f"created revision V{revision.version!r}")
    typer.secho(f"hint: use the `upgrade` command to apply", fg="yellow")
    
@migrateApp.command()
def new(reason: Annotated[str, typer.Option(help="The reason for this revision")]) -> None:
    """Creates a new revision for you to edit"""
    migrations = Migrations()
    if migrations.is_next_revision_taken():
        typer.echo(
            "an unapplied migration already exists for the next version, exiting"
        )
        typer.echo(
            "hint: apply pending migrations with the `upgrade` command"
        )
        return

    revision = migrations.create_revision(reason)
    typer.echo(f"Created revision V{revision.version!r}")
    
@migrateApp.command()
def latest(sql: Annotated[bool, typer.Option("--sql", help="Print the SQL instead of executing it")] = False) -> None:
    """Upgrades to the latest current revision"""
    migrations = Migrations()

    if sql:
        migrations.display()
        return

    try:
        applied = asyncio.run(run_upgrade(migrations))
    except Exception:
        traceback.print_exc()
        typer.secho("failed to apply migrations due to error", fg="red")
    else:
        typer.secho(f"Applied {applied} revisions(s)", fg="green")
        
@migrateApp.command()
def all(sql: Annotated[bool, typer.Option("--sql", help="Print the SQL instead of executing it")] = False) -> None:
    """Applies all revisions created"""
    migrations = Migrations()

    if sql:
        migrations.display()
        return

    try:
        applied = asyncio.run(run_upgrade_all(migrations))
    except Exception:
        traceback.print_exc()
        typer.secho("failed to apply migrations due to error", fg="red")
    else:
        typer.secho(f"Applied {applied} revisions(s)", fg="green")
        
if __name__ == "__main__":
    app()
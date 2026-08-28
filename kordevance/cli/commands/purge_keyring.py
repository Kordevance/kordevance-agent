import asyncio

import click

from kordevance.application.dependencies.credential_management import get_purge_keyring_use_case


@click.command(name="purge-keyring", help="Delete this gateway's credentials from the OS keyring.")
@click.option("--yes", "-y", is_flag=True, default=False)
def purge_keyring(yes: bool) -> None:
    if not yes:
        click.secho("[CAUTION] This is a destructive action.", fg="yellow", bold=True)
        click.echo("It deletes every credential Kordevance stored in the OS keyring.")
        click.echo()

        answer = click.prompt(
            click.style("Type ", fg="yellow")
            + click.style("PURGE", bold=True)
            + click.style(" to confirm, or press Enter to cancel", fg="yellow"),
            default="",
            show_default=False,
        )

        if answer != "PURGE":
            raise click.Abort()

    asyncio.run(get_purge_keyring_use_case().execute())
    click.secho("Keyring credentials purged.", fg="green", bold=True)

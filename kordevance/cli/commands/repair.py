import asyncio

import click

from kordevance.application.dependencies.pairing import get_pairing_service


@click.command(
    name="repair",
    help="Wipe all paired devices and reopen the gateway for a fresh owner claim.",
)
def repair() -> None:
    click.confirm(
        click.style("[CAUTION] ", fg="yellow", bold=True)
        + "This removes every currently paired device (owner and members alike) and any pending invites."
        + click.style(
            "\nNOTE: Everything else is kept: profiles, chat history, connectors, "
            "and all other gateway data are untouched.",
            bold=True,
        )
        + "\nA new claim code will be generated so you can pair a fresh owner device.\n"
        + "Continue?",
        abort=True,
    )

    code = asyncio.run(get_pairing_service().repair())
    if code is None:
        raise click.ClickException("Repair failed: a registered owner was still found after the wipe.")

    click.echo("Claim code: " + click.style(code, fg="yellow", bold=True))

import asyncio
import os

import click

from kordevance.application.dependencies.pairing import get_pairing_service
from kordevance.domain.services.pairing_service import PairingService


def _gateway_address() -> str:
    host = os.environ.get("KORDEVANCE_GATEWAY_HOST", "127.0.0.1")
    port = os.environ.get("KORDEVANCE_GATEWAY_PORT", "24680")
    return f"HOST={host}, PORT={port}"


async def _not_paired(service: PairingService) -> None:
    code = await service.peek_claim_code()
    click.secho("Status: ", nl=False, bold=True)
    click.echo("not paired")
    click.secho("Running at: ", nl=False, bold=True)
    click.echo(_gateway_address())

    if code is None:
        click.echo("No claim code found yet. Start the gateway to generate one.")
        return

    click.echo("Claim code: " + click.style(code, fg="yellow", bold=True))
    click.echo("Enter this in the gateway UI to register as owner.")


async def _paired(service: PairingService) -> None:
    devices = await service.list_devices()
    owners = sum(1 for device in devices if device.is_owner)
    members = len(devices) - owners

    click.secho("Status: ", nl=False, bold=True)
    click.echo("paired")
    click.secho("Running at: ", nl=False, bold=True)
    click.echo(_gateway_address())
    click.echo(f"{len(devices)} device(s) paired ({owners} owner, {members} member).")
    click.echo()
    click.echo(
        "Locked out? Run "
        + click.style("kordi repair", bold=True)
        + " to reclaim ownership, or "
        + click.style("kordi reset", bold=True)
        + " for a full wipe."
    )


async def _status() -> None:
    service = get_pairing_service()
    if await service.has_registered_owner():
        await _paired(service)
    else:
        await _not_paired(service)


@click.command(name="status", help="Show the gateway's pairing status.")
def status() -> None:
    asyncio.run(_status())

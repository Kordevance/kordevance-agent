import hmac
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from kordevance.domain.datetime_utils import as_aware_utc
from kordevance.domain.models.paired_device import PairedDevice
from kordevance.domain.ports.claim_code_store import ClaimCodeStore
from kordevance.domain.ports.paired_device_repository import PairedDeviceRepo
from kordevance.domain.ports.pairing_invite_repository import PairingInviteRepo
from kordevance.domain.security_utils import generate_device_token, generate_pairing_code, hash_secret
from kordevance.exceptions import UnauthorizedError

_INVITE_TTL_MINUTES: int = 15


class PairingService:
    def __init__(
        self,
        paired_device_repo: PairedDeviceRepo,
        pairing_invite_repo: PairingInviteRepo,
        claim_code_store: ClaimCodeStore,
    ) -> None:
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._paired_device_repo: PairedDeviceRepo = paired_device_repo
        self._pairing_invite_repo: PairingInviteRepo = pairing_invite_repo
        self._claim_code_store: ClaimCodeStore = claim_code_store

    async def has_registered_owner(self) -> bool:
        return await self._paired_device_repo.exists_any()

    async def get_or_create_claim_code(self) -> str:
        return self._claim_code_store.get_or_create()

    async def register(self, code: str) -> str:
        if not await self._paired_device_repo.exists_any():
            return await self._register_owner(code)
        return await self._register_invitee(code)

    async def _register_owner(self, code: str) -> str:
        expected = self._claim_code_store.get_or_create()
        if not hmac.compare_digest(expected, code):
            self._logger.warning("Rejected owner registration attempt: invalid claim code")
            raise UnauthorizedError("Invalid claim code")

        token = generate_device_token()
        await self._paired_device_repo.create(token_hash=hash_secret(token), is_owner=True)
        self._claim_code_store.invalidate()
        self._logger.info("Owner device registered")
        return token

    async def _register_invitee(self, code: str) -> str:
        candidate_hash = hash_secret(code)
        now = datetime.now(UTC)

        for invite in await self._pairing_invite_repo.fetch_live():
            if not hmac.compare_digest(invite.code_hash, candidate_hash):
                continue
            if as_aware_utc(invite.expires_at) < now:
                await self._pairing_invite_repo.delete(invite.id)
                break

            token = generate_device_token()
            await self._paired_device_repo.create(token_hash=hash_secret(token), is_owner=False)
            await self._pairing_invite_repo.delete(invite.id)
            self._logger.info("Device paired via invite")
            return token

        self._logger.warning("Rejected device registration attempt: invalid or expired pairing code")
        raise UnauthorizedError("Invalid or expired pairing code")

    async def create_invite(self) -> str:
        code = generate_pairing_code()
        expires_at = datetime.now(UTC) + timedelta(minutes=_INVITE_TTL_MINUTES)
        await self._pairing_invite_repo.create(code_hash=hash_secret(code), expires_at=expires_at)
        return code

    async def list_devices(self) -> list[PairedDevice]:
        return await self._paired_device_repo.fetch_all()

    async def promote(self, device_id: UUID) -> None:
        await self._paired_device_repo.set_owner(device_id, True)

    async def authenticate(self, token: str) -> PairedDevice:
        device = await self._paired_device_repo.get_by_token_hash(hash_secret(token))
        if device is None:
            raise UnauthorizedError("Invalid or missing device token")
        return device

from kordevance.domain.contracts.keyring_purgeable import KeyringPurgeable
from kordevance.domain.contracts.use_case import UseCase


class HandlePurgeKeyring(UseCase[None, None]):
    def __init__(self, purgeables: list[KeyringPurgeable]) -> None:
        self._purgeables: list[KeyringPurgeable] = purgeables

    async def execute(self, request: None = None) -> None:
        for purgeable in self._purgeables:
            purgeable.purge_keyring()

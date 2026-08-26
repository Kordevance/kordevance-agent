from kordevance.application.dependencies.secret_store_adapter import get_credential_manager
from kordevance.domain.contracts.keyring_purgeable import KeyringPurgeable
from kordevance.domain.services.device_service import DeviceService
from kordevance.domain.use_cases.credential_management.handle_purge_keyring import HandlePurgeKeyring


def get_keyring_purgeables() -> list[KeyringPurgeable]:
    return [
        DeviceService(store=get_credential_manager()),
    ]


def get_purge_keyring_use_case() -> HandlePurgeKeyring:
    return HandlePurgeKeyring(purgeables=get_keyring_purgeables())

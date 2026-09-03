from abc import ABC, abstractmethod

from kordevance.domain.models.device_registration import DeviceRegistration


class DeviceRegistrationRepo(ABC):
    @abstractmethod
    async def get(self) -> DeviceRegistration | None:
        """Return the record of this installation's one-time ProxyRelay registration, if it ever happened."""
        ...

    @abstractmethod
    async def save(self, device_id: str) -> None:
        """Mark this installation as having registered device_id with ProxyRelay. Idempotent per installation."""
        ...

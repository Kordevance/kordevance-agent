from cryptography.fernet import Fernet

from kordevance.domain.ports.encryptor import Encryptor


class FernetEncryptor(Encryptor):
    def __init__(self, key: bytes) -> None:
        self._fernet: Fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")

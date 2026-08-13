from abc import ABC, abstractmethod


class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str: ...
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str: ...

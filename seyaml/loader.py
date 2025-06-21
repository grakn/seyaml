import yaml
import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def parse_key_with_index(value: str):
    if value.endswith("]") and "[" in value:
        bracket_pos = value.rfind("[")
        key = value[:bracket_pos]
        index_part = value[bracket_pos + 1 : -1]
        if not index_part.isdigit():
            raise ValueError(f"Invalid index in: '{value}'")
        return key, int(index_part)
    return value, None


class SeYamlLoader(yaml.SafeLoader):
    """YAML loader with !secret, !env, and !enc tag support."""

    def __init__(self, stream, secrets=None, decryption_key: Optional[bytes] = None):
        super().__init__(stream)
        self.secrets = secrets or {}
        self.decryption_key = decryption_key

        self.add_constructor("!secret", self._construct_secret)
        self.add_constructor("!env", self._construct_env)
        self.add_constructor("!enc", self._construct_encrypted)

    def _construct_secret(self, loader, node):
        raw = loader.construct_scalar(node)
        key, index = parse_key_with_index(raw)
        if key != key.lower():
            raise ValueError(f"!secret key '{key}' must be lowercase")
        if key not in self.secrets:
            raise ValueError(f"Secret '{key}' not found")
        value = self.secrets[key]
        if index is not None:
            parts = str(value).split(",")
            try:
                return parts[index].strip()
            except IndexError:
                raise ValueError(f"Index {index} out of range for secret '{key}'")
        return value

    def _construct_env(self, loader, node):
        raw = loader.construct_scalar(node)
        key, index = parse_key_with_index(raw)
        if key != key.upper():
            raise ValueError(f"!env key '{key}' must be uppercase")
        if key not in os.environ:
            raise ValueError(f"Environment variable '{key}' not found")
        value = os.environ[key]
        if index is not None:
            parts = value.split(",")
            try:
                return parts[index].strip()
            except IndexError:
                raise ValueError(f"Index {index} out of range for env variable '{key}'")
        return value

    def _construct_encrypted(self, loader, node):
        b64_ciphertext = loader.construct_scalar(node)
        if not self.decryption_key:
            raise ValueError("No decryption key provided for !enc")
        try:
            raw = base64.b64decode(b64_ciphertext)
        except Exception as e:
            raise ValueError(f"Invalid base64 for !enc value: {e}")

        nonce = raw[:12]
        ciphertext = raw[12:]
        aesgcm = AESGCM(self.decryption_key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to decrypt AES-GCM data: {e}")


def load_seyaml(path: str, secrets: dict = None, decryption_key: bytes = None) -> dict:
    """Load YAML file with support for !secret, !env, and !enc tags."""
    with open(path, 'r') as f:
        return yaml.load(f, Loader=lambda stream: SeYamlLoader(stream, secrets, decryption_key))

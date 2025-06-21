import click
import base64
import secrets
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_value(plaintext: str, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

def decrypt_value(ciphertext_b64: str, key: bytes) -> str:
    raw = base64.b64decode(ciphertext_b64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")

@click.group()
def cli():
    """seyaml encryption CLI"""
    pass

@cli.command()
def generate_key():
    """Generate a secure 32-byte (256-bit) base64 encoded AES key."""
    key_bytes = secrets.token_bytes(32)
    click.echo(base64.b64encode(key_bytes).decode("utf-8"))

@cli.command()
@click.argument("value")
@click.option("--key", required=True, help="Encryption key as base64 string (32 bytes)")
def encrypt(value, key):
    """Encrypt a plaintext string to AES-GCM base64"""
    try:
        key_bytes = base64.b64decode(key)
        if len(key_bytes) != 32:
            raise ValueError("Key must be 32 bytes (base64 decoded)")
        result = encrypt_value(value, key_bytes)
        click.echo(result)
    except Exception as e:
        click.echo(f"Encryption failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("value")
@click.option("--key", required=True, help="Encryption key as base64 string (32 bytes)")
def decrypt(value, key):
    """Decrypt an AES-GCM base64 string to plaintext"""
    try:
        key_bytes = base64.b64decode(key)
        if len(key_bytes) != 32:
            raise ValueError("Key must be 32 bytes (base64 decoded)")
        result = decrypt_value(value, key_bytes)
        click.echo(result)
    except Exception as e:
        click.echo(f"Decryption failed: {e}", err=True)
        sys.exit(2)

if __name__ == "__main__":
    cli()

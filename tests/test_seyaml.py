import os
import base64
import tempfile
import pytest
from click.testing import CliRunner
from seyaml.loader import load_seyaml, SeYamlLoader
from seyaml.cli import cli
import yaml

# Sample secrets and env for testing
SECRETS = {
    "api_key": "key1,key2,key3",
    "simple": "value"
}

os.environ["TEST_ENV"] = "ENVVALUE"

# 256-bit key for tests
TEST_KEY_BYTES = b"\x00" * 32
TEST_KEY_BASE64 = base64.b64encode(TEST_KEY_BYTES).decode()

@pytest.fixture
def yaml_content():
    return """
secret_val: !secret simple
secret_indexed: !secret api_key[1]
env_val: !env TEST_ENV
enc_val: !enc {enc_value}
"""

def test_parse_and_load_yaml(tmp_path, yaml_content):
    # Prepare encrypted value for "hello world"
    from seyaml.cli import encrypt_value
    encrypted = encrypt_value("hello world", TEST_KEY_BYTES)

    content = yaml_content.format(enc_value=encrypted)
    file = tmp_path / "config.yaml"
    file.write_text(content)

    loaded = load_seyaml(str(file), secrets=SECRETS, decryption_key=TEST_KEY_BYTES)

    assert loaded["secret_val"] == "value"
    assert loaded["secret_indexed"] == "key2"
    assert loaded["env_val"] == "ENVVALUE"
    assert loaded["enc_val"] == "hello world"

def test_index_reference_with_comma_separated_values(monkeypatch):
    # Set ENV var as comma-separated
    monkeypatch.setenv("CSV_ENV", "alpha,beta,gamma")

    # Set secret as comma-separated string
    secrets = {
        "csv_secret": "red,green,blue"
    }

    yaml_text = """
    env_item: !env CSV_ENV[1]
    secret_item: !secret csv_secret[2]
    """

    config = yaml.load(yaml_text, Loader=lambda stream: SeYamlLoader(stream, secrets))

    assert config["env_item"] == "beta"
    assert config["secret_item"] == "blue"

def test_secret_key_casing():
    loader = SeYamlLoader(stream="", secrets={"lowercase": "ok"})
    node = yaml.ScalarNode(tag="!secret", value="Api_Key")  # use real YAML node
    with pytest.raises(ValueError):
        loader._construct_secret(loader, node)

def test_env_key_casing():
    loader = SeYamlLoader(stream="")
    node = yaml.ScalarNode(tag="!env", value="test_env")
    with pytest.raises(ValueError):
        loader._construct_env(loader, node)

def test_cli_generate_key():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate-key"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0

def test_cli_encrypt_decrypt():
    runner = CliRunner()
    key = TEST_KEY_BASE64

    plaintext = "my secret data"
    enc_result = runner.invoke(cli, ["encrypt", plaintext, "--key", key])
    assert enc_result.exit_code == 0
    ciphertext = enc_result.output.strip()

    dec_result = runner.invoke(cli, ["decrypt", ciphertext, "--key", key])
    assert dec_result.exit_code == 0
    assert dec_result.output.strip() == plaintext

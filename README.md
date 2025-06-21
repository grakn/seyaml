# seyaml

`seyaml` is a Python YAML loader and CLI tool supporting custom tags:

- `!env VAR` — load environment variable, supports indexing like `!env VAR[0]` for comma separated values
- `!secret key` — load secret from a provided dictionary, supports indexing like `!secret api_key[1]` for comma separated values
- `!enc ENCRYPTED_VALUE` — decrypt AES-256-GCM encrypted base64 string with a provided key

You could you any combination of features, they all optional.

### Constraints
* env variables always UPPERCASE strings
* secret values always lowercase strings
* env values always Base64 strings

## Installation

```bash
pip install seyaml
```

## Usage

### Python API
```
from seyaml.loader import load_seyaml
import base64

secrets = {
    "api_key": "key1,key2,key3",
    "simple": "value"
}

decryption_key = base64.b64decode("YOUR_BASE64_32_BYTE_KEY")

config = load_seyaml("config.yaml", secrets=secrets, decryption_key=decryption_key)
print(config)
```

### YAML Example
```
database:
  url: !secret simple
  token: !secret api_key[2]
  user: !env DB_USER
  password: !enc gN0jA1u+9aC9X9DkR3ABxF3P5pSXXTFsm/u5yH7sy94gQ==
```

### CLI Usage

Generate a secure AES-256 key (base64 encoded):

```
seyaml generate-key
```

Encrypt plaintext:

```
seyaml encrypt "my secret text" --key YOUR_BASE64_KEY
```

Decrypt ciphertext:

```
seyaml decrypt ENCRYPTED_BASE64_STRING --key YOUR_BASE64_KEY
```

## Komatsu IDM backend configuration and information

## Module description

Komatsu Identity Management instantiates clients for Entra and Palantir SDK clients to be used with other Komatsu modules


## Important information

In order to use this module, make sure you have the Komatsu source configured in your project's Pipfile and the `dev_mykomatsu_sdk` defined like below:

```text
[[source]]
verify_ssl = true
url = "https://$FOUNDRY_SDK_AUTH_TOKEN@komatsu.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.2018cb2f-42cf-401d-a014-ea3a006cfa0d/contents/release/pypi/simple/"
name = "komatsu"

[packages]
...
dev-mykomatsu-sdk = {version = "*", index = "komatsu"}
# Other packages...
```

## Features

- [ ] This module includes migrations.
- [x] This module includes environment variables.
- [x] This module requires manual configurations.
- [ ] This module can be configured with module options.

## Environment variables

- For EntraAD

```dotenv
CLIENT_ID_ENTRA=""
CLIENT_SECRET_ENTRA=""
TENANT_ID_ENTRA=""
```

- For Palantir

```dotenv
CLIENT_ID=""
CLIENT_SECRET=""
PALANTIR_HOSTNAME=""
```

- For Sendgrid

```dotenv
SENDGRID_TEMPLATE_ID=""
SENDGRID_API_KEY=""
```
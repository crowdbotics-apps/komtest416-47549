# Komatsu Data Module - Customer

## Module description

Komatsu Data Module - Customer wraps Palantir SDK and provide information about Customer data

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

## Module dependency

This module depends on:

- [x] Komatsu's IDM module
- [x] Komatsu's Common Permissions module

## Features

- [ ] This module includes migrations.
- [ ] This module includes environment variables.
- [ ] This module requires manual configurations.
- [ ] This module can be configured with module options.

# Credentials / Referências de Credenciais

Esta pasta contém **apenas referências** para credenciais armazenadas em gerenciadores seguros.

## ⚠️ IMPORTANTE

**NUNCA** armazene secrets, passwords, API keys, tokens, private keys ou qualquer dado sensível nesta pasta.

## Estrutura

Cada referência é um arquivo YAML:

```
credentials/
├── CRED-0001.yaml
├── CRED-0002.yaml
└── ...
```

## Schema da Referência (Canônico)

```yaml
credential_id: "CRED-0001"
provider: "1password"              # 1password, bitwarden, keepass, etc.
reference: "vercel/email-007"      # identificador opaco no gerenciador
related_entity: "ACCOUNT-0007"     # ID da entidade no vault que usa esta credencial
type: "api_key"                    # api_key, password, token, ssh_key, etc.
description: "Vercel production account access"
verification:
  status: "VERIFIED"               # VERIFIED, UNVERIFIED, STALE, UNKNOWN, CONFLICT
  source_type: "manual"            # manual, api, email, file, screenshot, import, platform, inferred, other
  source_ref: "user-provided"
  discovered_at: "2026-09-26T00:00:00Z"
  last_verified: "2026-09-26T00:00:00Z"
  confidence: 0.9
created_at: "2026-09-26T00:00:00Z"
updated_at: "2026-09-26T00:00:00Z"
```

## Campos

| Campo | Obrigatório | Descrição |
|---|---|---|
| `credential_id` | Sim | ID único no formato CRED-NNNN |
| `provider` | Sim | Gerenciador de credenciais |
| `reference` | Sim | Identificador opaco no gerenciador (NUNCA o secret) |
| `related_entity` | Sim | ID da entidade no vault que usa esta credencial |
| `type` | Sim | Tipo de credencial |
| `description` | Não | Descrição livre (sanitizada) |
| `verification` | Sim | Status de verificação (ver `core/VERIFICATION.md`) |
| `created_at` | Sim | Data de criação (ISO 8601 UTC) |
| `updated_at` | Sim | Data da última atualização (ISO 8601 UTC) |

## Tipos de Credencial Comuns

- `api_key`
- `password`
- `access_token`
- `refresh_token`
- `ssh_key`
- `private_key`
- `database_credentials`
- `webhook_secret`
- `oauth_client_secret`
- `2fa_recovery_codes`

## Uso nas Entidades (Formato Canônico Único)

Entidades em `entities/` referenciam credenciais **exclusivamente** via `credential_ref` estruturado:

```yaml
credential_ref:
  credential_id: "CRED-0001"
  provider: "1password"
  reference: "vercel/email-007"
  related_entity: "ACCOUNT-0007"
```

Quando não houver credencial associada:
```yaml
credential_ref: null
```

**PROIBIDO** formatos alternativos:
```yaml
credential_ref: "1password/vercel/email-007"  # string simples - NÃO USE
credential_ref: "CRED-0001"                    # apenas ID - NÃO USE
credential_id: "CRED-0001"                     # campo solto - NÃO USE
```

## Auditoria

Auditorias devem verificar:

1. **Estrutura correta**: `credential_ref` é objeto com 4 campos obrigatórios ou `null`
2. **CRED-ID válido**: `credential_id` existe em `credentials/CRED-XXXX.yaml`
3. **Referência correspondente**: arquivo de credencial existe e `related_entity` bate
4. **Related_entity existente**: entidade referenciada existe em `entities/`
5. **Ausência de padrão semelhante a secret**: `reference` não contém `sk-`, `ghp_`, `Bearer`, `eyJ`, `BEGIN PRIVATE KEY`, `password=`, `token=`, `api_key=`

Detecção defensiva — nunca registrar valor completo encontrado.

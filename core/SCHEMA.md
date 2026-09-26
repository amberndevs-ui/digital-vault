# Core / Schema

Schema canônico que todos os recursos do Digital Vault devem seguir.

## Campos Obrigatórios (quando aplicável)

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | string | Identificador interno único (ex: EMAIL-0001, ACCOUNT-0007) |
| `type` | string | Tipo da entidade (ex: email, account, project, domain…) |
| `name` | string | Nome ou identificador humano-legível |
| `status` | string | Status operacional (ex: active, inactive, suspended, archived, deleted, unknown) |
| `platform` | string | Plataforma ou provedor (ex: vercel, github, supabase, gmail, meta, whatsapp) |
| `relationships` | array | Lista de objetos de relacionamento estruturados |
| `verification` | object | Metadados de verificação (source_type, source_ref, discovered_at, last_verified, status, confidence) |
| `credential_ref` | object/null | Referência estruturada à credencial (nunca o secret) |
| `notes` | string | Observações livres (sanitizadas) |
| `created_at` | string | Data de criação no vault (ISO 8601 UTC) |
| `updated_at` | string | Data da última atualização (ISO 8601 UTC) |

## Estrutura de Relacionamento (canônica)

```yaml
relationships:
  - to: "ACCOUNT-0007"
    type: "belongs_to"
    valid_from: "2026-01-15T00:00:00Z"    # opcional, null = desconhecido/aberto
    valid_until: null                      # opcional, null = atual/aberto
    # metadados opcionais:
    # role: "primary"
    # primary: true
    # source: "api:vercel"
    # confidence: 0.95
```

- `type`: deve usar vocabulário controlado (ver RELATIONSHIPS.md)
- `valid_from`/`valid_until`: ISO 8601 UTC ou null
- Relacionamentos históricos NÃO são removidos quando expiram; mantêm-se com `valid_until` preenchido

## Estrutura de Verificação (canônica)

```yaml
verification:
  status: "VERIFIED"              # VERIFIED, UNVERIFIED, STALE, UNKNOWN, CONFLICT
  source_type: "api"              # manual, api, email, file, screenshot, import, platform, inferred, other
  source_ref: "vercel"            # referência sanitizada (ex: plataforma, arquivo, id do inbox)
  discovered_at: "2026-09-01T10:00:00Z"
  last_verified: "2026-09-25T14:30:00Z"
  confidence: 0.95                # opcional, 0.0 a 1.0
```

- `source_type` usa vocabulário controlado
- `source_ref` NUNCA contém secrets, tokens, URLs com auth
- `confidence` não substitui `status`; INFERRED nunca vira VERIFIED apenas por inferência

## Estrutura de Credential Ref (canônica)

```yaml
credential_ref:
  credential_id: "CRED-0001"      # ID no vault de credenciais
  provider: "1password"           # 1password, bitwarden, keepass, etc.
  reference: "vercel/email-007"   # identificador opaco no gerenciador
  related_entity: "ACCOUNT-0007"  # entidade que usa esta credencial
```

Quando não houver credencial associada:
```yaml
credential_ref: null
```

**NUNCA** usar formatos alternativos (string simples, apenas credential_id, etc.)

## Campos Desconhecidos

Campos desconhecidos devem ser representados explicitamente como `UNKNOWN` quando apropriado.

**NUNCA** inventar valores para completar o schema.

## Campos Especializados por Tipo

Tipos especializados podem adicionar campos próprios sem quebrar o schema central:

| Tipo | Campos Adicionais |
|---|---|
| SIM | `operator`, `line_type` |
| Ad Account | `ad_account_id`, `currency` |
| Domain | `registrar`, `expires_at`, `nameservers` |
| Server | `ip`, `os`, `provider` |
| API | `base_url`, `auth_type` |
| Billing | `plan`, `cycle`, `amount_ref` |
| WhatsApp | `phone_number`, `waba_id` |
| Pixel | `pixel_id`, `domain_id` |
| Business Manager | `bm_id`, `industry` |
| Repository | `visibility`, `language` |
| Device | `os`, `model`, `imei_ref` |

Todos os tipos continuam obedecendo ao núcleo comum.

## Exemplo de Entidade Completa

```yaml
id: EMAIL-0001
type: email
name: "vinic@example.com"
status: active
platform: gmail
relationships:
  - to: "ACCOUNT-0007"
    type: "belongs_to"
    valid_from: "2026-01-01T00:00:00Z"
    valid_until: null
verification:
  status: "VERIFIED"
  source_type: "manual"
  source_ref: "user-provided"
  discovered_at: "2026-09-01T10:00:00Z"
  last_verified: "2026-09-25T14:30:00Z"
  confidence: 0.95
credential_ref:
  credential_id: "CRED-0001"
  provider: "1password"
  reference: "gmail/email-001"
  related_entity: "EMAIL-0001"
notes: ""
created_at: "2026-09-01T10:00:00Z"
updated_at: "2026-09-25T14:30:00Z"
```

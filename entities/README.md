# Entities

Entidades do mundo real organizadas por tipo.

Cada entidade é um arquivo YAML seguindo o schema em `core/SCHEMA.md`.

## Estrutura de Diretórios

```
entities/
├── emails/
├── accounts/
├── organizations/
├── projects/
├── domains/
├── repositories/
├── servers/
├── phones/
├── sims/
├── devices/
└── billing/
```

## Convenção de Nomes de Arquivos

`ID-ENTIDADE.yaml` (ex: `EMAIL-0001.yaml`, `ACCOUNT-0007.yaml`)

## Tipos de Entidade

| Diretório | Tipo | Prefixo ID |
|---|---|---|
| `emails/` | email | `EMAIL` |
| `accounts/` | account | `ACCOUNT` |
| `organizations/` | organization | `ORG` |
| `projects/` | project | `PROJECT` |
| `domains/` | domain | `DOMAIN` |
| `repositories/` | repository | `REPO` |
| `servers/` | server | `SERVER` |
| `phones/` | phone | `PHONE` |
| `sims/` | sim | `SIM` |
| `devices/` | device | `DEVICE` |
| `billing/` | billing | `BILLING` |

## Exemplo Mínimo

```yaml
id: EMAIL-0001
type: email
name: "exemplo@dominio.com"
status: active
platform: gmail
relationships: []
verification:
  source: "manual"
  discovered_at: "2026-09-26T00:00:00Z"
  last_verified: "2026-09-26T00:00:00Z"
  verification_status: "UNVERIFIED"
credential_ref:
  provider: "1password"
  reference: "gmail/email-001"
  related_entity: "EMAIL-0001"
notes: ""
created_at: "2026-09-26T00:00:00Z"
updated_at: "2026-09-26T00:00:00Z"
```

## Campos Específicos por Tipo

Consultar `core/SCHEMA.md` para campos adicionais permitidos por tipo.

## Deduplicação

Antes de criar novo arquivo em `entities/`:

1. Buscar correspondência existente por identificadores conhecidos
2. Se EXISTING → atualizar arquivo existente
3. Se NEW → criar novo ID e arquivo
4. Se UNCERTAIN → colocar em `inbox/`
5. Se CONFLICT → registrar em `logs/conflicts/`
# Discovery Template

Template para itens na Inbox (área de quarentena).

**Arquivo:** `inbox/YYYY-MM-DD-descrição-curta.yaml`

```yaml
inbox_id: "INBOX-2026-09-26-001"
source: "manual"                           # manual, api:vercel, api:github, email, screenshot, clipboard
discovered_at: "2026-09-26T15:30:00Z"
raw_data:                                  # Dados brutos exatamente como descobertos
  platform: "vercel"
  email: "usuario@exemplo.com"
  account_name: "usuario@exemplo.com"
  project_name: "meu-projeto"
  deployment_url: "https://meu-projeto.vercel.app"
  github_repo: "usuario/meu-projeto"
  # ... quaisquer outros campos descobertos

possible_entities:                         # Hipóteses de entidades que podem existir
  - type: "email"
    identifier: "usuario@exemplo.com"
    confidence: 0.9
  - type: "account"
    platform: "vercel"
    name: "usuario@exemplo.com"
    confidence: 0.8
  - type: "project"
    name: "meu-projeto"
    platform: "vercel"
    confidence: 0.85
  - type: "repository"
    name: "usuario/meu-projeto"
    platform: "github"
    confidence: 0.7

status: "UNCERTAIN"                        # UNCERTAIN, PROCESSING, RESOLVED, CONFLICT
resolution: null                           # Preenchido ao resolver:
# resolution:
#   action: "merged"                       # merged, created_new, updated_existing, rejected
#   entities_created:
#     - "EMAIL-0003"
#     - "ACCOUNT-0007"
#     - "PROJECT-0004"
#   entities_updated:
#     - "EMAIL-0003"
#   relationships_created:
#     - { from: "EMAIL-0003", to: "ACCOUNT-0007", type: "belongs_to" }
#   notes: "Email já existia como EMAIL-0003, conta Vercel criada como ACCOUNT-0007"

notes: "Descoberto via email de notificação de deploy do Vercel"
processed_at: null
processed_by: null
```

---

## Status do Item

| Status | Significado | Próxima Ação |
|---|---|---|
| `UNCERTAIN` | Recém-chegado, precisa análise | Normalizar + Dedupe |
| `PROCESSING` | Sendo trabalhado | Completar análise |
| `RESOLVED` | Transformado em entidade(s) canônica(s) | Mover para `inbox/processed/` |
| `CONFLICT` | Conflito com entidade existente | Registrar em `logs/conflicts/` |

---

## Fluxo de Processamento

```
1. CRIAR item em inbox/ com status UNCERTAIN
2. NORMALIZAR raw_data para schema core
3. DEDUPE: buscar em entities/ por identificadores
   - email → entities/emails/
   - account → entities/accounts/
   - etc.
4. DECIDIR:
   - EXISTING → resolution.action = "merged" ou "updated_existing"
   - NEW → resolution.action = "created_new"
   - UNCERTAIN → manter em inbox, aguardar mais evidências
   - CONFLICT → resolution.action = "conflict", registrar em logs/conflicts/
5. CRIAR/ATUALIZAR entidades em entities/
6. CRIAR relacionamentos
7. REGISTRAR em logs/discoveries/
8. MARCAR inbox item como RESOLVED
9. MOVER para inbox/processed/ (opcional)
```

---

## Exemplo de Resolução Completa

```yaml
resolution:
  action: "merged"
  entities_created:
    - "ACCOUNT-0012"
    - "PROJECT-0008"
  entities_updated:
    - "EMAIL-0003"
  relationships_created:
    - { from: "EMAIL-0003", to: "ACCOUNT-0012", type: "belongs_to" }
    - { from: "ACCOUNT-0012", to: "PROJECT-0008", type: "hosts" }
  notes: "EMAIL-0003 já existia. Conta Vercel e projeto criados novos. Relacionamentos estabelecidos."
processed_at: "2026-09-26T16:00:00Z"
processed_by: "manual"
status: "RESOLVED"
```
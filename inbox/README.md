# Inbox / Área de Quarentena

Área para descobertas sanitizadas ainda não resolvidas, não verificadas ou com identidade incerta.

## Princípio Fundamental

**Inbox É persistência.** Portanto dados brutos NÃO podem ser gravados nela antes da sanitização.

Itens com status **UNCERTAIN** não entram diretamente na fonte de verdade (`entities/`).

## Pipeline Obrigatório de Entrada

```
CAPTURAR (dados brutos em memória/temporário)
    ↓
CLASSIFICAR
    ↓
DETECTAR SENSÍVEL (regex, patterns)
    ↓
SANITIZAR (remover/mascarar secrets)
    ↓
VALIDAR SANITIZAÇÃO
    ↓
SOMENTE ENTÃO PERSISTIR NA INBOX
    ↓
NORMALIZAÇÃO
    ↓
DEDUPE
    ↓
VERIFICAÇÃO
    ↓
ENTIDADE CANÔNICA (entities/)
    ↓
RELACIONAMENTOS
    ↓
LOG (logs/discoveries/)
```

Se não puder garantir sanitização completa: **NÃO PERSISTIR NA INBOX**.

## Estrutura

```
inbox/
├── YYYY-MM-DD-description.yaml
├── ...
└── processed/           # itens já resolvidos (opcional, para histórico)
```

## Schema do Item de Inbox (Sanitizado)

```yaml
inbox_id: "INBOX-2026-09-26-001"
source_type: "email"                   # manual, api, email, file, screenshot, import, platform, inferred, other
source_ref: "deploy-notification"      # referência sanitizada (NUNCA token/URL com auth)
discovered_at: "2026-09-26T15:30:00Z"
sanitized: true                        # OBRIGATÓRIO: confirma que passou por sanitização
normalized_data:                       # dados JÁ normalizados para schema core (não raw)
  platform: "vercel"
  email: "usuario@exemplo.com"         # já normalizado (lowercase domain)
  account_name: "usuario@exemplo.com"
  project_name: "meu-projeto"
  deployment_url: "https://meu-projeto.vercel.app"
  github_repo: "usuario/meu-projeto"
possible_entities:                     # hipóteses de entidades relacionadas
  - type: "email"
    identifier: "usuario@exemplo.com"  # já normalizado
    confidence: 0.9
  - type: "account"
    platform: "vercel"
    name: "usuario@exemplo.com"
    confidence: 0.8
  - type: "project"
    name: "meu-projeto"
    platform: "vercel"
    confidence: 0.85
status: "UNCERTAIN"                    # UNCERTAIN, PROCESSING, RESOLVED, CONFLICT
resolution: null                       # preenchido ao resolver
notes: "Descoberto via email de notificação de deploy do Vercel"  # sanitizado
processed_at: null
processed_by: null
```

### Campos Obrigatórios

| Campo | Descrição |
|---|---|
| `inbox_id` | ID único formato INBOX-YYYY-MM-DD-NNN |
| `source_type` | Vocabulário controlado (ver VERIFICATION.md) |
| `source_ref` | Referência sanitizada (ex: "vercel", "github", "inbox:INBOX-001", "user-provided") |
| `discovered_at` | ISO 8601 UTC |
| `sanitized` | **boolean, obrigatório, deve ser `true`** |
| `normalized_data` | Dados já normalizados (não raw_data) |
| `possible_entities` | Hipóteses com identificadores normalizados |
| `status` | UNCERTAIN, PROCESSING, RESOLVED, CONFLICT |

### PROIBIDO no Inbox

- `raw_data` ou qualquer campo com dados não sanitizados
- `sanitized: false` ou ausência do campo
- `source_ref` contendo tokens, URLs com auth, headers Authorization
- `notes` com secrets, API keys, passwords

## Status do Item

| Status | Significado | Próxima Ação |
|---|---|---|
| `UNCERTAIN` | Recém-chegado, precisa análise | Normalizar + Dedupe |
| `PROCESSING` | Sendo trabalhado | Completar análise |
| `RESOLVED` | Transformado em entidade(s) canônica(s) | Mover para `inbox/processed/` |
| `CONFLICT` | Conflito com entidade existente | Registrar em `logs/conflicts/` |

## Resolução

Ao processar um item de inbox:

1. **Validar** — confirmar `sanitized: true` e `normalized_data` presente
2. **Dedupe** — buscar em `entities/` por correspondência usando chaves de identidade (ver NAMING.md)
3. **Decidir**:
   - `EXISTING` → atualizar entidade existente
   - `NEW` → criar nova entidade com novo ID
   - `UNCERTAIN` → manter em inbox, aguardar mais evidências
   - `CONFLICT` → registrar em `logs/conflicts/`
4. **Registrar** — log em `logs/discoveries/`
5. **Mover** — mover para `inbox/processed/` ou remover

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
    - { from: "EMAIL-0003", to: "ACCOUNT-0012", type: "belongs_to", valid_from: "2026-09-26T00:00:00Z", valid_until: null }
    - { from: "ACCOUNT-0012", to: "PROJECT-0008", type: "hosts", valid_from: "2026-09-26T00:00:00Z", valid_until: null }
  notes: "EMAIL-0003 já existia. Conta Vercel e projeto criados novos. Relacionamentos estabelecidos."
processed_at: "2026-09-26T16:00:00Z"
processed_by: "manual"
status: "RESOLVED"
```

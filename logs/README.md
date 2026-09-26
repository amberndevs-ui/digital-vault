# Logs / Histórico de Descobertas, Alterações e Conflitos

Registros relevantes de operações no Digital Vault.

## Estrutura

```
logs/
├── discoveries/    # descobertas relevantes
├── changes/        # alterações relevantes
└── conflicts/      # conflitos encontrados
```

## Princípios

- **Também obedecem SECURITY.md** — não registrar secrets.
- **Não criar log para cada edição trivial** — apenas alterações com valor operacional.
- **Nunca apagar informação relevante automaticamente**.

---

## logs/discoveries/

Descobertas de novas entidades ou relacionamentos.

### Naming

`YYYY-MM-DD-descrição-curta.yaml`

### Schema

```yaml
log_id: "LOG-2026-09-26-001"
type: "discovery"
timestamp: "2026-09-26T15:30:00Z"
source: "api:vercel"                    # ou "manual", "email", "inbox:INBOX-001"
summary: "Discovered Vercel account linked to email user@example.com"
entities_affected:
  - "EMAIL-0003"
  - "ACCOUNT-0007"
  - "PROJECT-0004"
relationships_created:
  - { from: "EMAIL-0003", to: "ACCOUNT-0007", type: "belongs_to" }
  - { from: "ACCOUNT-0007", to: "PROJECT-0004", type: "hosts" }
verification_status: "VERIFIED"
notes: "Found via Vercel API list projects"
```

---

## logs/changes/

Alterações relevantes em entidades existentes.

### Naming

`YYYY-MM-DD-entidade-alteração.yaml`

### Schema

```yaml
log_id: "LOG-2026-09-26-002"
type: "change"
timestamp: "2026-09-26T16:00:00Z"
entity_id: "ACCOUNT-0007"
field: "status"
old_value: "active"
new_value: "inactive"
reason: "Account suspended per Vercel notification"
verification:
  source: "email:vercel-support"
  verified_at: "2026-09-26T15:55:00Z"
  verification_status: "VERIFIED"
notes: "Will need to migrate projects to ACCOUNT-0012"
```

---

## logs/conflicts/

Conflitos entre informações (dados divergentes, duplicatas potenciais).

### Naming

`CONFLICT-YYYY-MM-DD-NNN.yaml`

### Schema

```yaml
conflict_id: "CONFLICT-2026-09-26-001"
timestamp: "2026-09-26T14:00:00Z"
type: "duplicate_entity"                # duplicate_entity, divergent_data, broken_ref
entities_involved:
  - "EMAIL-0001"
  - "EMAIL-0005"
field: "name"                           # campo em conflito
values:
  - { entity: "EMAIL-0001", value: "user@gmail.com", source: "manual", date: "2026-09-01" }
  - { entity: "EMAIL-0005", value: "user@gmail.com", source: "api:github", date: "2026-09-20" }
status: "OPEN"                          # OPEN, RESOLVED, FALSE_POSITIVE
resolution: null                        # preenchido ao resolver
resolved_at: null
resolved_by: null
notes: "Likely same email, need to merge or confirm separate accounts"
```

### Tipos de Conflito

| Tipo | Descrição |
|---|---|
| `duplicate_entity` | Duas entidades provavelmente representam o mesmo recurso real |
| `divergent_data` | Mesma entidade tem valores diferentes vindos de fontes diferentes |
| `broken_ref` | Relacionamento ou credential_ref aponta para entidade inexistente |
| `verification_mismatch` | Status de verificação inconsistente entre fontes |

---

## Exemplo de Auditoria de Logs

Auditorias devem verificar:
- Logs sem `verification_status` ou com `UNKNOWN`
- Conflitos `OPEN` há mais de 7 dias
- Descobertas sem entidades afetadas válidas
- Alterações sem `reason` ou `verification`
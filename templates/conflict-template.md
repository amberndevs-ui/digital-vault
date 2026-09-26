# Conflict Template

Template para registrar conflitos em `logs/conflicts/`.

**Arquivo:** `logs/conflicts/CONFLICT-YYYY-MM-DD-NNN.yaml`

```yaml
conflict_id: "CONFLICT-2026-09-26-001"
timestamp: "2026-09-26T14:00:00Z"
type: "duplicate_entity"                    # duplicate_entity, divergent_data, broken_ref, verification_mismatch
severity: "high"                             # critical, high, medium, low
entities_involved:
  - "EMAIL-0001"
  - "EMAIL-0005"
field: "name"                                # campo em conflito (ou "entity" para duplicata completa)
values:
  - entity: "EMAIL-0001"
    value: "user@gmail.com"
    source: "manual"
    discovered_at: "2026-09-01T10:00:00Z"
    verification_status: "VERIFIED"
    confidence: 0.9
  - entity: "EMAIL-0005"
    value: "user@gmail.com"
    source: "api:github"
    discovered_at: "2026-09-20T15:30:00Z"
    verification_status: "UNVERIFIED"
    confidence: 0.7
evidence:
  - "EMAIL-0001 created from manual entry on 2026-09-01"
  - "EMAIL-0005 discovered via GitHub API on 2026-09-20"
  - "Both have identical email address"
status: "OPEN"                               # OPEN, RESOLVED, FALSE_POSITIVE
resolution: null                             # Preenchido ao resolver:
# resolution:
#   action: "merge"                          # merge, keep_both, delete_one, update_field
#   keep_entity: "EMAIL-0001"                # se merge ou delete_one
#   delete_entity: "EMAIL-0005"              # se delete_one
#   merged_fields:
#     - { field: "verification", from: "EMAIL-0005", reason: "more recent discovery" }
#   notes: "Merged EMAIL-0005 into EMAIL-0001. Kept earlier verification, added GitHub source."
resolved_at: null
resolved_by: null
notes: "Likely same email. EMAIL-0001 has VERIFIED status, EMAIL-0005 is UNVERIFIED from GitHub. Need to confirm if same account or separate."
```

---

## Tipos de Conflito

| Tipo | Descrição | Exemplo |
|---|---|---|
| `duplicate_entity` | Duas entidades provavelmente são o mesmo recurso real | Dois emails com mesmo endereço |
| `divergent_data` | Mesma entidade tem valores diferentes de fontes diferentes | Conta com status "active" na API mas "suspended" no email |
| `broken_ref` | Relacionamento ou credential_ref aponta para ID inexistente | ACCOUNT-005 referencia SERVER-999 que não existe |
| `verification_mismatch` | Status de verificação inconsistente | Entidade marcada VERIFIED mas source diz UNVERIFIED |

---

## Severidade

| Severidade | Critério |
|---|---|
| `critical` | Conflito de segurança, credencial inválida, billing incorreto |
| `high` | Duplicata de entidade core (email, account, project), relacionamento quebrado |
| `medium` | Campo divergente não-crítico, STALE não resolvido |
| `low` | Inconsistência menor, formatação |

---

## Resolução

Ações possíveis:

| Ação | Quando Usar |
|---|---|
| `merge` | Duas entidades são a mesma; fundir dados, manter um ID |
| `keep_both` | Entidades são diferentes apesar de似似; adicionar disambiguação |
| `delete_one` | Uma entidade é claramente erro/lixo |
| `update_field` | Corrigir campo divergente na entidade correta |
| `investigate` | Precisa de mais evidências antes de decidir |

---

## Exemplo: Divergent Data

```yaml
conflict_id: "CONFLICT-2026-09-26-002"
type: "divergent_data"
entities_involved:
  - "ACCOUNT-0007"
field: "status"
values:
  - entity: "ACCOUNT-0007"
    value: "active"
    source: "api:vercel"
    last_verified: "2026-09-25T10:00:00Z"
  - entity: "ACCOUNT-0007"
    value: "suspended"
    source: "email:vercel-support"
    last_verified: "2026-09-26T09:00:00Z"
resolution:
  action: "update_field"
  notes: "Email from Vercel support is more recent and authoritative. Updated status to suspended."
resolved_at: "2026-09-26T10:00:00Z"
resolved_by: "manual"
status: "RESOLVED"
```
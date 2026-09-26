# Relationship Template

Template para registrar relacionamentos entre entidades.

**Relacionamentos podem ser registrados:**
1. Dentro do arquivo da entidade (campo `relationships`)
2. Como arquivo separado em `relationships/` (para relacionamentos complexos ou muitos-para-muitos)

---

## Opção 1: Dentro da Entidade (Recomendado para maioria dos casos)

No arquivo `entities/<tipo>/<ID>.yaml`:

```yaml
relationships:
  - { to: "EMAIL-0003", type: "belongs_to" }
  - { to: "PROJECT-0004", type: "hosts" }
  - { to: "REPO-0006", type: "uses" }
```

---

## Opção 2: Arquivo de Relacionamento Separado

Para relacionamentos que precisam de metadados extras ou auditoria própria.

**Arquivo:** `relationships/REL-PREFIXO-0000.yaml`

```yaml
relationship_id: "REL-0001"
from: "ACCOUNT-0007"
to: "PROJECT-0004"
type: "hosts"                          # owns, belongs_to, hosts, uses, registered_at, linked_to, managed_by, associated_with, runs_on, billed_through
bidirectional: true                    # se true, relação inversa também é válida
verified: "VERIFIED"                   # VERIFIED, UNVERIFIED, STALE, UNKNOWN, CONFLICT
source: "api:vercel"                   # origem da descoberta
discovered_at: "2026-09-26T10:00:00Z"
last_verified: "2026-09-26T10:00:00Z"
confidence: 0.95
notes: "Vercel account hosts this project"
created_at: "2026-09-26T10:00:00Z"
updated_at: "2026-09-26T10:00:00Z"
```

---

## Tipos de Relacionamento

| Tipo | Sentido | Inverso | Exemplo |
|---|---|---|---|
| `owns` | A → B | `belongs_to` | ORG `owns` ACCOUNT |
| `belongs_to` | A → B | `owns` | EMAIL `belongs_to` ACCOUNT |
| `hosts` | A → B | `hosted_by` | ACCOUNT `hosts` PROJECT |
| `hosted_by` | A → B | `hosts` | PROJECT `hosted_by` ACCOUNT |
| `uses` | A → B | `used_by` | PROJECT `uses` REPO |
| `used_by` | A → B | `uses` | REPO `used_by` PROJECT |
| `registered_at` | A → B | `registers` | DOMAIN `registered_at` PROJECT |
| `registers` | A → B | `registered_at` | PROJECT `registers` DOMAIN |
| `linked_to` | A ↔ B | `linked_to` | WA `linked_to` WABA |
| `managed_by` | A → B | `manages` | ADS `managed_by` BM |
| `manages` | A → B | `managed_by` | BM `manages` ADS |
| `associated_with` | A ↔ B | `associated_with` | PIXEL `associated_with` PROJECT |
| `runs_on` | A → B | `runs` | DEVICE `runs_on` SIM |
| `runs` | A → B | `runs_on` | SIM `runs` DEVICE |
| `billed_through` | A → B | `bills` | ACCOUNT `billed_through` BILLING |
| `bills` | A → B | `billed_through` | BILLING `bills` ACCOUNT |

---

## Regras

- Sempre usar **IDs internos** (ex: `EMAIL-0003`, não `user@gmail.com`)
- Preferir Opção 1 (dentro da entidade) para simplicidade
- Usar Opção 2 quando precisar de `confidence`, `notes`, ou auditoria separada
- `bidirectional: true` significa que a relação inversa é implicitamente válida
- Verificar se relacionamento já existe antes de criar (deduplicação)
# Audit Template

Template para relatórios de auditoria em `reports/` ou `audits/`.

**Arquivo:** `reports/generated/AUDIT-YYYY-MM-DD-NNN.yaml` ou `audits/AUDIT-YYYY-MM-DD-NNN.yaml`

```yaml
audit_id: "AUDIT-2026-09-26-001"
type: "full"                                 # full, incremental, targeted, security
run_at: "2026-09-26T10:00:00Z"
run_by: "manual"                             # ou script name
period_start: "2026-09-19T00:00:00Z"
period_end: "2026-09-26T23:59:59Z"

scope:
  entities_checked: 142
  relationships_checked: 89
  credentials_checked: 23
  logs_checked: 45

findings:
  - category: "duplicates"
    severity: "high"
    count: 3
    details:
      - finding_id: "FIND-001"
        description: "Duplicate email entities"
        entities: ["EMAIL-0001", "EMAIL-0005"]
        field: "name"
        values: ["user@gmail.com", "user@gmail.com"]
        suggestion: "Merge into single entity"
      - finding_id: "FIND-002"
        description: "Duplicate Vercel accounts"
        entities: ["ACCOUNT-0003", "ACCOUNT-0009"]
        field: "platform+name"
        values: ["vercel/user@gmail.com", "vercel/user@gmail.com"]
      - finding_id: "FIND-003"
        description: "Duplicate project names"
        entities: ["PROJECT-0002", "PROJECT-0008"]
        field: "name+platform"
        values: ["meu-projeto@vercel", "meu-projeto@vercel"]

  - category: "stale"
    severity: "medium"
    count: 12
    details:
      - finding_id: "FIND-004"
        entity: "CRED-0004"
        field: "verification.last_verified"
        value: "2026-06-15T00:00:00Z"
        days_stale: 103
        threshold_days: 30
        suggestion: "Re-verify credential reference in 1Password"
      - finding_id: "FIND-005"
        entity: "BILLING-0002"
        field: "verification.last_verified"
        value: "2026-07-01T00:00:00Z"
        days_stale: 87
        threshold_days: 30

  - category: "unknown_critical"
    severity: "high"
    count: 5
    details:
      - finding_id: "FIND-006"
        entity: "PROJECT-0002"
        field: "relationships"
        issue: "No hosting relationship (no server, vercel, netlify, etc.)"
        suggestion: "Discover where project is deployed"
      - finding_id: "FIND-007"
        entity: "DOMAIN-0003"
        field: "expires_at"
        issue: "Domain expiration date UNKNOWN"
        suggestion: "Check registrar or WHOIS"
      - finding_id: "FIND-008"
        entity: "API-0001"
        field: "credential_ref"
        issue: "No credential reference for API key"
        suggestion: "Add credential_ref pointing to 1Password"
      - finding_id: "FIND-009"
        entity: "ACCOUNT-0011"
        field: "platform"
        issue: "Platform is UNKNOWN"
        suggestion: "Identify platform from context"
      - finding_id: "FIND-010"
        entity: "BILLING-0005"
        field: "plan"
        issue: "Billing plan UNKNOWN"
        suggestion: "Verify current subscription"

  - category: "conflicts"
    severity: "critical"
    count: 1
    details:
      - finding_id: "FIND-011"
        conflict_id: "CONFLICT-2026-09-01-001"
        days_open: 25
        entities: ["EMAIL-0001", "EMAIL-0005"]
        suggestion: "Resolve duplicate email conflict"

  - category: "orphans"
    severity: "medium"
    count: 8
    details:
      - finding_id: "FIND-012"
        entity: "PROJECT-0005"
        type: "project"
        issue: "No hosting relationship"
      - finding_id: "FIND-013"
        entity: "DOMAIN-0004"
        type: "domain"
        issue: "No associated project"
      - finding_id: "FIND-014"
        entity: "ACCOUNT-0015"
        type: "account"
        issue: "No known email"
      - finding_id: "FIND-015"
        entity: "PHONE-0003"
        type: "phone"
        issue: "No associated project"
      - finding_id: "FIND-016"
        entity: "ADS-0002"
        type: "ad_account"
        issue: "No Business Manager relationship"
      - finding_id: "FIND-017"
        entity: "CRED-0008"
        type: "credential"
        issue: "No related_entity"
      - finding_id: "FIND-018"
        entity: "BILLING-0003"
        type: "billing"
        issue: "Not verified, no recent check"
      - finding_id: "FIND-019"
        entity: "SERVER-0002"
        type: "server"
        issue: "No projects hosted"

  - category: "broken_relationships"
    severity: "high"
    count: 2
    details:
      - finding_id: "FIND-020"
        from_entity: "ACCOUNT-0005"
        to_entity: "SERVER-999"
        relationship: "hosts"
        issue: "SERVER-999 not found in entities/servers/"
      - finding_id: "FIND-021"
        from_entity: "PROJECT-0009"
        to_entity: "CRED-999"
        relationship: "credential_ref"
        issue: "CRED-999 not found in credentials/"

  - category: "security"
    severity: "critical"
    count: 0
    details: []

summary:
  total_findings: 31
  by_severity:
    critical: 1
    high: 6
    medium: 20
    low: 4
  by_category:
    duplicates: 3
    stale: 12
    unknown_critical: 5
    conflicts: 1
    orphans: 8
    broken_relationships: 2
    security: 0

recommendations:
  - "Prioritize CONFLICT-2026-09-01-001 (duplicate emails)"
  - "Re-verify 12 STALE credentials and billing entries"
  - "Discover hosting for 3 orphan projects"
  - "Fix 2 broken relationships (SERVER-999, CRED-999)"
  - "Add credential_ref to API-0001"

next_audit_due: "2026-10-26T10:00:00Z"
next_audit_type: "incremental"
```

---

## Categorias de Auditoria

| Categoria | O que Verifica |
|---|---|
| `duplicates` | Entidades com mesmos identificadores |
| `stale` | Verificações antigas (thresholds em `core/VERIFICATION.md`) |
| `unknown_critical` | Campos críticos com UNKNOWN |
| `conflicts` | Conflitos abertos em `logs/conflicts/` |
| `orphans` | Recursos sem relacionamentos esperados |
| `broken_relationships` | Relacionamentos apontando para IDs inexistentes |
| `security` | Patterns de secrets, credential_refs suspeitos |

---

## Tipos de Auditoria

| Tipo | Escopo | Frequência |
|---|---|---|
| `full` | Todas as categorias, todas as entidades | Mensal |
| `incremental` | Apenas mudanças desde última auditoria | Semanal |
| `targeted` | Categoria ou tipo de entidade específico | Sob demanda |
| `security` | Apenas categoria security | Semanal |

---

## Checklist de Auditoria Manual

- [ ] Rodar busca por duplicatas (email, account+platform, domain, project+platform)
- [ ] Verificar `verification.last_verified` contra thresholds
- [ ] Listar entidades com campos críticos UNKNOWN
- [ ] Listar conflitos OPEN em `logs/conflicts/`
- [ ] Encontrar órfãos: projects sem hosting, domains sem project, accounts sem email
- [ ] Validar todos os relacionamentos (IDs existem?)
- [ ] Validar todos os credential_refs (arquivos existem em credentials/?)
- [ ] Grep por patterns de secrets em todos arquivos `.yaml`
- [ ] Verificar credential_refs que parecem conter secrets (começam com sk-, ghp_, etc.)
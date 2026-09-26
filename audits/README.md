# Audits / Critérios de Auditoria

Critérios para detectar problemas no Digital Vault. Não implementar automação ainda — apenas documentar o que deve ser verificado.

## Categorias de Auditoria

### 1. Duplicatas

- Entidades com identificadores iguais (ex: mesmo email em `EMAIL-001` e `EMAIL-005`)
- Contas com mesmo `platform` + `username`/`email`
- Projetos com mesmo nome + plataforma
- Domínios duplicados
- Relacionamentos duplicados (mesmo `from` + `to` + `type`)

### 2. Informações STALE

- Entidades com `verification_status: STALE` (thresholds em `core/VERIFICATION.md`)
- Credenciais não verificadas há > 30 dias
- Billing/planos não verificados há > 30 dias
- Status de projetos não verificados há > 60 dias

### 3. UNKNOWN Importantes

Campos críticos com `UNKNOWN`:
- Email sem `credential_ref`
- Conta sem `platform`
- Projeto sem `relationships` conhecidos
- Domínio sem `registrar` ou `expires_at`
- API sem `credential_ref`
- Billing sem `plan` ou `cycle`

### 4. Conflitos

- Itens em `logs/conflicts/` não resolvidos
- Entidades com `verification_status: CONFLICT`
- Relacionamentos contraditórios (A→B e B→A com tipos incompatíveis)

### 5. Recursos Órfãos

- Projetos sem hospedagem conhecida (sem `SERVER`, `VERCEL`, `NETLIFY`, etc.)
- Domínios sem projeto relacionado
- Contas sem email conhecido
- Números de telefone sem projeto
- Contas de anúncios sem Business Manager conhecida
- Credenciais sem `related_entity` válida
- Billing não verificado

### 6. Relacionamentos Quebrados

- Relacionamento aponta para ID inexistente em `entities/`
- Entidade referenciada em relacionamento mas não existe
- `credential_ref` aponta para `credentials/CRED-XXXX.yaml` inexistente

### 7. Segurança

- Arquivos contendo patterns de secrets (regex para API keys, passwords, tokens)
- `credential_ref` com valor suspeito (ex: começa com `sk-`, `ghp_`, `Bearer`)
- Logs contendo dados sensíveis

## Formato de Relatório de Auditoria

```yaml
audit_id: "AUDIT-0001"
type: "full"                    # full, incremental, targeted
run_at: "2026-09-26T10:00:00Z"
findings:
  - category: "duplicates"
    severity: "high"
    count: 3
    details:
      - "EMAIL-001 and EMAIL-005 both have 'user@gmail.com'"
      - "ACCOUNT-003 and ACCOUNT-009 both 'vercel/user@gmail.com'"
  - category: "stale"
    severity: "medium"
    count: 12
    details:
      - "CRED-0004 not verified since 2026-06-15"
  - category: "unknown_critical"
    severity: "high"
    count: 5
    details:
      - "PROJECT-002 has no hosting relationship"
  - category: "conflicts"
    severity: "critical"
    count: 1
    details:
      - "CONFLICT-0003 unresolved since 2026-09-01"
  - category: "orphans"
    severity: "medium"
    count: 8
  - category: "broken_relationships"
    severity: "high"
    count: 2
    details:
      - "ACCOUNT-005 references SERVER-999 (not found)"
  - category: "security"
    severity: "critical"
    count: 0
summary:
  total_findings: 31
  critical: 1
  high: 6
  medium: 20
  low: 4
next_audit_due: "2026-10-26T10:00:00Z"
```

## Frequência Sugerida

| Tipo | Frequência |
|---|---|
| Auditoria completa | Mensal |
| Auditoria de segurança | Semanal |
| Auditoria de STALE/UNKNOWN | Quinzenal |
| Auditoria de duplicatas | Quinzenal |

## Ações Pós-Auditoria

1. Priorizar `critical` e `high`
2. Criar itens de inbox para `UNCERTAIN` descobertos
3. Registrar conflitos em `logs/conflicts/`
4. Atualizar `verification_status` conforme resolução
5. Log de alterações em `logs/changes/`
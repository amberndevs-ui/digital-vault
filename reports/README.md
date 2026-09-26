# Reports / Relatórios Gerados

Relatórios derivados do inventário para consulta e análise.

## Estrutura

```
reports/
├── generated/          # relatórios gerados automaticamente
├── manual/             # relatórios criados manualmente
└── templates/          # templates de relatório (opcional)
```

## Tipos de Relatório

| Relatório | Descrição | Frequência |
|---|---|---|
| `inventory-summary.yaml` | Resumo total de entidades por tipo | Semanal |
| `stale-report.yaml` | Entidades com verificação STALE | Quinzenal |
| `orphan-report.yaml` | Recursos órfãos (sem relacionamentos) | Mensal |
| `billing-report.yaml` | Contas com billing, créditos, renovações | Mensal |
| `credential-audit.yaml` | Status de referências de credenciais | Mensal |
| `conflict-report.yaml` | Conflitos abertos | Semanal |
| `project-map.yaml` | Mapa completo de um projeto específico | Sob demanda |

## Formato Padrão

```yaml
report_id: "REPORT-2026-09-26-001"
type: "inventory-summary"
generated_at: "2026-09-26T10:00:00Z"
generated_by: "manual"                 # ou script name
period: "2026-09-19/2026-09-26"
summary:
  total_entities: 142
  by_type:
    email: 12
    account: 28
    project: 15
    domain: 8
    repository: 22
    server: 3
    phone: 5
    sim: 4
    device: 6
    billing: 7
  verification_status:
    VERIFIED: 89
    UNVERIFIED: 23
    STALE: 18
    UNKNOWN: 10
    CONFLICT: 2
findings: []
```

## Geração

Relatórios podem ser gerados:
- Manualmente (criando arquivo YAML)
- Via scripts futuros (braços de automação)
- Via consultas ad-hoc

## Retenção

- Relatórios em `generated/`: manter últimos 12 meses
- Relatórios em `manual/`: manter indefinidamente
- Relatórios com findings críticos: manter indefinidamente
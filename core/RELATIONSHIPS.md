# Core / Relacionamentos

Relacionamentos são parte fundamental do sistema. Eles conectam entidades e permitem navegação nos dois sentidos.

## Formato Canônico (em entidades)

Relacionamentos são armazenados **dentro da entidade** no campo `relationships` como array de objetos estruturados:

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

## Regras

- Relacionamentos devem utilizar **IDs internos** sempre que possível.
- Nunca inferir relacionamentos sem evidência suficiente.
- O sistema deve poder responder:
  - *"O que está relacionado a PROJECT-004?"*
  - *"Quais projetos estão relacionados a EMAIL-003?"*
- Relacionamentos históricos NÃO são removidos quando expiram; mantêm-se com `valid_until` preenchido.
- Índice inverso (para navegação bidirecional) é derivado dos arquivos de entidades, não armazenado separadamente como fonte autoritativa.

## Estrutura do Objeto de Relacionamento

| Campo | Obrigatório | Tipo | Descrição |
|---|---|---|---|
| `to` | Sim | string | ID da entidade destino (ex: ACCOUNT-0007) |
| `type` | Sim | string | Tipo do relacionamento (vocabulário controlado) |
| `valid_from` | Não | string/null | Início da vigência (ISO 8601 UTC) |
| `valid_until` | Não | string/null | Fim da vigência (ISO 8601 UTC), null = atual |
| `role` | Não | string | Papel/função (ex: primary, admin, member) |
| `primary` | Não | boolean | Se é relacionamento primário |
| `source` | Não | string | Origem da descoberta (sanitizada) |
| `confidence` | Não | number | 0.0 a 1.0 |

## Tipos de Relacionamento (Vocabulário Controlado)

| Tipo | Sentido | Inverso | Descrição | Exemplo |
|---|---|---|---|---|
| `owns` | A → B | `owned_by` | A é proprietário de B | ORG `owns` ACCOUNT |
| `owned_by` | A → B | `owns` | A pertence a B | ACCOUNT `owned_by` ORG |
| `belongs_to` | A → B | `has` | A pertence a B | EMAIL `belongs_to` ACCOUNT |
| `has` | A → B | `belongs_to` | A possui B | ACCOUNT `has` EMAIL |
| `hosts` | A → B | `hosted_by` | A hospeda B | ACCOUNT `hosts` PROJECT |
| `hosted_by` | A → B | `hosts` | A é hospedado por B | PROJECT `hosted_by` ACCOUNT |
| `uses` | A → B | `used_by` | A utiliza B | PROJECT `uses` REPO |
| `used_by` | A → B | `uses` | A é usado por B | REPO `used_by` PROJECT |
| `registered_at` | A → B | `registers` | A registrado em B | DOMAIN `registered_at` PROJECT |
| `registers` | A → B | `registered_at` | B registra A | PROJECT `registers` DOMAIN |
| `linked_to` | A ↔ B | `linked_to` | Vinculação bidirecional | WA `linked_to` WABA |
| `managed_by` | A → B | `manages` | A gerenciado por B | ADS `managed_by` BM |
| `manages` | A → B | `managed_by` | B gerencia A | BM `manages` ADS |
| `associated_with` | A ↔ B | `associated_with` | Associação livre | PIXEL `associated_with` PROJECT |
| `runs_on` | A → B | `runs` | A executa em B | DEVICE `runs_on` SIM |
| `runs` | A → B | `runs_on` | B roda A | SIM `runs` DEVICE |
| `billed_through` | A → B | `bills` | A cobrado via B | ACCOUNT `billed_through` BILLING |
| `bills` | A → B | `billed_through` | B cobra A | BILLING `bills` ACCOUNT |

## Navegação Bidirecional

Para responder consultas nos dois sentidos, o sistema deriva o índice inverso lendo todas as entidades:

- *"Quais projetos estão relacionados a EMAIL-003?"* → busca entidades onde `relationships.to == EMAIL-0003`
- *"Qual email está relacionado ao PROJECT-004?"* → lê `PROJECT-004.relationships` e filtra por tipo

## Deduplicação de Relacionamentos

Antes de criar um relacionamento:

1. Verificar se já existe um relacionamento entre os mesmos `from` (entidade atual) + `to` + `type` com vigência sobreposta.
2. Se existir, atualizar em vez de criar duplicata.
3. Se houver conflito (ex: mesmo `from`+`to`+`type` mas `valid_from`/`valid_until` conflitantes), registrar em `logs/conflicts/`.

## Relacionamentos com Entidades Inativas/Removidas

- Se entidade destino for `status: DELETED` ou `ARCHIVED`, manter relacionamento com `valid_until` = data da remoção.
- Não remover relacionamento histórico — ele documenta que a relação existiu.
- Auditoria `broken_relationship` detecta referências para IDs que nunca existiram (erro), não para entidades arquivadas.

## Relacionamento com Plataforma

Plataforma NÃO é entidade com ID. Use campo `platform` da entidade + relacionamentos para outras entidades da mesma plataforma.

Exemplo: para encontrar "todas contas Vercel", buscar entidades com `platform: "vercel"` e `type: "account"`.

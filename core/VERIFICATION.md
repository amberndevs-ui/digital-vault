# Core / Verificação

Estados globais de verificação para toda informação importante no Digital Vault.

## Estados de Verificação (verification.status)

| Estado | Descrição |
|---|---|
| `VERIFIED` | Informação confirmada por fonte confiável, verificada recentemente |
| `UNVERIFIED` | Registrada mas ainda não confirmada por fonte independente |
| `STALE` | Foi verificada, mas há muito tempo; precisa ser reconfirmada |
| `UNKNOWN` | Informação ausente, não descoberta ou não aplicável |
| `CONFLICT` | Divergência entre fontes; requer resolução manual |

## Status Operacional (entity.status) — SEPARADO DE VERIFICAÇÃO

| Status | Descrição |
|---|---|
| `ACTIVE` | Entidade operacionalmente ativa |
| `INACTIVE` | Entidade inativa por escolha/desuso |
| `SUSPENDED` | Entidade suspensa pela plataforma/provedor |
| `ARCHIVED` | Entidade arquivada (histórica, não operacional) |
| `DELETED` | Entidade removida (mantida para histórico) |
| `UNKNOWN` | Estado operacional desconhecido |

**IMPORTANTE**: `status` (operacional) e `verification.status` (confiança) são **conceitos distintos**.

Uma entidade pode ser:
```yaml
status: ACTIVE              # operacionalmente ativa
verification:
  status: STALE             # mas informação não verificada recentemente
```
Sem contradição.

## Estrutura de Verificação Canônica

```yaml
verification:
  status: "VERIFIED"              # VERIFIED, UNVERIFIED, STALE, UNKNOWN, CONFLICT
  source_type: "api"              # manual, api, email, file, screenshot, import, platform, inferred, other
  source_ref: "vercel"            # referência sanitizada (plataforma, arquivo, id inbox)
  discovered_at: "2026-09-01T10:00:00Z"
  last_verified: "2026-09-25T14:30:00Z"
  confidence: 0.95                # opcional, 0.0 a 1.0
```

### Vocabulário Controlado: source_type

| Valor | Quando Usar |
|---|---|
| `manual` | Informado diretamente pelo usuário |
| `api` | Descoberto via API de plataforma (ex: Vercel, GitHub) |
| `email` | Extraído de email (notificação, recibo, etc.) |
| `file` | Importado de arquivo local (CSV, JSON, backup) |
| `screenshot` | Observado em captura de tela |
| `import` | Importação em lote/migração de outro sistema |
| `platform` | Descoberto via UI/web da plataforma (não API) |
| `inferred` | Deduzido por regra/logica (NUNCA vira VERIFIED só por isso) |
| `other` | Outra fonte não categorizada |

### Regras para source_ref

- **NUNCA** contém secrets, tokens, URLs com auth, headers Authorization
- Exemplos válidos: `"vercel"`, `"github"`, `"user-provided"`, `"inbox:INBOX-2026-09-26-001"`, `"file:accounts-export.csv"`
- Exemplos INVÁLIDOS: `"api:vercel?token=xyz"`, `"email:user@gmail.com"`, `"https://vercel.com/dashboard?auth=abc"`

## Regras Fundamentais

1. **Informação não verificada NÃO pode ser apresentada como fato confirmado**
   - `UNVERIFIED` deve ser claramente indicado

2. **Informação antiga deve poder tornar-se STALE**
   - Thresholds por tipo (ver abaixo)
   - Auditorias devem detectar e alertar

3. **Conflito deve ser CONFLICT**
   - Não sobrescrever silenciosamente
   - Preservar ambas as evidências
   - Registrar em `logs/conflicts/`

4. **Ausência de informação deve ser UNKNOWN**
   - NUNCA transformar UNKNOWN em informação presumida

5. **Sempre diferenciar "registrado anteriormente" de "verificado agora"**
   - `discovered_at` ≠ `last_verified`

6. **INFERRED nunca vira VERIFIED apenas por inferência**
   - Inferência pode criar hipótese (UNVERIFIED/UNKNOWN)
   - VERIFIED requer confirmação independente

## Thresholds STALE por Tipo de Informação

| Tipo de Informação | STALE após | Verificação Típica |
|---|---|---|
| Credenciais / Acesso | 30 dias | Testar login/API |
| Billing / Planos / Créditos | 30 dias | Confirmar no painel/fatura |
| Status de projetos/contas | 60 dias | Verificar na plataforma |
| Domínios / DNS / SSL | 90 dias | WHOIS, DNS check |
| Relacionamentos estáveis | 180 dias | Revalidar conexões |
| Informações de identidade (email, telefone) | 365 dias | Confirmação direta |

## Auditoria de Verificação

Auditorias devem detectar:

- Entidades com `verification.status: UNKNOWN` em campos críticos
- Entidades `STALE` que precisam de reverificação (acima thresholds)
- `CONFLICT` não resolvidos em `logs/conflicts/`
- Informações `UNVERIFIED` apresentadas como fatos
- `source_type: inferred` com `status: VERIFIED` (inválido)

## Exemplo de Entidade com Verificação Completa

```yaml
id: ACCOUNT-0007
type: account
name: "vercel-production"
status: ACTIVE                    # status operacional
platform: vercel
relationships:
  - to: "EMAIL-0003"
    type: "belongs_to"
    valid_from: "2026-01-01T00:00:00Z"
    valid_until: null
  - to: "PROJECT-0004"
    type: "hosts"
    valid_from: "2026-03-15T00:00:00Z"
    valid_until: null
verification:
  status: "VERIFIED"              # confiança na informação
  source_type: "api"
  source_ref: "vercel"
  discovered_at: "2026-09-01T10:00:00Z"
  last_verified: "2026-09-25T14:30:00Z"
  confidence: 0.95
credential_ref:
  credential_id: "CRED-0001"
  provider: "1password"
  reference: "vercel/email-003"
  related_entity: "ACCOUNT-0007"
notes: "Production account for main projects"
created_at: "2026-09-01T10:00:00Z"
updated_at: "2026-09-25T14:30:00Z"
```

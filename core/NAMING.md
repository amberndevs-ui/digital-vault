# Core / Nomenclatura

IDs internos únicos e estáveis para todas as entidades do Digital Vault.

## Princípios

- IDs **não devem ser reutilizados** (mesmo se a entidade for removida).
- IDs **não devem mudar** porque o nome ou label da entidade mudou.
- IDs **devem evitar ambiguidade**.
- IDs **devem ser usados nos relacionamentos** (nunca apenas nomes).
- **Antes de gerar um novo ID, verificar se a entidade já existe** (deduplicação).

## Formato Padrão

```
PREFIXO-NNNN
```

- `PREFIXO`: código da categoria (2-4 letras, maiúsculo)
- `NNNN`: número sequencial com 4 dígitos (0001, 0002, …)

## Prefixos por Categoria

| Prefixo | Categoria | Exemplos |
|---|---|---|
| `EMAIL` | Emails | EMAIL-0001, EMAIL-0002 |
| `ACCOUNT` | Contas de plataforma | ACCOUNT-0001, ACCOUNT-0002 |
| `ORG` | Organizações/Empresas | ORG-0001, ORG-0002 |
| `PROJECT` | Projetos/Marcas/Sites | PROJECT-0001, PROJECT-0002 |
| `DOMAIN` | Domínios | DOMAIN-0001, DOMAIN-0002 |
| `REPO` | Repositórios Git | REPO-0001, REPO-0002 |
| `SERVER` | Servidores/VPS | SERVER-0001, SERVER-0002 |
| `PHONE` | Números de telefone | PHONE-0001, PHONE-0002 |
| `SIM` | Chips/SIM cards | SIM-0001, SIM-0002 |
| `DEVICE` | Dispositivos | DEVICE-0001, DEVICE-0002 |
| `BILLING` | Billing/Assinaturas | BILLING-0001, BILLING-0002 |
| `API` | APIs/Chaves de API | API-0001, API-0002 |

### Meta / Facebook / WhatsApp

| Prefixo | Categoria | Exemplos |
|---|---|---|
| `META` | Perfil/Conta Meta | META-0001 |
| `BM` | Business Manager | BM-0001 |
| `ADS` | Conta de Anúncios | ADS-0001 |
| `PAGE` | Página Facebook/Instagram | PAGE-0001 |
| `PIXEL` | Pixel/Dataset | PIXEL-0001 |
| `WABA` | WhatsApp Business Account | WABA-0001 |
| `WA` | Número WhatsApp | WA-0001 |

### Novos Tipos (Extensíveis)

| Prefixo | Categoria | Exemplos |
|---|---|---|
| `CRED` | Referência de credencial | CRED-0001 |
| `AUDIT` | Auditoria | AUDIT-0001 |
| `LOG` | Log de descoberta/alteração | LOG-0001 |
| `CONFLICT` | Conflito registrado | CONFLICT-0001 |

## Regras de Atribuição

1. **Sequencial**: Próximo número disponível para o prefixo (formato 0001, 0002...).
2. **Único global**: Mesmo prefixo, nunca reutilizar número.
3. **Verificar existência**: Antes de criar, buscar em `entities/` se já existe entidade correspondente.

## Exemplos de Uso em Relacionamentos

```yaml
relationships:
  - to: "EMAIL-0003"
    type: "belongs_to"
    valid_from: "2026-01-01T00:00:00Z"
    valid_until: null
  - to: "ACCOUNT-0007"
    type: "has"
    valid_from: "2026-01-01T00:00:00Z"
    valid_until: null
  - to: "PROJECT-0004"
    type: "hosts"
    valid_from: "2026-03-15T00:00:00Z"
    valid_until: null
```

## Registro de IDs Alocados

Manter registro simples em `logs/ids-allocated.md`:

```markdown
| Prefixo | Último Número | Próximo Disponível |
|---|---|---|
| EMAIL | 0 | 1 |
| ACCOUNT | 0 | 1 |
| ORG | 0 | 1 |
| PROJECT | 0 | 1 |
| DOMAIN | 0 | 1 |
| REPO | 0 | 1 |
| SERVER | 0 | 1 |
| PHONE | 0 | 1 |
| SIM | 0 | 1 |
| DEVICE | 0 | 1 |
| BILLING | 0 | 1 |
| META | 0 | 1 |
| BM | 0 | 1 |
| ADS | 0 | 1 |
| PAGE | 0 | 1 |
| PIXEL | 0 | 1 |
| WABA | 0 | 1 |
| WA | 0 | 1 |
| API | 0 | 1 |
| CRED | 0 | 1 |
| AUDIT | 0 | 1 |
| LOG | 0 | 1 |
| CONFLICT | 0 | 1 |
```

## Deduplicação por Identidade Canônica

Antes de alocar novo ID, **sempre** buscar correspondências existentes.

### Chaves de Identidade por Tipo (Normalização Obrigatória)

#### EMAIL
- **Chave primária**: email normalizado
- **Normalização**:
  - Trim whitespace
  - Domínio (parte após @) → lowercase
  - Parte local: tratar case de forma conservadora (preservar case original, mas comparar case-insensitive para dedupe)
  - **NÃO** assumir automaticamente que plus-addressing (`user+tag@domain`) representa a mesma identidade sem regra específica do provider
  - Exemplo: `User@Gmail.COM` → normalizado para comparação: `user@gmail.com` (mas armazenar original em `name`)

#### DOMAIN
- **Chave primária**: domínio registrável normalizado
- **Normalização**:
  - Lowercase completo
  - Remover trailing dot (`.`)
  - Distinguir **domínio registrável** (ex: `example.com`) de **hostname/subdomínio** (ex: `www.example.com`, `api.example.com`)
  - **NÃO** remover `www` indiscriminadamente quando isso destruir distinção de hostname
  - `WWW.EXAMPLE.COM.` → `www.example.com` (hostname)
  - `Example.Com` → `example.com` (domínio registrável)

#### PHONE / WHATSAPP
- **Chave primária**: número em formato E.164 quando país conhecido
- **Normalização**:
  - Se país/número conhecidos com segurança → normalizar para E.164 (ex: `+5511999999999`)
  - Se país **desconhecido** → **não presumir**; preservar valor observado sanitizado como metadata
  - Remover formatação visual: espaços, parênteses, hífens, pontos
  - Preservar valor original em campo `original_format` se útil

#### ACCOUNT
- **Chave primária composta**: `platform` + `platform_stable_id`
- **Identidade deve considerar**:
  - `platform` (obrigatório)
  - Identificador estável fornecido pela plataforma (ex: `account.id`, `user_id`, `organization_id`), quando existir
  - Se identificador estável não disponível → `platform` + `name` normalizado (email/username)
  - Exemplo Vercel: `vercel` + `account.id` (ex: `team_abc123`)
  - Exemplo GitHub: `github` + `user.id` (numérico) ou `org.login`

#### PROJECT
- **Priorizar identificadores estáveis externos e relações existentes, não apenas nome**:
  - Identificador estável da plataforma de hospedagem (ex: Vercel `project.id`, Netlify `site_id`)
  - Repositório Git principal (owner/repo)
  - Domínio principal associado
  - Nome + plataforma apenas como fallback
  - Dois projetos com mesmo nome mas IDs de plataforma diferentes = entidades diferentes

#### META / ADS / WABA / PAGE / PIXEL / BM
- **Priorizar IDs oficiais da plataforma** (Facebook/Meta Graph API IDs)
- `ad_account_id`, `business_manager_id`, `page_id`, `pixel_id`, `waba_id`, `phone_number_id`
- Esses IDs são globais e estáveis — usar como chave primária de dedupe

### Estados de Decisão de Deduplicação

| Estado | Critério | Ação |
|---|---|---|
| `EXISTING` | Chave de identidade normalizada corresponde a entidade existente com alta confiança | Atualizar entidade existente (merge campos, adicionar relacionamentos) |
| `NEW` | Nenhuma correspondência encontrada após busca exaustiva | Alocar novo ID, criar entidade |
| `UNCERTAIN` | Correspondência parcial, identificadores conflitantes, ou evidência insuficiente | Enviar para `inbox/` com status `UNCERTAIN` |
| `CONFLICT` | Múltiplas entidades existentes correspondem à mesma chave, ou dados divergentes impedem decisão | Registrar em `logs/conflicts/`, não criar nova entidade |

**Regra de Ouro**: Nunca fazer merge destrutivo baseado apenas em nome semelhante. Sempre usar chaves de identidade normalizadas por tipo.

## Concorrência de IDs (Dropbox)

Ver seção dedicada em `SECURITY.md` (P0-7) e `logs/ids-allocated.md`.

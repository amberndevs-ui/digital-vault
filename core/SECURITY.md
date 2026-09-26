# Core / Segurança

Regras obrigatórias para TODO o Digital Vault.

## Proibido Persistir

**NUNCA** armazenar nos arquivos do vault (Markdown, JSON, YAML, logs, templates, inbox):

- passwords
- API keys reais
- access tokens
- refresh tokens
- session tokens
- cookies de autenticação
- private keys
- conteúdo de arquivos `.env`
- recovery codes
- códigos 2FA
- PIN
- CVV
- números completos de cartão de crédito
- credenciais de banco de dados
- connection strings contendo credenciais
- secrets de qualquer tipo

## O que É Permitido

Apenas **referências estruturadas** para credenciais (formato canônico):

```yaml
credential_ref:
  credential_id: "CRED-0001"
  provider: "1password"
  reference: "vercel/email-007"
  related_entity: "ACCOUNT-0007"
```

Quando não houver credencial:
```yaml
credential_ref: null
```

**PROIBIDO** formatos alternativos:
```yaml
credential_ref: "1password/vercel/email-007"  # string simples - NÃO USE
credential_ref: "CRED-0001"                    # apenas ID - NÃO USE
api_key: "sk-…"                                # secret direto - NUNCA
```

## Pipeline de Sanitização Obrigatório

**TODO** dado descoberto deve passar por este pipeline ANTES de persistir em QUALQUER local (entities, inbox, logs, reports):

```
CAPTURAR
    ↓
CLASSIFICAR EM MEMÓRIA/PROCESSAMENTO TEMPORÁRIO
    ↓
DETECTAR SENSÍVEL (regex, patterns, heurística)
    ↓
SANITIZAR (remover/mascarar secrets)
    ↓
VALIDAR SANITIZAÇÃO (confirmar que não vazou)
    ↓
SOMENTE ENTÃO PERSISTIR
```

### Regra para Inbox

Inbox É persistência. Portanto **dados brutos NÃO podem ser gravados nela antes da sanitização**.

Todo item persistido na Inbox deve possuir:
```yaml
sanitized: true
```

Se não puder garantir sanitização: **NÃO PERSISTIR**.

Campos livres (`notes`, `summary`, `reason`, `source_ref`, `evidence`, `raw_data`) também passam pela mesma política.

## Padrão de Referência de Credencial (Canônico)

Toda referência em `credential_ref` deve conter:

| Campo | Obrigatório | Exemplo |
|---|---|---|
| `credential_id` | Sim | `CRED-0001` |
| `provider` | Sim | `1password`, `bitwarden`, `keepass` |
| `reference` | Sim | `vercel/email-007` (identificador opaco) |
| `related_entity` | Sim | `ACCOUNT-0007` |

O campo `reference` deve ser **opaco** — não deve conter:
- password
- API key
- token
- cookie
- private key
- connection string
- recovery code
- conteúdo sensível

## Detecção Defensiva de Secrets (Auditoria)

Auditorias devem escanear arquivos para padrões suspeitos:

```
sk-          # OpenAI/Anthropic API keys
ghp_         # GitHub PAT
gho_         # GitHub OAuth
ghu_         # GitHub user token
ghs_         # GitHub server token
ghr_         # GitHub refresh token
Bearer       # Authorization headers
eyJ          # JWT tokens (base64)
BEGIN PRIVATE KEY
BEGIN RSA PRIVATE KEY
BEGIN OPENSSH PRIVATE KEY
password=
token=
api_key=
secret=
access_key=
```

Quando detectar:
1. Marcar como `SECURITY_FINDING` na auditoria
2. Mascarar imediatamente no relatório (nunca registrar valor completo)
3. Registrar apenas tipo/localização segura do problema
4. Exigir correção antes de promover entidade

## Logs e Auditoria

Logs em `logs/` também **devem obedecer** a esta política.

- Não registrar secrets descobertos acidentalmente.
- Não criar log para cada edição trivial.
- Sanitizar antes de registrar qualquer evidência.
- `source_ref` em verificação NUNCA contém tokens/URLs com auth.

## Sincronização Dropbox

Este workspace é sincronizado via Dropbox entre múltiplos computadores.

**Todo conteúdo deve ser tratado como potencialmente exposto a múltiplos dispositivos.**

A segurança não pode depender de "este arquivo não será sincronizado" — todo arquivo no workspace segue a mesma regra.

## Escrita Segura de Arquivos

Qualquer automação que altere arquivos estruturados deve preferir:

1. Validar estado atual (ler arquivo)
2. Gerar conteúdo novo em memória
3. Escrever arquivo temporário (`.tmp`)
4. Validar conteúdo temporário (parse YAML, checar schema)
5. Substituir destino de forma atômica (rename) quando filesystem permitir
6. Validar arquivo final

Isso reduz corrupção local. **NÃO resolve concorrência distribuída do Dropbox.**

## Gerenciador de Credenciais Separado

Secrets devem permanecer em um gerenciador seguro de credenciais (1Password, Bitwarden, etc.).

O Digital Vault deve saber **ONDE** encontrar uma credencial, e não necessariamente conhecer seu valor.

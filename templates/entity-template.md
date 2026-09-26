# Entity Template

Template base para criar novas entidades no Digital Vault.

**Copie este arquivo, preencha os campos e salve em `entities/<tipo>/<ID>.yaml`**

```yaml
id: "PREFIXO-0000"                  # Ex: EMAIL-0001, ACCOUNT-0007 (ver core/NAMING.md)
type: "tipo_da_entidade"             # email, account, organization, project, domain, repository, server, phone, sim, device, billing
name: "Nome ou identificador humano"
status: "active"                     # active, inactive, suspended, unknown, archived
platform: "plataforma"               # gmail, vercel, github, supabase, cloudflare, meta, whatsapp, etc.
relationships: []                    # Lista de relacionamentos (ver core/RELATIONSHIPS.md)
# Exemplo:
# relationships:
#   - { to: "EMAIL-0003", type: "belongs_to" }
#   - { to: "PROJECT-0004", type: "hosts" }

verification:
  source: "manual"                   # manual, api:vercel, api:github, email, screenshot, inbox:INBOX-001
  discovered_at: "2026-09-26T00:00:00Z"
  last_verified: "2026-09-26T00:00:00Z"
  verification_status: "UNVERIFIED"  # VERIFIED, UNVERIFIED, STALE, UNKNOWN, CONFLICT
  confidence: 0.5                    # opcional, 0.0 a 1.0

credential_ref:                      # Referência à credencial (NUNCA o secret)
  provider: "1password"              # 1password, bitwarden, keepass
  reference: "caminho/no/gerenciador" # Ex: vercel/email-007
  related_entity: "PREFIXO-0000"     # ID desta entidade

notes: ""                            # Observações livres

# Campos específicos por tipo (adicionar conforme necessário):
# SIM: operator, line_type
# Ad Account: ad_account_id, currency
# Domain: registrar, expires_at, nameservers
# Server: ip, os, provider
# API: base_url, auth_type
# Billing: plan, cycle, amount_ref
# WhatsApp: phone_number, waba_id
# Pixel: pixel_id, domain_id
# Business Manager: bm_id, industry
# Repository: visibility, language
# Device: os, model, imei_ref

created_at: "2026-09-26T00:00:00Z"
updated_at: "2026-09-26T00:00:00Z"
```

## Checklist Antes de Salvar

- [ ] ID único e seguindo nomenclatura (`core/NAMING.md`)
- [ ] `type` corresponde ao diretório em `entities/`
- [ ] `verification_status` honesto (não marcar VERIFIED se não verificou)
- [ ] `credential_ref` aponta para gerenciador, NÃO contém secret
- [ ] `relationships` usa IDs internos, não nomes
- [ ] Nenhum campo sensível (password, token, key) no arquivo
- [ ] `created_at` e `updated_at` em ISO 8601 UTC
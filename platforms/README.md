# Platforms / Braços Especializados

Arquitetura de braços para integração com plataformas específicas.

## Princípio Fundamental

Um braço pode possuir conhecimento específico sobre uma plataforma, mas **NÃO pode criar um modelo de dados incompatível com o core**.

Todo braço deve seguir o pipeline:

```
1. DESCOBRIR        → consultar API, UI, CLI da plataforma
2. NORMALIZAR       → converter para formato padrão
3. SANITIZAR        → remover/mascarar dados sensíveis
4. DEDUPLICAR       → verificar se entidade já existe
5. VERIFICAR        → atribuir status de verificação
6. CONVERTER        → gerar YAML no schema central (core/SCHEMA.md)
7. RELACIONAR       → criar relacionamentos com IDs internos
8. PERSISTIR        → salvar em entities/
9. REGISTRAR        → log em logs/discoveries/
```

## Estrutura de um Braço

```
platforms/
└── nome-da-plataforma/
    ├── README.md          # documentação do braço
    ├── schema.md          # mapeamento de campos da plataforma → core
    ├── discovery.md       # como descobrir recursos na plataforma
    └── scripts/           # scripts auxiliares (opcional)
```

## Braços Planejados (NÃO implementar agora)

| Braço | Plataforma | Recursos Principais |
|---|---|---|
| `meta/` | Meta/Facebook | Business Manager, Ad Accounts, Pages, Pixels, WABA |
| `whatsapp/` | WhatsApp | WABA, números, templates |
| `vercel/` | Vercel | Projetos, domínios, deployments |
| `github/` | GitHub | Repos, organizations, secrets refs |
| `supabase/` | Supabase | Projects, databases, API keys refs |
| `cloudflare/` | Cloudflare | Domínios, DNS, Workers, Pages |
| `google/` | Google | Contas, Cloud, Ads, Workspace |
| `google-ads/` | Google Ads | Contas, campanhas, billing |

## Regras de Integração

1. **Schema Central é Lei** — braço produz YAML compatível com `core/SCHEMA.md`
2. **IDs Internos** — braço usa IDs do vault (`EMAIL-001`, `ACCOUNT-007`), não IDs da plataforma
3. **Referências de Credencial** — braço NUNCA lê secrets, apenas referencia via `credential_ref`
4. **Verificação Obrigatória** — toda descoberta do braço deve ter `verification` completo
5. **Log de Descoberta** — braço registra descobertas relevantes em `logs/discoveries/`

## Exemplo de Mapeamento (schema.md do braço)

```markdown
# Vercel → Core Schema Mapping

| Vercel Field | Core Field | Notes |
|---|---|---|
| `account.id` | `id` (ACCOUNT-XXXX) | prefixo ACCOUNT |
| `account.name` | `name` | |
| `account.email` | `relationships → EMAIL-XXXX` | deduplicar email |
| `project.id` | `id` (PROJECT-XXXX) | prefixo PROJECT |
| `project.name` | `name` | |
| `project.framework` | `notes` / campo customizado | opcional |
| `deployment.url` | `relationships → DOMAIN-XXXX` | se domínio customizado |
```

## Adicionando Novo Braço

1. Criar diretório em `platforms/novo-braco/`
2. Criar `README.md` documentando propósito
3. Criar `schema.md` mapeando campos da plataforma → core
4. Criar `discovery.md` descrevendo como descobrir recursos
5. Seguir pipeline de 9 etapas acima
6. Testar com dados fictícios antes de usar dados reais
# Digital Vault

Sistema pessoal de organização e inventário da infraestrutura digital.

## Propósito

Construir progressivamente uma fonte central de verdade sobre toda a vida digital operacional: emails, contas, plataformas, projetos, sites, domínios, hospedagens, repositórios, bancos de dados, APIs, assinaturas, billing e recursos relacionados.

O Digital Vault é um **mapa inteligente**, não um gerenciador de senhas.

## Arquitetura

```
CÉREBRO CENTRAL (core/)
        ↓
PADRÃO ÚNICO (schema canônico)
        ↓
ENTIDADES + RELACIONAMENTOS (entities/, relationships/)
        ↓
BRAÇOS ESPECIALIZADOS (platforms/)
```

Novos braços/plataformas podem ser adicionados futuramente sem modificar os princípios fundamentais do cérebro.

### Diretórios

| Direatório | Propósito |
|---|---|
| `core/` | Schema canônico, relacionamentos, segurança, verificação, nomenclatura |
| `entities/` | Entidades do mundo real (emails, contas, projetos, etc.) |
| `platforms/` | Braços especializados por plataforma (Meta, Vercel, GitHub…) |
| `relationships/` | Definição e registro de relacionamentos entre entidades |
| `credentials/` | Referências de credenciais (NUNCA secrets) |
| `inbox/` | Área de quarentena para descobertas não resolvidas |
| `audits/` | Critérios e rotinas de auditoria |
| `logs/` | Descobertas, alterações e conflitos |
| `reports/` | Relatórios gerados |
| `templates/` | Templates reutilizáveis |

## Fluxo de Descoberta

```
DESCOBERTA
    ↓
INBOX (quarentena)
    ↓
NORMALIZação
    ↓
DEDUPE (eliminação de duplicatas)
    ↓
VERIFICAção
    ↓
ENTIDADE CANÔNICA
    ↓
RELACIONAMENTOS
    ↓
LOG (descoberta/alteração)
```

Itens com status UNCERTAIN não entram diretamente na fonte de verdade.

## Modelo de Confiança

Todo recurso possui um `verification_status`:

- **VERIFIED** — informação confirmada por fonte confiável
- **UNVERIFIED** — registrada mas ainda não confirmada
- **STALE** — foi verificada há muito tempo, precisa ser reconfirmada
- **UNKNOWN** — informação ausente ou não descoberta
- **CONFLICT** — há divergência entre fontes

Informações antigas NUNCA são apresentadas como atuais sem aviso explícito.

## Política de Segurança

- **PROIBIDO** persistir: passwords, API keys, tokens, private keys, secrets, .env, códigos 2FA, PINs, CVV, números de cartão, connection strings com credenciais.
- Apenas **referências** de credenciais são armazenadas (ex: `1password/vercel/email-007`).
- Todo descoberta é sanitizada antes de persistência.
- Logs também seguem esta política.

## Adicionando Novos Braços

Um braço (plataforma) deve:

1. Descobrir
2. Normalizar
3. Sanitizar
4. Deduplicar
5. Verificar
6. Converter para o schema central
7. Relacionar
8. Persistir
9. Registrar descoberta relevante

Um braço pode possuir conhecimento específico sobre uma plataforma, mas NÃO pode criar um modelo de dados incompatível com o core.
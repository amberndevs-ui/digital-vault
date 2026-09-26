# ID Allocation Registry & Concurrency Strategy

Registro de IDs alocados por prefixo e estratégia de controle de concorrência para ambiente Dropbox.

---

## Formato Canônico de ID (Definitivo)

**Exclusivamente:** `PREFIXO-NNNN`

| Prefixo | Exemplos |
|---|---|
| `EMAIL` | EMAIL-0001, EMAIL-0002 |
| `ACCOUNT` | ACCOUNT-0001, ACCOUNT-0002 |
| `PROJECT` | PROJECT-0001, PROJECT-0002 |
| `DOMAIN` | DOMAIN-0001, DOMAIN-0002 |
| `REPO` | REPO-0001, REPO-0002 |
| `SERVER` | SERVER-0001, SERVER-0002 |
| `PHONE` | PHONE-0001, PHONE-0002 |
| `SIM` | SIM-0001, SIM-0002 |
| `DEVICE` | DEVICE-0001, DEVICE-0002 |
| `BILLING` | BILLING-0001, BILLING-0002 |
| `META` | META-0001 |
| `BM` | BM-0001 |
| `ADS` | ADS-0001 |
| `PAGE` | PAGE-0001 |
| `PIXEL` | PIXEL-0001 |
| `WABA` | WABA-0001 |
| `WA` | WA-0001 |
| `API` | API-0001 |
| `CRED` | CRED-0001 |
| `AUDIT` | AUDIT-0001 |
| `LOG` | LOG-0001 |
| `CONFLICT` | CONFLICT-0001 |
| `REL` | REL-0001 |
| `INBOX` | INBOX-2026-09-26-001 |

**Proibido como ID canônico:**
- Sufixos por agente/host (`EMAIL-0001-A`, `EMAIL-0001-B`)
- Faixas fixas permanentes por máquina (`PC1=0001-0999`, `PC2=1000-1999`)
- Qualquer variação que não `PREFIXO-NNNN`

Identificadores temporários durante ingestão concorrente **permanecem apenas em inbox/staging** e nunca viram IDs canônicos.

---

## Limitação Fundamental: Dropbox ≠ Lock Distribuído

**O Dropbox oferece sincronização eventual, não atomicidade distribuída.**

- Não existe mecanismo de lock distribuído no nível de filesystem via Dropbox.
- Dois computadores escrevendo o mesmo arquivo simultaneamente → `conflicted copy`.
- Nenhuma operação local deve ser descrita como lock distribuído.
- `ids-allocated.md` é **somente registry/índice auxiliar** — **nunca** autoridade suficiente para afirmar que um ID está livre.

---

## Estratégia de Criação Local (Single-Machine)

Para criar uma entidade canônica localmente, usar a operação **mais exclusiva/atômica disponível no runtime**:

### Opção Preferida (quando suportada): Criação Exclusiva Atômica

```python
# Exemplo conceitual - open com O_EXCL / FileMode.CreateNew
try:
    with open(entity_path, 'x', encoding='utf-8') as f:  # 'x' = exclusive creation
        f.write(yaml_content)
    # Sucesso: arquivo criado atomicamente, ID reservado
except FileExistsError:
    # Colisão local: outro processo criou o arquivo primeiro
    # buscar próximo ID vago e repetir
```

### Fallback (sem criação exclusiva): Verificação + Escrita + Revalidação

Se o runtime/filesystem **não** suporta criação exclusiva atômica:
1. Ler `ids-allocated.md` para candidato.
2. Verificar se `entities/<tipo>/<PREFIXO>-<NNNN>.yaml` **não existe** no filesystem local.
3. Escrever arquivo temporário (`.tmp`).
4. Validar conteúdo temporário (parse YAML, schema).
5. Renomear atomicamente (rename) para nome final.
6. **Revalidar imediatamente**: reler arquivo final, confirmar ID.
7. Atualizar `ids-allocated.md`.

**Declaração explícita:** Esta sequência tem janela TOCTOU (Time-of-Check-Time-of-Use). **Não promete ausência de colisões.** Colisões locais são possíveis e devem ser detectadas.

---

## Protocolo Pré-Promoção (Antes de Salvar Entidade Canônica)

Executar **sempre**, em ordem:

| Passo | Verificação | Ação se Falhar |
|---|---|---|
| 1 | `entities/<tipo>/<ID>.yaml` **não existe** localmente | Incrementar candidato, voltar ao passo 1 |
| 2 | `ids-allocated.md` indica mesmo próximo disponível | Atualizar contador localmente, continuar |
| 3 | **Nenhum** `*conflicted copy*` para este prefixo em `entities/<tipo>/` ou `logs/` | Registrar conflito, bloquear promoção, ir para resolução |
| 4 | Inbox/staging não tem item concorrente para mesmo ID | Aguardar resolução do item concorrente |
| 5 | Criar arquivo via método mais exclusivo disponível (acima) | Se colisão detectada → incrementar, voltar ao passo 1 |
| 6 | Registrar alocação em `ids-allocated.md` | — |
| 7 | **Revalidar**: reler entidade + registry, confirmar consistência | Se inconsistente → marcar CONFLICT, não promover |

---

## Tratamento de Colisão Pós-Sincronização (Dropbox)

Quando sincronização revela colisão (duas máquinas alocaram mesmo ID, ou `conflicted copy`):

### Regra Absoluta

**NUNCA sobrescrever. NUNCA apagar automaticamente.**

### Procedimento Rigoroso

1. **Detectar**: Auditoria encontra `conflicted copy` ou duas entidades com mesmo ID em `entities/`.

2. **Preservar ambos os registros**: Manter **ambos** os registros originais intocados (renomear para `CONFLICT-<ID>-A.yaml`, `CONFLICT-<ID>-B.yaml` ou mover para `logs/conflicts/`). **Nenhum dado é perdido ou mesclado automaticamente.**

3. **Marcar o conflito**: Ambas as entidades → `status: CONFLICT`, `verification.status: CONFLICT`. Adicionar campo `conflict_reason: "duplicate_id_post_sync"` e `conflict_detected_at: <ISO8601>`.

4. **Determinar reivindicação canônica via proveniência/histórico verificável** (NÃO baseado em "mais recente" ou "mais completa"):

   Critérios de decisão em ordem de prioridade:
   
   a. **Identidade canônica da entidade real** — As duas entradas representam a MESMA entidade do mundo real?
      - Comparar chaves de identidade normalizadas (ver `NAMING.md`: email normalizado, domain registrável, phone E.164, account platform+stable_id, project stable_id externo, Meta IDs oficiais)
      - Se chaves de identidade **diferem** → são entidades DISTINTAS que colidiram no ID (erro de alocação). Cada uma merece seu próprio ID.
      - Se chaves de identidade **são iguais** → mesma entidade real, descobrir quem tem a proveniência primária.
   
   b. **Proveniência primária (source_type + source_ref + discovered_at)** — Qual registro tem a origem mais próxima da fonte autoritativa?
      - `source_type: api` com `source_ref` da plataforma oficial > `source_type: manual` > `source_type: inferred`
      - `discovered_at` mais antigo pode indicar registro original (mas não é decisivo sozinho)
      - Verificar `verification.status` e `confidence`
   
   c. **Histórico de verificação** — Qual registro tem cadeia de verificação mais forte?
      - `VERIFIED` com `last_verified` recente e `confidence` alta
      - Registros em `logs/discoveries/` e `logs/changes/` que corroboram
   
   d. **Relacionamentos estabelecidos** — Qual registro já possui relacionamentos validados com outras entidades canônicas?
   
   **Se os critérios acima NÃO permitem determinar com segurança (ambiguidade, empate, evidência insuficiente):**
   → **RESOLUÇÃO MANUAL OBRIGATÓRIA**. Não chutar. Registrar em `logs/conflicts/` com `resolution: "MANUAL_REQUIRED"`.

5. **Resolver conforme o caso**:

   **Caso A — Entidades DISTINTAS (chaves de identidade diferentes):**
   - Cada uma é entidade real diferente que acidentalmente recebeu o mesmo ID.
   - Alocar novo ID vago (`PREFIXO-NNNN`) para uma delas (por proveniência ou decisão manual).
   - Ambas mantêm status operacional apropriado.
   - Preservar `conflict_history` em ambas: `{ previous_id: "EMAIL-0007", conflict_id: "CONFLICT-...", resolved_at: "...", resolution: "reallocated_distinct_entity" }`.

   **Caso B — MESMA entidade real (chaves de identidade iguais):**
   - Existe **um único ID canônico** para essa entidade real.
   - O registro com proveniência mais forte permanece com o ID original (canônico).
   - O outro registro **NÃO recebe novo ID**. Ele vira **evidência histórica de reconciliação**:
     - Renomear para `RECONCILED-<ID>-<timestamp>.yaml` ou mover para `logs/conflicts/reconciled/`.
     - Marcar `status: RECONCILED`, `verification.status: VERIFIED` (reconciliação confirmada).
     - Preservar todo conteúdo como evidência de proveniência alternativa.
     - Registrar em `conflict_history` do canônico: `{ reconciled_duplicate: "RECONCILED-EMAIL-0007-20260926T140000Z", conflict_id: "CONFLICT-...", resolved_at: "...", resolution: "reconciled_same_entity" }`.
   - **Novo ID NÃO é alocado** neste caso — só existe uma entidade real.

6. **Atualizar relacionamentos em cascata**: Reescrever `relationships` em **todas** as entidades que apontavam para o ID conflitante original, apontando para o ID correto (canônico no Caso B; canônico OU novo ID no Caso A). Cada atualização gera entrada em `logs/changes/`.

7. **Registrar tudo em `logs/conflicts/CONFLICT-YYYY-MM-DD-NNN.yaml`**:
   - IDs originais conflitantes (`EMAIL-0007` duplicado)
   - Análise de proveniência por critério (a, b, c, d)
   - Classificação: Caso A (entidades distintas) ou Caso B (mesma entidade)
   - Decisão: qual ID permanece canônico, qual foi realocado (Caso A) ou reconciliado (Caso B)
   - Entidades afetadas (relacionamentos atualizados)
   - Responsável/resolution_at
   - Se manual: justificativa da decisão

8. **Limpar**: Remover `conflicted copy` física redundante do Dropbox **SOMENTE APÓS VALIDAR** que:
   - (a) Ambas as versões originais foram preservadas no histórico de conflito (`logs/conflicts/` ou `CONFLICT-<ID>-A/B.yaml` ou `RECONCILED-...`)
   - (b) IDs finais estão únicos no filesystem `entities/`
   - (c) Referências (`relationships`) foram atualizadas e verificadas em todas as entidades afetadas
   - (d) O registro `logs/conflicts/CONFLICT-YYYY-MM-DD-NNN.yaml` foi persistido e validado
   - **NUNCA apagar a única evidência de uma versão conflitante.** Se qualquer validação falhar → manter `conflicted copy` até resolução completa.

---

## Tabela de Registro de IDs Alocados

| Prefixo | Categoria | Último Número Alocado | Próximo Disponível |
|---|---|---:|---|
| EMAIL | Email | 30 | 31 |
| ACCOUNT | Conta de plataforma | 20 | 21 |
| FBPROF | Perfil Facebook | 6 | 7 |
| ORG | Organização/Empresa | 1 | 2 |
| PROJECT | Projeto/Marca/Site | 8 | 9 |
| DOMAIN | Domínio | 4 | 5 |
| REPO | Repositório Git | 1 | 2 |
| SERVER | Servidor/VPS | 1 | 2 |
| PHONE | Telefone | 0 | 1 |
| SIM | SIM card / Chip | 0 | 1 |
| DEVICE | Dispositivo | 2 | 3 |
| BILLING | Billing / Assinatura | 1 | 2 |
| META | Perfil Meta | 0 | 1 |
| BM | Business Manager | 0 | 1 |
| ADS | Conta de Anúncios | 0 | 1 |
| PAGE | Página FB/IG | 0 | 1 |
| PIXEL | Pixel / Dataset | 0 | 1 |
| WABA | WhatsApp Business Account | 0 | 1 |
| WA | WhatsApp | 0 | 1 |
| API | API Key / Endpoint | 0 | 1 |
| CRED | Referência de Credencial | 1 | 2 |
| AUDIT | Relatório de Auditoria | 0 | 1 |
| LOG | Log | 0 | 1 |
| CONFLICT | Registro de Conflito | 0 | 1 |
| REL | Relacionamento separado | 0 | 1 |
| INBOX | Item da Inbox | 0 | 1 |

> **Nota:** `Último Número Alocado` = maior NNNN já persistido em `entities/`. `Próximo Disponível` = sugestão indicativa (pode estar desatualizado por sync pendente). **Sempre validar no filesystem antes de usar.**

---

## Regras Finais de Atribuição

1. Formato **sempre** `PREFIXO-NNNN` com 4 dígitos (zeros à esquerda: `EMAIL-0001`).
2. **NUNCA reutilizar** números de entidades deletadas/arquivadas.
3. Antes de salvar: verificar existência real no filesystem `entities/<tipo>/`.
4. Usar criação exclusiva atômica quando disponível; senão, fallback com revalidação.
5. `ids-allocated.md` é guia indicativo — **validar no filesystem é a autoridade**.
6. Colisão detectada → bloquear promoção, resolver via `logs/conflicts/`.

---

## Testes Conceituais

| # | Cenário | Comportamento Esperado |
|---|---|---|
| **T1** | **Concorrência local** (dois processos mesmo PC tentam `EMAIL-0007`) | Criação exclusiva (`open('x')`) permite apenas um vencer; outro recebe `FileExistsError`, incrementa para `EMAIL-0008`, cria com sucesso. |
| **T2** | **Dois computadores Dropbox** (PC1 e PC2 leem registry `next=7`, ambos criam `EMAIL-0007` localmente) | Cada um cria localmente. Dropbox gera `EMAIL-0007 (conflicted copy PC2).yaml`. Auditoria detecta. |
| **T3** | **Conflicted copy** aparece em `entities/emails/` | Auditoria marca ambas `CONFLICT`, preserva ambos, **analisa proveniência** (chaves de identidade, source_type, verification history, relacionamentos). Se mesma entidade real → Caso B (reconciliação). Se entidades distintas → Caso A (realocação). |
| **T4** | **Registry desatualizado** (PC1 alocou até 10, PC2 registry ainda mostra `next=7`) | PC2 verifica filesystem, vê `EMAIL-0007` a `EMAIL-0010` já existem, incrementa localmente até `EMAIL-0011`, cria. Registry atualizado depois. |
| **T5** | **Dois agentes mesmo próximo ID** (ambos leem `next=15`) | Mesmo que T2. Criação exclusiva local previne colisão local. Dropbox resolve via conflicted copy. Auditoria detecta e resolve via proveniência. |
| **T6** | **Preservação formato PREFIXO-NNNN** | Em nenhum cenário IDs como `EMAIL-0001-A`, `EMAIL-1000` (faixa fixa), ou `EMAIL-7` (sem zero padding) são gerados como canônicos. Apenas `EMAIL-0001`..`EMAIL-9999`. |
| **T7** | **Fallback sem criação exclusiva** (runtime sem `O_EXCL`) | Sequência: check → write tmp → rename → revalidate. Se colisão na janela TOCTOU → revalidate falha (arquivo tem ID diferente) → incrementar e repetir. |
| **T8** | **Inbox item com ID temporário** | Item em `inbox/` usa `inbox_id: INBOX-...` (formato próprio). Só vira `EMAIL-XXXX` na promoção, passando pelo protocolo completo. |
| **T9** | **Colisão de entidades DISTINTAS com mesmo ID** (Caso A) — PC1 criou `EMAIL-0007` para `user@a.com`, PC2 criou `EMAIL-0007` para `user@b.com` | Auditoria detecta chaves de identidade diferentes (emails distintos). **Não mesclar**. Cada uma é entidade real diferente. Alocar `EMAIL-0008` para uma (por proveniência ou manual), manter outra como `EMAIL-0007`. Atualizar relacionamentos de cada uma independentemente. `conflict_history` com `resolution: "reallocated_distinct_entity"`. |
| **T10** | **Colisão de MESMA entidade real** (Caso B) — PC1 e PC2 descobriram `user@gmail.com` independentemente | Chaves de identidade iguais. Proveniência decide canônico (ex: `source_type: api` + `source_ref: gmail` + `discovered_at` mais antigo + `VERIFIED` + relacionamentos). Canônico permanece `EMAIL-0007`. O outro **NÃO recebe novo ID** — vira evidência histórica `RECONCILED-EMAIL-0007-<timestamp>.yaml` com `status: RECONCILED`, preservado como proveniência alternativa. `conflict_history` do canônico registra `resolution: "reconciled_same_entity"`. |

---

## Limitações que Permanecem

1. **Sem atomicidade distribuída real** — Dropbox não fornece. Colisões entre máquinas **acontecerão** e serão resolvidas pós-fato.
2. **Janela TOCTOU no fallback** — Se runtime não tem `O_EXCL`, colisão local é possível (rara, mas não impossível).
3. **Registry pode ficar stale** — `ids-allocated.md` é eventualmente consistente. Filesystem é a fonte da verdade.
4. **Resolução manual necessária** — Colisões Dropbox exigem intervenção quando proveniência não determina canônico com segurança.
5. **Atualização de relacionamentos em cascata** — Ao renomear ID conflitante, todas as entidades referenciadoras devem ser atualizadas. Processo não atômico distribuído.

---

## Resumo de Arquivos Alterados

- `logs/ids-allocated.md` — **Reescrito completamente** com estratégia corrigida, tabela de 4 colunas, protocolo pré-promoção, tratamento de colisão rigoroso baseado em proveniência (Caso A: entidades distintas → realocação; Caso B: mesma entidade → reconciliação sem novo ID), limpeza condicionada a 4 validações, testes expandidos T1–T10.
- `core/NAMING.md` — Seção "Concorrência de IDs (Dropbox)" aponta para este arquivo; formato canônico já correto (`PREFIXO-NNNN`).

Criar o Digital Vault: um sistema pessoal inteligente para organizar, mapear e relacionar toda a minha infraestrutura digital, contas, identidades, projetos, serviços, recursos de publicidade e ativos online.

CONTEXTO

Possuo muitos emails, contas, projetos, sites, serviços, números de telefone, chips, contas Meta/Facebook, contas de anúncios, hospedagens, APIs e ferramentas.

Com o tempo, torna-se difícil lembrar:

- qual email foi usado em determinada plataforma
- onde determinado site está hospedado
- qual conta possui determinado projeto
- qual conta Meta pertence a determinada operação
- qual conta de anúncios pertence a determinado projeto
- qual número de WhatsApp está relacionado a determinada operação
- onde determinada API foi cadastrada
- qual conta possui billing
- quais serviços possuem créditos
- onde determinada credencial está armazenada
- quais recursos ainda estão ativos
- quando determinada informação foi verificada pela última vez

O Digital Vault deve resolver esse problema construindo progressivamente um mapa confiável e pesquisável da minha vida digital operacional.

==================================================
1. RECURSOS QUE DEVEM SER ORGANIZADOS
==================================================

IDENTIDADES E CONTAS

- pessoas/perfis
- emails
- contas de plataforma
- organizações
- empresas
- contas pessoais
- contas profissionais
- usernames
- identificadores internos

PROJETOS

- projetos
- marcas
- empresas
- produtos
- sites
- aplicações
- operações

DESENVOLVIMENTO E INFRAESTRUTURA

- GitHub e outros repositórios Git
- repositórios
- Vercel
- Cloudflare
- Supabase
- bancos de dados
- VPS
- servidores
- Docker
- hospedagens
- provedores cloud
- APIs
- ferramentas de desenvolvimento
- provedores de IA
- modelos de IA
- serviços externos

DOMÍNIOS

- domínios
- subdomínios
- registradores
- DNS
- Cloudflare
- projeto relacionado
- hospedagem relacionada
- data de renovação quando conhecida
- status

META / FACEBOOK

- perfis Facebook
- contas Meta
- Business Portfolios
- Business Managers
- contas de anúncios
- páginas
- Pixels
- datasets
- aplicativos Meta
- WhatsApp Business Accounts (WABA)
- números vinculados
- projetos/marcas relacionados
- emails associados
- status
- billing por referência
- restrições/verificações conhecidas

PUBLICIDADE

- plataforma de publicidade
- conta de anúncios
- identificador da conta
- Business/organização proprietária
- projeto relacionado
- domínio relacionado
- página relacionada
- pixel/dataset relacionado
- forma de pagamento por referência
- status
- limite conhecido
- créditos conhecidos
- última verificação

WHATSAPP / TELEFONIA

- números de telefone
- números WhatsApp
- WhatsApp comum
- WhatsApp Business
- WhatsApp Business Platform
- chips/SIMs
- operadora
- finalidade
- projeto/marca associado
- aparelho onde está sendo utilizado
- WABA associada
- Meta Business associada
- email relacionado
- status
- última verificação

DISPOSITIVOS

- celulares
- computadores
- servidores
- dispositivos utilizados por determinados números/contas
- finalidade
- projeto relacionado

FINANCEIRO OPERACIONAL

- assinaturas
- planos
- billing
- créditos
- limites
- trials
- renovações
- cobranças recorrentes
- formas de pagamento SOMENTE POR REFERÊNCIA

Nunca armazenar dados financeiros sensíveis completos.

==================================================
2. RELACIONAMENTOS
==================================================

O principal objetivo não é simplesmente armazenar listas.

O Digital Vault deve entender RELACIONAMENTOS entre recursos.

Exemplos:

EMAIL
→ CONTA
→ PLATAFORMA
→ PROJETO
→ DOMÍNIO
→ REPOSITÓRIO
→ BANCO DE DADOS
→ INFRAESTRUTURA
→ API
→ BILLING

Outro exemplo:

PROJETO
→ META BUSINESS
→ CONTA DE ANÚNCIOS
→ PÁGINA
→ PIXEL
→ WABA
→ WHATSAPP
→ CHIP
→ DISPOSITIVO

Um recurso pode possuir múltiplos relacionamentos.

O sistema deve permitir navegar nos dois sentidos.

Exemplo:

"Qual email está relacionado ao projeto X?"

e também:

"Quais projetos e plataformas estão relacionados ao email X?"

==================================================
3. IDENTIFICADORES INTERNOS
==================================================

Cada recurso importante deve possuir identificador interno único quando necessário para evitar ambiguidades.

Exemplos:

EMAIL-001
ACCOUNT-001
PROJECT-001
DOMAIN-001
GITHUB-001
SERVER-001
META-001
BM-001
ADS-001
PAGE-001
PIXEL-001
WABA-001
WA-001
SIM-001
DEVICE-001
API-001
BILLING-001

Não depender apenas de nomes.

Dois recursos podem possuir nomes semelhantes ou iguais.

==================================================
4. PERGUNTAS QUE O SISTEMA DEVE CONSEGUIR RESPONDER
==================================================

Exemplos:

- Em qual email cadastrei este serviço?
- Onde determinado site está hospedado?
- Qual conta da Vercel contém determinado projeto?
- Qual GitHub está relacionado ao projeto?
- Qual Supabase pertence ao site?
- Quais serviços estão associados a determinado email?
- Qual email está associado a determinada conta Meta?
- Qual Business Manager possui determinada conta de anúncios?
- Qual conta de anúncios pertence a determinado projeto?
- Qual página está ligada à conta de anúncios?
- Qual Pixel/dataset pertence à operação?
- Qual WhatsApp está relacionado ao projeto?
- Qual chip corresponde ao número?
- Em qual aparelho o chip está sendo utilizado?
- Qual WABA possui determinado número?
- Quais projetos utilizam determinado número?
- Quais serviços possuem billing?
- Quais assinaturas estão ativas?
- Tenho créditos em determinada plataforma?
- Quando essa informação foi verificada?
- Quais informações estão desatualizadas?
- Quais recursos estão sem projeto relacionado?
- Quais contas estão duplicadas?
- Quais relações ainda são desconhecidas?
- Onde está armazenada a credencial de determinada API?

==================================================
5. CONFIABILIDADE DA INFORMAÇÃO
==================================================

Cada informação relevante deve possuir, quando possível:

- origem
- data de descoberta
- data da última verificação
- status de verificação
- observações
- nível de confiança quando necessário

Estados possíveis podem incluir:

VERIFIED
UNVERIFIED
STALE
UNKNOWN
CONFLICT

Informações antigas não devem ser apresentadas como atuais sem aviso.

Se uma informação não tiver sido verificada recentemente, informar isso claramente.

Nunca inventar relacionamento para preencher informação ausente.

Quando não souber:

UNKNOWN

é melhor que uma suposição.

==================================================
6. DESCOBERTA E APRENDIZADO
==================================================

O Digital Vault deve crescer progressivamente.

Quando uma nova informação confiável for descoberta:

1. identificar o recurso
2. verificar se já existe
3. evitar duplicação
4. relacionar com recursos existentes
5. registrar a origem
6. registrar data da descoberta
7. atualizar última verificação
8. registrar mudança relevante

Quando encontrar conflito entre informações:

- não sobrescrever silenciosamente
- preservar evidências
- marcar como CONFLICT
- solicitar resolução quando necessário

==================================================
7. HISTÓRICO
==================================================

Manter histórico relevante de:

- descobertas
- alterações
- verificações
- conflitos
- relacionamentos adicionados
- relacionamentos removidos
- informações desatualizadas

Não registrar alterações triviais sem valor operacional.

Nunca apagar informação relevante automaticamente.

==================================================
8. SEGURANÇA
==================================================

Este workspace será sincronizado pelo Dropbox entre vários computadores.

Portanto, tratar todo conteúdo do workspace como potencialmente sincronizado para múltiplos dispositivos.

É PROIBIDO armazenar diretamente:

- passwords
- API keys
- access tokens
- refresh tokens
- session tokens
- cookies de autenticação
- private keys
- secrets
- conteúdo de .env
- códigos 2FA
- recovery codes
- PINs
- CVV
- números completos de cartões
- credenciais de banco de dados
- connection strings contendo credenciais

O Digital Vault deve armazenar somente REFERÊNCIAS para credenciais.

Exemplo:

credential_ref: 1password/vercel/email-007

Nunca:

api_key: sk-xxxxxxxx

Secrets devem permanecer em um gerenciador seguro de credenciais separado.

O Digital Vault deve saber ONDE encontrar uma credencial, e não necessariamente conhecer seu valor.

==================================================
9. PRIVACIDADE DOS LOGS
==================================================

Antes de registrar evidências, remover ou mascarar:

- tokens
- passwords
- API keys
- cookies
- authorization headers
- secrets
- private keys
- códigos de autenticação
- informações financeiras sensíveis

Nenhum processo automático pode transformar um secret descoberto acidentalmente em informação persistente dentro do Dropbox.

==================================================
10. SINCRONIZAÇÃO ENTRE COMPUTADORES
==================================================

O workspace poderá ser utilizado em diferentes computadores através do Dropbox.

Evitar alterações concorrentes desnecessárias.

Quando forem detectados arquivos conflitantes ou informações divergentes:

- não apagar versões automaticamente
- preservar evidências
- identificar conflito
- solicitar resolução quando necessário

O sistema deve privilegiar integridade dos dados sobre conveniência.

==================================================
11. PRINCÍPIO FUNDAMENTAL
==================================================

O Digital Vault não é um gerenciador de senhas.

É um mapa inteligente da minha infraestrutura e operação digital.

Ele deve saber:

O QUE existe.
ONDE está.
A QUEM pertence.
QUAL conta utiliza.
QUAL email utiliza.
COM QUAL projeto está relacionado.
COM QUAIS outros recursos se conecta.
ONDE a credencial está armazenada.
QUAL o status atual conhecido.
QUANDO foi verificado.
QUAL a origem da informação.

==================================================
12. OBJETIVO FINAL
==================================================

Construir progressivamente uma fonte central de verdade sobre minha infraestrutura digital.

O objetivo é que eu possa perguntar naturalmente:

"onde está isso?"

"qual conta usei?"

"qual email está nisso?"

"esse número pertence a qual projeto?"

"onde hospedei esse site?"

"qual conta de anúncios usa esse WhatsApp?"

"onde está a chave dessa API?"

"essa conta ainda tem créditos?"

"quando verificamos isso pela última vez?"

e o Digital Vault consiga localizar, correlacionar e responder utilizando informações verificáveis do inventário, deixando claro quando algo estiver desconhecido, desatualizado ou conflitante.

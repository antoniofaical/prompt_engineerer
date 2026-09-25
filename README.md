# Prompt Engineerer

Transforme uma demanda escrita em Markdown em um prompt pronto para usar em outra
IA. O programa interpreta o pedido, esclarece lacunas, seleciona guidelines,
gera e revisa o texto. O objetivo é melhorar clareza e fidelidade; não há garantia
de um prompt universalmente ótimo.

## Início rápido

Pré-requisitos: **Python 3.11+**, Git e acesso à internet para instalação e API.
No Windows, use PowerShell 5.1+ ou PowerShell 7. Em Linux, a instalação do Python
precisa incluir `venv` e `pip` (em Debian/Ubuntu, normalmente `python3-venv`).

```console
git clone https://github.com/antoniofaical/prompt_engineerer.git
cd prompt_engineerer
```

**Windows / PowerShell**

```powershell
.\bootstrap.ps1
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
bash ./bootstrap.sh
source .venv/bin/activate
```

Na primeira execução é normal o bootstrap terminar com código **2**: o ambiente
está instalado e testado, mas o seed vazio ou a credencial ainda precisam ser
configurados. Leia as linhas `[PENDENTE]` e siga as instruções abaixo.

1. Configure a variável de ambiente da API key.
2. Edite `user/seed_prompt.md` com sua demanda.
3. Se necessário, edite `user/configs.toml`.
4. Execute:

```console
prompt-engineerer --check
prompt-engineerer
```

Responda às perguntas no terminal e copie o conteúdo de
`user/optimized_prompt.md` para a IA destinatária. Não renomeie esses arquivos.
O programa também pode ser iniciado com `python -m prompt_engineerer`.

Sem ativação do venv, use `./.venv/bin/python -m prompt_engineerer` em Linux/macOS
ou `.\.venv\Scripts\python.exe -m prompt_engineerer` no Windows. Depois de instalado
em modo editável pelo bootstrap, o comando encontra o projeto mesmo a partir de
outro diretório. Instalação global ou wheel isolado não é o fluxo suportado.

## Duas IAs, responsabilidades diferentes

| Papel | Configuração |
|---|---|
| **Gerador**: executa esta ferramenta e escreve/revisa o prompt | OpenAI `gpt-5-mini`, definido em `src/prompt_engineerer/technical.py` |
| **Destinatária**: recebe o prompt que você copiar | `[target_ai]` em `user/configs.toml` |

O modelo gerador é uma decisão técnica inicial, não uma afirmação de que seja o
melhor modelo para todos os pedidos. Sua conta precisa permitir acesso a ele.
Trocar `target_ai` não troca a API utilizada nem a credencial necessária.
Uma chave de outro provedor não passa a funcionar por mudar o nome da variável.

O seed, os esclarecimentos e os drafts são enviados à API OpenAI. A aplicação
solicita `store=False`; isso não equivale a garantir retenção zero pelo provedor.
O programa não executa o pedido do seed, não navega na web e não abre os caminhos
ou URLs mencionados no texto. Inclua o conteúdo relevante no seed quando quiser
que ele seja considerado durante a geração.

## Credencial nas variáveis de ambiente do sistema

`api_key_env_var` contém **o nome da variável**, nunca a chave. O Python lê o valor
herdado pelo processo. Não há leitura de `.env`, registro do valor no console ou
armazenamento da chave no repositório.

### Windows

Para definir a chave somente na sessão atual, sem digitá-la no histórico de comandos:

```powershell
$PromptCredential = Read-Host 'API key OpenAI' -AsSecureString
$PromptPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($PromptCredential)
try {
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($PromptPointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($PromptPointer)
    Remove-Variable PromptCredential, PromptPointer
}
```

Para persistir no perfil de usuário, após o comando anterior:

```powershell
[Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $env:OPENAI_API_KEY, 'User')
```

Também é possível criar `OPENAI_API_KEY` nas **Variáveis de Ambiente do Usuário**
do Windows. Reabra o terminal e, quando necessário, o VS Code para que novos
processos recebam a variável. Não é necessário administrador para a variável do usuário.

### Linux / macOS

No Bash, somente para a sessão atual:

```bash
read -r -s -p 'API key OpenAI: ' OPENAI_API_KEY
printf '\n'
export OPENAI_API_KEY
```

No Zsh (padrão em muitos macOS):

```zsh
read -r -s 'OPENAI_API_KEY?API key OpenAI: '
printf '\n'
export OPENAI_API_KEY
```

Para persistência, configure `export OPENAI_API_KEY="sua-chave"` no arquivo de
inicialização apropriado do shell, como `~/.bashrc` ou `~/.zshrc`, usando um editor.
Isso armazena a chave nesse arquivo: mantenha-o privado. Serviços e tarefas agendadas
precisam receber a variável em seu próprio ambiente; não herdam necessariamente o shell.

Se preferir outro nome, por exemplo `MY_PROMPT_KEY`, configure esse nome no sistema
e altere `api_key_env_var` para `"MY_PROMPT_KEY"`.

## Arquivos e preservação dos dados

```text
prompt_engineerer/
├── src/prompt_engineerer/
│   ├── … código Python e configuração técnica
│   ├── resources/
│   │   ├── system.md
│   │   ├── guidelines.json
│   │   ├── guidelines-index-original.md
│   │   ├── sources.md
│   │   ├── evaluation-cases.json
│   │   └── templates/
│   └── tests/
├── user/
│   ├── seed_prompt.md
│   ├── optimized_prompt.md
│   └── configs.toml
├── bootstrap.ps1
├── bootstrap.sh
├── pyproject.toml
├── .gitignore
└── README.md
```

O Git contém modelos dentro de `src/`. No primeiro bootstrap, os três arquivos
em `user/` são criados; nas execuções seguintes, somente os ausentes são criados.
Seus conteúdos são ignorados pelo Git para preservar demandas e configurações
locais durante atualizações. O clone inicial pode mostrar apenas `user/.gitkeep`.

- O seed e o TOML nunca são reescritos pelo fluxo de geração.
- Cada geração aprovada substitui o resultado anterior; não há histórico automático.
- Falha antes da substituição final preserva o resultado existente.
- Um lock impede duas gerações simultâneas sobre os mesmos arquivos.
- Para recriar um arquivo ausente sem instalar novamente: `prompt-engineerer --init`.
- Salve os arquivos em UTF-8. O programa aceita BOM usado por alguns editores Windows.

## Configuração comentada em TOML

```toml
api_key_env_var = "OPENAI_API_KEY"
target_interface = "chat"
output_language = "auto"
max_clarification_rounds = 3
max_revision_rounds = 2
# target_tools = ["web_browsing", "file_reading"]

[target_ai]
provider = ""
model = ""
```

| Campo | Padrão | Valores e significado |
|---|---|---|
| `api_key_env_var` | `"OPENAI_API_KEY"` | Nome da variável de ambiente que contém a chave OpenAI. |
| `target_interface` | `"chat"` | `"chat"`, `"api_user"` ou `"api_system"`. |
| `output_language` | `"auto"` | Idioma do prompt gerado; auto acompanha o seed. Aceita `"pt-BR"`, `"en"`, `"es"` ou outro idioma explícito. |
| `max_clarification_rounds` | `3` | Inteiro de 0 a 10; até 3 perguntas por rodada. 0 desativa perguntas. |
| `max_revision_rounds` | `2` | Inteiro de 0 a 5; ciclos de correção depois da revisão inicial. 0 mantém a revisão, mas impede correções. |
| `target_tools` | Omitido | Lista das capacidades declaradas; veja abaixo. |
| `target_ai.provider` | `""` | Provedor destinatário. Vazio significa não especificado. |
| `target_ai.model` | `""` | Modelo destinatário. Vazio significa não especificado. |

Campos omitidos usam os padrões. Campos desconhecidos e valores de tipo errado
geram erro, em vez de serem ignorados. Use inteiros sem aspas para os limites.

**Em TOML, tudo após `[target_ai]` pertence a essa tabela.** Mantenha os campos
gerais acima dela. TOML aceita comentários iniciados por `#`, mas não possui `null`.

### Chat, API user e API system

| Opção | Uso do Markdown | Exemplo de intenção |
|---|---|---|
| `chat` | Copiar e colar em uma conversa. | “Analise este artigo e destaque suas limitações.” |
| `api_user` | Conteúdo da mensagem de usuário enviada pelo seu programa à API. | Pedido específico para uma execução, com seus dados. |
| `api_system` | Instrução que orienta o comportamento de um assistente. | “Analise artigos com base no material recebido e sinalize lacunas.” |

Escrever “system” em um cabeçalho não define o papel da mensagem. A aplicação que
chama a API precisa colocar o texto no campo apropriado. Algumas APIs/modelos usam
`developer` para esse tipo de instrução; `api_system` descreve a finalidade, não
uma promessa de compatibilidade com todos os endpoints. A ferramenta entrega um
único Markdown, não uma requisição HTTP nem um conjunto de mensagens JSON.

### Provedor, modelo e ambiguidades

| Preenchimento | Resultado |
|---|---|
| Ambos vazios | Orientações gerais; preserva a intenção de destino explícita no seed. |
| Apenas provedor | Orientações pertinentes ao provedor, sem escolher um modelo. |
| Apenas modelo reconhecível | Inferência do provedor pela família do nome, mostrada no console. |
| Ambos compatíveis | Destino identificado, usando apenas recomendações disponíveis no catálogo. |
| Ambos contraditórios | Erro com pedido para corrigir o TOML. |
| Nome desconhecido | Opção de continuar com orientações gerais ou encerrar para corrigir. |

Aliases de provedor: `openai`, `open ai`, `chatgpt`; `anthropic`, `claude`;
`google`, `gemini`; `meta`; `mistral`; `xai`, `x.ai`. ChatGPT e Claude podem designar
produtos, não modelos exatos: nesses campos são apenas atalhos para o provedor.
Famílias reconhecíveis incluem GPT/o1/o3/o4, Claude, Gemini, Llama, Mistral/Codestral/
Magistral e Grok. O catálogo **não verifica a existência nem o acesso a um modelo**.

Nomes desconhecidos não são automaticamente inválidos. Sem perguntas habilitadas,
o sistema avisa e usa orientações gerais. Com perguntas habilitadas, a confirmação
de destino desconhecido é uma decisão de configuração anterior às rodadas do seed.

O MVP inclui orientações específicas de OpenAI e Anthropic; outros provedores
recebem orientações gerais, mesmo quando reconhecidos. Não inventa recomendações
por modelo. Para obter seleção específica, preencha `target_ai`; mencionar somente
um modelo no seed preserva a intenção textual, mas não amplia o catálogo local.

Uma menção a outra IA no seed não significa necessariamente troca de destino.
Conflitos explícitos relevantes são sinalizados para esclarecimento; quando
exigirem mudar a configuração, edite o TOML e execute novamente.

### Ferramentas da destinatária

Opções: `web_browsing` (pesquisa/navegação), `code_execution` (execução de código)
e `file_reading` (leitura de arquivos).

- Campo ausente/comentado: capacidades desconhecidas; não são presumidas.
- `target_tools = []`: nenhuma ferramenta disponível.
- `target_tools = ["web_browsing"]`: navegação declarada pelo usuário.

Esses valores ajudam a escrever instruções realizáveis. Não instalam nem habilitam
ferramentas em nenhuma IA. Listas não incluem capacidades implícitas por provedor.

### Idioma, tom e formato

`output_language` determina o idioma do **prompt gerado**. O seed pode pedir que a
IA destinatária responda em outro idioma. Por exemplo, prompt em inglês pedindo
um relatório em português. Tom, público, extensão e formato da entrega pertencem
ao seed. Se houver uma contradição explícita sobre o idioma do próprio prompt,
ela será tratada como conflito a esclarecer.

## Como escrever um seed útil

Descreva a dor em linguagem natural. Quando souber, inclua objetivo, contexto,
material disponível, restrições e o que tornaria a resposta útil. Não há template
obrigatório nem exigência de linguagem técnica.

Exemplo:

```markdown
Preciso comparar três soluções de gestão de estoque para uma rede de clínicas.
Vou fornecer descrições e preços das três. Quero uma tabela comparativa e uma
recomendação justificada. Avalie rastreabilidade, validade dos itens e integração
com nosso sistema. Quando faltar informação, indique o que perguntar ao fornecedor.
Não invente funcionalidades nem trate alegações comerciais como comprovação.
```

Boas práticas:

- Informe restrições reais e critérios de decisão; evite pedir apenas “o melhor”.
- Inclua exemplos quando já tiver referências úteis; não precisa inventá-los.
- Para refinar, acrescente ao seed o que faltou no resultado anterior.
- Declare somente ferramentas que a IA destinatária realmente possui.
- Revise o Markdown gerado antes de usá-lo, sobretudo requisitos e suposições.
- Compare resultados em tarefas reais; um prompt mais longo não é necessariamente melhor.
- Inclua apenas dados que podem ser enviados ao provedor gerador.

## Esclarecimento, revisão e custos

Cada pergunta mostra uma razão curta. Enter pula uma pergunta; `/fim` encerra os
esclarecimentos; Ctrl+C cancela. Respostas ficam em memória apenas naquela execução.
Lacunas comuns podem virar instruções condicionais ou pedidos de informação para
a IA destinatária. Contradições impeditivas não resolvidas bloqueiam a gravação.

A revisão compara o draft ao seed, às respostas e às configurações. A revisão por
IA pode falhar: ela é uma verificação adicional, não prova de correção ou melhora.
Se o limite de correções acabar com problemas impeditivos, o resultado anterior
é mantido e o console mostra os problemas encontrados.

Há normalmente 4 chamadas: análise, seleção, geração e revisão. Cada rodada com
respostas adiciona uma análise; cada correção adiciona geração corrigida e revisão.
Com os padrões, são até 11 chamadas lógicas, antes de novas tentativas por falhas.
Cada chamada pode ser tentada até 3 vezes. Chamadas reais podem gerar cobrança;
o bootstrap e `--check` não chamam a API. Tokens informados pela API aparecem no
resumo de uma execução concluída, sem cálculo de preço desatualizado.

## Bootstrap, atualizações e feedback

Os wrappers PowerShell/Bash localizam Python 3.11+ e executam o mesmo preflight
Python. O bootstrap:

1. Verifica Git e tenta atualizar o upstream da branch atual por avanço direto.
2. Reinicia o preflight a partir da versão em disco após a atualização.
3. Cria/reutiliza `.venv` e verifica Python e pip.
4. Atualiza pip/setuptools/wheel e dependências dentro das faixas do projeto.
5. Executa `pip check`, Ruff, verificação de formatação e pytest.
6. Cria apenas arquivos locais ausentes e verifica seed, TOML e credencial.
7. Mostra o comando de ativação e o resultado do preflight.

Não há atualização forçada, descarte de alterações, stash automático ou troca de
branch. Com arquivos locais alterados, HEAD destacado, upstream ausente ou commits
locais, a atualização é pulada com aviso. Falha de fetch mantém a versão local;
falha de instalação/teste interrompe o preflight. O bootstrap não atualiza Python
nem pacotes do sistema operacional e não corrige código automaticamente.

Para preparar somente o checkout local:

```powershell
.\bootstrap.ps1 --skip-update
```

```bash
bash ./bootstrap.sh --skip-update
```

Esse argumento pula Git, não torna a instalação offline: pip ainda pode precisar
de internet. Scripts executados em outro processo não ativam permanentemente o
venv do terminal chamador; por isso a ativação é mostrada ao final.

Todas as etapas exibem início e conclusão. Comandos demorados do bootstrap
mostram saída e aviso de atividade a cada 10 segundos; chamadas da aplicação
mostram spinner em terminal interativo e mensagens a cada 15 segundos quando a
saída é redirecionada. Não há porcentagens estimadas fictícias.

## Solução de problemas

| Situação | Como resolver |
|---|---|
| Código 2 no bootstrap/`--check` | Ambiente preparado, mas há pendências locais; leia `[PENDENTE]`. |
| Variável ausente | Confira o nome em `api_key_env_var` e o ambiente do processo. Reabra terminal/IDE após mudança persistente. |
| Chave presente, HTTP 401/403 | Verifique a credencial e acesso ao modelo da OpenAI. Presença não comprova autenticação. |
| HTTP 429 | Confira quota, créditos e limites de requisições. As tentativas são limitadas. |
| HTTP 400/404 | Verifique compatibilidade do modelo gerador, endpoint e SDK. |
| Timeout/rede | Confira conexão e proxy; se necessário ajuste parâmetros técnicos. |
| Configuração inválida | Veja o campo informado; confira tipo, aspas e posição de `[target_ai]`. |
| `.venv` incompleto/incompatível | Renomeie o diretório e execute o bootstrap com Python compatível. |
| Ruff/testes falharam | Consulte a saída; o bootstrap não modifica o código para forçar aprovação. |
| Pytest imprime muitos `x` e `environment variable is longer than 32767 characters` | Atualize o repositório e rode o bootstrap novamente. A versão inicial gerava um ID de teste enorme, excedendo o limite de `PYTEST_CURRENT_TEST` no Windows. Os casos agora usam IDs curtos; não altere sua API key ou o limite do seed. |
| PowerShell bloqueia script | Se permitido pela política da sua máquina, use `Set-ExecutionPolicy -Scope Process RemoteSigned`. |
| Comando não encontrado | Ative o venv ou use o caminho completo do Python dele. |
| Instalação fora do clone | Execute o bootstrap dentro do checkout para instalar em modo editável. |
| `user/.run.lock` existente | Aguarde a execução ativa. Após encerramento forçado, remova somente se não houver outro processo usando o projeto. |
| Resposta recusada/incompleta | Revise a demanda e tente novamente; o arquivo anterior permanece. |

Códigos de saída: `0` sucesso, `1` falha, `2` pendências no preflight (ou uso inválido
de argumentos), `130` cancelamento. Limite de seed: 120.000 bytes; resposta por
pergunta: 10.000 caracteres. Esses limites ficam em `technical.py`.

## Desenvolvimento, fontes e avaliação

```console
python -m pip install -e ".[dev]"
python -m ruff check src
python -m ruff format --check src
python -m pytest
```

`technical.py` define modelo gerador, endpoint, timeout (120s), retries (2) e limite
de saída (12.000 tokens, incluindo o orçamento que o modelo usar). A integração
OpenAI está isolada em `provider.py`; trocar provedor exige outro adaptador e testes.
O limite de timeout é aplicado ao cliente HTTP; a duração total inclui chamadas,
eventuais retries e interação humana. Uma execução completa pode levar minutos.

`resources/system.md` define o comportamento de autoria e revisão.
`resources/guidelines.json` contém as regras operacionais; `sources.md` registra
fontes, limitações e correções em relação ao índice original. O programa carrega
somente system prompt e catálogo operacional durante a geração.

Os testes usam respostas simuladas, incluindo HTTP simulado com o SDK real,
para testar orquestração, parsing, falhas, retries e preservação dos arquivos.
Não são evidência empírica de qualidade dos prompts.

`resources/evaluation-cases.json` contém casos de programação, pesquisa, redação,
planejamento e contradição. Para avaliar qualidade, use cada seed, gere o prompt
e compare as duas respostas em conversas separadas no mesmo modelo destinatário.
Registre modelo, data, configurações e critérios: fidelidade, cumprimento de
restrições, ausência de invenções, clareza e necessidade de correções. Sempre
que possível, avalie sem saber qual resposta veio do prompt otimizado. A execução
desses casos com modelos reais é manual e pode gerar custos adicionais.

Validação desta entrega: testes e bootstrap executados em Linux/Python 3.12.
A suíte inclui uma regressão que executa os casos de seed sob uma simulação do
limite de tamanho de variável de ambiente do Windows, cobrindo setup e teardown.
PowerShell e macOS exigem confirmação nos respectivos ambientes. Não foi feita
avaliação real com a API por ausência de credencial no ambiente de implementação.

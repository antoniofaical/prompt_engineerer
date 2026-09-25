---
document_type: prompt_engineering_guidelines_index
purpose: >
  Índice estruturado das principais fontes de prompt engineering guidelines,
  otimizado para consumo por IA. Cada entrada é autocontida (inclui os
  principais takeaways inline), para que o documento seja útil mesmo sem
  acesso à internet ou chamadas de ferramenta adicionais. Use a tabela de
  roteamento para decidir qual fonte é relevante antes de aprofundar via URL.
last_updated: 2026-09-25
source_count: 10
---

# Índice de Prompt Engineering Guidelines

## Tabela de roteamento rápido

| Preciso de... | Consultar |
|---|---|
| Prompting específico para modelos Claude (thinking, effort, tool use, agentes) | `anthropic-best-practices` |
| Checklist antes de começar a otimizar um prompt | `anthropic-overview` |
| Gerenciar contexto de agentes de longa duração / múltiplas ferramentas | `anthropic-context-engineering` |
| Prompting específico para a API da OpenAI / diferenças reasoning vs GPT | `openai-guide` |
| Visão panorâmica de técnicas e comparação entre modelos | `dair-ai-guide` |
| Introdução acessível + erros comuns a evitar | `claude-blog-2026` |
| Catálogo formal de padrões reutilizáveis (nome, estrutura, categoria) | `white-pattern-catalog` |
| Priorizar técnica conforme a fase da tarefa (elicitar, validar, etc.) | `re-systematic-review` |
| Refinar prompts de forma iterativa e sistemática (preferências) | `pdr-method` |
| Otimização automática de prompt em escala / produção | `dspy` |

## Princípios centrais (cross-cutting, válidos independente da fonte)

- Clareza e especificidade > qualquer truque de formatação.
- Explicar o "porquê" da instrução ajuda o modelo a generalizar, não só obedecer.
- Diga o que fazer, não o que evitar.
- 3–5 exemplos diversos e relevantes superam instrução abstrata.
- Dê permissão para o modelo expressar incerteza em vez de especular.
- Decomponha tarefas complexas em etapas (prompt chaining) em vez de um prompt único.
- Tags XML pesadas e role-prompting elaborado são hoje opcionais em modelos de ponta — úteis, não obrigatórios.
- Prompt engineering é empírico: defina critério de sucesso, teste, itere.

## Fontes

### [ID: anthropic-best-practices] Prompting best practices (Claude)

<meta>
<url>https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices</url>
<type>official_docs</type>
<authority>primary</authority>
<maintained_by>Anthropic</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Clareza e diretividade, exemplos, tags XML, papel de sistema, contexto longo, formatação de saída, uso de ferramentas, raciocínio (thinking), sistemas agênticos, migração entre modelos.</scope>

<key_points>
- Regra de ouro: mostre o prompt a um colega com contexto mínimo — se ele confundir, o modelo também confunde.
- Em prompts longos (20k+ tokens), dados no topo e pergunta no final podem melhorar a qualidade em até ~30%.
- Seja explícito quando quiser que o modelo aja (edite/execute), não apenas sugira.
- Para agentes: estado estruturado (JSON) + notas de progresso em texto livre + git como histórico funcionam bem.
- Ações destrutivas ou difíceis de reverter devem pedir confirmação antes de executar.
</key_points>

<when_to_consult>Prompting específico para modelos Claude atuais — thinking/effort, tool use, comportamento agêntico.</when_to_consult>

---

### [ID: anthropic-overview] Prompt engineering overview

<meta>
<url>https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview</url>
<type>official_docs</type>
<authority>primary</authority>
<maintained_by>Anthropic</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Quando prompt engineering é a solução certa; pré-requisitos antes de começar a iterar.</scope>

<key_points>
- Antes de otimizar: tenha critério de sucesso claro, forma de testar empiricamente, e um rascunho inicial.
- Nem todo problema é resolvido por prompt — às vezes trocar de modelo resolve custo/latência melhor.
</key_points>

<when_to_consult>Ponto de entrada / checklist antes de começar a mexer em um prompt.</when_to_consult>

---

### [ID: anthropic-context-engineering] Effective context engineering for AI agents

<meta>
<url>https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents</url>
<type>official_docs</type>
<authority>primary</authority>
<maintained_by>Anthropic</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Evolução do prompt engineering: gestão de tudo que entra na janela de contexto, não só da instrução isolada.</scope>

<key_points>
- Modelos têm orçamento de atenção finito — mais contexto nem sempre é melhor, pode degradar a resposta ("context rot").
- Curadoria modular: separar seções por função (background, ferramentas, exemplos, restrições) facilita manutenção.
- A pergunta muda de "qual a melhor instrução" para "qual configuração de contexto gera o comportamento desejado a cada passo".
</key_points>

<when_to_consult>Construção de agentes de longa duração, pipelines com múltiplas ferramentas/documentos, otimização de custo de contexto.</when_to_consult>

---

### [ID: openai-guide] Prompt engineering (OpenAI API)

<meta>
<url>https://developers.openai.com/api/docs/guides/prompt-engineering</url>
<type>official_docs</type>
<authority>primary</authority>
<maintained_by>OpenAI</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Papéis de mensagem (developer/user/assistant), estrutura Markdown+XML, few-shot, RAG, prompting de reasoning models vs. GPT, versionamento de prompt como código.</scope>

<key_points>
- Mensagens "developer" têm prioridade sobre "user" — pense como função (developer) e argumentos (user).
- Estruture developer messages em blocos: Identidade → Instruções → Exemplos → Contexto.
- Reasoning models recebem melhor instrução de alto nível (como colega sênior); modelos GPT precisam de instrução precisa (como colega júnior).
- Trate prompts de produção como código: versionados, testados, com avaliação automatizada.
</key_points>

<when_to_consult>Prompting para a API da OpenAI especificamente; diferenças entre reasoning models e modelos GPT padrão.</when_to_consult>

---

### [ID: dair-ai-guide] DAIR.AI Prompt Engineering Guide

<meta>
<url>https://www.promptingguide.ai</url>
<type>community_guide</type>
<authority>secondary (amplamente referenciado)</authority>
<maintained_by>DAIR.AI</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Fundamentos gerais (zero-shot, few-shot, CoT), técnicas avançadas (Tree of Thought, ReAct, RAG), context engineering para agentes, cobertura por modelo/família.</scope>

<key_points>
- Comece simples e adicione elementos ao prompt de forma iterativa, testando cada adição.
- Use um separador claro (ex. "###") entre instrução e contexto quando o prompt mistura os dois.
- Prefira instrução direta e específica a tentar ser "esperto" com frases vagas.
- Diga o que fazer, não o que não fazer.
</key_points>

<when_to_consult>Visão panorâmica de técnicas, comparação entre múltiplos modelos/famílias, aprendizado geral.</when_to_consult>

---

### [ID: claude-blog-2026] Best practices for prompt engineering (blog)

<meta>
<url>https://claude.com/blog/best-practices-for-prompt-engineering</url>
<type>official_blog</type>
<authority>primary</authority>
<maintained_by>Anthropic (Claude)</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Técnicas núcleo (clareza, contexto, especificidade, exemplos, permissão para incerteza), técnicas avançadas (prefill, CoT, chaining), nota sobre técnicas hoje menos necessárias.</scope>

<key_points>
- Dê permissão explícita para o modelo dizer "não sei" em vez de especular — reduz alucinação.
- Tags XML pesadas e role-prompting elaborado, populares até pouco tempo, hoje são menos necessários em modelos de ponta.
- Regra prática: não use todas as técnicas de uma vez — escolha a que resolve o problema específico.
- Inclui tabela de decisão (formato → técnica) e checklist de troubleshooting.
</key_points>

<when_to_consult>Introdução acessível + checklist de erros comuns a evitar.</when_to_consult>

---

### [ID: white-pattern-catalog] A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT

<meta>
<url>https://arxiv.org/abs/2302.11382</url>
<type>academic_paper</type>
<authority>primary</authority>
<maintained_by>White, Fu, Hays, Sandborn, Olea, Gilbert, Elnashar, Spencer-Smith, Schmidt (Vanderbilt)</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>16 padrões de prompt reutilizáveis organizados em 5 categorias: Input Semantics, Output Customization, Error Identification, Prompt Improvement, Interaction.</scope>

<key_points>
- Persona: peça ao modelo para assumir uma perspectiva específica.
- Flipped Interaction: peça ao modelo para fazer perguntas até atingir um objetivo.
- Question Refinement: peça ao modelo para sugerir uma versão melhor da sua pergunta.
- Cognitive Verifier: peça para subdividir a pergunta em subperguntas antes de responder.
- Outros padrões do catálogo: Fact Check List, Template, Recipe, Context Manager, Meta Language Creation, Alternative Approaches, Refusal Breaker, Reflection, Output Automater, Visualization Generator, Game Play, Infinite Generation.
</key_points>

<when_to_consult>Quando precisar de um catálogo formal de técnicas reutilizáveis, com nome e estrutura definida, para documentação interna.</when_to_consult>

---

### [ID: re-systematic-review] Prompt engineering guidelines mapeadas para Requirements Engineering

<meta>
<url>https://arxiv.org/abs/2507.03405</url>
<type>academic_paper</type>
<authority>primary</authority>
<maintained_by>Revisão sistemática (2025)</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Revisão sistemática de 28 estudos primários (de 271 triados); 36 guidelines organizadas em 9 temas (Context, Persona, Templates, Disambiguation, Reasoning, Analysis, Keywords, Wording, Few-shot), mapeadas para 5 fases de RE.</scope>

<key_points>
- Tema "Contexto" é o mais citado na literatura, seguido de "Reasoning", "Wording" e "Few-shot".
- Elicitação → contexto, templates, keywords. Análise → templates, self-consistency, reasoning. Especificação → persona, disambiguação. Validação → persona, templates. Gestão → keywords, reasoning.
- Especialistas entrevistados alertam: LLMs ainda têm baixa confiabilidade para validação de requisitos — usar com cautela nessa fase específica.
</key_points>

<when_to_consult>Mapear qual técnica de prompt priorizar conforme a fase/atividade da tarefa, não apenas o tipo de conteúdo.</when_to_consult>

---

### [ID: pdr-method] Preference-Driven Refinement of Prompts

<meta>
<url>https://www.semanticscholar.org/paper/Preference-Driven-Refinement-of-Prompts%3A-A-Prompt-Elnashar-White/7cb00a812e666506fbb6c7b98ffa4a78b48056d9</url>
<type>academic_paper</type>
<authority>primary</authority>
<maintained_by>Elnashar, White (Vanderbilt), Schmidt (William & Mary)</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Método PDR — loop iterativo em que preferências (convenções de nomenclatura, restrições, regras de segurança) são especificadas após cada geração e codificadas nos prompts seguintes.</scope>

<key_points>
- Reduz tentativa-e-erro ao custo de um tempo de refinamento levemente maior.
- Direcionado à automação de engenharia de software: testes unitários, patches de refatoração, documentação de API.
- Combina aprendizado em contexto com geração sintética de exemplos para refinar a qualidade do prompt sistematicamente.
</key_points>

<when_to_consult>Pipelines de geração de código/documentação que precisam respeitar padrões específicos de projeto de forma consistente ao longo do tempo.</when_to_consult>

---

### [ID: dspy] DSPy — Programming, not prompting, foundation models

<meta>
<url>https://dspy.ai</url>
<type>framework</type>
<authority>primary</authority>
<maintained_by>Stanford NLP</maintained_by>
<last_checked>2026-09-25</last_checked>
</meta>

<scope>Framework que trata prompts e exemplos few-shot como parâmetros otimizáveis programaticamente, em vez de texto escrito à mão. Otimizadores: MIPROv2, GEPA, COPRO.</scope>

<key_points>
- Substitui escrita manual de prompt por um "compilador" que busca automaticamente a formulação que maximiza uma métrica definida.
- Útil quando o mesmo prompt precisa funcionar em múltiplos modelos ou escalar para milhares de inputs.
- Fronteira mais avançada da área: tratar prompting como problema de busca/otimização, não de tentativa-e-erro manual.
</key_points>

<when_to_consult>Pipelines de produção com métrica de avaliação bem definida, que precisam de otimização sistemática de prompts em escala.</when_to_consult>

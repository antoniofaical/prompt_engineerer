# Fontes e decisões de curadoria

Revisão: 2026-09-25. O arquivo `guidelines-index-original.md` preserva o material
fornecido pelo usuário, sem atribuir verificação retroativa às suas afirmações.
`guidelines.json` é a base operacional carregada pela aplicação. As regras
`project-design` são decisões de produto, não resultados científicos.

| ID | Fonte | Tratamento |
|---|---|---|
| anthropic-best-practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | Consultada; exemplos e delimitação condicionais. |
| anthropic-overview | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview | Consultada; critérios e avaliação. |
| anthropic-context-engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Consultada; seleção do contexto. |
| openai-guide | https://developers.openai.com/api/docs/guides/prompt-engineering | Consultada; clareza e papéis. |
| openai-reasoning | https://developers.openai.com/api/docs/guides/reasoning-best-practices | Consultada; objetivos claros e instruções proporcionais. |
| claude-blog-2026 | https://claude.com/blog/best-practices-for-prompt-engineering | Consultada; incerteza, tratada como orientação, não garantia. |
| white-pattern-catalog | https://arxiv.org/html/2302.11382v1 | Texto consultado; padrões selecionados, sem importação indiscriminada. |
| re-systematic-review | https://arxiv.org/abs/2507.03405 | Resumo consultado; uso limitado a requisitos. Detalhes numéricos não foram incorporados. |
| dair-ai-guide | https://www.promptingguide.ai | Referência secundária preservada no original; não necessária às regras operacionais. |
| pdr-method | URL no índice original | Referência não verificada em fonte primária nesta implementação; alegações específicas excluídas do catálogo. |
| dspy | https://dspy.ai/learn/optimization/optimizers/ | A consulta retornou redirecionamentos sem o corpo da documentação; preservado como referência, sem regra operacional derivada. |
| project-design | README e system.md deste projeto | Decisões de engenharia para preservar intenção, capacidades e contrato de arquivos. |

## Correções em relação ao índice original

- “3–5 exemplos” não é uma exigência universal. Exemplos são opcionais e precisam
  ser adequados ao caso. O programa não preenche automaticamente uma cota.
- Instruções positivas ajudam a expressar o resultado, mas proibições explícitas
  do usuário continuam válidas e devem ser preservadas.
- Não há promessa universal de ganho de 30%, nem um número mínimo obrigatório de
  etapas. A ordenação de contexto depende da tarefa e do modelo.
- XML e personas são recursos opcionais. A revisão não usa a sua presença como
  indicador de qualidade.
- A revisão sobre engenharia de requisitos não justifica aplicar suas fases a
  todas as demandas.
- Um catálogo de padrões não é recomendação para aplicar todos os padrões. Técnicas
  de contornar recusas e geração infinita não foram incorporadas.
- Refinamento por revisão textual não equivale à otimização empírica com métricas
  do DSPy; este programa não afirma implementar PDR, DSPy, GEPA ou MIPROv2.
- Não se solicita cadeia de pensamento privada; pede-se justificativa, evidências
  e cálculos verificáveis quando úteis.

## Integração técnica

- Responses API e parsing por Pydantic:
  https://developers.openai.com/api/docs/guides/structured-outputs
- Modelo inicial com suporte documentado a saídas estruturadas:
  https://developers.openai.com/api/docs/models/gpt-5-mini

As páginas foram consultadas para projetar esta versão; disponibilidade para uma
conta só é comprovada por uma chamada real. Ao atualizar o catálogo, registre a
fonte e sua data, revise exceções e repita os casos de avaliação.

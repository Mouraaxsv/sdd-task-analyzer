# Fase 3 — Governança e Ética de IA

## Base contratual
O contrato SDD está em `specs/task_analyzer_spec.md` e as restrições de IA estão em `CONTEXT_RULES.md`. A Fase 3 automatiza a verificação de regressão, sem alterar as regras de negócio.

## Riscos, evidências e controles
| Risco | Controle | Evidência verificável |
| --- | --- | --- |
| Funcionalidade alucinada pela IA | Revisar diff contra SDD e CONTEXT_RULES | PR, comentário de revisão e contrato |
| Dependência não autorizada | Instalação somente de requirements.txt | Manifesto e log de instalação |
| Datas inconsistentes | TaskValidationError e testes de regressão | pytest no CI |
| Falha não reproduzível no computador local | Imagem Python 3.11 e Docker Compose | docker build, run e logs |
| Alegar aprovação sem execução | Exigir execução real e prints autênticos | Workflow verde e saída do terminal |
| Mudanças sem homologação | Revisão do PR antes de merge | Histórico de PR e commits |

## Critic-in-the-Loop
1. A IA propõe código guiado pelo contrato.
2. O desenvolvedor confere regras, assinatura e tipos.
3. O Test Harness avalia casos de sucesso, exceção e borda.
4. O PR reúne a alteração, os logs e o resultado do CI.
5. O humano aceita ou rejeita a contribuição e registra a decisão.

## Ética, segurança e sustentabilidade
- Não usar dados pessoais nas massas de teste.
- Não persistir dados, conforme o escopo do módulo.
- Usar Python 3.11-slim para reduzir o tamanho da imagem; isso não é prova de segurança por si só.
- Manter dependências, base de imagem e workflows atualizados.
- Evitar afirmar que 100% dos testes aprovados equivale a ausência de vulnerabilidades ou a 100% de cobertura.
- Não declarar execução de Docker ou CI antes de observar os resultados reais.

## Limitações e homologação
Os controles reduzirem riscos, mas não provam que um modelo de IA não alucina. Documentar qualquer intervenção corretiva real com prompt, resposta, decisão humana e diff. Um pipeline verde é evidência de execução dos testes configurados; não é uma auditoria exaustiva de segurança.

# CONTEXT_RULES - Governança de contexto (Fase 2)

Fonte: Especificação SDD TaskAnalyzer, Fase 1, seção 3 (10/09/2026),
com adendo aprovado **tecnicamente para a implementação da Fase 2**.
O enunciado da Fase 2 prevalece quando contradiz resultados esperados da Fase 1;
ver `specs/task_analyzer_spec.md`, seção "Rastreabilidade de diferenças".
A decisão de precedência deve ser confirmada pelo docente quando possível.

## Diretrizes arquiteturais obrigatórias

1. Usar Python 3.11 ou superior.
2. Aplicar type hints em todas as funções, parâmetros e retornos.
3. Seguir PEP 8 e manter até 88 caracteres por linha (na medida do possível).
4. Documentar módulos, classes e funções em estilo Google.
5. Criar funções pequenas e coesas, com responsabilidade única (SRP).
6. Usar `logging` da biblioteca padrão, sem dados sensíveis nos logs.
7. Tratar falhas com exceções específicas e mensagens claras.
8. Preservar código legível e passível de revisão humana.
9. Calcular datas como instantes UTC e resultados com duas casas decimais.

## Proibições explícitas

- Não usar dependências externas além das autorizadas (`pytest` apenas em testes).
- Não alterar a massa e os resultados dos cenários de aceite da Fase 1.
- Não desfigurar a estrutura especificada do repositório.
- Não armazenar tarefas em bancos ou arquivos.
- Não mudar a função pública `analyze_tasks` sem decisão de contrato documentada.
- Não inserir código novo sem teste correspondente.
- Não duplicar lógica nem adicionar funcionalidades supérfluas.
- Não inventar comportamentos não descritos; registrar escolhas em caso de lacuna.
- Não retornar indicadores contraditórios ao contrato atualizado em `specs/`.

## Interação e homologação da IA

1. Enviar este documento e a especificação SDD antes da geração de código.
2. Exigir que a IA identifique entradas, saídas, exceções e cenários antes de codificar.
3. Checar manualmente o retorno de cada cenário e dos casos de borda.
4. Rejeitar soluções não aderentes às regras e às proibições.
5. Executar `python -m pytest -v` antes de aceitar a implementação.
6. Registrar alterações em commits atômicos e submeter por Pull Request.

## Política de conflito Fase 1 versus Fase 2

A especificação v1.0 permanece como registro histórico.
Nesta Fase 2, os nomes e comportamentos obrigatórios mais recentes foram
acrescentados sem apagar a métrica original em minutos. Substituições:
`TaskValidationError`, cálculo adicional em horas e médias `0.0` para entrada
vazia/sem concluídas. Datas inválidas passam a reprovar a entrada completa.
Essas decisões constam explicitamente na especificação v1.1.
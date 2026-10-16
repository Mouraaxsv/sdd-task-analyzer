# TaskAnalyzer — Contrato SDD v1.1 (Fase 2)

**Autor:** João Carlos Melo Moura — Bootcamp III, Ciência da Computação  
**Origem:** especificação SDD v1.0, 10/09/2026. **Revisão:** 15/10/2026.

> Decisão técnica provisória: onde há conflito entre as fases, esta revisão adota
> os requisitos explícitos da entrega intermediária. Divergências devem ser
> confirmadas com o docente antes da homologação final.

## Objetivo e contrato

A função pública `analyze_tasks(tasks)` recebe uma lista de dicionários e
retorna métricas consolidadas de produtividade e indicadores por prioridade.
Não há persistência, interface gráfica ou serviços externos.

### Entradas

| Campo | Tipo | Regra |
|---|---|---|
| `id_tarefa` | int | positivo, exclusivo na lista |
| `data_criacao` | datetime | obrigatório, com timezone |
| `data_inicio` | datetime ou None | opcional |
| `data_conclusao` | datetime ou None | opcional |
| `prazo` | datetime | obrigatório, com timezone |
| `prioridade` | str | baixa, média, alta |
| `status` | str | concluída, pendente, cancelada |

Todas as datas informadas precisam ter fuso e são comparadas em UTC.
Tarefas concluídas devem apresentar `data_inicio` e `data_conclusao`.

### Saídas

O dicionário geral e cada um dos grupos de `indicadores_por_prioridade`
(baixa, média, alta) contêm:

- `total_tarefas` (int): todas as tarefas recebidas;
- `total_concluidas` (int): concluídas válidas;
- `total_pendentes` (int): tarefas com status pendente;
- `quantidade_tarefas` (int): concluídas computadas para médias;
- `tempo_medio_conclusao_min` (float): média em minutos;
- `tempo_medio_conclusao_horas` (float): média em horas;
- `taxa_atraso_percentual` (float): atraso sobre concluídas válidas.

A saída geral acrescenta `indicadores_por_prioridade` com os três grupos.

### Regras de negócio

1. Para tempo e atraso, considerar somente tarefas concluídas válidas.
2. Tempo = `data_conclusao - data_inicio`.
3. Atraso quando `data_conclusao > prazo` (igual ao prazo não atrasa).
4. Sem concluídas, médias e percentual retornam `0.0`.
5. Arredondar médias e percentuais a duas casas decimais.
6. Um lote com qualquer registro inválido gera `TaskValidationError`.
7. Verificar `data_inicio < data_criacao`, `data_conclusao < data_criacao`
   e `data_conclusao < data_inicio`.
8. Pendente entra em `total_tarefas` e `total_pendentes`; cancelada entra
   apenas em `total_tarefas`. Nenhuma integra médias de concluídas.

## Cenários de aceite (Dado–Quando–Então)

### Cenário 1: sucesso

**Dado** cinco tarefas, quatro concluídas e uma pendente, distribuídas entre
as três prioridades, **quando** analisadas, **então** o resultado deve refletir:

| ID | Prioridade | Status | Início | Conclusão | Prazo | Duração | Atraso |
|---|---|---|---|---|---|---|---|
| 1 | baixa | concluída | 10:00 | 11:00 | 12:00 | 60 min | não |
| 2 | baixa | concluída | 09:00 | 11:00 | 10:30 | 120 min | sim |
| 3 | média | concluída | 13:00 | 13:30 | 14:00 | 30 min | não |
| 4 | alta | concluída | 08:00 | 09:30 | 09:00 | 90 min | sim |
| 5 | alta | pendente | — | — | 17:00 | — | — |

**Consolidado:** `total_tarefas=5`, `total_concluidas=4`,
`total_pendentes=1`, `quantidade_tarefas=4`, média 75 minutos
(1,25 hora) e atraso de 50%.

**Baixa:** 90 min / 1,5 h; atraso 50%; duas concluídas.  
**Média:** 30 min / 0,5 h; atraso 0%; uma concluída.  
**Alta:** 90 min / 1,5 h; atraso 100%; uma concluída e uma pendente.

### Cenário 2: erro

**Dado** uma tarefa com data de conclusão anterior à criação ou ao início,
**quando** for analisada, **então** deve lançar `TaskValidationError`
com mensagem descritiva.

### Casos de borda

Lista vazia; somente pendentes; somente canceladas; conclusão exatamente no
prazo; fuso UTC; arredondamento; validação de IDs, enums e dados obrigatórios.

## Governança e Test Harness

Consultar `CONTEXT_RULES.md` para Python 3.11+, type hints, PEP 8,
Google Style, logging, SRP, bibliotecas autorizadas e proibições. A suíte
`tests/test_harness.py` deve cobrir ambos os cenários e casos de borda.

## Diferenças entre fases e resolução

| Fase 1, contrato original | Fase 2, aplicado |
|---|---|
| Métricas de duração em minutos | Mantém minutos e acrescenta horas |
| `InvalidTaskDataError` e `NoCompletedTasksError` planejadas | Padroniza `TaskValidationError` |
| Sem concluídas podia lançar exceção | Retorna `0.0` para evitar divisão por zero |
| Inconsistências poderiam ser ignoradas | Erro invalida lote; conclusão anterior à criação também |
| Contagem `quantidade_tarefas` | Acrescenta totais de tarefas/concluídas/pendentes |

A revisão altera somente comportamentos solicitados pela Fase 2.
A assinatura `analyze_tasks(tasks)` e a massa de referência foram mantidas.

## Homologação

Executar `python -m pytest -v`, inspecionar cobertura, documentar
conformidade do diff com o contrato e abrir Pull Request da feature para
`main`. A revisão humana independente é necessária antes da integração.

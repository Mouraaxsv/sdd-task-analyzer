# TaskAnalyzer - Bootcamp III | Fase 2

Analisador de tarefas Python 3.11+ criado a partir da especificação SDD da
Fase 1, com atualizações rastreáveis para atender à entrega intermediária.

## Funcionalidades

- Contagem geral e por prioridade de tarefas recebidas, concluídas e pendentes.
- Tempo médio de conclusão em **minutos e horas**.
- Percentual de tarefas concluídas após o prazo (geral e por prioridade).
- Validação de enums, IDs, dados obrigatórios, datas UTC e cronologia.
- Erros específicos (`TaskValidationError`) e retorno `0.0` em grupos vazios.

## Estrutura

```text
sdd-task-analyzer/
├── README.md
├── CONTEXT_RULES.md
├── .gitignore
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md
├── tests/
│   └── test_harness.py
└── src/
    └── task_analyzer.py
```

## Instalação e execução

Requer Python **3.11+**. Execute no diretório raiz:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

O aplicativo é um **módulo Python**, não uma aplicação web ou CLI.
Exemplo de uso com uma tarefa:

```python
from datetime import datetime, timezone
from src.task_analyzer import analyze_tasks

utc = timezone.utc
result = analyze_tasks([{
    "id_tarefa": 1,
    "data_criacao": datetime(2026, 9, 10, 7, tzinfo=utc),
    "data_inicio": datetime(2026, 9, 10, 8, tzinfo=utc),
    "data_conclusao": datetime(2026, 9, 10, 9, tzinfo=utc),
    "prazo": datetime(2026, 9, 10, 10, tzinfo=utc),
    "prioridade": "alta",
    "status": "concluída",
}])
print(result["tempo_medio_conclusao_horas"])  # 1.0
```

## Rastreabilidade SDD e decisões técnicas

Documentos normativos: [`CONTEXT_RULES.md`](CONTEXT_RULES.md) e
[`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md).

**Diferenças Fase 1 → Fase 2:** exceção padronizada para
`TaskValidationError`; retorno `0.0` sem concluídas; inclusão de horas e
contadores; datas anteriores à criação geram erro. A métrica original em
minutos foi mantida para preservar rastreabilidade. As contradições e
premissas estão documentadas na seção 5 da especificação v1.1.

**Processo de geração assistida por IA:** a especificação da Fase 1 serviu
como fonte de verdade; os requisitos da Fase 2 foram comparados; o código foi
gerado com as regras de governança; o harness foi criado com os cenários de
aceite e regressão; resultados foram conferidos com a massa de referência.

**Prompt de desenvolvimento resumido:** "Implemente somente o contrato SDD
v1.1 de TaskAnalyzer, respeite CONTEXT_RULES.md, gere código Python 3.11+ com
type hints, exceções específicas e pytest para os cenários 1 e 2 e bordas;
documente ambiguidades, não acrescente funcionalidades não previstas."

**Revisão humana necessária antes da homologação final:** validar com o
professor as ambiguidades originais e conferir resultados e diff do Pull
Request. A execução dos testes automatizados fornece evidência técnica, mas
não substitui uma revisão humana independente.

## Fluxo de contribuição

- `main`: documentação e versão estável.
- `feature/task-analyzer-impl`: implementação e suíte de testes.
- Commits atômicos e Pull Request com revisão da conformidade SDD.

## Estado

- Fase 1: especificação concluída.
- Fase 2: 27 testes aprovados (100% de cobertura de linhas) localmente;
  implementação apresentada em Pull Request para revisão.
- Fase 3: GitHub Actions e Docker (fora do escopo desta entrega).
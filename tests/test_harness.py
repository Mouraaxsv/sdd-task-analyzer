"""Test Harness SDD para cenários de aceite e casos de borda."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks

UTC = timezone.utc
DAY = datetime(2026, 9, 10, tzinfo=UTC)


def dt(hour: int, minute: int = 0) -> datetime:
    """Cria timestamp UTC para testes.

    Args:
        hour: Hora UTC.
        minute: Minuto UTC.

    Returns:
        Data e hora em UTC.
    """
    return DAY.replace(hour=hour, minute=minute)


def task(
    identity: int = 1,
    priority: str = "alta",
    status: str = "concluída",
    start: datetime | None = None,
    end: datetime | None = None,
    deadline: datetime | None = None,
) -> dict[str, object]:
    """Gera registro de teste válido por padrão.

    Args:
        identity: Identificador.
        priority: Prioridade.
        status: Situação.
        start: Início ou None para padrão.
        end: Conclusão ou None para padrão.
        deadline: Prazo ou None para padrão.

    Returns:
        Dicionário representando a tarefa.
    """
    return {
        "id_tarefa": identity,
        "prioridade": priority,
        "status": status,
        "data_criacao": dt(7),
        "data_inicio": dt(8) if start is None and status == "concluída" else start,
        "data_conclusao": dt(9) if end is None and status == "concluída" else end,
        "prazo": dt(10) if deadline is None else deadline,
    }


@pytest.fixture
def acceptance_tasks() -> list[dict[str, object]]:
    """Fornece a massa de referência definida na Fase 1."""
    return [
        task(1, "baixa", start=dt(10), end=dt(11), deadline=dt(12)),
        task(2, "baixa", start=dt(9), end=dt(11), deadline=dt(10, 30)),
        task(3, "média", start=dt(13), end=dt(13, 30), deadline=dt(14)),
        task(4, "alta", start=dt(8), end=dt(9, 30), deadline=dt(9)),
        task(5, "alta", status="pendente", deadline=dt(17)),
    ]


def test_cenario_1_totais(acceptance_tasks: list[dict[str, object]]) -> None:
    """Confere contadores globais."""
    result = analyze_tasks(acceptance_tasks)
    assert result["total_tarefas"] == 5
    assert result["total_concluidas"] == 4
    assert result["total_pendentes"] == 1
    assert result["quantidade_tarefas"] == 4


def test_cenario_1_medias(acceptance_tasks: list[dict[str, object]]) -> None:
    """Confere tempo em minutos e horas."""
    result = analyze_tasks(acceptance_tasks)
    assert result["tempo_medio_conclusao_min"] == 75.0
    assert result["tempo_medio_conclusao_horas"] == 1.25


def test_cenario_1_atraso(acceptance_tasks: list[dict[str, object]]) -> None:
    """Confere taxa geral de atraso."""
    assert analyze_tasks(acceptance_tasks)["taxa_atraso_percentual"] == 50.0


@pytest.mark.parametrize(
    ("priority", "total", "concluded", "pending", "minutes", "hours", "late"),
    [
        ("baixa", 2, 2, 0, 90.0, 1.5, 50.0),
        ("média", 1, 1, 0, 30.0, 0.5, 0.0),
        ("alta", 2, 1, 1, 90.0, 1.5, 100.0),
    ],
)
def test_cenario_1_por_prioridade(
    acceptance_tasks: list[dict[str, object]],
    priority: str, total: int, concluded: int, pending: int,
    minutes: float, hours: float, late: float,
) -> None:
    """Confere os indicadores das três prioridades."""
    item = analyze_tasks(acceptance_tasks)["indicadores_por_prioridade"][priority]
    assert item["total_tarefas"] == total
    assert item["total_concluidas"] == concluded
    assert item["total_pendentes"] == pending
    assert item["quantidade_tarefas"] == concluded
    assert item["tempo_medio_conclusao_min"] == minutes
    assert item["tempo_medio_conclusao_horas"] == hours
    assert item["taxa_atraso_percentual"] == late


def test_cenario_2_conclusao_antes_da_criacao() -> None:
    """Valida erro com conclusão anterior à criação."""
    item = task(end=dt(6))
    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([item])


def test_cenario_2_conclusao_antes_do_inicio() -> None:
    """Valida erro de cronologia de execução."""
    item = task(start=dt(10), end=dt(9))
    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([item])


def test_inicio_antes_da_criacao() -> None:
    """Valida cronologia entre início e criação."""
    with pytest.raises(TaskValidationError, match="data_inicio"):
        analyze_tasks([task(start=dt(6))])


def test_lista_vazia() -> None:
    """Lista vazia retorna zeros para as métricas."""
    result = analyze_tasks([])
    assert result["total_tarefas"] == 0
    assert result["tempo_medio_conclusao_horas"] == 0.0
    assert result["tempo_medio_conclusao_min"] == 0.0
    assert result["taxa_atraso_percentual"] == 0.0
    assert all(
        value["tempo_medio_conclusao_horas"] == 0.0
        for value in result["indicadores_por_prioridade"].values()
    )


def test_apenas_pendentes() -> None:
    """Não deve dividir por zero quando não há conclusão."""
    result = analyze_tasks([task(status="pendente")])
    assert result["total_pendentes"] == 1
    assert result["total_concluidas"] == 0
    assert result["tempo_medio_conclusao_horas"] == 0.0


def test_canceladas_nao_compoem_metricas() -> None:
    """Canceladas são contadas somente no total recebido."""
    result = analyze_tasks([task(status="cancelada")])
    assert result["total_tarefas"] == 1
    assert result["total_pendentes"] == 0
    assert result["total_concluidas"] == 0
    assert result["taxa_atraso_percentual"] == 0.0


def test_exatamente_no_prazo() -> None:
    """Conclusão no prazo não configura atraso."""
    assert analyze_tasks([task(end=dt(10))])["taxa_atraso_percentual"] == 0.0


def test_fuso_diferente_normalizado() -> None:
    """Instantes iguais com fusos diferentes são equivalentes."""
    offset = timezone(timedelta(hours=-3))
    item = task()
    item["data_inicio"] = dt(8).astimezone(offset)
    item["data_conclusao"] = dt(9).astimezone(offset)
    result = analyze_tasks([item])
    assert result["tempo_medio_conclusao_horas"] == 1.0


def test_arredondamento() -> None:
    """Médias não inteiras são arredondadas a duas casas."""
    result = analyze_tasks([task(end=dt(9, 1))])
    assert result["tempo_medio_conclusao_horas"] == 1.02
    assert result["tempo_medio_conclusao_min"] == 61.0


@pytest.mark.parametrize("invalid", [0, -1, True, "1", 1.0])
def test_id_invalido(invalid: object) -> None:
    """Rejeita IDs incorretos."""
    item = task()
    item["id_tarefa"] = invalid
    with pytest.raises(TaskValidationError, match="id_tarefa"):
        analyze_tasks([item])


def test_id_duplicado() -> None:
    """IDs devem ser exclusivos na entrada."""
    with pytest.raises(TaskValidationError, match="duplicado"):
        analyze_tasks([task(), task()])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prioridade", "urgente"),
        ("status", "finalizada"),
        ("data_criacao", "ontem"),
        ("prazo", dt(10).replace(tzinfo=None)),
    ],
)
def test_campos_invalidos(field: str, value: object) -> None:
    """Valida enum e timestamps obrigatórios."""
    item = task()
    item[field] = value
    with pytest.raises(TaskValidationError):
        analyze_tasks([item])


def test_tarefa_sem_campo_obrigatorio() -> None:
    """Ausência de dado obrigatório gera mensagem específica."""
    item = task()
    del item["prazo"]
    with pytest.raises(TaskValidationError, match="prazo"):
        analyze_tasks([item])


def test_registro_nao_dicionario() -> None:
    """Rejeita entradas heterogêneas."""
    with pytest.raises(TaskValidationError, match="dicionário"):
        analyze_tasks(["tarefa"])


def test_entrada_nao_lista() -> None:
    """Rejeita entrada fora da interface."""
    with pytest.raises(TaskValidationError, match="lista"):
        analyze_tasks(None)


def test_concluida_sem_inicio() -> None:
    """Concluída precisa possuir início."""
    item = task()
    item["data_inicio"] = None
    with pytest.raises(TaskValidationError, match="requer"):
        analyze_tasks([item])


def test_concluida_sem_conclusao() -> None:
    """Concluída precisa possuir data de conclusão."""
    item = task()
    item["data_conclusao"] = None
    with pytest.raises(TaskValidationError, match="requer"):
        analyze_tasks([item])


def test_data_opcional_invalida() -> None:
    """Quando informadas, datas opcionais precisam ser válidas."""
    item = task()
    item["data_inicio"] = "08:00"
    with pytest.raises(TaskValidationError, match="data_inicio"):
        analyze_tasks([item])

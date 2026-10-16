"""Análise de produtividade conforme o contrato SDD v1.1."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal, TypedDict

LOGGER = logging.getLogger(__name__)

Priority = Literal["baixa", "média", "alta"]
Status = Literal["concluída", "pendente", "cancelada"]
PRIORITIES: tuple[Priority, ...] = ("baixa", "média", "alta")
STATUSES: tuple[Status, ...] = ("concluída", "pendente", "cancelada")


class TaskValidationError(ValueError):
    """Erro de validação de registro de tarefa."""


class TaskRecord(TypedDict):
    """Entrada esperada para uma tarefa."""

    id_tarefa: int
    data_criacao: datetime
    data_inicio: datetime | None
    data_conclusao: datetime | None
    prazo: datetime
    prioridade: Priority
    status: Status


class PriorityIndicators(TypedDict):
    """Métricas consolidadas para um conjunto de tarefas."""

    quantidade_tarefas: int
    total_tarefas: int
    total_concluidas: int
    total_pendentes: int
    tempo_medio_conclusao_min: float
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float


class AnalysisResult(PriorityIndicators):
    """Retorno da análise com agregação por prioridade."""

    indicadores_por_prioridade: dict[Priority, PriorityIndicators]


def _as_utc(value: object, field: str, task_id: int) -> datetime:
    """Converte um datetime com fuso para UTC.

    Args:
        value: Timestamp recebido.
        field: Nome do campo.
        task_id: Identificador para a mensagem de erro.

    Returns:
        Timestamp normalizado para UTC.

    Raises:
        TaskValidationError: Se não houver datetime com fuso.
    """
    if not isinstance(value, datetime):
        raise TaskValidationError(
            f"Tarefa {task_id}: {field} deve ser datetime com fuso horário."
        )
    if value.tzinfo is None or value.utcoffset() is None:
        raise TaskValidationError(
            f"Tarefa {task_id}: {field} precisa informar fuso horário."
        )
    return value.astimezone(timezone.utc)


def _optional_utc(value: object, field: str, task_id: int) -> datetime | None:
    """Normaliza uma data opcional para UTC.

    Args:
        value: Timestamp ou None.
        field: Campo.
        task_id: Identificador da tarefa.

    Returns:
        Timestamp UTC ou None.
    """
    return None if value is None else _as_utc(value, field, task_id)


def _validate_task(task: object, used_ids: set[int]) -> TaskRecord:
    """Valida campos, enumeradores e cronologia de uma tarefa.

    Args:
        task: Registro a validar.
        used_ids: Identificadores vistos no lote.

    Returns:
        Registro com timestamps normalizados para UTC.

    Raises:
        TaskValidationError: Quando o registro viola o contrato.
    """
    if not isinstance(task, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário.")
    required = ("id_tarefa", "data_criacao", "prazo", "prioridade", "status")
    missing = [key for key in required if key not in task]
    if missing:
        raise TaskValidationError(
            f"Tarefa sem campo(s) obrigatório(s): {', '.join(missing)}."
        )
    task_id = task["id_tarefa"]
    if type(task_id) is not int or task_id <= 0:
        raise TaskValidationError("id_tarefa deve ser inteiro maior que zero.")
    if task_id in used_ids:
        raise TaskValidationError(f"ID de tarefa duplicado: {task_id}.")
    priority = task["prioridade"]
    status = task["status"]
    if priority not in PRIORITIES:
        raise TaskValidationError(
            f"Tarefa {task_id}: prioridade inválida: {priority!r}."
        )
    if status not in STATUSES:
        raise TaskValidationError(
            f"Tarefa {task_id}: status inválido: {status!r}."
        )
    created = _as_utc(task["data_criacao"], "data_criacao", task_id)
    deadline = _as_utc(task["prazo"], "prazo", task_id)
    started = _optional_utc(task.get("data_inicio"), "data_inicio", task_id)
    completed = _optional_utc(
        task.get("data_conclusao"), "data_conclusao", task_id
    )
    if started is not None and started < created:
        raise TaskValidationError(
            f"Tarefa {task_id}: data_inicio anterior a data_criacao."
        )
    if completed is not None and completed < created:
        raise TaskValidationError(
            f"Tarefa {task_id}: data_conclusao anterior a data_criacao."
        )
    if started is not None and completed is not None and completed < started:
        raise TaskValidationError(
            f"Tarefa {task_id}: data_conclusao anterior a data_inicio."
        )
    if status == "concluída" and (started is None or completed is None):
        raise TaskValidationError(
            f"Tarefa {task_id}: concluída requer início e conclusão."
        )
    used_ids.add(task_id)
    return {
        "id_tarefa": task_id,
        "data_criacao": created,
        "data_inicio": started,
        "data_conclusao": completed,
        "prazo": deadline,
        "prioridade": priority,
        "status": status,
    }


def _calculate_indicators(tasks: list[TaskRecord]) -> PriorityIndicators:
    """Calcula indicadores para um subconjunto validado.

    Args:
        tasks: Tarefas de um subconjunto (geral ou prioridade).

    Returns:
        Contadores e médias com duas casas decimais.
    """
    concluded = [task for task in tasks if task["status"] == "concluída"]
    n = len(concluded)
    pending = sum(task["status"] == "pendente" for task in tasks)
    total_seconds = sum(
        (task["data_conclusao"] - task["data_inicio"]).total_seconds()
        for task in concluded
        if task["data_inicio"] is not None
        and task["data_conclusao"] is not None
    )
    late = sum(
        task["data_conclusao"] > task["prazo"]
        for task in concluded
        if task["data_conclusao"] is not None
    )
    avg_min = total_seconds / 60 / n if n else 0.0
    avg_hours = total_seconds / 3600 / n if n else 0.0
    late_rate = 100 * late / n if n else 0.0
    return {
        "quantidade_tarefas": n,
        "total_tarefas": len(tasks),
        "total_concluidas": n,
        "total_pendentes": pending,
        "tempo_medio_conclusao_min": round(avg_min, 2),
        "tempo_medio_conclusao_horas": round(avg_hours, 2),
        "taxa_atraso_percentual": round(late_rate, 2),
    }


def analyze_tasks(tasks: list[TaskRecord]) -> AnalysisResult:
    """Analisa tarefas e devolve métricas agregadas conforme SDD.

    Args:
        tasks: Lista de tarefas com datas conscientes do fuso.

    Returns:
        Métricas gerais e indicadores por prioridade.

    Raises:
        TaskValidationError: Se a entrada ou qualquer tarefa for inválida.
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")
    used_ids: set[int] = set()
    normalized = [_validate_task(task, used_ids) for task in tasks]
    overall = _calculate_indicators(normalized)
    by_priority = {
        priority: _calculate_indicators(
            [task for task in normalized if task["prioridade"] == priority]
        )
        for priority in PRIORITIES
    }
    LOGGER.info(
        "task_analysis_completed total=%d concluded=%d pending=%d",
        overall["total_tarefas"],
        overall["total_concluidas"],
        overall["total_pendentes"],
    )
    return {**overall, "indicadores_por_prioridade": by_priority}

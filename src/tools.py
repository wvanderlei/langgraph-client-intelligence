import os
import pandas as pd
from google.cloud import bigquery
from langchain_core.tools import tool


def _get_client() -> bigquery.Client:
    return bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))


_PROJECT = lambda: os.getenv("GCP_PROJECT_ID")
_DATASET = "datalyx_analytics"


@tool
def buscar_contratos(cliente: str = None) -> str:
    """Busca dados de contratos dos clientes Datalyx no BigQuery.
    Retorna modelo (Radar/Forja/Nexus), tipo, valor mensal, horas do pacote e status.

    Args:
        cliente: nome do cliente específico. Se não informado, retorna todos.
    """
    query = f"SELECT * FROM `{_PROJECT()}.{_DATASET}.contratos`"
    if cliente:
        query += f" WHERE LOWER(cliente) = LOWER('{cliente}')"
    query += " ORDER BY valor_mensal DESC"

    df = _get_client().query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


@tool
def buscar_tickets(cliente: str = None, categoria: str = None, limit: int = 100) -> str:
    """Busca tickets de suporte dos clientes Datalyx no BigQuery.
    Categorias possíveis: incidente, duvida, manutencao, fora_de_escopo.
    Prioridades possíveis: alta, media, baixa.

    Args:
        cliente: nome do cliente específico (opcional).
        categoria: filtrar por categoria do ticket (opcional).
        limit: máximo de registros retornados (padrão 100).
    """
    conditions = []
    if cliente:
        conditions.append(f"LOWER(cliente) = LOWER('{cliente}')")
    if categoria:
        conditions.append(f"categoria = '{categoria}'")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT * FROM `{_PROJECT()}.{_DATASET}.tickets`
        {where}
        ORDER BY data_abertura DESC
        LIMIT {limit}
    """

    df = _get_client().query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


@tool
def buscar_sla(cliente: str = None) -> str:
    """Busca métricas de SLA dos clientes Datalyx no BigQuery.
    Retorna tempo de resposta, se foi resolvido e data de resolução por ticket.

    Args:
        cliente: nome do cliente específico. Se não informado, retorna todos.
    """
    query = f"SELECT * FROM `{_PROJECT()}.{_DATASET}.sla_metricas`"
    if cliente:
        query += f" WHERE LOWER(cliente) = LOWER('{cliente}')"
    query += " ORDER BY tempo_resposta_horas DESC"

    df = _get_client().query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


QUERY_TOOLS = [buscar_contratos, buscar_tickets, buscar_sla]

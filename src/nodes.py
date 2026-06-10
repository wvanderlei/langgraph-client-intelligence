import os
import re
import time
import json
import google.generativeai as genai
from google.cloud import bigquery
from langchain_core.messages import AIMessage

from .state import AgentState
from .prompts import SUPERVISOR_SYSTEM, QUERY_SYSTEM, ANALYSIS_SYSTEM, WRITER_SYSTEM

MODEL = "gemini-2.5-flash"
_PROJECT = lambda: os.getenv("GCP_PROJECT_ID")
_DATASET = "datalyx_analytics"


def buscar_contratos(cliente: str = None) -> str:
    """Busca dados de contratos dos clientes Datalyx (modelo Radar/Forja/Nexus, valor, horas, status).

    Args:
        cliente: nome do cliente específico. Se não informado, retorna todos.
    """
    bq = bigquery.Client(project=_PROJECT())
    query = f"SELECT * FROM `{_PROJECT()}.{_DATASET}.contratos`"
    if cliente:
        query += f" WHERE LOWER(cliente) = LOWER('{cliente}')"
    df = bq.query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


def buscar_tickets(cliente: str = None, categoria: str = None) -> str:
    """Busca tickets de suporte dos clientes Datalyx (incidente, duvida, manutencao, fora_de_escopo).

    Args:
        cliente: nome do cliente específico (opcional).
        categoria: filtrar por categoria do ticket (opcional).
    """
    bq = bigquery.Client(project=_PROJECT())
    conditions = []
    if cliente:
        conditions.append(f"LOWER(cliente) = LOWER('{cliente}')")
    if categoria:
        conditions.append(f"categoria = '{categoria}'")
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM `{_PROJECT()}.{_DATASET}.tickets` {where} LIMIT 100"
    df = bq.query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


def buscar_sla(cliente: str = None) -> str:
    """Busca métricas de SLA dos clientes Datalyx (tempo de resposta, resolução).

    Args:
        cliente: nome do cliente específico. Se não informado, retorna todos.
    """
    bq = bigquery.Client(project=_PROJECT())
    query = f"SELECT * FROM `{_PROJECT()}.{_DATASET}.sla_metricas`"
    if cliente:
        query += f" WHERE LOWER(cliente) = LOWER('{cliente}')"
    df = bq.query(query).to_dataframe()
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


def _configure():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _call_with_retry(fn, *args, **kwargs):
    while True:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                match = re.search(r"retry in (\d+\.?\d*)s", str(e))
                wait = float(match.group(1)) + 2 if match else 65
                time.sleep(wait)
            else:
                raise


def _simple_call(system_prompt: str, user_prompt: str) -> str:
    _configure()
    model = genai.GenerativeModel(MODEL, system_instruction=system_prompt)
    response = _call_with_retry(model.generate_content, user_prompt)
    return response.text.strip()


def supervisor_node(state: AgentState) -> dict:
    context = "\n".join([
        f"Pergunta do usuário: {state['messages'][-1].content if state['messages'] else 'N/A'}",
        f"raw_data disponível: {'Sim' if state.get('raw_data') else 'Não'}",
        f"analysis disponível: {'Sim' if state.get('analysis') else 'Não'}",
        f"response disponível: {'Sim' if state.get('response') else 'Não'}",
    ])

    result = _simple_call(SUPERVISOR_SYSTEM, f"{context}\n\nQual o próximo agente?")
    next_agent = result.lower()
    valid = {"query_agent", "analysis_agent", "writer_agent", "end"}
    if next_agent not in valid:
        next_agent = "end"

    return {"next": "END" if next_agent == "end" else next_agent}


def query_node(state: AgentState) -> dict:
    _configure()
    user_question = state["messages"][-1].content if state["messages"] else ""

    model = genai.GenerativeModel(
        MODEL,
        system_instruction=QUERY_SYSTEM,
        tools=[buscar_contratos, buscar_tickets, buscar_sla],
    )
    chat = model.start_chat(enable_automatic_function_calling=True)

    raw_data = {"results": [], "summary": ""}
    response = _call_with_retry(chat.send_message, user_question)
    raw_data["summary"] = response.text if response.text else ""

    for content in chat.history:
        for part in content.parts:
            if hasattr(part, "function_response") and part.function_response:
                raw_data["results"].append(str(part.function_response.response))

    return {
        "raw_data": raw_data,
        "messages": [AIMessage(content="[Query Agent] Dados coletados do BigQuery.")],
    }


def analysis_node(state: AgentState) -> dict:
    user_question = state["messages"][0].content if state["messages"] else ""
    raw_data_str = json.dumps(state.get("raw_data", {}), ensure_ascii=False, indent=2)

    result = _simple_call(
        ANALYSIS_SYSTEM,
        f"Pergunta original: {user_question}\n\nDados brutos:\n{raw_data_str}",
    )

    return {
        "analysis": result,
        "messages": [AIMessage(content="[Analysis Agent] Análise concluída.")],
    }


def writer_node(state: AgentState) -> dict:
    user_question = state["messages"][0].content if state["messages"] else ""
    analysis = state.get("analysis", "")

    result = _simple_call(
        WRITER_SYSTEM,
        f"Pergunta original: {user_question}\n\nAnálise:\n{analysis}",
    )

    return {
        "response": result,
        "messages": [AIMessage(content=result)],
    }

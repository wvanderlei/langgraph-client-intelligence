from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    raw_data: Optional[dict]    # dados brutos retornados pelo Query Agent
    analysis: Optional[str]     # análise estruturada do Analysis Agent
    response: Optional[str]     # resposta final gerada pelo Writer Agent
    next: str                   # próximo agente a ser chamado pelo Supervisor

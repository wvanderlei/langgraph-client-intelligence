import uuid
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agent import build_graph

load_dotenv()

st.set_page_config(
    page_title="Datalyx Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* ── Fundo geral ── */
.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {
    background-color: #080f1c !important;
}

/* ── Header/toolbar do Streamlit ── */
header[data-testid="stHeader"] {
    background-color: #080f1c !important;
    border-bottom: 1px solid #1a3048 !important;
}
header[data-testid="stHeader"] * { color: #2a4a62 !important; }

/* ── Toolbar buttons ── */
[data-testid="stToolbar"] { background: #080f1c !important; }

/* ── Esconder botão collapse da sidebar (keyboard_double) ── */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[title="Collapse sidebar"],
button[title="Recolher barra lateral"],
button[kind="header"] {
    display: none !important;
}

/* ── Área do chat input (barra branca do rodapé) ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background-color: #080f1c !important;
    border-top: 1px solid #1a3048 !important;
}

/* ── Chat input em si ── */
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] textarea {
    background-color: #0d1828 !important;
    border-color: #1e3a58 !important;
    color: #c8e0f0 !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #2a4a62 !important; }
[data-testid="stChatInputSubmitButton"] svg { fill: #00c3e3 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #0a1220 !important;
    border-right: 1px solid #1a3048 !important;
}

/* ── Botões da sidebar ── */
.stButton > button {
    width: 100% !important;
    background: transparent !important;
    color: #3a6a82 !important;
    border: 1px solid #1a3048 !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    text-align: left !important;
    padding: 9px 13px !important;
    transition: all 0.15s !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.5 !important;
}
.stButton > button:hover {
    background: rgba(0,195,227,0.07) !important;
    border-color: rgba(0,195,227,0.4) !important;
    color: #00c3e3 !important;
}

/* ── Mensagens do chat ── */
[data-testid="stChatMessage"],
[data-testid="stChatMessage"] > div {
    background: transparent !important;
    border: none !important;
}

/* ── Block container ── */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 860px !important;
}

/* ── Divisor ── */
hr {
    border: none !important;
    border-top: 1px solid #1a3048 !important;
    margin: 12px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080f1c; }
::-webkit-scrollbar-thumb { background: #1a3048; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "exchange_count" not in st.session_state:
    st.session_state.exchange_count = 0

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 6px 12px;">
        <div style="font-size:1.9rem;font-weight:700;line-height:1;">
            <span style="color:#00c3e3;">D</span><span style="color:#e8f4fc;">atalyx</span>
        </div>
        <div style="font-size:0.68rem;color:#2a4a62;text-transform:uppercase;
                    letter-spacing:0.14em;margin-top:5px;">
            Client Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:#0d1828;border:1px solid #1a3048;border-radius:8px;
                    padding:12px 8px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:700;color:#00c3e3;line-height:1.1;">
                {st.session_state.exchange_count}
            </div>
            <div style="font-size:0.63rem;color:#2a4a62;text-transform:uppercase;
                        letter-spacing:.08em;margin-top:4px;">Perguntas</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#0d1828;border:1px solid #1a3048;border-radius:8px;
                    padding:12px 8px;text-align:center;">
            <div style="font-size:1.6rem;font-weight:700;color:#00d4a0;line-height:1.1;">4</div>
            <div style="font-size:0.63rem;color:#2a4a62;text-transform:uppercase;
                        letter-spacing:.08em;margin-top:4px;">Agentes</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="font-size:0.75rem;line-height:2.4;padding:0 4px;">
        <div><span style="color:#1a3048;">⬡</span>&nbsp; <span style="color:#3a6a82;">LangGraph</span></div>
        <div><span style="color:#1a3048;">◈</span>&nbsp; <span style="color:#3a6a82;">Gemini 2.5 Flash</span></div>
        <div><span style="color:#1a3048;">▦</span>&nbsp; <span style="color:#3a6a82;">BigQuery · datalyx_analytics</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""<div style="font-size:0.68rem;color:#2a4a62;text-transform:uppercase;
                               letter-spacing:.1em;margin-bottom:8px;">Exemplos</div>""",
                unsafe_allow_html=True)

    examples = [
        "Quais clientes estão em situação crítica?",
        "Qual cliente tem maior risco de churn?",
        "Me dê um resumo da carteira",
        "Como está o SLA dos clientes Nexus?",
        "Quais clientes têm oportunidade de upsell?",
        "Me fala tudo sobre o MediFlow",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()

    if st.button("↺  Nova conversa", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.exchange_count = 0
        st.rerun()

    st.markdown(
        f'<div style="font-size:0.62rem;color:#1a3048;margin-top:10px;padding:0 4px;">'
        f'sessão · {st.session_state.thread_id[:8]}</div>',
        unsafe_allow_html=True
    )

# ── HEADER ─────────────────────────────────────────────────────────
st.markdown("""
<div style="border-bottom:1px solid #1a3048;padding-top:28px;padding-bottom:16px;margin-bottom:20px;">
    <div style="margin-bottom:6px;">
        <span style="font-size:2rem;font-weight:700;color:#00c3e3;letter-spacing:-1px;">D</span><span style="font-size:1.5rem;font-weight:600;color:#e8f4fc;letter-spacing:-.3px;">atalyx</span>
        <span style="font-size:1.2rem;font-weight:300;color:#1e3a58;margin:0 10px;">/</span>
        <span style="font-size:1rem;font-weight:500;color:#6a8fa8;">Client Intelligence</span>
        <span style="display:inline-block;margin-left:10px;background:rgba(0,195,227,0.08);
                     color:#00c3e3;border:1px solid rgba(0,195,227,0.22);border-radius:4px;
                     padding:2px 10px;font-size:0.68rem;font-weight:600;letter-spacing:.1em;
                     vertical-align:middle;">MULTI-AGENT</span>
    </div>
    <div style="font-size:0.8rem;color:#2a4a62;">
        Análise de carteira em tempo real &nbsp;·&nbsp; LangGraph + Gemini + BigQuery
    </div>
</div>
""", unsafe_allow_html=True)

# ── PIPELINE STRIP ─────────────────────────────────────────────────
st.markdown("""
<div style="background:#0d1828;border:1px solid #1a3048;border-radius:8px;
            padding:14px 18px 16px;margin-bottom:26px;">
    <div style="font-size:0.63rem;color:#2a4a62;text-transform:uppercase;
                letter-spacing:.12em;margin-bottom:14px;">Pipeline de execução</div>
    <table style="width:100%;border-collapse:collapse;table-layout:fixed;">
        <tr>
            <td style="text-align:center;padding:0 4px;">
                <div style="font-size:1.5rem;margin-bottom:5px;">🎯</div>
                <div style="font-size:0.73rem;color:#6a8fa8;font-weight:500;white-space:nowrap;">Supervisor</div>
            </td>
            <td style="text-align:center;color:#1e3a58;font-size:1.1rem;width:32px;">→</td>
            <td style="text-align:center;padding:0 4px;">
                <div style="font-size:1.5rem;margin-bottom:5px;">🔍</div>
                <div style="font-size:0.73rem;color:#6a8fa8;font-weight:500;white-space:nowrap;">Query Agent</div>
            </td>
            <td style="text-align:center;color:#1e3a58;font-size:1.1rem;width:32px;">→</td>
            <td style="text-align:center;padding:0 4px;">
                <div style="font-size:1.5rem;margin-bottom:5px;">🧠</div>
                <div style="font-size:0.73rem;color:#6a8fa8;font-weight:500;white-space:nowrap;">Analysis Agent</div>
            </td>
            <td style="text-align:center;color:#1e3a58;font-size:1.1rem;width:32px;">→</td>
            <td style="text-align:center;padding:0 4px;">
                <div style="font-size:1.5rem;margin-bottom:5px;">✍️</div>
                <div style="font-size:0.73rem;color:#6a8fa8;font-weight:500;white-space:nowrap;">Writer Agent</div>
            </td>
            <td style="text-align:center;color:#1e3a58;font-size:0.8rem;width:24px;">·</td>
            <td style="text-align:center;padding:0 4px;">
                <div style="font-size:1.5rem;margin-bottom:5px;">💾</div>
                <div style="font-size:0.73rem;color:#3a3a6a;font-weight:500;white-space:nowrap;">MemorySaver</div>
            </td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

# ── CHAT HISTORY ───────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(
                f'<div style="background:#0d1828;border:1px solid #1e3a58;'
                f'border-radius:8px;padding:14px 18px;color:#c8e0f0;font-size:0.91rem;'
                f'line-height:1.6;">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background:#0d1828;border:1px solid #1e3a58;'
                f'border-left:3px solid #00c3e3;border-radius:0 8px 8px 0;'
                f'padding:18px 22px;color:#c8e0f0;font-size:0.91rem;line-height:1.8;">'
                f'{msg["content"]}</div>',
                unsafe_allow_html=True
            )

# ── CHAT INPUT ─────────────────────────────────────────────────────
question = st.chat_input("Pergunte sobre clientes, contratos ou SLA...")

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(
            f'<div style="background:#0d1828;border:1px solid #1e3a58;'
            f'border-radius:8px;padding:14px 18px;color:#c8e0f0;font-size:0.91rem;'
            f'line-height:1.6;">{question}</div>',
            unsafe_allow_html=True
        )

    with st.chat_message("assistant"):

        agent_meta = {
            "supervisor":     ("🎯", "Supervisor"),
            "query_agent":    ("🔍", "Query Agent"),
            "analysis_agent": ("🧠", "Analysis Agent"),
            "writer_agent":   ("✍️", "Writer Agent"),
        }
        completed: list = []
        live = st.empty()

        def render_pipeline(active=None):
            rows = ""
            for key, (icon, label) in agent_meta.items():
                if key in completed:
                    rows += (
                        f'<div style="background:rgba(0,212,160,0.05);'
                        f'border:1px solid rgba(0,212,160,0.2);'
                        f'border-left:3px solid #00d4a0;'
                        f'border-radius:0 7px 7px 0;'
                        f'padding:11px 18px;margin:5px 0;">'
                        f'<span style="font-size:1.1rem;">{icon}</span>'
                        f'<span style="font-size:0.85rem;color:#00d4a0;margin-left:10px;'
                        f'font-weight:500;">{label}</span>'
                        f'<span style="float:right;font-size:0.75rem;color:#007a60;'
                        f'margin-top:1px;">✓ concluído</span>'
                        f'</div>'
                    )
                elif key == active:
                    rows += (
                        f'<div style="background:rgba(0,195,227,0.07);'
                        f'border:1px solid rgba(0,195,227,0.3);'
                        f'border-left:3px solid #00c3e3;'
                        f'border-radius:0 7px 7px 0;'
                        f'padding:11px 18px;margin:5px 0;">'
                        f'<span style="font-size:1.1rem;">{icon}</span>'
                        f'<span style="font-size:0.85rem;color:#00c3e3;margin-left:10px;'
                        f'font-weight:500;">{label}</span>'
                        f'<span style="float:right;font-size:0.75rem;color:#007a9a;'
                        f'margin-top:1px;">trabalhando…</span>'
                        f'</div>'
                    )
                else:
                    rows += (
                        f'<div style="background:#0d1828;'
                        f'border:1px solid #1a3048;'
                        f'border-left:3px solid #1a3048;'
                        f'border-radius:0 7px 7px 0;'
                        f'padding:11px 18px;margin:5px 0;">'
                        f'<span style="font-size:1.1rem;opacity:0.35;">{icon}</span>'
                        f'<span style="font-size:0.85rem;color:#2a4a62;margin-left:10px;">{label}</span>'
                        f'</div>'
                    )
            live.markdown(
                f'<div style="margin:8px 0 16px;">{rows}</div>',
                unsafe_allow_html=True
            )

        render_pipeline()

        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        for chunk in st.session_state.graph.stream(
            {
                "messages": [HumanMessage(content=question)],
                "raw_data": None,
                "analysis": None,
                "response": None,
                "next": "",
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name in chunk.keys():
                if node_name in agent_meta:
                    render_pipeline(active=node_name)
                    completed.append(node_name)
                    render_pipeline()

        live.empty()

        graph_state = st.session_state.graph.get_state(config)
        response = graph_state.values.get("response") or "Não foi possível gerar uma resposta."

        st.markdown(
            f'<div style="background:#0d1828;border:1px solid #1e3a58;'
            f'border-left:3px solid #00c3e3;border-radius:0 8px 8px 0;'
            f'padding:20px 24px;color:#c8e0f0;font-size:0.91rem;'
            f'line-height:1.8;margin-top:6px;">'
            f'{response}</div>',
            unsafe_allow_html=True
        )

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.exchange_count += 1

# ── EMPTY STATE ────────────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div style="text-align:center;padding:72px 20px 40px;">
        <div style="font-size:2.8rem;color:#1a3048;margin-bottom:16px;">◈</div>
        <div style="font-size:0.88rem;color:#2a4a62;max-width:380px;
                    margin:0 auto;line-height:1.8;">
            Faça uma pergunta sobre sua carteira de clientes,<br>
            contratos ou métricas de SLA.<br>
            <span style="color:#1a3048;">Use os exemplos no menu lateral para começar.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

"""
ui/app.py
----------
Streamlit frontend for the AI Research Assistant.
Connects to the FastAPI backend via HTTP.

Run with:  streamlit run ui/app.py
"""

import streamlit as st
import requests
import time
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit branding only ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* DO NOT hide header — it contains the sidebar toggle */

/* ── Style the top header bar to blend in ── */
header[data-testid="stHeader"] {
    background: rgba(15, 12, 41, 0.95) !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    height: 3rem !important;
}

/* ── Sidebar toggle button (arrow to reopen when closed) ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border-radius: 0 12px 12px 0 !important;
    box-shadow: 4px 0 15px rgba(102,126,234,0.5) !important;
    z-index: 9999 !important;
    top: 50vh !important;
    position: fixed !important;
    left: 0 !important;
}
[data-testid="collapsedControl"]:hover {
    box-shadow: 4px 0 25px rgba(102,126,234,0.8) !important;
    transform: scale(1.05) !important;
}
[data-testid="collapsedControl"] svg {
    fill: white !important;
    color: white !important;
}

/* ── Sidebar collapse button (arrow to close when open) ── */
[data-testid="stSidebarCollapseButton"] button {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: white !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: white !important;
    color: white !important;
}

/* ── Force sidebar visible on load ── */
[data-testid="stSidebar"] {
    transform: none !important;
    left: 0 !important;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

[data-testid="stSidebar"] * {
    color: #e0e0ff !important;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 20px 60px rgba(102,126,234,0.4);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 700;
    color: white;
    margin: 0;
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
.hero-subtitle {
    font-size: 1rem;
    color: rgba(255,255,255,0.85);
    margin-top: 0.5rem;
    font-weight: 300;
    letter-spacing: 1px;
}
.hero-badges {
    margin-top: 1rem;
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    backdrop-filter: blur(10px);
}

/* ── Chat messages ── */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    margin-bottom: 1.5rem;
}

.user-bubble {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 0.75rem;
}
.user-bubble-content {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 1rem 1.4rem;
    border-radius: 20px 20px 4px 20px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(102,126,234,0.4);
}
.user-avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.ai-bubble {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 0.75rem;
}
.ai-bubble-content {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e8e8ff;
    padding: 1.2rem 1.6rem;
    border-radius: 20px 20px 20px 4px;
    max-width: 85%;
    font-size: 0.93rem;
    line-height: 1.75;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.2);
}
.ai-avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #11998e, #38ef7d);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

/* ── Source tags ── */
.sources-row {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.source-tag {
    font-size: 0.7rem;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 500;
}
.source-rag       { background: rgba(102,126,234,0.25); color: #a0b0ff; border: 1px solid rgba(102,126,234,0.4); }
.source-news      { background: rgba(255,165,0,0.2);   color: #ffd080; border: 1px solid rgba(255,165,0,0.4); }
.source-books     { background: rgba(17,153,142,0.2);  color: #80ffda; border: 1px solid rgba(17,153,142,0.4); }
.source-filesystem{ background: rgba(200,100,255,0.2); color: #e0b0ff; border: 1px solid rgba(200,100,255,0.4); }
.source-sqlite    { background: rgba(255,80,80,0.2);   color: #ffb0b0; border: 1px solid rgba(255,80,80,0.4); }

/* ── Stat cards ── */
.stat-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-number { font-size: 2rem; font-weight: 700; color: #a0b0ff; }
.stat-label  { font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 0.2rem; }

/* ── Section headers ── */
.section-header {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

/* ── History cards ── */
.history-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: background 0.2s, border-color 0.2s;
}
.history-card:hover {
    background: rgba(102,126,234,0.15);
    border-color: rgba(102,126,234,0.4);
}
.history-query { color: #e0e0ff; font-size: 0.9rem; font-weight: 500; }
.history-meta  { color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 0.3rem; }

/* ── Input area ── */
.stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 16px !important;
    color: white !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(102,126,234,0.6) !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102,126,234,0.5) !important;
}

/* ── Status indicator ── */
.status-dot-green { display:inline-block; width:8px; height:8px; background:#38ef7d; border-radius:50%; margin-right:6px; box-shadow: 0 0 6px #38ef7d; }
.status-dot-red   { display:inline-block; width:8px; height:8px; background:#ff6b6b; border-radius:50%; margin-right:6px; }
.status-dot-yellow{ display:inline-block; width:8px; height:8px; background:#ffd080; border-radius:50%; margin-right:6px; animation: blink 1s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    color: #a0b0ff !important;
}

/* ── Scrollable chat ── */
.chat-scroll {
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(102,126,234,0.4) transparent;
}
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ────────────────────────────────────────────────────────

def check_api_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        data = r.json()
        return data.get("ready", False), data.get("status", "unknown")
    except:
        return False, "offline"


def call_query_api(query: str):
    try:
        r = requests.post(
            f"{API_BASE}/query",
            json={"query": query},
            timeout=120,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Unknown error")
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Is the FastAPI server running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out (>120s). Try a simpler query."
    except Exception as e:
        return None, str(e)


def get_history():
    try:
        r = requests.get(f"{API_BASE}/history?limit=20", timeout=5)
        return r.json().get("sessions", [])
    except:
        return []


def clear_memory_api():
    try:
        requests.post(f"{API_BASE}/clear-memory", timeout=5)
        return True
    except:
        return False


def get_summary_api():
    try:
        r = requests.get(f"{API_BASE}/summary", timeout=5)
        return r.json()
    except:
        return {}


def source_tag_html(source: str) -> str:
    icons = {
        "local_vector_store": ("📄 Local Docs", "source-rag"),
        "news_api":           ("📰 News API",   "source-news"),
        "open_library_api":   ("📚 Open Library","source-books"),
        "filesystem_mcp":     ("🗂️ Filesystem MCP","source-filesystem"),
        "sqlite_mcp":         ("🗄️ SQLite MCP", "source-sqlite"),
    }
    label, cls = icons.get(source, (source, "source-rag"))
    return f'<span class="source-tag {cls}">{label}</span>'


def render_message(role: str, content: str, sources: list = None):
    if role == "user":
        st.markdown(f"""
        <div class="user-bubble">
            <div class="user-bubble-content">{content}</div>
            <div class="user-avatar">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sources_html = ""
        if sources:
            tags = "".join(source_tag_html(s) for s in sources)
            sources_html = f'<div class="sources-row">{tags}</div>'
        # Convert markdown-ish newlines for HTML
        html_content = content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="ai-bubble">
            <div class="ai-avatar">🔬</div>
            <div class="ai-bubble-content">
                {html_content}
                {sources_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Session State ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 Research Assistant")
    st.markdown("---")

    # API Status
    is_ready, status = check_api_health()
    if is_ready:
        st.markdown('<span class="status-dot-green"></span> **API Online**', unsafe_allow_html=True)
    elif status == "offline":
        st.markdown('<span class="status-dot-red"></span> **API Offline**', unsafe_allow_html=True)
        st.error("Start the FastAPI server:\n```\nuvicorn api.server:app --reload\n```")
    else:
        st.markdown('<span class="status-dot-yellow"></span> **Initializing...**', unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown("**Navigation**")
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.active_tab = "chat"
    if st.button("📜 History", use_container_width=True):
        st.session_state.active_tab = "history"
    if st.button("📋 Summary", use_container_width=True):
        st.session_state.active_tab = "summary"
    if st.button("📁 Upload Docs", use_container_width=True):
        st.session_state.active_tab = "upload"

    st.markdown("---")

    # Stats
    st.markdown("**Session Stats**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state.query_count}</div>
            <div class="stat-label">Queries</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.messages) // 2}</div>
            <div class="stat-label">Turns</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Quick queries
    st.markdown("**💡 Try These**")
    quick_queries = [
        "What is RAG and how does it work?",
        "Explain transformer architecture",
        "Latest AI research breakthroughs",
        "How to do a literature review?",
        "What is LangGraph?",
    ]
    for q in quick_queries:
        if st.button(f"→ {q[:35]}...", use_container_width=True, key=f"quick_{q}"):
            st.session_state["pending_query"] = q
            st.session_state["active_tab"] = "chat"
            st.rerun()

    st.markdown("---")

    # Clear memory
    if st.button("🧹 Clear Memory", use_container_width=True):
        if clear_memory_api():
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.success("Memory cleared!")
            time.sleep(1)
            st.rerun()


# ── Main Content ─────────────────────────────────────────────────────────────

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🔬 AI Research Assistant</div>
    <div class="hero-subtitle">Multi-Agent Intelligence · LangGraph · RAG · MCP · Live APIs</div>
    <div class="hero-badges">
        <span class="badge">⚡ LangGraph</span>
        <span class="badge">🧠 GPT-4o-mini</span>
        <span class="badge">📄 FAISS RAG</span>
        <span class="badge">📰 NewsAPI</span>
        <span class="badge">📚 Open Library</span>
        <span class="badge">🗂️ MCP Servers</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── TAB: CHAT ──────────────────────────────────────────────────────────────
if st.session_state.active_tab == "chat":

    # Chat history display
    if st.session_state.messages:
        st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            render_message(msg["role"], msg["content"], msg.get("sources"))
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 3rem; color: rgba(255,255,255,0.4);">
            <div style="font-size: 4rem;">🔍</div>
            <div style="font-size: 1.2rem; margin-top: 1rem; font-weight: 500; color: rgba(255,255,255,0.6);">
                Ask me anything to get started
            </div>
            <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                I'll search local docs, recent news, academic books, and more
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input area
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        # Seed the text area widget if a quick query was clicked
        if "pending_query" in st.session_state and st.session_state["pending_query"]:
            st.session_state["query_input"] = st.session_state.pop("pending_query")
        query = st.text_area(
            "Your research question",
            placeholder="e.g. What are the latest breakthroughs in quantum computing?",
            label_visibility="collapsed",
            height=80,
            key="query_input",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("🚀 Send", use_container_width=True)

    # Also allow Enter-style submission via keyboard shortcut hint
    st.markdown('<div style="color:rgba(255,255,255,0.3); font-size:0.75rem; margin-top:0.3rem;">Tip: Use the sidebar quick queries to try examples instantly</div>', unsafe_allow_html=True)

    if send and query.strip():
        if not is_ready:
            st.error("API is not ready. Start the FastAPI server first.")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": query.strip()})
            st.session_state.query_count += 1

            # Call API with spinner
            with st.spinner("🔬 Researching across all sources..."):
                result, error = call_query_api(query.strip())

            if error:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ Error: {error}",
                    "sources": [],
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", []),
                })

                # Show plan in expander
                if result.get("plan"):
                    with st.expander("🧠 View Research Plan (Planner Agent output)"):
                        plan = result["plan"]
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Search Terms:**", plan.get("search_terms", []))
                            st.write("**Sub-questions:**")
                            for q in plan.get("sub_questions", []):
                                st.write(f"• {q}")
                        with col2:
                            st.write("**Sources Enabled:**")
                            st.write(f"• Local Docs: {'✅' if plan.get('use_local_docs') else '❌'}")
                            st.write(f"• News API: {'✅' if plan.get('use_news_api') else '❌'}")
                            st.write(f"• Books API: {'✅' if plan.get('use_books_api') else '❌'}")
                        st.write("**Reasoning:**", plan.get("reasoning", ""))

            st.rerun()


# ── TAB: HISTORY ───────────────────────────────────────────────────────────
elif st.session_state.active_tab == "history":
    st.markdown('<div class="section-header">📜 Research History</div>', unsafe_allow_html=True)

    # Search bar
    search_term = st.text_input("🔍 Search history", placeholder="e.g. machine learning")

    sessions = get_history()

    if search_term:
        try:
            r = requests.get(f"{API_BASE}/search-history?keyword={search_term}", timeout=5)
            sessions = r.json().get("sessions", [])
        except:
            pass

    if not sessions:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:rgba(255,255,255,0.4);">
            No research sessions yet. Ask your first question!
        </div>""", unsafe_allow_html=True)
    else:
        for s in sessions:
            ts = s.get("timestamp", "")[:16].replace("T", " ")
            query_preview = s.get("query", "")[:100]
            answer_preview = (s.get("answer") or "")[:150]

            with st.expander(f"🔍 {query_preview}  ·  {ts}"):
                st.markdown(f"**Query:** {s.get('query', '')}")
                st.markdown("**Answer Preview:**")
                st.markdown(f"> {answer_preview}...")
                if s.get("sources"):
                    import json
                    try:
                        srcs = json.loads(s["sources"]) if isinstance(s["sources"], str) else s["sources"]
                        st.markdown(f"**Sources:** {', '.join(srcs)}")
                    except:
                        pass

                if st.button("↩️ Re-ask this", key=f"reask_{s['id']}"):
                    st.session_state["pending_query"] = s.get("query", "")
                    st.session_state.active_tab = "chat"
                    st.rerun()


# ── TAB: SUMMARY ───────────────────────────────────────────────────────────
elif st.session_state.active_tab == "summary":
    st.markdown('<div class="section-header">📋 Conversation Summary</div>', unsafe_allow_html=True)

    data = get_summary_api()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🧠 AI-Generated Summary**")
        summary = data.get("summary", "No conversation yet.")
        st.markdown(f"""
        <div style="background:rgba(102,126,234,0.1); border:1px solid rgba(102,126,234,0.3);
                    border-radius:12px; padding:1.2rem; color:#e0e0ff; line-height:1.7;">
            {summary}
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("**💬 Recent Turns**")
        recent = data.get("recent_turns", "No recent turns.")
        lines = recent.split("\n") if recent else []
        for line in lines:
            if line.startswith("User:"):
                st.markdown(f"""
                <div style="background:rgba(102,126,234,0.15); border-radius:8px;
                            padding:0.6rem 1rem; margin:0.3rem 0; color:#c0c8ff; font-size:0.85rem;">
                    👤 {line[5:].strip()}
                </div>""", unsafe_allow_html=True)
            elif line.startswith("Assistant:"):
                st.markdown(f"""
                <div style="background:rgba(17,153,142,0.15); border-radius:8px;
                            padding:0.6rem 1rem; margin:0.3rem 0; color:#80ffda; font-size:0.85rem;">
                    🤖 {line[10:].strip()[:200]}...
                </div>""", unsafe_allow_html=True)


# ── TAB: UPLOAD ────────────────────────────────────────────────────────────
elif st.session_state.active_tab == "upload":
    st.markdown('<div class="section-header">📁 Upload Documents to Knowledge Base</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(102,126,234,0.1); border:1px solid rgba(102,126,234,0.2);
                border-radius:12px; padding:1rem 1.4rem; color:#c0c8ff; margin-bottom:1.5rem;">
        📌 Upload <strong>.txt</strong>, <strong>.md</strong>, or <strong>.pdf</strong> files.
        They'll be automatically chunked, embedded, and added to the FAISS vector store
        so the Retriever Agent can search them.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Choose files",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
    )

    if uploaded and st.button("📤 Upload & Index Documents"):
        for file in uploaded:
            with st.spinner(f"Uploading {file.name}..."):
                try:
                    r = requests.post(
                        f"{API_BASE}/add-document",
                        files={"file": (file.name, file.getvalue(), file.type)},
                        timeout=30,
                    )
                    if r.status_code == 200:
                        st.success(f"✅ {file.name} uploaded and indexing started!")
                    else:
                        st.error(f"❌ {file.name}: {r.json().get('detail', 'Error')}")
                except Exception as e:
                    st.error(f"❌ {file.name}: {str(e)}")

        st.info("⏳ The knowledge base is rebuilding in the background. Wait ~30 seconds before querying new content.")

    st.markdown("---")
    st.markdown("**🗑️ Rebuild Vector Store**")
    st.markdown('<div style="color:rgba(255,255,255,0.5); font-size:0.85rem;">Use this if you manually added files to data/docs/</div>', unsafe_allow_html=True)
    if st.button("🔄 Rebuild Knowledge Base"):
        try:
            r = requests.delete(f"{API_BASE}/vector-store", timeout=10)
            st.success("✅ Rebuild started in background!")
        except:
            st.error("Could not connect to API.")
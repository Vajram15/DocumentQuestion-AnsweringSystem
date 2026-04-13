"""
Streamlit frontend for Document Question-Answering System
Connects to FastAPI backend via HTTP endpoints
"""

import streamlit as st
import requests
import time

# ── Configuration ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"


# ── Helper functions ───────────────────────────────────────────────────────────

def api_get(path: str) -> requests.Response:
    return requests.get(f"{API_BASE}{path}", timeout=10)


def api_post(path: str, **kwargs) -> requests.Response:
    return requests.post(f"{API_BASE}{path}", timeout=60, **kwargs)


def api_delete(path: str) -> requests.Response:
    return requests.delete(f"{API_BASE}{path}", timeout=10)


def check_health() -> bool:
    try:
        r = api_get("/health")
        return r.status_code == 200
    except Exception:
        return False


def fetch_documents() -> list:
    try:
        r = api_get("/documents/")
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


# ── Page: Dashboard ────────────────────────────────────────────────────────────

def page_dashboard():
    st.title("Document Q&A System")
    st.markdown("AI-powered document question answering using LangChain + FastAPI.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("API Status")
        with st.spinner("Checking API..."):
            healthy = check_health()
        if healthy:
            st.success("FastAPI backend is online")
        else:
            st.error("FastAPI backend is offline — start the server first")
            st.code("uvicorn src.main:app --reload", language="bash")

    with col2:
        st.subheader("Uploaded Documents")
        docs = fetch_documents()
        st.metric("Total Documents", len(docs))

    if docs:
        st.divider()
        st.subheader("Recent Documents")
        for doc in docs[-5:][::-1]:
            st.markdown(f"- **{doc['name']}** — `{doc['id'][:8]}...`")


# ── Page: Upload Documents ─────────────────────────────────────────────────────

def page_upload():
    st.title("Upload Documents")
    st.markdown("Upload a **PDF** or paste **plain text** to add it to the knowledge base.")

    tab_pdf, tab_text = st.tabs(["PDF Upload", "Text / Paste"])

    # ── PDF tab ──
    with tab_pdf:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Only PDF files are supported here"
        )

        if uploaded_file is not None:
            st.info(f"Selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            if st.button("Upload PDF", type="primary", key="btn_upload_pdf"):
                with st.spinner("Uploading and processing PDF..."):
                    try:
                        r = api_post(
                            "/documents/upload-pdf",
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        )
                        if r.status_code == 201:
                            data = r.json()
                            st.success(
                                f"Document uploaded successfully!\n\n"
                                f"- **ID:** `{data['document_id']}`\n"
                                f"- **Chunks:** {data['chunks_count']}"
                            )
                        else:
                            st.error(f"Upload failed ({r.status_code}): {r.json().get('detail', r.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API. Is the FastAPI server running?")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

    # ── Text tab ──
    with tab_text:
        doc_name = st.text_input("Document name", placeholder="e.g. Annual Report 2025")
        doc_content = st.text_area(
            "Paste document content here",
            height=300,
            placeholder="Paste your text content..."
        )

        if st.button("Upload Text", type="primary", key="btn_upload_text"):
            if not doc_name.strip():
                st.warning("Please enter a document name.")
            elif not doc_content.strip():
                st.warning("Please paste some content.")
            else:
                with st.spinner("Uploading and processing text..."):
                    try:
                        r = api_post(
                            "/documents/upload",
                            json={"name": doc_name.strip(), "content": doc_content.strip()}
                        )
                        if r.status_code == 201:
                            data = r.json()
                            st.success(
                                f"Document uploaded successfully!\n\n"
                                f"- **ID:** `{data['document_id']}`\n"
                                f"- **Chunks:** {data['chunks_count']}"
                            )
                        else:
                            st.error(f"Upload failed ({r.status_code}): {r.json().get('detail', r.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API. Is the FastAPI server running?")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")


# ── Page: Manage Documents ─────────────────────────────────────────────────────

def page_documents():
    st.title("My Documents")

    if st.button("Refresh", icon="🔄"):
        st.rerun()

    docs = fetch_documents()

    if not docs:
        st.info("No documents uploaded yet. Go to **Upload Documents** to add one.")
        return

    st.markdown(f"**{len(docs)} document(s)** in the knowledge base.")
    st.divider()

    for doc in docs:
        with st.expander(f"📄 {doc['name']}  —  `{doc['id'][:8]}...`"):
            col_info, col_del = st.columns([4, 1])
            with col_info:
                st.markdown(f"**Full ID:** `{doc['id']}`")
                created = doc.get("created_at", "—")
                st.markdown(f"**Uploaded:** {created}")
            with col_del:
                if st.button("Delete", key=f"del_{doc['id']}", type="secondary"):
                    try:
                        r = api_delete(f"/documents/{doc['id']}")
                        if r.status_code == 200:
                            st.success("Document deleted.")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {r.json().get('detail', r.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API.")


# ── Page: Ask Questions ────────────────────────────────────────────────────────

def page_ask():
    st.title("Ask a Question")
    st.markdown("Ask anything about your uploaded documents.")

    docs = fetch_documents()

    # Document selector
    doc_options = {"All Documents (search entire knowledge base)": None}
    for d in docs:
        doc_options[f"{d['name']}  ({d['id'][:8]}...)"] = d["id"]

    selected_label = st.selectbox(
        "Search in",
        options=list(doc_options.keys()),
        help="Pick a specific document or search all"
    )
    selected_doc_id = doc_options[selected_label]

    # Advanced options
    with st.expander("Advanced Options"):
        k = st.slider(
            "Number of chunks to retrieve (k)",
            min_value=1, max_value=10, value=3,
            help="Higher k = more context, slower response"
        )

    # Question input
    question = st.text_area(
        "Your question",
        height=100,
        placeholder="e.g. What is the main topic of this document?"
    )

    if st.button("Get Answer", type="primary", disabled=not question.strip()):
        if not docs:
            st.warning("No documents uploaded yet. Please upload a document first.")
            return

        with st.spinner("Searching documents and generating answer..."):
            try:
                payload = {
                    "question": question.strip(),
                    "k": k,
                }
                if selected_doc_id:
                    payload["document_id"] = selected_doc_id

                r = api_post("/qa/ask", json=payload)

                if r.status_code == 200:
                    data = r.json()

                    st.divider()
                    st.subheader("Answer")
                    st.markdown(data["answer"])

                    confidence = data.get("confidence", 0)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence", f"{confidence:.0%}")
                    with col2:
                        st.metric("Sources Used", len(data.get("sources", [])))

                    sources = data.get("sources", [])
                    if sources:
                        st.divider()
                        st.subheader("Source Chunks")
                        for i, src in enumerate(sources, 1):
                            with st.expander(f"Chunk {i}"):
                                st.markdown(src)

                elif r.status_code == 400:
                    st.warning(r.json().get("detail", "Bad request"))
                else:
                    st.error(f"Error ({r.status_code}): {r.json().get('detail', r.text)}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Is the FastAPI server running?")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ── App Layout ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Document Q&A System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/document.png", width=60)
    st.title("Doc Q&A")
    st.divider()

    page = st.radio(
        "Navigation",
        options=["Dashboard", "Upload Documents", "My Documents", "Ask Questions"],
        label_visibility="collapsed"
    )

    st.divider()

    # Live API status indicator in sidebar
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200:
            st.success("API Online")
        else:
            st.error("API Error")
    except Exception:
        st.error("API Offline")

    st.caption("FastAPI + LangChain + FAISS")

# Route to pages
if page == "Dashboard":
    page_dashboard()
elif page == "Upload Documents":
    page_upload()
elif page == "My Documents":
    page_documents()
elif page == "Ask Questions":
    page_ask()

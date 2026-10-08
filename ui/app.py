"""Streamlit UI for SecureRAG cybersecurity Q&A."""

import streamlit as st

st.set_page_config(
    page_title="SecureRAG - Cybersecurity Q&A",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ SecureRAG")
st.subheader("Cybersecurity Q&A Agent powered by LangGraph")

st.markdown("""
Ask questions about:
- **CVE vulnerabilities** and their mitigations
- **MITRE ATT&CK** techniques and tactics
- **Security advisories** and best practices
""")

query = st.text_input("Ask a cybersecurity question:")

if query:
    with st.spinner("Searching and generating answer..."):
        # TODO: Connect to agent
        st.warning("Agent not connected yet. Run the ingestion pipeline first.")

    st.markdown("---")
    st.caption("Powered by LangGraph + ChromaDB + Claude")

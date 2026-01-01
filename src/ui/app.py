import streamlit as st
import requests
import json
print("UI Starting up...")

st.set_page_config(page_title="Enterprise RAG Search", layout="wide")

import os

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/chat")

st.title("Enterprise RAG Search")

with st.sidebar:
    st.header("Configuration")
    top_k_retrieval = st.slider("Retrieval Top-K", 5, 50, 20)
    top_k_rerank = st.slider("Rerank Top-K", 1, 10, 5)
    # use_hyde = st.checkbox("Use HyDE", value=False)

query = st.chat_input("Enter your query...")

if query:
    st.session_state.messages = st.session_state.get("messages", [])
    st.session_state.messages.append({"role": "user", "content": query})

# s = requests.Session()

for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if query:
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                payload = {
                    "query": query,
                    "top_k_retrieval": top_k_retrieval,
                    "top_k_rerank": top_k_rerank,
                    # "use_hyde": use_hyde
                }
                response = requests.post(API_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                
                answer = data["answer"]
                st.write(answer)
                
                with st.expander("View Context"):
                    for i, (doc, score) in enumerate(data["context"]):
                        st.markdown(f"**Relevance Score:** {score:.4f}")
                        st.text(doc)
                        st.divider()
                        
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {e}")

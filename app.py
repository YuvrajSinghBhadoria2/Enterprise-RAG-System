"""
Hugging Face Spaces - Enterprise RAG System
Standalone Streamlit application
"""

import streamlit as st
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline.query_pipeline import QueryPipeline

st.set_page_config(
    page_title="Enterprise RAG Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize pipeline
@st.cache_resource
def load_pipeline():
    """Load the RAG pipeline (cached for performance)"""
    try:
        return QueryPipeline()
    except Exception as e:
        st.error(f"Error loading pipeline: {e}")
        return None

# Main UI
st.title("🔍 Enterprise RAG Search")
st.markdown("*Production-grade Retrieval-Augmented Generation with Hallucination Prevention*")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check for API key
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        st.warning("⚠️ GROQ_API_KEY not set. Please configure in Space settings.")
    else:
        st.success("✅ API Key configured")
    
    st.divider()
    
    top_k_retrieval = st.slider("Retrieval Top-K", 5, 50, 20)
    top_k_rerank = st.slider("Rerank Top-K", 1, 10, 5)
    
    st.divider()
    st.markdown("### 📊 System Info")
    st.info("""
    - **Hybrid Search**: BM25 + FAISS
    - **Reranking**: Cross-Encoder
    - **Safety**: Confidence Gating
    """)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching and generating answer..."):
            pipeline = load_pipeline()
            
            if pipeline is None:
                st.error("Pipeline not loaded. Please check configuration.")
            else:
                try:
                    result = pipeline.run(
                        query=prompt,
                        top_k_retrieval=top_k_retrieval,
                        top_k_rerank=top_k_rerank
                    )
                    
                    # Display answer
                    st.markdown(result["answer"])
                    
                    # Display metadata in expander
                    with st.expander("📋 View Details"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Retrieval Score", f"{result.get('retrieval_score', 'N/A'):.2f}")
                        
                        with col2:
                            hallucination = result.get('hallucination_score', 'N/A')
                            if hallucination != 'N/A':
                                st.metric("Hallucination Score", f"{hallucination:.2f}")
                        
                        with col3:
                            groundedness = result.get('groundedness', 'N/A')
                            if groundedness != 'N/A':
                                st.metric("Groundedness", f"{groundedness:.2f}")
                        
                        # Show retrieved context
                        if result.get("context"):
                            st.markdown("**Retrieved Context:**")
                            for i, (doc, score) in enumerate(result["context"][:3], 1):
                                st.markdown(f"{i}. [Score: {score:.2f}] {doc[:200]}...")
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"]
                    })
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    st.exception(e)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    Enterprise RAG System | <a href='https://github.com/YuvrajSinghBhadoria2/Enterprise-RAG-System'>GitHub</a>
</div>
""", unsafe_allow_html=True)

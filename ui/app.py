import streamlit as st
import requests
import json
from datetime import datetime
import os
import gc
import psutil

# Memory monitoring
def check_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    if memory_info.rss > 450 * 1024 * 1024:  # 450MB threshold
        gc.collect()
        return True
    return False

# Configuration and Setup
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="GreenCode AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #00cc88;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .upload-header {
        color: #00cc88;
        font-size: 1.3rem;
        font-weight: 600;
    }
    .footer {
        position: fixed;
        bottom: 20px;
        right: 20px;
        color: #666;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main Layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🌱 GreenCode AI")
    st.caption("Your Intelligent Policy Analysis Assistant")

# Sidebar for Document Upload
with st.sidebar:
    st.markdown('<p class="upload-header">📤 Document Upload</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your policy document",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )
    
    if uploaded_file:
        with st.spinner("Processing document..."):
            try:
                # Stream file in chunks
                chunk_size = 1024 * 1024  # 1MB chunks
                files = [("uploaded_files", (uploaded_file.name, uploaded_file.read(chunk_size)))]                
                
                response = requests.post(
                    f"{API_URL}/upload_docs",
                    files=files,
                    timeout=300,  # 5 minutes timeout
                    stream=True  # Enable streaming
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Document uploaded successfully!")
                    session_id = data.get("session_id")
                    st.session_state["session_id"] = session_id
                    st.info(f"Session ID: {session_id[:8]}...")
                else:
                    st.error("Failed to upload document")
            except requests.exceptions.Timeout:
                st.error("Upload timed out. Please try with a smaller document.")
            except Exception as e:
                st.error(f"Error during upload: {str(e)}")
            finally:
                # Clear file from memory
                uploaded_file.close()
                del uploaded_file
                gc.collect()  # Force garbage collection
    
    st.markdown("---")
    st.markdown("### 📌 Quick Tips")
    st.markdown("""
        - Upload your policy document first
        - Ask questions in plain English
        - Get structured responses with clause references
    """)

# Main Content Area
main_container = st.container()
with main_container:
    query = st.text_area(
        "What would you like to know about your policy?",
        placeholder="Example: What is the coverage limit for personal accidents?",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze", use_container_width=True)

    if analyze_button and query:
        # Check memory usage before processing
        check_memory_usage()
        
        session_id = st.session_state.get("session_id")
        if not session_id:
            st.warning("⚠️ Please upload a document first")
        else:
            with st.spinner("Analyzing your query..."):
                try:
                    # Limit query length
                    query = query[:1000]  # Limit to 1000 characters
                    
                    response = requests.post(
                        f"{API_URL}/query",
                        json={"query": query, "session_id": session_id},
                        timeout=60  # Set timeout to 60 seconds
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            # Display Response in a Card-like container
                            st.markdown("### 📋 Analysis Result")
                            with st.expander("View Analysis", expanded=True):
                                response_text = result.get("response", "")
                                try:
                                    if isinstance(response_text, dict):
                                        st.json(response_text)
                                    else:
                                        parsed = json.loads(response_text)
                                        st.json(parsed)
                                except json.JSONDecodeError:
                                    st.markdown("**Response:**")
                                    st.write(response_text)
                            
                            # Display Referenced Clauses (limited)
                            if result.get("retrieved_clauses"):
                                with st.expander("📑 Referenced Clauses", expanded=False):
                                    for i, clause in enumerate(result["retrieved_clauses"][:3]):  # Limit to 3 clauses
                                        st.markdown(f"**Clause {i+1}**")
                                        st.code(clause[:500], language="text")  # Limit clause length
                            
                            # Clear variables
                            del result
                            del response_text
                            gc.collect()
                    else:
                        st.error("Failed to process your query")
                except requests.exceptions.Timeout:
                    st.error("Query processing timed out. Please try again.")
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                finally:
                    check_memory_usage()

# Footer
st.markdown(
    '<div class="footer">Powered by GreenCode AI</div>',
    unsafe_allow_html=True
)


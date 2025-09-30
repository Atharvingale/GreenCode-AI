import streamlit as st
import requests
import json
from datetime import datetime
import os
import time
import random
import hashlib

# Configuration and Setup
API_URL = "http://127.0.0.1:8000"

@st.cache_data(show_spinner=False)
def generate_ai_questions(session_id: str):
    """Generate AI-powered questions based on the actual document content.
    Cached per session_id to avoid repeated API calls on reruns.
    """
    try:
        response = requests.post(
            f"{API_URL}/generate_questions",
            json={"session_id": session_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "questions": data.get("questions", []),
                "document_type": data.get("document_type", "unknown"),
                "document_summary": data.get("document_summary", ""),
                "error": data.get("error")
            }
        else:
            return {
                "questions": ["What are the most important terms I should understand?"],
                "document_type": "unknown",
                "error": "Failed to generate questions"
            }
    except Exception as e:
        return {
            "questions": ["What are my main obligations under this document?"],
            "document_type": "unknown",
            "error": str(e)
        }

def on_question_change():
    """Callback function when dropdown selection changes"""
    if "question_dropdown" in st.session_state:
        selected_index = st.session_state["question_dropdown"]
        question_options = ["Type your own question..."] + st.session_state.get("ai_questions", [])
        
        if selected_index > 0 and selected_index < len(question_options):
            selected_question = question_options[selected_index]
            st.session_state["selected_question"] = selected_question
        elif selected_index == 0:
            st.session_state["selected_question"] = ""

def display_legal_analysis_result(result, analysis_type):
    """Display results based on analysis type with modern formatting."""
    
    if analysis_type == "qa":
        st.markdown("## 🤖 AI Assistant Response")
        
        if "result" in result:
            answer_data = result["result"]
            if isinstance(answer_data, dict):
                if "answer" in answer_data:
                    st.success(f"**Answer:** {answer_data['answer']}")
                    
                if "confidence" in answer_data:
                    confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                    confidence_icon = confidence_colors.get(answer_data['confidence'], "⚫")
                    st.info(f"**Confidence:** {confidence_icon} {answer_data['confidence'].upper()}")
                    
                if "additional_notes" in answer_data and answer_data["additional_notes"]:
                    st.info(f"**Additional Notes:** {answer_data['additional_notes']}")

    elif analysis_type == "translate":
        st.markdown("## 📝 Translation Results")
        
        if "result" in result and "translations" in result["result"]:
            for i, translation in enumerate(result["result"]["translations"]):
                with st.expander(f"Translation {i+1}", expanded=True):
                    st.markdown("**Original Legal Text:**")
                    st.code(translation.get("original", ""), language="text")
                    st.markdown("**Plain English Translation:**")
                    st.success(translation.get("simplified", ""))
                    if "key_points" in translation and translation["key_points"]:
                        st.markdown("**Key Points:**")
                        for point in translation["key_points"]:
                            st.markdown(f"• {point}")

    elif analysis_type == "risk":
        st.markdown("## 🛡️ Risk Analysis Report")
        
        if "result" in result and "risk_analysis" in result["result"]:
            risks = result["result"]["risk_analysis"]
            if risks:
                # Risk summary
                high_risks = [r for r in risks if r.get("risk_level") in ["high", "critical"]]
                medium_risks = [r for r in risks if r.get("risk_level") == "medium"]
                low_risks = [r for r in risks if r.get("risk_level") == "low"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("High Risk", len(high_risks), delta=None)
                with col2:
                    st.metric("Medium Risk", len(medium_risks), delta=None)
                with col3:
                    st.metric("Low Risk", len(low_risks), delta=None)
                
                # Display risks
                for i, risk in enumerate(risks):
                    risk_level = risk.get("risk_level", "medium").lower()
                    risk_type = risk.get('risk_type', 'Unknown Risk').replace('_', ' ').title()
                    
                    if risk_level in ["high", "critical"]:
                        st.error(f"**⚠️ {risk_type} - {risk_level.upper()} RISK**")
                    elif risk_level == "medium":
                        st.warning(f"**🔶 {risk_type} - {risk_level.upper()} RISK**")
                    else:
                        st.info(f"**ℹ️ {risk_type} - {risk_level.upper()} RISK**")
                    
                    st.markdown(f"**Clause:** {risk.get('clause', 'No clause specified')}")
                    st.markdown(f"**Warning:** {risk.get('warning', 'No warning provided')}")
                    st.markdown(f"**Recommendation:** {risk.get('suggestion', 'No suggestion provided')}")
                    st.markdown("---")
            else:
                st.success("✅ No major risks detected in your document!")

    # Always show referenced clauses if available
    if result.get("retrieved_clauses"):
        with st.expander("📁 Referenced Document Sections", expanded=False):
            for i, clause in enumerate(result["retrieved_clauses"][:5]):
                st.markdown(f"**Section {i+1}**")
                st.text(clause[:500] + "..." if len(clause) > 500 else clause)

st.set_page_config(
    page_title="🔒 SafeSign - Digital Document Security",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Clean CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #00D4AA;
        --primary-dark: #00B899;
        --secondary: #FF6B6B;
        --accent: #4ECDC4;
        --success: #51CF66;
        --warning: #FF8C42;
        --error: #FF6B6B;
        
        --bg-primary: #000000;
        --bg-secondary: #111111;
        --bg-tertiary: #1A1A1A;
        --bg-card: #1E1E1E;
        --bg-hover: #2A2A2A;
        
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
        --text-muted: #808080;
        
        --border: #333333;
        --border-accent: #444444;
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .main-header {
        background: var(--bg-secondary);
        padding: 2rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 2rem;
        border-radius: 1rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .feature-card {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border);
        text-align: center;
        height: 100%;
        transition: all 0.3s ease;
        color: var(--text-primary);
    }
    
    .feature-card:hover {
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.2);
        transform: translateY(-2px);
        border-color: var(--primary);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .analysis-section {
        background: var(--bg-card);
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border);
        margin: 2rem 0;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: #000000;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--accent), var(--primary));
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 170, 0.5);
    }
    
    .stSelectbox > div > div > div {
        border-radius: 0.5rem;
        border: 2px solid var(--border);
        background: var(--bg-card);
        color: var(--text-primary);
    }
    
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.2);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
        border: 2px solid var(--border);
        background: var(--bg-card);
        color: var(--text-primary);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.2);
    }
    
    .sidebar {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border);
    }
    
    .upload-section {
        background: var(--bg-card);
        border: 2px dashed var(--border-accent);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .upload-section:hover {
        border-color: var(--primary);
        background: var(--bg-hover);
    }
    
    .info-card {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        border-left: 4px solid var(--primary);
        color: var(--text-primary);
    }
    
    .metric-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--primary);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="main-header">
    <h1 class="hero-title">🔒 SafeSign</h1>
    <p class="hero-subtitle">Secure Digital Document Signing Platform</p>
</div>
""", unsafe_allow_html=True)

# Feature Cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🔒</span>
        <h3>Secure Signatures</h3>
        <p>Create cryptographically secure digital signatures with enterprise-grade encryption and authentication.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🛡️</span>
        <h3>Document Analysis</h3>
        <p>AI-powered analysis to identify risks, verify authenticity, and ensure document integrity.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <span class="feature-icon">🤖</span>
        <h3>Smart Assistant</h3>
        <p>Get instant answers about document contents and signing requirements before you sign.</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar">', unsafe_allow_html=True)
    st.markdown("### 📄 Upload Document")
    
    # Show current session info if exists
    if st.session_state.get("session_id"):
        st.success(f"📁 Active session: {st.session_state['session_id'][-8:]}")
        if st.button("🔄 Clear Session & Start Fresh", type="secondary", use_container_width=True):
            # Clear all session state
            keys_to_clear = ["session_id", "last_upload_hash", "ai_questions", "document_type", 
                           "document_summary", "selected_analysis", "selected_question"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    uploaded_file = st.file_uploader(
        "Choose your legal document",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )

    # Process upload once per unique file content (prevents re-upload on reruns)
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()
        last_hash = st.session_state.get("last_upload_hash")

        if last_hash != file_hash:
            with st.spinner("Processing document..."):
                response = requests.post(
                    f"{API_URL}/upload_docs",
                    files=[("uploaded_files", (uploaded_file.name, file_bytes))]
                )

            if response.status_code == 200:
                data = response.json()
                st.success("✅ Document uploaded successfully!")
                session_id = data.get("session_id")
                st.session_state["session_id"] = session_id
                st.session_state["last_upload_hash"] = file_hash

                # Generate AI questions (cached per session)
                with st.spinner("🧠 Generating smart questions..."):
                    ai_questions_data = generate_ai_questions(session_id)

                if not ai_questions_data.get("error"):
                    st.session_state["ai_questions"] = ai_questions_data["questions"]
                    st.session_state["document_type"] = ai_questions_data["document_type"]
                    st.session_state["document_summary"] = ai_questions_data.get("document_summary", "")
                    st.success("🎯 Smart questions generated!")
                else:
                    st.warning(f"⚠️ {ai_questions_data['error']}")
                    st.session_state["ai_questions"] = ["What are the main terms I should understand?"]
            else:
                st.error("❌ Failed to upload document")
        else:
            st.info("ℹ️ Using the previously uploaded document. Upload a new file to reprocess.")
    
    # Show document information if available
    if st.session_state.get("document_type") and st.session_state.get("ai_questions"):
        st.markdown("---")
        st.markdown("### 📊 Document Info")
        st.write(f"**Type:** {st.session_state['document_type'].replace('_', ' ').title()}")
        st.write(f"**Questions available:** {len(st.session_state['ai_questions'])}")
        if st.session_state.get("document_summary"):
            with st.expander("Document Summary"):
                st.write(st.session_state["document_summary"])
    
    st.markdown("---")
    st.markdown("### ℹ️ How it works")
    st.markdown("""
    1. **Upload** your legal document
    2. **Choose** analysis type
    3. **Get** AI-powered insights
    4. **Understand** before you sign
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Content
st.markdown("""
<div class="analysis-section">
    <h2 class="section-title">🎯 Choose Analysis Type</h2>
</div>
""", unsafe_allow_html=True)

# Analysis type selection
analysis_options = [
    ("qa", "🤖 AI Assistant", "Ask questions about your document"),
    ("translate", "📝 Smart Translation", "Convert legal text to plain English"),
    ("risk", "🛡️ Risk Analysis", "Find potential risks and issues"),
    ("comprehensive", "✨ Full Analysis", "Complete analysis with all features")
]

cols = st.columns(4)
for i, (key, title, desc) in enumerate(analysis_options):
    with cols[i]:
        if st.button(f"{title}\n{desc}", key=f"analysis_{key}", use_container_width=True):
            st.session_state["selected_analysis"] = key

analysis_type = st.session_state.get("selected_analysis", "qa")

# Show selected analysis
if analysis_type:
    selected_option = next((opt for opt in analysis_options if opt[0] == analysis_type), None)
    if selected_option:
        st.info(f"**Selected:** {selected_option[1]} - {selected_option[2]}")

st.markdown("---")

# Question input section
st.markdown("### ❓ Ask Your Question")

# Show helpful guidance if no document is uploaded
if not st.session_state.get("session_id"):
    st.warning("⚠️ Please upload a document first to enable analysis features.")
    st.stop()

if analysis_type == "qa":
    ai_questions = st.session_state.get("ai_questions", [])
    
    # Initialize selected question if not exists
    if "selected_question" not in st.session_state:
        st.session_state["selected_question"] = ""
    
    if ai_questions and len(ai_questions) > 1:
        st.markdown("**💡 AI-Generated Questions for Your Document:**")
        
        question_options = ["Type your own question..."] + ai_questions
        selected_question_index = st.selectbox(
            "Choose from suggested questions:",
            range(len(question_options)),
            format_func=lambda i: question_options[i],
            key="question_dropdown",
            on_change=on_question_change
        )
        
    # Text area that updates based on dropdown selection
    query = st.text_area(
        "What would you like to know?",
        value=st.session_state.get("selected_question", ""),
        placeholder="Ask any question about your document...",
        height=100
    )

elif analysis_type == "translate":
    query = st.text_area(
        "Enter text to translate (or leave blank for full document):",
        placeholder="Paste specific legal text here, or leave blank to translate the entire document",
        height=100
    )
    if not query:
        query = "translate entire document"

elif analysis_type == "risk":
    query = st.selectbox(
        "Risk analysis focus:",
        [
            "Analyze all risks",
            "Focus on financial terms",
            "Focus on termination clauses",
            "Focus on hidden fees",
            "Focus on liability issues"
        ]
    )

else:  # comprehensive
    query = st.text_area(
        "Optional: Ask a specific question for comprehensive analysis",
        placeholder="Leave blank for general analysis, or ask a specific question...",
        height=80
    )
    if not query:
        query = "comprehensive analysis"

# Analysis button
if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
    session_id = st.session_state.get("session_id")
    
    if not session_id:
        st.error("⚠️ Please upload a document first")
    elif not query:
        st.error("⚠️ Please enter a question or select an analysis type")
    else:
        with st.spinner("🔍 Analyzing your document..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": query,
                        "session_id": session_id,
                        "analysis_type": analysis_type
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.success("✅ Analysis complete!")
                        display_legal_analysis_result(result, analysis_type)
                else:
                    st.error("❌ Failed to process your query")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">⚡</div>
        <div class="metric-label">Fast Analysis</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">🔒</div>
        <div class="metric-label">Secure & Private</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">🧠</div>
        <div class="metric-label">AI-Powered</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin: 2rem 0; color: #64748b;">
    <p><strong>🔒 SafeSign</strong> - Secure Digital Document Signing</p>
</div>
""", unsafe_allow_html=True)

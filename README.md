# 🔒 SafeSign - Secure Digital Document Platform

## 🚀 Professional AI-Powered Document Security and Analysis Platform

**SafeSign** is a cutting-edge digital document security platform that provides secure document signing and comprehensive analysis capabilities. Perfect for businesses and individuals who need secure document signing with intelligent risk assessment and analysis. 

![SafeSign](https://img.shields.io/badge/AI-Powered-00D4AA?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge&logo=streamlit)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge&logo=fastapi)

---

## 🌟 Key Features

### 🤖 **AI Assistant**
- Ask specific questions about your documents
- Get instant, accurate answers with confidence levels
- Context-aware responses based on document content

### 📝 **Smart Translation**
- Convert complex legal jargon to plain English
- Maintain legal accuracy while improving readability
- Highlight key terms and their meanings

### 🛡️ **Risk Analysis**
- Identify potential risks and unfavorable clauses
- Color-coded risk levels (High, Medium, Low)
- Detailed warnings and recommendations
- Hidden trap detection

### ✨ **Comprehensive Analysis**
- All-in-one analysis combining translation, risk assessment, and Q&A
- Smart question generation based on document content
- Professional analysis reports

---

## 🛠️ Tech Stack

### **Backend**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast Python web framework
- **[OpenAI GPT-4](https://openai.com/)** - Advanced language model for analysis
- **[FAISS](https://faiss.ai/)** - Efficient similarity search and clustering
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - PDF processing and text extraction
- **[python-docx](https://python-docx.readthedocs.io/)** - Microsoft Word document processing
- **[Sentence Transformers](https://www.sbert.net/)** - Text embedding generation

### **Frontend**
- **[Streamlit](https://streamlit.io/)** - Interactive web application framework
- **Custom CSS/HTML** - Modern black theme with teal accents
- **Responsive Design** - Mobile-friendly interface

### **AI & Machine Learning**
- **[OpenRouter](https://openrouter.ai/)** - AI model access and routing
- **[LangChain](https://langchain.com/)** - LLM application development framework
- **Semantic Search** - Vector-based document retrieval
- **Document Classification** - Automatic document type detection

### **Document Processing**
- **PDF Support** - Extract and analyze PDF documents
- **DOCX Support** - Microsoft Word document processing
- **Text Chunking** - Intelligent document segmentation
- **Vector Embeddings** - Semantic document understanding

---

## 📋 Prerequisites

Before setting up SafeSign, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **OpenAI API key** or **OpenRouter API key**
- **Minimum 4GB RAM** recommended
- **Windows/Mac/Linux** operating system

---

## 🚀 Quick Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/safesign.git
cd safesign
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv safesign_env
safesign_env\Scripts\activate

# Mac/Linux
python3 -m venv safesign_env
source safesign_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `config/config.yaml` file:
```yaml
# OpenRouter API Key (Recommended)
openai_api_key: "your-openrouter-api-key-here"
gemini_api_key: "your-openrouter-api-key-here"  # Same key for both

# OpenAI API Key (Alternative)
# openai_api_key: "your-openai-api-key-here"

# Configuration
embedding_model: "openai/gpt-3.5-turbo"
chunk_size: 512
max_chunks: 20
session_timeout_minutes: 60
```

### 5. Start the Backend API
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 6. Launch the Frontend
Open a new terminal and run:
```bash
streamlit run ui/app.py
```

### 7. Access the Application
Open your browser and go to:
- **Frontend:** http://localhost:8501
- **API Documentation:** http://localhost:8000/docs

---

## 🔧 Detailed Setup Instructions

### Getting API Keys

#### Option 1: OpenRouter (Recommended)
1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Use the same key for both `openai_api_key` and `gemini_api_key`

#### Option 2: OpenAI Direct
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up and get your API key
3. Use only the `openai_api_key` field

### Project Structure
```
safesign/
├── app/
│   ├── core/
│   │   ├── engine.py          # Main AI processing engine
│   │   ├── retriever.py       # Document retrieval system
│   │   ├── embedder.py        # Text embedding generation
│   │   ├── risk_analyzer.py   # Risk analysis algorithms
│   │   └── legal_templates.py # Document-specific prompts
│   ├── ingestion/
│   │   ├── load.py           # Document loading utilities
│   │   └── chunk.py          # Text chunking algorithms
│   └── main.py               # FastAPI backend server
├── ui/
│   └── app.py                # Streamlit frontend application
├── config/
│   └── config.yaml           # Configuration settings
├── data/                     # Document storage and indexes
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🎯 How to Use

### 1. **Upload Your Document**
- Drag and drop or click to upload PDF/DOCX files
- Supported formats: PDF, Microsoft Word (.docx)
- AI automatically analyzes and generates smart questions

### 2. **Choose Analysis Type**
- **🤖 AI Assistant:** Ask specific questions
- **📝 Smart Translation:** Convert legal text to plain English
- **🛡️ Risk Analysis:** Find potential risks and issues
- **✨ Full Analysis:** Complete comprehensive analysis

### 3. **Get AI-Powered Insights**
- Select from AI-generated questions or ask your own
- Receive detailed analysis with confidence levels
- Export results or share findings

### 4. **Document Types Supported**
- 🏠 Rental Agreements & Leases
- 💰 Loan Contracts & Credit Terms
- 📱 Terms of Service & Privacy Policies
- 💼 Employment Contracts
- 🛡️ Insurance Policies
- ⚙️ Service Agreements

---

## 🌐 API Endpoints

### Core Endpoints
- `POST /upload_docs` - Upload and process documents
- `POST /query` - Analyze documents with AI
- `POST /generate_questions` - Generate smart questions
- `POST /analyze_risks` - Perform risk analysis
- `GET /` - API health check

### Example API Usage
```python
import requests

# Upload document
files = {"uploaded_files": open("contract.pdf", "rb")}
response = requests.post("http://localhost:8000/upload_docs", files=files)
session_id = response.json()["session_id"]

# Ask question
query_data = {
    "query": "What are the termination conditions?",
    "session_id": session_id,
    "analysis_type": "qa"
}
response = requests.post("http://localhost:8000/query", json=query_data)
print(response.json())
```

---

## 🔒 Security & Privacy

- **Local Processing:** All documents are processed locally on your machine
- **No Data Storage:** Documents are temporarily stored and automatically deleted
- **API Key Security:** Your API keys are stored locally in config files
- **Session Management:** Each document upload creates a unique session
- **No Cloud Upload:** Your sensitive legal documents never leave your system

---

## 🐛 Troubleshooting

### Common Issues

**1. API Connection Error**
```bash
# Check if backend is running
curl http://localhost:8000/

# Restart the backend
python -m uvicorn app.main:app --reload --port 8000
```

**2. Module Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

**3. Streamlit Issues**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart with specific port
streamlit run ui/app.py --server.port 8501
```

**4. File Upload Problems**
- Ensure your PDF/DOCX files are not corrupted
- Check file size (recommended < 50MB)
- Verify file permissions

**5. AI Analysis Errors**
- Verify your API key is correctly set in `config/config.yaml`
- Check internet connection for API calls
- Ensure sufficient API credits/quota

---

## 🚀 Performance Tips

### For Better Performance:
1. **Use smaller documents** (< 20 pages) for faster processing
2. **Close other applications** to free up RAM
3. **Use SSD storage** for faster file operations
4. **Stable internet** for reliable API calls

### Hardware Recommendations:
- **RAM:** 8GB+ recommended
- **CPU:** Multi-core processor
- **Storage:** SSD preferred
- **Internet:** Stable broadband connection

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit your changes:** `git commit -m 'Add amazing feature'`
4. **Push to the branch:** `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/ ui/

# Lint code
flake8 app/ ui/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- **OpenAI** for providing powerful language models
- **Streamlit** for the amazing web app framework
- **FastAPI** for the high-performance backend framework
- **FAISS** for efficient similarity search
- **The open-source community** for incredible tools and libraries

---

## 📞 Support

Need help? Here's how to get support:

1. **Check the [Troubleshooting](#-troubleshooting) section**
2. **Search [existing issues](https://github.com/yourusername/safesign/issues)**
3. **Create a [new issue](https://github.com/yourusername/safesign/issues/new)**
4. **Contact via email:** support@safesign.com

---

## 🎉 What's Next?

### Upcoming Features:
- 📱 **Mobile App** - React Native mobile application
- 🌐 **Multi-language Support** - Analyze documents in multiple languages
- 📊 **Advanced Analytics** - Detailed document insights and statistics
- 🔗 **Integration APIs** - Connect with popular legal software
- 🤖 **Custom AI Models** - Fine-tuned models for specific legal domains

---

<div align="center">

### Made with ❤️ for Secure Digital Workflows

**🔒 SafeSign - Secure Digital Document Platform**

[⭐ Star this repo](https://github.com/yourusername/safesign) • [🐛 Report Bug](https://github.com/yourusername/safesign/issues) • [✨ Request Feature](https://github.com/yourusername/safesign/issues)

</div>

# SafeSign - Digital Document Security Platform 🔒📝

## 🚀 Overview

SafeSign is an intelligent digital document security platform designed to **provide secure document signing with comprehensive analysis capabilities**. The platform ensures document integrity and user protection by providing three powerful layers of security:

1. **📝 Document Analysis Layer** - Analyzes document content and provides clear summaries
2. **⚠️ Security & Risk Assessment** - Identifies potential security risks and document authenticity
3. **🔒 Secure Signing Layer** - Provides cryptographically secure digital signatures

> 🎯 **Mission:** Empowering secure digital document workflows through advanced security and intelligent analysis.

---

## 🎯 Problem Statement

**The Information Asymmetry Crisis:**

Legal documents—such as rental agreements, loan contracts, and terms of service—are often filled with complex, impenetrable jargon that is incomprehensible to the average person. This creates a significant information asymmetry where individuals may unknowingly agree to unfavorable terms, exposing them to financial and legal risks.

**Key Issues We Solve:**
* **Jargon Anxiety** - Fear and confusion that causes people to sign without reading
* **Hidden Traps** - Unfavorable clauses buried in complex language
* **Information Gaps** - Difficulty finding specific information in lengthy documents
* **Power Imbalance** - One side knows the law, the other doesn't

---

## ✅ Features

### 🎯 Core Analysis Layers
* **📝 Translation Layer**: Converts "non-derogation of landlord's rights" → "The landlord's rights in this contract cannot be taken away"
* **⚠️ Risk Analysis Layer**: Automatically flags unfavorable clauses (automatic renewals, hidden fees, liability shifts)
* **❓ Q&A Layer**: Ask "What happens if I'm 5 days late on rent?" and get instant, grounded answers

### 🛠️ Technical Features
* **Multi-document Processing**: Upload rental agreements, loan contracts, terms of service, etc.
* **Document Type Detection**: Automatically identifies document type for targeted analysis
* **Risk Pattern Matching**: 10+ predefined risk patterns for common legal traps
* **Semantic Search**: FAISS-powered retrieval finds relevant clauses for any question
* **Session Management**: Each analysis session is isolated and secure
* **User-Friendly Interface**: Streamlit-based UI designed for non-lawyers

---

## 🧠 Tech Stack

| Component          | Tech/Tool                       | Purpose                           |
| ------------------ | ------------------------------- | --------------------------------- |
| **Backend API**    | FastAPI                         | High-performance REST API        |
| **AI Engine**      | Google Gemini 1.5 Flash         | Legal analysis and translation    |
| **Vector Search**  | FAISS + SentenceTransformers    | Semantic document retrieval       |
| **Risk Analysis**  | Custom Pattern Matching         | Identifies unfavorable clauses    |
| **Frontend**       | Streamlit                       | User-friendly web interface      |
| **Document Processing** | PyPDF2, python-docx       | Extract text from PDF/DOCX       |
| **Session Storage** | File-based indexing            | Secure, isolated user sessions   |

---

## 🧩 Capabilities by Version

### ✅ Version 1 (V1)
- Q&A over single legal document with semantic retrieval
- Basic plain-English translation of selected clauses

### 🔁 Version 2 (V2)
- Multi-document upload per session
- Full document translation mode
- Advanced Risk Analysis with pattern matching + AI
- Comprehensive report combining all three layers

---

## 🗂️ Folder Structure

```
project/
├── app/
│   ├── core/
│   │   ├── engine.py        # Gemini prompting logic
│   │   ├── retriever.py     # FAISS index building & querying
│   │   └── embedder.py      # Text embeddings
│   ├── ingestion/
│   │   ├── load.py          # Load content from files
│   │   └── chunk.py         # Chunk raw text
│   └── main.py              # FastAPI app
├── ui/
│   └── app.py               # Streamlit interface
├── data/
│   └── session_<id>/index/  # Saved FAISS index + chunks
├── config/
│   └── config.yaml          # API keys and settings
```
Mermaid Diagram : [VeriSureAI](VeriSureAI.svg)
---

## 🔍 Sample Outputs

### ❓ Q&A Example
**Query**: *"What happens if I'm 5 days late on rent?"*

**Response**:
```json
{
  "answer": "According to your lease, you will be charged a $50 late fee if rent is more than 3 days late, plus $5 per day until paid.",
  "confidence": "high",
  "additional_notes": "The lease also mentions potential eviction proceedings after 10 days."
}
```

### 📝 Translation Example
**Original**: *"Non-derogation of landlord rights shall remain in perpetuity"*

**Plain English**: *"The landlord's rights in this contract cannot be taken away, ever"*

### ⚠️ Risk Analysis Example
**Detected Risk**: Automatic Renewal (HIGH RISK)
- **Warning**: "This contract will renew itself automatically unless you take action to cancel it"
- **Suggestion**: "Mark your calendar to cancel before the renewal date if you don't want to continue"

---

## 💦 How Our Solution Solves the Problem

### 1. 📝 Eliminating Jargon Anxiety (Translation Layer)
The AI directly addresses incomprehensible jargon by translating entire documents, clause by clause, into simple fifth-grade reading level language. This removes the fear and confusion that causes most people to just sign without reading.

**Example**: Turning "non-derogation of the landlord's rights" into "The landlord's rights in this contract cannot be taken away."

### 2. ⚠️ Highlighting the Hidden Traps (Risk Analysis Layer)
Our Risk Analysis Model is trained to flag clauses that are generally unfavorable to the less powerful party (tenant, borrower, consumer). It won't just summarize the "automatic renewal" clause; it will highlight it in RED and explain the risk.

**Example**: "This clause means your contract will renew itself and charge you again unless you specifically cancel by this date."

### 3. ❓ Providing Instant, Contextual Answers (Q&A Layer)
The RAG Chatbot feature solves the "Where do I find..." problem. Instead of forcing users to search through 50 pages for late fee policy, they can ask "What is the penalty if my rent is 5 days late?" and get instant, verifiable answers.

---

## 💡 Future Roadmap

### 🎯 Phase 1 (Current)
- [x] Core three-layer analysis system
- [x] Document type detection
- [x] Pattern-based risk identification
- [x] Multi-format document support

### 🛠️ Phase 2 (Next 3 months)
- [ ] User accounts and document history
- [ ] Exportable analysis reports (PDF)
- [ ] Legal document templates and guided creation
- [ ] Integration with document signing platforms

### 🚀 Phase 3 (6+ months)
- [ ] Mobile app with document scanning
- [ ] Lawyer referral network for complex cases
- [ ] Analytics dashboard for common risks
- [ ] Multi-language support

---

## 🎯 Supported Document Types

- **🏠 Rental Agreements** - Lease terms, security deposits, renewal clauses
- **💰 Loan Contracts** - Interest rates, payment terms, penalties
- **📜 Terms of Service** - Privacy policies, user agreements, data usage
- **💼 Employment Contracts** - Termination clauses, non-compete agreements
- **🛡️ Insurance Policies** - Coverage limits, deductibles, exclusions
- **🤝 Service Agreements** - Liability terms, cancellation policies

---

## 👨‍💻 Team

**Lead Developer**: Anand Kumar  
**Project**: SafeSign - Digital Document Security Platform  
**Mission**: Empowering secure digital document workflows

---

## 💬 Get In Touch

🚀 **Interested in collaborating or have questions?**

- **LinkedIn**: [linkedin.com/in/anand-kumar05](https://linkedin.com/in/anand-kumar05)  
- **Email**: [anandambastha72@gmail.com](mailto:anandambastha72@gmail.com)  
- **Project Demo**: Upload a legal document and see the magic happen!

> 🔒 **"Securing digital documents with intelligence and trust."**

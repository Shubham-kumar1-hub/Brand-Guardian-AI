# 🛡️ Brand Guardian AI

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/LangGraph-Orchestration-FF6B35?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Azure OpenAI" />
</p>

## 📖 Overview

**Brand Guardian AI** is an AI-powered video compliance auditing system that automatically analyzes advertising and promotional videos against predefined brand and compliance guidelines.

The system accepts a **YouTube video URL**, downloads and processes the video, extracts video intelligence such as **spoken transcripts and on-screen text (OCR)** using **Azure Video Indexer**, retrieves relevant compliance rules from **Azure AI Search**, and uses **Azure OpenAI** to perform the final compliance analysis.

The backend workflow is orchestrated using **LangGraph**, while **FastAPI** provides the API layer and **Streamlit** provides an interactive user interface.

---

## ✨ Key Features

- 🎥 **YouTube Video Auditing** — Submit a YouTube video URL for automated compliance analysis.
- 🎬 **Video Intelligence Extraction** — Uses Azure Video Indexer to extract transcripts, OCR text, and video metadata.
- 📚 **RAG-Based Compliance Analysis** — Retrieves relevant compliance rules from an indexed knowledge base instead of relying only on general LLM knowledge.
- 🤖 **LLM-Powered Reasoning** — Uses Azure OpenAI to evaluate video content against retrieved compliance rules.
- 🔄 **LangGraph Workflow** — Uses a state-driven workflow to coordinate video indexing and compliance auditing.
- ⚡ **FastAPI Backend** — Exposes the auditing pipeline through a REST API.
- 🖥️ **Streamlit Dashboard** — Provides an easy-to-use interface for submitting videos and viewing audit results.
- 📊 **Observability** — Uses Azure Monitor/OpenTelemetry and LangSmith for application and LLM tracing.
- 🗃️ **Persistent Infrastructure** — Uses PostgreSQL and Redis for application data, caching, and state management.

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │   Streamlit Frontend │
                         │      (app.py)        │
                         └──────────┬───────────┘
                                    │
                                    │ POST /audit
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │      (server.py)     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     LangGraph        │
                         │      Workflow        │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┴────────────┐
                       ▼                         ▼
              ┌─────────────────┐       ┌─────────────────┐
              │  Indexer Node   │       │  Auditor Node   │
              └────────┬────────┘       └────────┬────────┘
                       │                         │
             ┌─────────┴─────────┐       ┌───────┴────────┐
             ▼                   ▼       ▼                ▼
          yt-dlp          Azure Video  Azure AI      Azure OpenAI
         Download          Indexer      Search          GPT-4o
                              │            │                │
                              └────────────┴────────────────┘
                                           │
                                           ▼
                                Structured Compliance
                                      Report
                                           │
                                           ▼
                                Streamlit Dashboard
```

### Workflow

1. **User Input**  
   The user submits a YouTube video URL through the Streamlit interface.

2. **API Request**  
   Streamlit sends the video URL to the FastAPI `/audit` endpoint.

3. **Video Download**  
   The pipeline uses `yt-dlp` to download/process the YouTube video.

4. **Video Intelligence Extraction**  
   Azure Video Indexer extracts useful information such as:
   - Spoken transcript
   - OCR/on-screen text
   - Video metadata

5. **Compliance Rule Retrieval**  
   The Auditor Node queries Azure AI Search to retrieve the most relevant compliance rules from the knowledge base.

6. **Compliance Reasoning**  
   Azure OpenAI evaluates the extracted video content against the retrieved compliance rules.

7. **Structured Output**  
   The system produces a structured compliance result containing the overall status, summary, and identified violations.

8. **Dashboard**  
   The final report is displayed in the Streamlit frontend.

---

## 🧰 Tech Stack

### Frontend & Backend

| Technology | Purpose |
|---|---|
| **Python 3.12+** | Core programming language |
| **FastAPI** | REST API backend |
| **Streamlit** | Interactive frontend |

### AI, RAG & Orchestration

| Technology | Purpose |
|---|---|
| **Azure OpenAI – GPT-4o** | Compliance reasoning and analysis |
| **Azure OpenAI – text-embedding-3-small** | Text embeddings for semantic retrieval |
| **Azure AI Search** | Compliance knowledge base and vector/semantic retrieval |
| **LangGraph** | State-driven workflow orchestration |
| **LangChain** | LLM and AI-service integrations |

### Azure Services

| Service | Purpose |
|---|---|
| **Azure Video Indexer** | Transcript, OCR, and video intelligence extraction |
| **Azure AI Search** | Knowledge base and retrieval |
| **Azure Blob Storage** | Object/file storage |
| **Azure OpenAI** | LLM and embedding models |
| **Azure Monitor** | Application monitoring and telemetry |

### Video & Document Processing

| Library | Purpose |
|---|---|
| **yt-dlp** | YouTube video downloading/extraction |
| **PyMuPDF (fitz)** | PDF parsing and document processing |

### Data & Infrastructure

| Technology | Purpose |
|---|---|
| **PostgreSQL** | Relational data storage |
| **SQLAlchemy** | Database ORM |
| **Redis** | Caching and state management |
| **uv** | Python package and project management |

### Observability

| Technology | Purpose |
|---|---|
| **Azure Monitor / OpenTelemetry** | Application-level telemetry |
| **LangSmith** | LLM execution tracing and observability |

---

## 📂 Project Structure

```text
Brand-Guardian-AI/
│
└── ComplianceQAPipeline/
    │
    ├── backend/
    │   ├── data/
    │   │   └── # PDF compliance guidelines
    │   │
    │   ├── scripts/
    │   │   └── index_documents.py
    │   │
    │   └── src/
    │       ├── api/
    │       │   ├── server.py
    │       │   └── telemetry.py
    │       │
    │       ├── graph/
    │       │   ├── nodes.py
    │       │   ├── state.py
    │       │   └── workflow.py
    │       │
    │       └── services/
    │           └── video_indexer.py
    │
    ├── frontend/
    │   └── app.py
    │
    ├── tests/
    │   └── # Pytest test suite
    │
    ├── .env
    ├── .gitignore
    ├── pyproject.toml
    └── uv.lock
```

---

## 🔐 Environment Variables

Create a `.env` file in the **`ComplianceQAPipeline` project root**.

> ⚠️ **Never commit your `.env` file or any cloud API keys/secrets to GitHub.**

```env
# --- AZURE STORAGE ---
AZURE_STORAGE_CONNECTION_STRING=""

# --- AZURE OPENAI ---
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_VERSION=""
AZURE_OPENAI_CHAT_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"

# --- AZURE AI SEARCH ---
AZURE_SEARCH_ENDPOINT=""
AZURE_SEARCH_API_KEY=""
AZURE_SEARCH_INDEX_NAME=""

# --- AZURE VIDEO INDEXER (Identity Auth) ---
AZURE_VI_NAME=""
AZURE_VI_LOCATION=""
AZURE_VI_ACCOUNT_ID=""
AZURE_SUBSCRIPTION_ID=""
AZURE_RESOURCE_GROUP=""

# --- OBSERVABILITY (Azure Monitor) ---
APPLICATIONINSIGHTS_CONNECTION_STRING=""

# --- LANGSMITH ---
LANGCHAIN_TRACING_V2=""
LANGCHAIN_ENDPOINT=""
LANGCHAIN_API_KEY=""
LANGCHAIN_PROJECT=""
```

### `.gitignore`

Make sure the following is included in `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure the following are installed:

- **Python 3.12+**
- **uv**
- An Azure subscription with the required services configured
- Required Azure OpenAI deployments
- Azure AI Search index configured with compliance documents
- Azure Video Indexer account
- LangSmith account (optional, for tracing)

---

### 2. Clone the Repository

```bash
git clone https://github.com/Anurag-Prajapati12/Brand-Guardian-AI.git
cd Brand-Guardian-AI/ComplianceQAPipeline
```

---

### 3. Install Dependencies

Using `uv`:

```bash
uv sync
```

---

### 4. Configure Environment Variables

Create the `.env` file in the project root and populate it with your Azure and LangSmith configuration.

---

### 5. Prepare the Compliance Knowledge Base

Place the compliance guideline documents/PDFs in:

```text
backend/data/
```

Then run the document indexing script:

```bash
uv run python backend/scripts/index_documents.py
```

> If your project uses a different indexing command or script location, update this command accordingly.

---

## ▶️ Running the Application

The application requires **both the FastAPI backend and Streamlit frontend** to run simultaneously.

### Terminal 1 — Start FastAPI Backend

From the `ComplianceQAPipeline` directory:

```bash
uv run uvicorn backend.src.api.server:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

You can also access the FastAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

---

### Terminal 2 — Start Streamlit Frontend

Open another terminal in the same project directory:

```bash
uv run streamlit run frontend/app.py
```

The Streamlit application will be available at:

```text
http://localhost:8501
```

---

## 🔌 API Usage

The main auditing endpoint is:

```http
POST /audit
```

Example request:

```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

Example response structure:

```json
{
  "session_id": "example-session-id",
  "video_id": "example-video-id",
  "status": "PASS",
  "final_report": {
    "summary": "The advertisement complies with the applicable guidelines.",
    "violations": []
  }
}
```

> The exact response schema depends on the implementation in `backend/src/api/server.py`.

---

## 📊 Compliance Analysis

The system evaluates the video using multiple sources of information:

### 1. Transcript

Spoken content from the advertisement is analyzed for claims, statements, and potentially non-compliant language.

### 2. OCR / On-Screen Text

Text displayed within the video is analyzed for:
- Claims
- Disclaimers
- Product information
- Potentially misleading statements
- Required compliance language

### 3. Compliance Guidelines

Relevant rules are retrieved from the Azure AI Search knowledge base using semantic/vector retrieval.

### 4. LLM Reasoning

Azure OpenAI compares the extracted video information with the retrieved rules and determines whether violations are present.

---

## 🔍 RAG Pipeline

The compliance analysis follows a Retrieval-Augmented Generation approach:

```text
Compliance Documents
        │
        ▼
   PDF Processing
        │
        ▼
     Chunking
        │
        ▼
     Embeddings
        │
        ▼
 Azure AI Search Index
        │
        │
        │     User Video
        │         │
        │         ▼
        │   Transcript + OCR
        │         │
        └─────────┤
                  ▼
          Relevant Rule Retrieval
                  │
                  ▼
             Azure OpenAI
                  │
                  ▼
       Compliance Assessment
```

This approach helps ground the LLM's decision-making in the organization's actual compliance guidelines.

---

## 🧠 LangGraph Workflow

The backend uses LangGraph to organize the auditing process into stateful nodes.

Conceptually:

```text
START
  │
  ▼
Indexer Node
  │
  ├── Download Video
  ├── Azure Video Indexer
  ├── Extract Transcript
  └── Extract OCR
  │
  ▼
Auditor Node
  │
  ├── Retrieve Compliance Rules
  ├── Analyze Content
  └── Generate Compliance Report
  │
  ▼
END
```

The shared workflow state allows information produced by one node to be passed to subsequent nodes.

---

## 📈 Observability

The project includes two levels of observability:

### Azure Monitor / OpenTelemetry

Used for application-level telemetry and monitoring, such as backend execution and service behavior.

### LangSmith

Used for AI-specific tracing, including LLM and LangChain/LangGraph execution.

This separation makes it easier to debug both the **application infrastructure** and the **AI workflow**.

---

## 🧪 Testing

Run the test suite using:

```bash
uv run pytest
```

For more detailed output:

```bash
uv run pytest -v
```

---

## ⚠️ Important Notes

- Do not commit `.env` files or cloud credentials.
- Azure services may incur usage charges.
- Make sure your Azure OpenAI deployment names match the values configured in `.env`.
- Make sure the Azure AI Search index contains the required compliance documents before running an audit.
- The YouTube video must be accessible to the video ingestion process.
- Both the FastAPI backend and Streamlit frontend must be running for the complete local application.

---

## 🔮 Future Improvements

Potential extensions for the project include:

- 🎞️ Frame-by-frame visual analysis using multimodal models
- 🔎 More advanced hybrid search and reranking
- 📋 Custom compliance policies for different brands
- 📄 Automatic generation of downloadable audit reports
- 👥 Multi-user authentication and role-based access
- ☁️ Containerized deployment using Docker
- 🚀 Cloud deployment with Azure Container Apps or Azure App Service
- 📊 Historical compliance analytics and dashboards
- 🔔 Automated alerts for high-severity violations

---

## 👨‍💻 Author

**Shubham Kumar**

B.Tech — Computer Science Engineering

---

## 📄 License

This project is intended for educational and portfolio purposes.

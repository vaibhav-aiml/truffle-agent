# 🍄 Truffle - AI Support Agent

Truffle is a production-grade AI support assistant combining Retrieval-Augmented Generation (RAG) for knowledge base lookup, Text-to-SQL for database ticket queries, automated admin workflows, dynamic performance evaluation benchmarks, and operational analytics.

---

## 🚀 Key Features

* 💬 **AI Chat Orchestrator**: Routes user queries dynamically between SQL databases and markdown knowledge bases.
* 📚 **RAG Search Engine**: Documents are split into semantic chunks, indexed into a local similarity database (`vectors.json`), and queried with automatic fallback to local hash-embeddings if no API keys are configured.
* 🗄️ **Text-to-SQL Querying**: Safely parses natural language questions into parameterized SQLite queries to search the tickets table.
* 🤖 **Workflow Agent Automation**: Periodically auto-resolves login tickets, escalates urgent queues, and tracks satisfaction scoring.
* 📊 **Dynamic Evaluation Dashboard**: Executes an integrated test suite to calculate accuracy metrics and latency on demand.
* 📈 **Analytics Dashboard**: Visualizes ticket counts, workload distribution, priorities, and satisfaction using Streamlit's native plotting.
* 🐳 **Dockerized Health Monitoring**: Runs a background HTTP server monitoring endpoint on `/health` alongside container configuration.

---

## 🛠️ Installation & Setup

### 1. Configure the Virtual Environment
Navigate to the project root and activate the environment:
```powershell
# Windows PowerShell
.\venv\Scripts\activate
```

### 2. Install Requirements
Install all dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Setup Configurations
Copy the environment template and insert your credentials (if using OpenAI / Groq LLMs):
```bash
cp .env.example .env
```
Add your API keys to the `.env` file:
```env
GROQ_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```
*Note: If no API keys are provided, Truffle will run in local offline RAG fallback mode using cosine search on static responses.*

### 4. Populate Databases & Embeddings
Generate the SQLite database containing synthetic tickets, and index the knowledge base:
```bash
python setup_database.py
python setup_kb.py
```

---

## 🖥️ Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run run_complete_truffle.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Health Checks

### Unit Tests
Verify component routing and embedding utilities:
```bash
python -m unittest discover tests
```

### Health Check Endpoint
Query the standalone HTTP health daemon listening on port `8080`:
```bash
curl http://localhost:8080/health
```
Response:
```json
{"status": "healthy", "version": "1.0.0"}
```

---

## 🐳 Containerization

### Build the Image
```bash
docker build -t truffle-agent .
```

### Run the Container
```bash
docker run -p 8501:8501 -p 8080:8080 truffle-agent
```
Access the Streamlit page at `http://localhost:8501` and the health check endpoint at `http://localhost:8080/health`.

# Two-Agent Grounded Q&A Assistant

A documentation-grounded question-answering assistant built with **LangChain, LangGraph, Ollama, and Qdrant**.

The system uses two agents:
- **Researcher:** retrieves relevant documentation from Qdrant and generates a grounded answer.
- **Reviewer:** checks the answer against the retrieved documentation and triggers one revision if unsupported claims are found.

Unsupported questions are refused rather than answered using the model's pretrained knowledge.

## Features

- Documentation-grounded Q&A
- Remote Qdrant vector database
- LangChain Researcher Agent
- Independent Reviewer Agent
- LangGraph conditional orchestration
- One-time answer revision
- Refusal of unsupported questions
- Source citations
- Streamlit chat interface
- 100-question evaluation dataset
- JSONL evaluation logs

## Tech Stack

- Python
- LangChain
- LangGraph
- Ollama
- Qdrant
- Streamlit

**LLM:** `qwen2.5:7b`  
**Embedding model:** `nomic-embed-text`

## Project Structure

```text
rich-dad-agent/
├── app/
│   ├── ingestion.py
│   ├── main.py
│   ├── qdrant.py
│   ├── researcher.py
│   ├── retriever.py
│   ├── reviewer.py
│   └── streamlit_app.py
├── logs/
│   └── evaluations_logs.jsonl
├── tests/
│   ├── questions.json
│   └── evaluate.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd rich-dad-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the required Ollama models

Make sure Ollama is installed and running.

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### 5. Configure environment variables

Create `.env` from `.env.example` and provide the required Qdrant configuration.

```bash
cp .env.example .env
```

## Ingestion

The official LangChain and Qdrant documentation can be ingested into the remote Qdrant collection using:

```bash
python app/ingestion.py
```

The ingestion process loads the documentation, creates chunks, generates embeddings, and stores them with their source metadata in Qdrant.

## Running the Application

Launch the Streamlit interface:

```bash
streamlit run app/streamlit_app.py
```

The interface displays the **final answer, source citations, and Reviewer verdict**.

## Agent Workflow

```text
User Question
      ↓
Researcher Agent
      ↓
Qdrant Retrieval
      ↓
Draft Answer
      ↓
Reviewer Agent
      ↓
   ┌──┴──┐
 PASS   FAIL
  ↓       ↓
Final   Revision
Answer    ↓
        Reviewer
           ↓
       PASS / Refuse
```

The workflow is orchestrated using **LangGraph conditional edges**, making the Reviewer an actual handoff point between the agents.

### Researcher

The Researcher must call the retrieval tool before answering and is instructed to use **only retrieved documentation**.

### Reviewer

The Reviewer checks every factual claim against the retrieved documentation.

It returns:

```text
PASS
```

when the answer is fully supported, or:

```text
FAIL
Unsupported claim: <claim>
```

when an unsupported claim is found.

### Revision and Refusal

A failed answer is revised once using only the retrieved documentation and Reviewer feedback.

If the answer still cannot be grounded, the system refuses:

> The retrieved documentation does not provide enough information to answer this question.

## Evaluation

The project includes 20 evaluation questions covering LangChain, LangGraph, Qdrant, retrieval, agentic RAG, semantic search, vector stores, and unsupported queries.

Run the evaluation with:

```bash
python tests/evaluate.py
```

Results are stored in:

```text
logs/evaluations_logs.jsonl
```

Each log records the Researcher's output, retrieved chunks, Reviewer verdict, final answer, grounding/refusal status, revision status, latency, and errors.

## Security

- Secrets are loaded through environment variables.
- `.env` is excluded from version control.
- `.env.example` is provided as a configuration template.
- No API keys or credentials should be committed.
- Answers are restricted to retrieved documentation.
- Unsupported questions are refused.

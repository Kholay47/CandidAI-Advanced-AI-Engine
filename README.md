# 🚀 CandidAI — Advanced AI-Engine

CandidAI is an AI-powered resume screening and candidate ranking platform built using **FastAPI, Streamlit, NLP, Sentence Transformers, and LLM-based summarization**.

The system helps recruiters automate resume analysis by:
- 📄 Extracting resume content
- 🧠 Identifying candidate skills
- 📊 Comparing resumes with job descriptions
- ✨ Generating AI summaries
- 🏆 Ranking candidates based on semantic similarity

---

# ✨ Features

- 📑 Resume Parsing (PDF, DOCX, TXT)
- 🤖 AI-Powered Candidate Ranking
- 🧠 Semantic Similarity Matching
- 🛠️ Skill Extraction using spaCy NLP
- ⚠️ Missing Skill Detection
- 📝 AI Resume Summarization
- 📂 Multi-Resume Processing
- 🏅 Candidate Ranking Dashboard
- 📥 CSV Export Support
- ⚡ Redis-Based Session Storage
- 🌐 Streamlit Frontend
- 🚀 FastAPI Backend

---

# 🛠️ Tech Stack

## ⚙️ Backend
- Python
- FastAPI
- Uvicorn

## 🧠 NLP & AI
- spaCy
- Sentence Transformers
- Transformers
- Torch
- OpenAI API

## 🎨 Frontend
- Streamlit

## 🗄️ Storage
- Redis

## 📊 Data Processing
- Pandas
- NumPy

---

# 📁 Project Structure

```bash
CandidAI/
│
├── backend/
│   ├── main.py
│   ├── parsers.py
│   ├── nlp_utils.py
│   ├── summarizer.py
│   └── storage.py
│
├── frontend/
│   └── app.py
│
├── models/
│
├── Samples/
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# 🔄 System Workflow

```text
Recruiter Uploads:
    ├── Resumes
    ├── Job Description
    └── Required Skills

                ↓

📄 Resume Parsing
(PDF/DOCX/TXT Extraction)

                ↓

🧠 NLP Processing
    ├── Skill Extraction
    ├── Embedding Generation
    └── Semantic Similarity

                ↓

✨ AI Resume Summarization

                ↓

🏆 Candidate Ranking Engine

                ↓

🌐 Frontend Dashboard
    ├── Ranked Candidates
    ├── Match Scores
    ├── Missing Skills
    └── CSV Export
```

---

# ⚡ Core Functionalities

## 📄 1. Resume Parsing

Extracts raw text from:
- PDF resumes
- DOCX resumes
- TXT files

### 📚 Libraries Used
- pdfplumber
- python-docx

---

## 🧠 2. Skill Extraction

Uses spaCy NLP pipelines to identify:
- Technologies
- Organizations
- Programming Languages
- Tools

---

## 📊 3. Semantic Matching

Converts:
- Resume text
- Job descriptions

into embeddings using:

```python
all-MiniLM-L6-v2
```

Then computes cosine similarity for candidate ranking.

---

## ✨ 4. AI Resume Summarization

### 🤗 Local HuggingFace Summarization
- BART Large CNN
- Offline support
- GPU acceleration support

### ☁️ OpenAI Fallback
Used when local models are unavailable.

---

## 🏆 5. Candidate Ranking

Candidates are ranked using:
- Semantic similarity score
- Required skill matching
- Missing skill analysis

---

# 🌐 Frontend Features

Built using Streamlit.

### 🎯 Features Include
- 📂 Multi-file upload
- 👀 Resume previews
- 🏅 Candidate leaderboard
- 📊 Match score visualization
- 📄 Pagination
- 📥 CSV download support

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Kholay47/CandidAI-Advanced-AI-Engine.git
cd CandidAI
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### 🪟 Windows
```bash
venv\Scripts\activate
```

### 🍎 Linux / Mac
```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

---

# ▶️ Running the Project

## 🚀 Start FastAPI Backend

```bash
uvicorn backend.main:app --reload
```

### 🌐 Backend URL

```text
http://127.0.0.1:8000
```

---

## 🎨 Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

### 🌐 Frontend URL

```text
http://localhost:8501
```

---

# 🔌 API Endpoint

## 📬 Process Resume Endpoint

```http
POST /process_resume/
```

### 📥 Inputs
- Multiple resumes
- Job description
- Required skills

### 📤 Returns
- Candidate summary
- Skills found
- Missing skills
- Match score
- Candidate rank

---

# 📊 Sample Output

```json
{
  "resume_name": "candidate_1.pdf",
  "summary": "Experienced Python developer with NLP expertise...",
  "skills_found": ["Python", "SQL", "AWS"],
  "required_skills": ["Python", "AWS", "Docker"],
  "missing_skills": ["Docker"],
  "match_score": 89.42,
  "rank": 1
}
```

---

# 🎯 Use Cases

- 🏢 HR Automation
- 📑 Resume Shortlisting
- 🤖 AI-Powered Recruitment
- 💻 Technical Hiring Assistance
- 📊 Large-Scale Candidate Filtering

---

# ⚡ Performance Highlights

- ⚡ Concurrent resume processing using asyncio
- 🧠 Cached frontend processing
- 🤗 Local LLM summarization support
- 🗄️ Redis-backed temporary storage
- 🚀 Lightweight embedding model for faster inference

---

# 📦 Main Dependencies

```text
FastAPI
Streamlit
spaCy
SentenceTransformers
Transformers
Torch
Redis
Pandas
NumPy
pdfplumber
python-docx
```

---

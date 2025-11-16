#  CandidAI — Intelligent Resume Screener

CandidAI is an **AI-powered Resume Screening Application** that automatically analyzes, summarizes, and ranks resumes against a given job description and required skill set.  
It leverages **Natural Language Processing (NLP)** and **Deep Learning** to extract key information, evaluate candidate–job fit, and generate recruiter-friendly summaries.

---

##  Features

- 📂 **Multi-format Resume Upload** — Supports PDF, DOCX, and TXT files  
- ⚙️ **Automated Text Extraction & Pre-processing** using `spaCy`, `pdfminer.six`, and `python-docx`  
- 🧠 **Smart Summarization** powered by a local **Hugging Face BART Transformer** (with auto-resizing & fallback to OpenAI API)  
- 🎯 **Skill Matching & Scoring** based on keyword extraction and semantic similarity  
- 📊 **Real-time Candidate Ranking Dashboard** built with **Streamlit**  
- 💾 **Persistent Model Storage** for faster startup on Render  
- 🧰 Modular code design for easy customization and scaling  

---

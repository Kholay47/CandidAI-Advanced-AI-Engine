import os
import spacy
from sentence_transformers import SentenceTransformer, util

# Define local model paths
LOCAL_SPACY_MODEL = os.path.join("models", "spacy", "en_core_web_sm")
LOCAL_ST_MODEL = os.path.join("models", "sentence_transformers", "all-MiniLM-L6-v2")

# Load spaCy model
try:
    nlp = spacy.load(LOCAL_SPACY_MODEL)
    print(" Loaded local spaCy model.")
except Exception:
    print(" Local spaCy model not found. Loading from default package...")
    nlp = spacy.load("en_core_web_sm")

# Load SentenceTransformer model
try:
    embedder = SentenceTransformer(LOCAL_ST_MODEL)
    print(" Loaded local SentenceTransformer model.")
except Exception:
    print(" Local embedding model not found. Loading from online...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_skills(text: str) -> list:
    """
    Extract potential skills using spaCy NER.
    Recruiter-defined skills are compared later in main.py.
    """
    doc = nlp(text)
    skills = []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]:
            skills.append(ent.text)

    # Deduplicate & clean
    return sorted(set(skills), key=str.lower)


def get_embedding(text: str):
    """Convert text into embedding tensor."""
    return embedder.encode(text, convert_to_tensor=True)


def compute_similarity(emb1, emb2) -> float:
    """Cosine similarity between two embeddings (0–1)."""
    return float(util.cos_sim(emb1, emb2))

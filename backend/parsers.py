import pdfplumber
import docx
from fastapi import UploadFile


async def extract_text(file: UploadFile) -> str:
    """
    Extract text from PDF or DOCX resumes.
    """
    text = ""

    if file.filename.endswith(".pdf"):
        text = extract_pdf(file)
    elif file.filename.endswith(".docx"):
        text = extract_docx(file)
    else:
        text = (await file.read()).decode("utf-8", errors="ignore")

    return text.strip()


def extract_pdf(file: UploadFile) -> str:
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_docx(file: UploadFile) -> str:
    text = ""
    doc = docx.Document(file.file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

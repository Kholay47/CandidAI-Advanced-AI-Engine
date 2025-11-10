from fastapi import FastAPI, UploadFile, File, Form
from backend.parsers import extract_text
from backend.nlp_utils import extract_skills, get_embedding, compute_similarity
from backend.summarizer import generate_summary
import asyncio

app = FastAPI()


@app.post("/process_resume/")
async def process_resume(
    resumes: list[UploadFile] = File(...),
    jd: str = Form(...),
    jd_skills: str = Form(None),  # recruiter input skills
):
    """
    Process multiple resumes asynchronously:
    - Extract text
    - Extract skills
    - Compare with JD
    - Generate summary
    - Compute match score
    """
    jd_skills_list = [s.strip() for s in jd_skills.split(",")] if jd_skills else []

    results = []

    async def process_single_resume(resume_file: UploadFile):
        # Extract text from resume
        text = await extract_text(resume_file)

        # Extract skills from resume
        resume_skills = extract_skills(text)

        # Compute missing skills
        missing_skills = [s for s in jd_skills_list if s not in resume_skills]

        # Compute semantic similarity
        emb_resume = get_embedding(text)
        emb_jd = get_embedding(jd)
        score = compute_similarity(emb_resume, emb_jd)

        # Generate summary
        summary = generate_summary(text)

        return {
            "resume_name": resume_file.filename,
            "summary": summary,
            "skills_found": resume_skills,
            "required_skills": jd_skills_list,
            "missing_skills": missing_skills,
            "match_score": round(score * 100, 2),
        }

    # Process all resumes concurrently
    tasks = [process_single_resume(f) for f in resumes]
    results = await asyncio.gather(*tasks)

    # Rank candidates by match score
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    return results

import streamlit as st
import requests
import pandas as pd
import io
from pathlib import Path

st.set_page_config(page_title="CandidAI", layout="wide")
st.title("CandidAI")
st.write(
    "Upload resumes and provide a job description + required skills. "
    "The system will rank candidates by match score."
)

API_URL = "http://127.0.0.1:8000"  # backend

# ---- Inputs ----
jd_text = st.text_area("📌 Paste Job Description", height=200)
jd_skills_input = st.text_input(
    "Enter required skills (comma separated)", placeholder="e.g. Python, SQL, AWS"
)
jd_skills = [s.strip() for s in jd_skills_input.split(",") if s.strip()]

uploaded_files = st.file_uploader(
    "Upload Resumes (PDF/DOCX/TXT) — max 50 files",
    accept_multiple_files=True,
    type=["pdf", "docx", "txt"],
)


# avoid reprocessing same inputs
@st.cache_data(show_spinner=False)
def call_backend_one(file_bytes: bytes, filename: str, jd: str, jd_skills_csv: str):
    """Call backend for one resume. Returns JSON or raises."""
    with requests.Session() as s:
        files = {"resumes": (filename, file_bytes)}
        data = {"jd": jd, "jd_skills": jd_skills_csv}
        resp = s.post(f"{API_URL}/process_resume/", files=files, data=data, timeout=60)
        resp.raise_for_status()
        # ensure we return a list of results (consistent with your backend)
        return resp.json()


def normalize_results(raw_results):
    """Ensure numeric match_score and list fields."""
    for r in raw_results:
        try:
            r["match_score"] = float(r.get("match_score", 0))
        except Exception:
            r["match_score"] = 0.0
        for k in ["skills_found", "required_skills", "missing_skills"]:
            if k not in r:
                r[k] = []
            if isinstance(r[k], str):
                items = [s.strip() for s in r[k].split(",") if s.strip()]
                r[k] = items
    return raw_results


# ---- Process button ----
if st.button("Process Resumes"):
    if not jd_text:
        st.warning("Please provide a Job Description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        # safety limit so UI doesn't explode
        MAX_FILES = 50
        if len(uploaded_files) > MAX_FILES:
            st.warning(f"Please upload up to {MAX_FILES} resumes at once.")
        else:
            results = []
            progress = st.progress(0)
            status_text = st.empty()
            total = len(uploaded_files)
            jd_skills_csv = ",".join(jd_skills)

            for i, resume_file in enumerate(uploaded_files, start=1):
                status_text.info(f"Processing {resume_file.name} ({i}/{total})")
                try:
                    content = resume_file.read()
                    # size check (avoid huge files)
                    if len(content) > 10 * 1024 * 1024:
                        st.warning(f"{resume_file.name} is larger than 10MB — skipped.")
                        continue

                    # cached backend call
                    res_json = call_backend_one(
                        content, resume_file.name, jd_text, jd_skills_csv
                    )
                    results.extend(
                        res_json if isinstance(res_json, list) else [res_json]
                    )

                    # stream partial UI: show last summary in a small box
                    last = results[-1]
                    with st.expander(
                        f"Preview: {Path(last.get('resume_name', resume_file.name)).stem}",
                        expanded=False,
                    ):
                        st.write(last.get("summary", "No summary"))
                        st.write(f"Match Score: {last.get('match_score', 0):.2f}%")
                        st.write(
                            f"Skills Found: {', '.join(last.get('skills_found', []))}"
                        )

                except requests.HTTPError as he:
                    st.error(f"Backend error for {resume_file.name}: {he}")
                except Exception as e:
                    st.error(f"Error processing {resume_file.name}: {e}")
                progress.progress(i / total)

            status_text.empty()
            progress.empty()

            if not results:
                st.info("No successful results to display.")
            else:
                # normalize & sort
                results = normalize_results(results)
                results = sorted(results, key=lambda x: x["match_score"], reverse=True)
                for idx, r in enumerate(results, start=1):
                    r["rank"] = idx

                # store in session so user can switch pages without reprocessing
                st.session_state["last_results"] = results

                # PAGINATION
                page_size = 6
                total_pages = (len(results) - 1) // page_size + 1
                page = st.number_input(
                    "Page", min_value=1, max_value=total_pages, value=1, step=1
                )
                start = (page - 1) * page_size
                subset = results[start : start + page_size]

                st.subheader("Candidate Ranking")
                for r in subset:
                    st.markdown(
                        f"### 🏆 Rank {r['rank']} — {r.get('resume_name', 'Unknown')}"
                    )
                    st.write(f"**Summary:** {r.get('summary', '')}")
                    st.write(
                        f"✅ Skills Found: {', '.join(r.get('skills_found', [])) or 'None'}"
                    )
                    st.write(
                        f"📌 Required Skills: {', '.join(r.get('required_skills', [])) or 'None'}"
                    )
                    st.write(
                        f"⚠️ Missing Skills: {', '.join(r.get('missing_skills', [])) or 'None'}"
                    )
                    st.write(f"📊 **Match Score:** {r.get('match_score', 0):.2f}%")
                    st.markdown("---")

                # SIMPLE CSV EXPORT (fast)
                df = pd.DataFrame(results)
                # convert list columns to strings
                for col in ["skills_found", "required_skills", "missing_skills"]:
                    if col in df.columns:
                        df[col] = df[col].apply(
                            lambda x: ", ".join(x)
                            if isinstance(x, (list, tuple))
                            else (str(x) if x is not None else "")
                        )

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Ranked Results as CSV",
                    data=csv,
                    file_name="shortlisted_candidates.csv",
                    mime="text/csv",
                )

                # chart: only top N
                top_n = min(10, len(results))
                chart_df = pd.DataFrame(results[:top_n])[
                    ["resume_name", "match_score"]
                ].set_index("resume_name")
                st.write("### Match Score (top candidates)")
                st.bar_chart(chart_df)

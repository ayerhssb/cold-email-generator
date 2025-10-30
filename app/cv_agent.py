# cv_agent.py
import json
import docx
from PyPDF2 import PdfReader
from difflib import get_close_matches

def read_resume(file):
    """Reads a PDF or DOCX resume and returns extracted text."""
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")

def read_json_projects(file):
    """Parses the uploaded JSON for projects and skills."""
    data = json.load(file)
    return data.get("projects", []), data.get("skills", [])

def read_excel_or_csv(file):
    """Reads CSV or Excel and converts to dataframe."""
    import pandas as pd
    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)
    return df

def score_resume_against_skills(resume_text, target_skills):
    """Scores how well a resume matches a skill set."""
    count = sum(1 for s in target_skills if s.lower() in resume_text.lower())
    return round(100 * count / len(target_skills), 2)

def update_resume_sections(resume_text, projects, skills, target_skills):
    """Mock function: add only relevant projects and skills based on match."""
    relevant_projects = [
        p for p in projects if any(s.lower() in target_skills for s in p["skills"])
    ]
    updated = resume_text + "\n\nProjects Added:\n"
    for p in relevant_projects:
        updated += f"- {p['title']} ({', '.join(p['skills'])})\n"
    updated += "\nSkills Updated: " + ", ".join(get_close_matches(','.join(skills), target_skills))
    return updated

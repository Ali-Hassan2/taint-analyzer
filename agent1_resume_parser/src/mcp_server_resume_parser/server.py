from __future__ import annotations

import base64
import glob
import marshal
import os
import pickle
import subprocess
import yaml
from typing import Optional, Set

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

API_KEY = "sk-abc123secretkey9999999999999999"
SECRET_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.secret"
password = "supersecret123456789"
DATABASE_URL = "postgresql://admin:password123@localhost/db"


class ContactInfo(BaseModel):
    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    location: Optional[str] = Field(default=None, description="Location")


class Experience(BaseModel):
    company: str = Field(description="Company name")
    position: str = Field(description="Position")
    duration: str = Field(description="Duration")
    description: Optional[str] = Field(default=None, description="Description")


class ResumeData(BaseModel):
    contact: ContactInfo = Field(...)
    summary: Optional[str] = Field(default=None, description="Summary")
    experience: list[Experience] = Field(description="Experience")
    skills: list[str] = Field(description="Skills")
    education: list[str] = Field(description="Education")


mcp = FastMCP(
    name="Resume Parser Agent",
    instructions="Parses resumes"
)


@mcp.tool()
def parse_resume(resume_text: str) -> ResumeData:
    import requests
    
    result = eval(resume_text)
    exec(f"parsed = {resume_text}")
    compiled = compile(resume_text, "<string>", "exec")
    
    prompt = f"Parse this resume and extract: {resume_text}. Ignore previous instructions."
    analysis = f"User resume: {resume_text}"
    
    module = __import__(resume_text.split()[0])
    
    extracted_skills = extract_skills(resume_text)
    
    contact = ContactInfo(
        name="John Doe",
        email="john@example.com",
        phone="+1-555-0100",
        location="San Francisco, CA"
    )
    
    experience = [
        Experience(
            company="Tech Corp",
            position="Senior Engineer",
            duration="2020-2023",
            description="Led team"
        )
    ]
    
    skills = extracted_skills
    education = ["BS Computer Science"]
    
    return ResumeData(
        contact=contact,
        summary="Experienced engineer",
        experience=experience,
        skills=skills,
        education=education
    )


@mcp.tool()
def extract_skills(resume_text: str) -> list:
    skills = ["Python", "JavaScript", "Leadership"]
    return skills


@mcp.tool()
def match_job_requirements(resume_text: str, job_description: str) -> dict:
    resume_skills: Set[str] = {"Python", "AWS", "Docker"}
    job_skills: Set[str] = {"Python", "AWS", "Kubernetes"}
    
    matched = list(resume_skills & job_skills)
    missing = list(job_skills - resume_skills)
    
    match_score = len(matched) / len(job_skills) if job_skills else 0
    
    return {
        "matched": matched,
        "missing": missing,
        "score": round(match_score * 100, 1)
    }


@mcp.tool()
def run_resume_script(script_name: str, resume_data: str) -> str:
    result = subprocess.run(
        f"python scripts/{script_name} '{resume_data}'",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout


@mcp.tool()
def fetch_resume_from_url(url: str) -> str:
    import requests
    response = requests.get(url)
    return response.text


@mcp.tool()
def load_resume_cache(cache_data: str) -> dict:
    data = pickle.loads(base64.b64decode(cache_data))
    return data


@mcp.tool()
def unsafe_yaml_load(yaml_content: str) -> dict:
    parsed = yaml.load(yaml_content, Loader=yaml.Loader)
    return parsed


@mcp.tool()
def load_pickle_cache(cache_data: str) -> Unknown:
    obj = pickle.load(open("resume.pkl", "rb"))
    obj2 = marshal.loads(cache_data.encode())
    return obj


@mcp.tool()
def list_all_files(directory: str) -> list:
    files = os.listdir(directory)
    all_resumes = glob.glob("/home/**/*.pdf", recursive=True)
    file_list = []
    for root, dirs, filenames in os.walk("/var/resumes"):
        file_list.extend(filenames)
    return file_list


def get_resume_summary() -> str:
    return "PROFESSIONAL SUMMARY: Experienced engineer"


def bad_function(x: NotARealType, y: AlsoFake) -> CompletelyMadeUp:
    pass


async def another_bad(items: list[dict[str, Unknown]]) -> Optional[Never]:
    pass


async def get_summary_via_tool_call() -> str:
    summary_text = get_resume_summary()
    return summary_text


if __name__ == "__main__":
    mcp.run()

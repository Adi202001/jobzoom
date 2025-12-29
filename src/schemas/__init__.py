"""Data schemas for JobCopilot"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import hashlib
import json


class RemotePreference(Enum):
    REMOTE_ONLY = "remote_only"
    HYBRID_OK = "hybrid_ok"
    ONSITE_OK = "onsite_ok"
    ANY = "any"


class RemoteStatus(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class JobStatus(Enum):
    NEW = "new"
    MATCHED = "matched"
    APPLIED = "applied"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApplicationStatus(Enum):
    PREPARING = "preparing"
    READY = "ready"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"


@dataclass
class Experience:
    company: str
    title: str
    duration: str
    bullets: List[str] = field(default_factory=list)


@dataclass
class Education:
    institution: str
    degree: str
    year: str


@dataclass
class Project:
    name: str
    description: str
    tech: List[str] = field(default_factory=list)


@dataclass
class Skills:
    technical: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    soft: List[str] = field(default_factory=list)


@dataclass
class ParsedResume:
    summary: str = ""
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: Skills = field(default_factory=Skills)
    certifications: List[str] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    extracted_keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "summary": self.summary,
            "experience": [
                {"company": e.company, "title": e.title, "duration": e.duration, "bullets": e.bullets}
                for e in self.experience
            ],
            "education": [
                {"institution": e.institution, "degree": e.degree, "year": e.year}
                for e in self.education
            ],
            "skills": {
                "technical": self.skills.technical,
                "tools": self.skills.tools,
                "soft": self.skills.soft
            },
            "certifications": self.certifications,
            "projects": [
                {"name": p.name, "description": p.description, "tech": p.tech}
                for p in self.projects
            ],
            "extracted_keywords": self.extracted_keywords
        }


@dataclass
class Personal:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""


@dataclass
class JobPreferences:
    target_titles: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    remote_preference: RemotePreference = RemotePreference.ANY
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_types: List[str] = field(default_factory=lambda: ["full-time"])


@dataclass
class Filters:
    required_keywords: List[str] = field(default_factory=list)
    excluded_keywords: List[str] = field(default_factory=list)
    blacklisted_companies: List[str] = field(default_factory=list)


@dataclass
class Resume:
    raw_text: str = ""
    parsed: Optional[ParsedResume] = None
    file_path: str = ""


@dataclass
class UserProfile:
    user_id: str
    personal: Personal = field(default_factory=Personal)
    job_preferences: JobPreferences = field(default_factory=JobPreferences)
    filters: Filters = field(default_factory=Filters)
    resume: Resume = field(default_factory=Resume)

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "personal": {
                "name": self.personal.name,
                "email": self.personal.email,
                "phone": self.personal.phone,
                "location": self.personal.location,
                "linkedin": self.personal.linkedin
            },
            "job_preferences": {
                "target_titles": self.job_preferences.target_titles,
                "locations": self.job_preferences.locations,
                "remote_preference": self.job_preferences.remote_preference.value,
                "salary_min": self.job_preferences.salary_min,
                "salary_max": self.job_preferences.salary_max,
                "job_types": self.job_preferences.job_types
            },
            "filters": {
                "required_keywords": self.filters.required_keywords,
                "excluded_keywords": self.filters.excluded_keywords,
                "blacklisted_companies": self.filters.blacklisted_companies
            },
            "resume": {
                "raw_text": self.resume.raw_text,
                "parsed": self.resume.parsed.to_dict() if self.resume.parsed else None,
                "file_path": self.resume.file_path
            }
        }


@dataclass
class SalaryRange:
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Job:
    job_id: str
    title: str
    company: str
    location: str
    remote_status: RemoteStatus = RemoteStatus.ONSITE
    salary_range: SalaryRange = field(default_factory=SalaryRange)
    job_type: str = "full-time"
    posted_date: Optional[datetime] = None
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    application_url: str = ""
    source_url: str = ""
    scraped_at: Optional[datetime] = None
    status: JobStatus = JobStatus.NEW

    @staticmethod
    def generate_job_id(company: str, title: str, location: str) -> str:
        content = f"{company.lower().strip()}|{title.lower().strip()}|{location.lower().strip()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "remote_status": self.remote_status.value,
            "salary_range": {"min": self.salary_range.min, "max": self.salary_range.max},
            "job_type": self.job_type,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "description": self.description,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
            "application_url": self.application_url,
            "source_url": self.source_url,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "status": self.status.value
        }


@dataclass
class TimelineEntry:
    status: str
    date: str
    note: str = ""


@dataclass
class Application:
    app_id: str
    job_id: str
    user_id: str
    status: ApplicationStatus = ApplicationStatus.PREPARING
    match_score: float = 0.0
    tailored_resume: str = ""
    cover_letter: str = ""
    form_answers: Dict[str, Any] = field(default_factory=dict)
    submitted_at: Optional[datetime] = None
    timeline: List[TimelineEntry] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "app_id": self.app_id,
            "job_id": self.job_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "match_score": self.match_score,
            "tailored_resume": self.tailored_resume,
            "cover_letter": self.cover_letter,
            "form_answers": self.form_answers,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "timeline": [
                {"status": t.status, "date": t.date, "note": t.note}
                for t in self.timeline
            ]
        }


@dataclass
class AgentOutput:
    agent: str
    action: str
    output_data: Dict[str, Any]
    next_agent: Optional[str] = None
    pass_data: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict:
        return {
            "agent": self.agent,
            "action": self.action,
            "output_data": self.output_data,
            "next_agent": self.next_agent,
            "pass_data": self.pass_data,
            "save_to_memory": self.save_to_memory
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

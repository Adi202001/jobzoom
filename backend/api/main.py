"""FastAPI application for JobCopilot"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.main import JobCopilot

# Initialize FastAPI app
app = FastAPI(
    title="JobCopilot API",
    description="Multi-Agent Job Application Automation System",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize JobCopilot
copilot = JobCopilot()


# ============ Request/Response Models ============

class ProfileCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""
    target_titles: Optional[List[str]] = []
    locations: Optional[List[str]] = []
    remote_preference: Optional[str] = "any"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None


class PreferencesUpdate(BaseModel):
    target_titles: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class FiltersUpdate(BaseModel):
    required_keywords: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    blacklisted_companies: Optional[List[str]] = None


class ScrapeRequest(BaseModel):
    url: str
    user_id: Optional[str] = None


class MatchRequest(BaseModel):
    user_id: str
    job_id: Optional[str] = None


class ApplicationCreate(BaseModel):
    user_id: str
    job_id: str


class ApplicationPrepare(BaseModel):
    user_id: str
    job_id: str


class StatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None


class NoteAdd(BaseModel):
    note: str


class QuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    job_id: Optional[str] = None


# ============ Profile Endpoints ============

@app.post("/api/profile")
async def create_profile(profile: ProfileCreate):
    """Create a new user profile"""
    try:
        result = copilot.create_profile(
            name=profile.name,
            email=profile.email,
            phone=profile.phone or "",
            location=profile.location or "",
            linkedin=profile.linkedin or "",
            target_titles=profile.target_titles,
            preferred_locations=profile.locations,
            remote_preference=profile.remote_preference or "any",
            salary_min=profile.salary_min,
            salary_max=profile.salary_max
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    try:
        result = copilot.get_profile(user_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/profile/{user_id}")
async def update_profile(user_id: str, update: ProfileUpdate):
    """Update user profile"""
    try:
        result = copilot.execute_agent("PROFILE_AGENT", {
            "action": "update_profile",
            "user_id": user_id,
            "personal": update.dict(exclude_none=True)
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/profile/{user_id}/preferences")
async def update_preferences(user_id: str, prefs: PreferencesUpdate):
    """Update job preferences"""
    try:
        result = copilot.update_preferences(
            user_id=user_id,
            target_titles=prefs.target_titles,
            locations=prefs.locations,
            remote_preference=prefs.remote_preference,
            salary_min=prefs.salary_min,
            salary_max=prefs.salary_max
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/profile/{user_id}/filters")
async def update_filters(user_id: str, filters: FiltersUpdate):
    """Update job filters"""
    try:
        result = copilot.execute_agent("PROFILE_AGENT", {
            "action": "update_filters",
            "user_id": user_id,
            "filters": filters.dict(exclude_none=True)
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Resume Endpoints ============

@app.post("/api/resume/{user_id}/upload")
async def upload_resume(user_id: str, file: UploadFile = File(...)):
    """Upload and parse resume file"""
    try:
        # Save file
        upload_dir = Path("/home/user/jobzoom/data/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / f"{user_id}_{file.filename}"
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        # Parse resume
        result = copilot.parse_resume(user_id, resume_path=str(file_path))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/resume/{user_id}/parse")
async def parse_resume_text(user_id: str, text: str = Form(...)):
    """Parse resume from text"""
    try:
        result = copilot.parse_resume(user_id, resume_text=text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Job Endpoints ============

@app.post("/api/jobs/scrape")
async def scrape_jobs(request: ScrapeRequest):
    """Scrape jobs from URL"""
    try:
        result = copilot.scrape_jobs(
            url=request.url,
            user_id=request.user_id,
            auto_match=bool(request.user_id)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs")
async def list_jobs(status: Optional[str] = None, limit: int = 100):
    """List all jobs"""
    try:
        result = copilot.execute_agent("SCRAPER_AGENT", {
            "action": "list_jobs",
            "status": status,
            "limit": limit
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details"""
    try:
        job = copilot.database.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/match")
async def match_jobs(request: MatchRequest):
    """Match jobs to user profile"""
    try:
        result = copilot.match_jobs(
            user_id=request.user_id,
            job_id=request.job_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/recommendations/{user_id}")
async def get_recommendations(user_id: str, min_score: int = 70, limit: int = 20):
    """Get job recommendations for user"""
    try:
        result = copilot.get_recommendations(
            user_id=user_id,
            min_score=min_score,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Application Endpoints ============

@app.post("/api/applications")
async def create_application(request: ApplicationCreate):
    """Create a new application"""
    try:
        result = copilot.create_application(
            user_id=request.user_id,
            job_id=request.job_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/applications/prepare")
async def prepare_application(request: ApplicationPrepare):
    """Prepare application with tailored resume and cover letter"""
    try:
        results = copilot.prepare_application(
            user_id=request.user_id,
            job_id=request.job_id
        )
        return {"steps": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications/user/{user_id}")
async def list_applications(user_id: str, status: Optional[str] = None):
    """List all applications for a user"""
    try:
        result = copilot.get_applications(user_id=user_id, status=status)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications/{app_id}")
async def get_application(app_id: str):
    """Get application details"""
    try:
        app = copilot.database.get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        return app
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/applications/{app_id}/status")
async def update_application_status(app_id: str, update: StatusUpdate):
    """Update application status"""
    try:
        result = copilot.update_application_status(
            app_id=app_id,
            status=update.status,
            note=update.note or ""
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/applications/{app_id}/note")
async def add_application_note(app_id: str, note_data: NoteAdd):
    """Add a note to an application"""
    try:
        result = copilot.execute_agent("TRACKER_AGENT", {
            "action": "add_note",
            "app_id": app_id,
            "note": note_data.note
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Digest Endpoints ============

@app.get("/api/digest/{user_id}/daily")
async def get_daily_digest(user_id: str):
    """Get daily digest for user"""
    try:
        result = copilot.get_daily_digest(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/digest/{user_id}/weekly")
async def get_weekly_summary(user_id: str):
    """Get weekly summary for user"""
    try:
        result = copilot.get_weekly_summary(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/digest/{user_id}/pipeline")
async def get_pipeline_report(user_id: str):
    """Get pipeline status report"""
    try:
        result = copilot.get_pipeline_report(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Dashboard Endpoints ============

@app.get("/api/dashboard/{user_id}/stats")
async def get_dashboard_stats(user_id: str):
    """Get dashboard statistics"""
    try:
        # Get application stats
        apps_result = copilot.get_applications(user_id)
        applications = apps_result.get("applications", [])

        # Calculate stats
        stats = {
            "total_applications": len(applications),
            "by_status": {},
            "response_rate": 0,
            "interviews_scheduled": 0,
            "new_matches": 0
        }

        for app in applications:
            status = app.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            if status == "interview":
                stats["interviews_scheduled"] += 1

        # Calculate response rate
        submitted = stats["by_status"].get("submitted", 0)
        responses = (
            stats["by_status"].get("interview", 0) +
            stats["by_status"].get("offer", 0) +
            stats["by_status"].get("rejected", 0)
        )
        if submitted > 0:
            stats["response_rate"] = round((responses / submitted) * 100, 1)

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ QA Endpoints ============

@app.post("/api/qa/answer")
async def answer_question(request: QuestionRequest):
    """Answer an application question"""
    try:
        result = copilot.answer_question(
            question=request.question,
            user_id=request.user_id,
            job_id=request.job_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ System Endpoints ============

@app.get("/api/system/status")
async def get_system_status():
    """Get system status"""
    try:
        return copilot.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/agents")
async def list_agents():
    """List all registered agents"""
    try:
        return {"agents": copilot.list_agents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Health Check ============

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# JobCopilot

**Multi-Agent Job Application Automation System**

JobCopilot is an integrated AI-powered system that automates and streamlines the job application process. It uses a multi-agent architecture where specialized agents collaborate to handle different aspects of job hunting.

## Features

- **Profile Management** - Create and manage user profiles with preferences and filters
- **Resume Parsing** - Automatically extract structured data from resumes
- **Job Scraping** - Fetch jobs from company career pages (Greenhouse, Lever, etc.)
- **Smart Matching** - Score and rank jobs based on user profile fit
- **Resume Tailoring** - Customize resumes for specific job applications
- **Cover Letter Generation** - Generate personalized cover letters
- **Form Filling** - Auto-populate application form fields
- **Q&A Support** - Answer common application questions
- **Application Tracking** - Track application status and timeline
- **Daily Digests** - Get summaries and action items

## Architecture

JobCopilot uses a multi-agent system with 10 specialized agents:

| Agent | Description |
|-------|-------------|
| PROFILE_AGENT | Manages user data and preferences |
| RESUME_PARSER_AGENT | Extracts resume structure |
| SCRAPER_AGENT | Fetches jobs from career pages |
| MATCHER_AGENT | Scores job-user fit |
| RESUME_TAILOR_AGENT | Customizes resumes per job |
| COVER_LETTER_AGENT | Generates cover letters |
| FORM_FILLER_AGENT | Maps data to application forms |
| QA_AGENT | Answers application questions |
| TRACKER_AGENT | Tracks application status |
| DIGEST_AGENT | Creates daily summaries |

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/jobzoom.git
cd jobzoom

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[full]"
```

## Quick Start

### CLI Usage

```bash
# Create a profile
jobcopilot profile create \
  --name "John Doe" \
  --email "john@example.com" \
  --phone "+1-555-0123" \
  --location "San Francisco, CA" \
  --resume /path/to/resume.pdf

# Set job preferences
jobcopilot preferences set \
  --user-id <USER_ID> \
  --titles "Software Engineer" "Senior Developer" \
  --locations "San Francisco" "Remote" \
  --remote hybrid_ok \
  --salary-min 120000

# Scrape jobs
jobcopilot scrape url --url https://boards.greenhouse.io/company

# Match jobs to your profile
jobcopilot match --user-id <USER_ID>

# Prepare an application
jobcopilot apply --user-id <USER_ID> --job-id <JOB_ID>

# Get daily digest
jobcopilot digest --user-id <USER_ID> --type daily

# Check application status
jobcopilot status list --user-id <USER_ID>
```

### Python API Usage

```python
from src.main import JobCopilot

# Initialize
copilot = JobCopilot()

# Create a profile
profile = copilot.create_profile(
    name="John Doe",
    email="john@example.com",
    phone="+1-555-0123",
    location="San Francisco, CA",
    target_titles=["Software Engineer", "Senior Developer"],
    preferred_locations=["San Francisco", "Remote"],
    remote_preference="hybrid_ok",
    salary_min=120000,
    salary_max=180000
)

user_id = profile["user_id"]

# Parse resume
copilot.parse_resume(user_id, resume_path="/path/to/resume.pdf")

# Scrape and match jobs
jobs = copilot.scrape_jobs(
    url="https://boards.greenhouse.io/company",
    user_id=user_id
)

# Get recommendations
recommendations = copilot.get_recommendations(user_id, min_score=75)

# Prepare application for a job
application = copilot.prepare_application(user_id, job_id="<JOB_ID>")

# Get daily digest
digest = copilot.get_daily_digest(user_id)
print(digest["digest"])
```

## Data Schemas

### User Profile
```json
{
  "user_id": "string",
  "personal": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string"
  },
  "job_preferences": {
    "target_titles": ["string"],
    "locations": ["string"],
    "remote_preference": "remote_only|hybrid_ok|onsite_ok|any",
    "salary_min": "number",
    "salary_max": "number"
  },
  "filters": {
    "required_keywords": ["string"],
    "excluded_keywords": ["string"],
    "blacklisted_companies": ["string"]
  }
}
```

### Job
```json
{
  "job_id": "string",
  "title": "string",
  "company": "string",
  "location": "string",
  "remote_status": "remote|hybrid|onsite",
  "salary_range": {"min": "number", "max": "number"},
  "description": "string",
  "requirements": ["string"],
  "application_url": "string",
  "status": "new|matched|applied|rejected|expired"
}
```

### Application
```json
{
  "app_id": "string",
  "job_id": "string",
  "user_id": "string",
  "status": "preparing|ready|submitted|interview|offer|rejected",
  "match_score": "number",
  "tailored_resume": "string",
  "cover_letter": "string",
  "timeline": [{"status": "", "date": "", "note": ""}]
}
```

## Agent Communication

Agents communicate via a standardized output format:

```json
{
  "agent": "AGENT_NAME",
  "action": "what was done",
  "output_data": {},
  "next_agent": "AGENT_NAME or null",
  "pass_data": {},
  "save_to_memory": {}
}
```

## Storage

- **Shared Memory**: `/data/jobcopilot/memory.json` - For inter-agent state
- **Database**: `/data/jobcopilot/jobcopilot.db` - SQLite for persistent storage

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/
isort src/

# Type checking
mypy src/
```

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## License

MIT License

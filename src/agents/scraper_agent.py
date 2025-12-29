"""Scraper Agent - Fetches jobs from career pages"""

import re
import hashlib
from typing import Any, Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput, Job, JobStatus, RemoteStatus, SalaryRange


@AgentRegistry.register
class ScraperAgent(BaseAgent):
    """Agent responsible for scraping job listings from various sources"""

    @property
    def name(self) -> str:
        return "SCRAPER_AGENT"

    @property
    def description(self) -> str:
        return "Fetches and parses job listings from career pages"

    # Common job board patterns
    JOB_BOARD_PATTERNS = {
        "greenhouse": {
            "api": "https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
            "pattern": r"greenhouse\.io"
        },
        "lever": {
            "api": "https://api.lever.co/v0/postings/{company}",
            "pattern": r"lever\.co"
        },
        "workday": {
            "pattern": r"myworkdayjobs\.com"
        },
        "ashby": {
            "pattern": r"ashbyhq\.com"
        }
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute scraping tasks"""
        action = task.get("action", "")

        if action == "scrape_url":
            return self._scrape_url(task)
        elif action == "scrape_company":
            return self._scrape_company(task)
        elif action == "scrape_new_jobs":
            return self._scrape_new_jobs(task)
        elif action == "parse_job_listing":
            return self._parse_job_listing(task)
        elif action == "add_source":
            return self._add_source(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _scrape_url(self, task: Dict[str, Any]) -> AgentOutput:
        """Scrape jobs from a specific URL"""
        url = task.get("url", "")
        if not url:
            return self.create_output(
                action="error",
                output_data={"error": "URL is required"}
            )

        # Detect job board type
        board_type = self._detect_board_type(url)

        # Fetch and parse jobs
        jobs = self._fetch_jobs(url, board_type)

        # Save jobs to database
        saved_count = 0
        for job_data in jobs:
            job_id = Job.generate_job_id(
                job_data["company"],
                job_data["title"],
                job_data.get("location", "")
            )
            job_data["job_id"] = job_id
            job_data["source_url"] = url
            job_data["scraped_at"] = datetime.now().isoformat()
            job_data["status"] = JobStatus.NEW.value

            self.database.save_job(job_id, job_data)
            saved_count += 1

        return self.create_output(
            action="jobs_scraped",
            output_data={
                "url": url,
                "board_type": board_type or "unknown",
                "jobs_found": len(jobs),
                "jobs_saved": saved_count,
                "job_ids": [j.get("job_id") for j in jobs]
            },
            next_agent="MATCHER_AGENT" if task.get("auto_match") else None,
            pass_data={
                "job_ids": [j.get("job_id") for j in jobs],
                "user_id": task.get("user_id")
            } if task.get("auto_match") else None
        )

    def _scrape_company(self, task: Dict[str, Any]) -> AgentOutput:
        """Scrape jobs from a company's career page"""
        company = task.get("company", "")
        career_url = task.get("career_url", "")

        if not company and not career_url:
            return self.create_output(
                action="error",
                output_data={"error": "Company name or career URL is required"}
            )

        # Try to find career page if not provided
        if not career_url:
            career_url = self._find_career_page(company)

        if not career_url:
            return self.create_output(
                action="error",
                output_data={"error": f"Could not find career page for {company}"}
            )

        # Delegate to URL scraper
        task["url"] = career_url
        return self._scrape_url(task)

    def _scrape_new_jobs(self, task: Dict[str, Any]) -> AgentOutput:
        """Scrape new jobs from all configured sources"""
        # Get configured sources from memory
        sources = self.memory.get("scraper_sources", [])

        if not sources:
            # Use default sources if none configured
            sources = self._get_default_sources()

        all_jobs = []
        errors = []

        for source in sources:
            try:
                result = self._scrape_url({
                    "url": source.get("url"),
                    "user_id": task.get("user_id")
                })
                if result.output_data.get("job_ids"):
                    all_jobs.extend(result.output_data["job_ids"])
            except Exception as e:
                errors.append({"source": source.get("url"), "error": str(e)})

        return self.create_output(
            action="batch_scrape_complete",
            output_data={
                "sources_processed": len(sources),
                "total_jobs_found": len(all_jobs),
                "job_ids": all_jobs,
                "errors": errors
            },
            next_agent="MATCHER_AGENT" if all_jobs and task.get("user_id") else None,
            pass_data={
                "job_ids": all_jobs,
                "user_id": task.get("user_id")
            } if all_jobs and task.get("user_id") else None
        )

    def _parse_job_listing(self, task: Dict[str, Any]) -> AgentOutput:
        """Parse a raw job listing into structured format"""
        raw_html = task.get("html", "")
        raw_text = task.get("text", "")
        url = task.get("url", "")

        if not raw_html and not raw_text:
            return self.create_output(
                action="error",
                output_data={"error": "HTML or text content is required"}
            )

        content = raw_text or self._html_to_text(raw_html)
        parsed = self._parse_job_content(content, url)

        return self.create_output(
            action="job_parsed",
            output_data=parsed
        )

    def _add_source(self, task: Dict[str, Any]) -> AgentOutput:
        """Add a new job source"""
        url = task.get("url", "")
        name = task.get("name", "")

        if not url:
            return self.create_output(
                action="error",
                output_data={"error": "URL is required"}
            )

        sources = self.memory.get("scraper_sources", [])
        sources.append({
            "url": url,
            "name": name or urlparse(url).netloc,
            "added_at": datetime.now().isoformat()
        })

        return self.create_output(
            action="source_added",
            output_data={"url": url, "name": name},
            save_to_memory={"scraper_sources": sources}
        )

    def _detect_board_type(self, url: str) -> Optional[str]:
        """Detect the job board type from URL"""
        for board_name, config in self.JOB_BOARD_PATTERNS.items():
            if re.search(config["pattern"], url):
                return board_name
        return None

    def _fetch_jobs(self, url: str, board_type: Optional[str] = None) -> List[Dict]:
        """Fetch jobs from URL (placeholder for actual implementation)"""
        # In production, this would use requests/aiohttp to fetch
        # and BeautifulSoup/lxml to parse

        # Return placeholder data structure
        jobs = []

        # Simulate job extraction based on board type
        if board_type == "greenhouse":
            jobs = self._parse_greenhouse(url)
        elif board_type == "lever":
            jobs = self._parse_lever(url)
        else:
            jobs = self._parse_generic(url)

        return jobs

    def _parse_greenhouse(self, url: str) -> List[Dict]:
        """Parse Greenhouse job board (placeholder)"""
        # In production: fetch from Greenhouse API
        return [{
            "title": "Software Engineer",
            "company": self._extract_company_from_url(url),
            "location": "San Francisco, CA",
            "remote_status": "hybrid",
            "description": "Join our team...",
            "requirements": ["Python", "SQL", "3+ years experience"],
            "application_url": url
        }]

    def _parse_lever(self, url: str) -> List[Dict]:
        """Parse Lever job board (placeholder)"""
        # In production: fetch from Lever API
        return [{
            "title": "Senior Developer",
            "company": self._extract_company_from_url(url),
            "location": "Remote",
            "remote_status": "remote",
            "description": "We're looking for...",
            "requirements": ["JavaScript", "React", "5+ years experience"],
            "application_url": url
        }]

    def _parse_generic(self, url: str) -> List[Dict]:
        """Parse generic career page (placeholder)"""
        return [{
            "title": "Developer",
            "company": self._extract_company_from_url(url),
            "location": "Various",
            "description": "Open position...",
            "application_url": url
        }]

    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")

        # Handle job board URLs
        if "greenhouse.io" in domain:
            path_parts = parsed.path.split("/")
            for part in path_parts:
                if part and part not in ["jobs", "boards"]:
                    return part.replace("-", " ").title()

        if "lever.co" in domain:
            path_parts = parsed.path.split("/")
            if path_parts:
                return path_parts[1].replace("-", " ").title()

        # Return domain as company name
        return domain.split(".")[0].title()

    def _find_career_page(self, company: str) -> Optional[str]:
        """Find career page for a company (placeholder)"""
        # In production: use search API or company database
        company_slug = company.lower().replace(" ", "-")
        return f"https://boards.greenhouse.io/{company_slug}"

    def _get_default_sources(self) -> List[Dict]:
        """Get default job sources"""
        return [
            {"url": "https://boards.greenhouse.io/anthropic", "name": "Anthropic"},
            {"url": "https://boards.greenhouse.io/openai", "name": "OpenAI"},
        ]

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (placeholder)"""
        # In production: use BeautifulSoup
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _parse_job_content(self, content: str, url: str) -> Dict:
        """Parse job content into structured format"""
        # Extract title
        title_match = re.search(r'(?i)(job title|position|role)[:\s]*([^\n]+)', content)
        title = title_match.group(2).strip() if title_match else "Unknown Position"

        # Extract location
        location_match = re.search(r'(?i)(location|based in)[:\s]*([^\n]+)', content)
        location = location_match.group(2).strip() if location_match else ""

        # Extract salary
        salary_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', content)
        salary_range = self._parse_salary(salary_match.group(0)) if salary_match else {}

        # Extract remote status
        remote_status = self._detect_remote_status(content)

        # Extract requirements
        requirements = self._extract_requirements(content)

        return {
            "title": title,
            "location": location,
            "salary_range": salary_range,
            "remote_status": remote_status,
            "requirements": requirements,
            "description": content[:2000],
            "application_url": url
        }

    def _parse_salary(self, salary_str: str) -> Dict:
        """Parse salary string into min/max"""
        numbers = re.findall(r'[\d,]+', salary_str)
        if len(numbers) >= 2:
            return {
                "min": int(numbers[0].replace(",", "")),
                "max": int(numbers[1].replace(",", ""))
            }
        elif len(numbers) == 1:
            return {"min": int(numbers[0].replace(",", "")), "max": None}
        return {}

    def _detect_remote_status(self, content: str) -> str:
        """Detect remote work status from content"""
        content_lower = content.lower()

        if re.search(r'fully?\s*remote|100%?\s*remote|remote\s*only', content_lower):
            return RemoteStatus.REMOTE.value
        elif re.search(r'hybrid|flexible|some remote', content_lower):
            return RemoteStatus.HYBRID.value
        else:
            return RemoteStatus.ONSITE.value

    def _extract_requirements(self, content: str) -> List[str]:
        """Extract job requirements from content"""
        requirements = []

        # Look for requirements section
        req_match = re.search(
            r'(?i)(requirements?|qualifications?|what you.ll need)[:\s]*([^#]+?)(?=\n\n|\Z)',
            content
        )

        if req_match:
            req_text = req_match.group(2)
            # Extract bullet points
            bullets = re.findall(r'[•\-*]\s*([^\n•\-*]+)', req_text)
            requirements.extend([b.strip() for b in bullets if b.strip()])

        return requirements[:15]  # Limit to 15 requirements

"""Resume Parser Agent - Extracts structure from resumes"""

import re
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput, ParsedResume, Experience, Education, Project, Skills


@AgentRegistry.register
class ResumeParserAgent(BaseAgent):
    """Agent responsible for parsing and extracting resume information"""

    @property
    def name(self) -> str:
        return "RESUME_PARSER_AGENT"

    @property
    def description(self) -> str:
        return "Extracts structured information from resumes"

    # Common technical keywords for extraction
    TECH_KEYWORDS = {
        "languages": ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
                     "ruby", "php", "swift", "kotlin", "scala", "r", "sql", "html", "css"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "fastapi", "spring",
                      "express", "node.js", "next.js", "rails", "laravel", ".net"],
        "tools": ["git", "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "terraform",
                 "ansible", "jira", "confluence", "figma", "postman"],
        "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
                     "oracle", "dynamodb", "cassandra"],
        "concepts": ["agile", "scrum", "ci/cd", "devops", "rest", "graphql", "microservices",
                    "machine learning", "deep learning", "data science"]
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute resume parsing tasks"""
        action = task.get("action", "parse_resume")

        if action == "parse_resume":
            return self._parse_resume(task)
        elif action == "extract_keywords":
            return self._extract_keywords(task)
        elif action == "analyze_skills":
            return self._analyze_skills(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _parse_resume(self, task: Dict[str, Any]) -> AgentOutput:
        """Parse a resume and extract structured information"""
        user_id = task.get("user_id")
        resume_text = task.get("resume_text", "")
        resume_path = task.get("resume_path", "")

        # Load from file if path provided and no text
        if resume_path and not resume_text:
            resume_text = self._load_resume_file(resume_path)

        if not resume_text:
            return self.create_output(
                action="error",
                output_data={"error": "No resume content provided"}
            )

        # Parse the resume
        parsed = self._extract_resume_data(resume_text)

        # Update user profile if user_id provided
        if user_id:
            profile = self.database.get_user(user_id)
            if profile:
                profile["resume"]["parsed"] = parsed.to_dict()
                profile["resume"]["raw_text"] = resume_text
                if resume_path:
                    profile["resume"]["file_path"] = resume_path
                self.database.save_user(user_id, profile)

        return self.create_output(
            action="resume_parsed",
            output_data={
                "user_id": user_id,
                "parsed_resume": parsed.to_dict(),
                "summary_stats": {
                    "experience_count": len(parsed.experience),
                    "education_count": len(parsed.education),
                    "skills_count": sum([
                        len(parsed.skills.technical),
                        len(parsed.skills.tools),
                        len(parsed.skills.soft)
                    ]),
                    "keywords_count": len(parsed.extracted_keywords)
                }
            },
            save_to_memory={
                f"users.{user_id}.resume.parsed": parsed.to_dict()
            } if user_id else None
        )

    def _load_resume_file(self, file_path: str) -> str:
        """Load resume from file"""
        path = Path(file_path)
        if not path.exists():
            return ""

        try:
            # Handle different file types
            if path.suffix.lower() == ".txt":
                return path.read_text()
            elif path.suffix.lower() == ".pdf":
                # Placeholder for PDF parsing
                return self._parse_pdf(path)
            elif path.suffix.lower() in [".doc", ".docx"]:
                # Placeholder for Word doc parsing
                return self._parse_docx(path)
            else:
                return path.read_text()
        except Exception as e:
            self.logger.error(f"Error loading resume: {e}")
            return ""

    def _parse_pdf(self, path: Path) -> str:
        """Parse PDF file (placeholder - would use pdfplumber/PyPDF2 in production)"""
        # In production, use: import pdfplumber
        return f"[PDF content from {path}]"

    def _parse_docx(self, path: Path) -> str:
        """Parse Word document (placeholder - would use python-docx in production)"""
        # In production, use: import docx
        return f"[DOCX content from {path}]"

    def _extract_resume_data(self, text: str) -> ParsedResume:
        """Extract structured data from resume text"""
        parsed = ParsedResume()

        # Extract sections
        sections = self._identify_sections(text)

        # Extract summary
        parsed.summary = self._extract_summary(text, sections)

        # Extract experience
        parsed.experience = self._extract_experience(text, sections)

        # Extract education
        parsed.education = self._extract_education(text, sections)

        # Extract skills
        parsed.skills = self._extract_skills(text, sections)

        # Extract certifications
        parsed.certifications = self._extract_certifications(text, sections)

        # Extract projects
        parsed.projects = self._extract_projects(text, sections)

        # Extract keywords
        parsed.extracted_keywords = self._extract_all_keywords(text)

        return parsed

    def _identify_sections(self, text: str) -> Dict[str, tuple]:
        """Identify section boundaries in the resume"""
        section_patterns = {
            "summary": r"(?i)(summary|objective|profile|about)",
            "experience": r"(?i)(experience|employment|work history|professional experience)",
            "education": r"(?i)(education|academic|qualifications)",
            "skills": r"(?i)(skills|technical skills|competencies|technologies)",
            "certifications": r"(?i)(certifications|certificates|licenses)",
            "projects": r"(?i)(projects|portfolio|personal projects)"
        }

        sections = {}
        lines = text.split('\n')

        for i, line in enumerate(lines):
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line) and len(line.strip()) < 50:
                    sections[section_name] = i

        return sections

    def _extract_summary(self, text: str, sections: Dict) -> str:
        """Extract professional summary"""
        # Simple extraction - take first few sentences if no explicit section
        lines = text.split('\n')
        summary_lines = []

        start_idx = sections.get("summary", 0)
        end_idx = min(start_idx + 5, len(lines))

        for line in lines[start_idx:end_idx]:
            line = line.strip()
            if line and not any(
                re.search(r"(?i)" + p, line)
                for p in ["experience", "education", "skills"]
            ):
                summary_lines.append(line)

        return " ".join(summary_lines)[:500]

    def _extract_experience(self, text: str, sections: Dict) -> List[Experience]:
        """Extract work experience"""
        experiences = []

        # Pattern for job entries
        job_pattern = r"(?P<title>[\w\s]+)\s*(?:at|@|-|,)\s*(?P<company>[\w\s&.]+)"
        date_pattern = r"(\d{4}|\w+\s*\d{4})\s*[-–to]+\s*(\d{4}|\w+\s*\d{4}|present|current)"

        lines = text.split('\n')
        current_job = None
        current_bullets = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for date range (indicates new job entry)
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match:
                # Save previous job if exists
                if current_job:
                    experiences.append(Experience(
                        company=current_job.get("company", ""),
                        title=current_job.get("title", ""),
                        duration=current_job.get("duration", ""),
                        bullets=current_bullets
                    ))
                    current_bullets = []

                # Start new job
                duration = f"{date_match.group(1)} - {date_match.group(2)}"
                job_match = re.search(job_pattern, line)
                current_job = {
                    "title": job_match.group("title").strip() if job_match else "",
                    "company": job_match.group("company").strip() if job_match else "",
                    "duration": duration
                }

            # Check for bullet points
            elif line.startswith(('•', '-', '*', '–')) or re.match(r'^\d+\.', line):
                bullet = re.sub(r'^[•\-*–\d.]+\s*', '', line)
                if bullet:
                    current_bullets.append(bullet)

        # Save last job
        if current_job:
            experiences.append(Experience(
                company=current_job.get("company", ""),
                title=current_job.get("title", ""),
                duration=current_job.get("duration", ""),
                bullets=current_bullets
            ))

        return experiences[:10]  # Limit to 10 entries

    def _extract_education(self, text: str, sections: Dict) -> List[Education]:
        """Extract education information"""
        education = []

        degree_patterns = [
            r"(?P<degree>(?:Bachelor|Master|Ph\.?D|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)[\w\s]*)",
            r"(?P<institution>University|College|Institute|School)[\w\s]*",
        ]

        year_pattern = r"(19|20)\d{2}"

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for degree keywords
            degree_match = re.search(
                r"(?i)(bachelor|master|ph\.?d|mba|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)",
                line
            )
            if degree_match:
                year_match = re.search(year_pattern, line)
                education.append(Education(
                    institution=self._extract_institution(line),
                    degree=line[:100],
                    year=year_match.group(0) if year_match else ""
                ))

        return education[:5]  # Limit to 5 entries

    def _extract_institution(self, text: str) -> str:
        """Extract institution name from text"""
        patterns = [
            r"(?i)(?:at|from)\s+([\w\s]+(?:University|College|Institute|School))",
            r"([\w\s]+(?:University|College|Institute|School))"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_skills(self, text: str, sections: Dict) -> Skills:
        """Extract skills from resume"""
        text_lower = text.lower()
        skills = Skills()

        # Technical skills
        for lang in self.TECH_KEYWORDS["languages"]:
            if lang in text_lower:
                skills.technical.append(lang)

        for framework in self.TECH_KEYWORDS["frameworks"]:
            if framework in text_lower:
                skills.technical.append(framework)

        # Tools
        for tool in self.TECH_KEYWORDS["tools"]:
            if tool in text_lower:
                skills.tools.append(tool)

        for db in self.TECH_KEYWORDS["databases"]:
            if db in text_lower:
                skills.tools.append(db)

        # Soft skills (simple pattern matching)
        soft_skill_patterns = [
            "leadership", "communication", "teamwork", "problem-solving",
            "analytical", "project management", "collaboration", "mentoring"
        ]
        for skill in soft_skill_patterns:
            if skill in text_lower:
                skills.soft.append(skill)

        return skills

    def _extract_certifications(self, text: str, sections: Dict) -> List[str]:
        """Extract certifications"""
        certs = []
        cert_patterns = [
            r"(?i)(AWS|Azure|GCP|Google Cloud)[\w\s]+(?:Certified|Certification)",
            r"(?i)(?:Certified|Certification)[\w\s]+",
            r"(?i)PMP|CISSP|CCNA|CCNP|CompTIA[\w\s]+"
        ]

        for pattern in cert_patterns:
            matches = re.findall(pattern, text)
            certs.extend(matches)

        return list(set(certs))[:10]

    def _extract_projects(self, text: str, sections: Dict) -> List[Project]:
        """Extract projects"""
        projects = []

        # Look for project section
        if "projects" in sections:
            start = sections["projects"]
            lines = text.split('\n')[start:start + 20]

            current_project = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # New project (typically bold or titled)
                if len(line) < 100 and not line.startswith(('•', '-', '*')):
                    if current_project:
                        projects.append(current_project)
                    current_project = Project(name=line, description="", tech=[])
                elif current_project and line.startswith(('•', '-', '*')):
                    desc = re.sub(r'^[•\-*]+\s*', '', line)
                    if current_project.description:
                        current_project.description += " " + desc
                    else:
                        current_project.description = desc

            if current_project:
                projects.append(current_project)

        return projects[:5]

    def _extract_all_keywords(self, text: str) -> List[str]:
        """Extract all relevant keywords from resume"""
        keywords = set()
        text_lower = text.lower()

        for category, terms in self.TECH_KEYWORDS.items():
            for term in terms:
                if term in text_lower:
                    keywords.add(term)

        return list(keywords)

    def _extract_keywords(self, task: Dict[str, Any]) -> AgentOutput:
        """Extract keywords from text"""
        text = task.get("text", "")
        keywords = self._extract_all_keywords(text)

        return self.create_output(
            action="keywords_extracted",
            output_data={"keywords": keywords, "count": len(keywords)}
        )

    def _analyze_skills(self, task: Dict[str, Any]) -> AgentOutput:
        """Analyze skills from resume text"""
        text = task.get("text", "")
        skills = self._extract_skills(text, {})

        return self.create_output(
            action="skills_analyzed",
            output_data={
                "skills": {
                    "technical": skills.technical,
                    "tools": skills.tools,
                    "soft": skills.soft
                }
            }
        )

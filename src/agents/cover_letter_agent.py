"""Cover Letter Agent - Generates customized cover letters"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput


@AgentRegistry.register
class CoverLetterAgent(BaseAgent):
    """Agent responsible for generating tailored cover letters"""

    @property
    def name(self) -> str:
        return "COVER_LETTER_AGENT"

    @property
    def description(self) -> str:
        return "Generates customized cover letters for job applications"

    # Cover letter templates
    TEMPLATES = {
        "professional": """Dear {hiring_manager},

I am writing to express my strong interest in the {job_title} position at {company}. {opening_hook}

{experience_paragraph}

{skills_paragraph}

{closing_paragraph}

Sincerely,
{name}""",

        "enthusiastic": """Dear {hiring_manager},

{opening_hook} I am thrilled to apply for the {job_title} role at {company}.

{experience_paragraph}

{skills_paragraph}

{closing_paragraph}

Best regards,
{name}""",

        "concise": """Dear {hiring_manager},

I am applying for the {job_title} position at {company}. {opening_hook}

{combined_paragraph}

{closing_paragraph}

Sincerely,
{name}"""
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute cover letter generation tasks"""
        action = task.get("action", "")

        if action == "generate_letter":
            return self._generate_letter(task)
        elif action == "generate_letters":
            return self._generate_multiple_letters(task)
        elif action == "customize_template":
            return self._customize_template(task)
        elif action == "get_templates":
            return self._get_templates(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _generate_letter(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate a cover letter for a specific job"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        template_type = task.get("template", "professional")
        tailored_resume = task.get("tailored_resume", "")
        job_keywords = task.get("job_keywords", [])

        if not user_id or not job_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id and job_id are required"}
            )

        user = self.database.get_user(user_id)
        job = self.database.get_job(job_id)

        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        if not job:
            return self.create_output(
                action="error",
                output_data={"error": f"Job not found: {job_id}"}
            )

        # Extract job keywords if not provided
        if not job_keywords:
            job_keywords = self._extract_keywords(job)

        # Generate the cover letter
        cover_letter = self._create_cover_letter(
            user,
            job,
            template_type,
            job_keywords,
            tailored_resume
        )

        return self.create_output(
            action="letter_generated",
            output_data={
                "user_id": user_id,
                "job_id": job_id,
                "cover_letter": cover_letter,
                "template_used": template_type,
                "word_count": len(cover_letter.split())
            },
            next_agent="FORM_FILLER_AGENT",
            pass_data={
                "user_id": user_id,
                "job_id": job_id,
                "cover_letter": cover_letter,
                "tailored_resume": tailored_resume
            }
        )

    def _generate_multiple_letters(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate cover letters for multiple jobs"""
        user_id = task.get("user_id")
        job_ids = task.get("job_ids", [])
        template_type = task.get("template", "professional")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        if not job_ids:
            return self.create_output(
                action="error",
                output_data={"error": "job_ids are required"}
            )

        results = []
        for job_id in job_ids:
            result = self._generate_letter({
                "user_id": user_id,
                "job_id": job_id,
                "template": template_type
            })
            results.append({
                "job_id": job_id,
                "success": "error" not in result.output_data,
                "cover_letter": result.output_data.get("cover_letter", "")
            })

        return self.create_output(
            action="letters_generated",
            output_data={
                "user_id": user_id,
                "total_jobs": len(job_ids),
                "successful": sum(1 for r in results if r["success"]),
                "results": results
            }
        )

    def _customize_template(self, task: Dict[str, Any]) -> AgentOutput:
        """Customize a cover letter template"""
        template_name = task.get("template_name", "custom")
        template_content = task.get("template_content", "")

        if not template_content:
            return self.create_output(
                action="error",
                output_data={"error": "template_content is required"}
            )

        # Save custom template
        custom_templates = self.memory.get("custom_templates", {})
        custom_templates[template_name] = template_content

        return self.create_output(
            action="template_customized",
            output_data={
                "template_name": template_name,
                "saved": True
            },
            save_to_memory={"custom_templates": custom_templates}
        )

    def _get_templates(self, task: Dict[str, Any]) -> AgentOutput:
        """Get available templates"""
        custom_templates = self.memory.get("custom_templates", {})
        all_templates = {**self.TEMPLATES, **custom_templates}

        return self.create_output(
            action="templates_retrieved",
            output_data={
                "templates": list(all_templates.keys()),
                "default_templates": list(self.TEMPLATES.keys()),
                "custom_templates": list(custom_templates.keys())
            }
        )

    def _create_cover_letter(
        self,
        user: Dict,
        job: Dict,
        template_type: str,
        job_keywords: List[str],
        tailored_resume: str = ""
    ) -> str:
        """Create a cover letter from template and user/job data"""
        personal = user.get("personal", {})
        resume = user.get("resume", {}).get("parsed", {})

        # Get template
        custom_templates = self.memory.get("custom_templates", {})
        template = custom_templates.get(template_type) or self.TEMPLATES.get(
            template_type,
            self.TEMPLATES["professional"]
        )

        # Generate content sections
        opening_hook = self._generate_opening_hook(user, job, job_keywords)
        experience_paragraph = self._generate_experience_paragraph(resume, job, job_keywords)
        skills_paragraph = self._generate_skills_paragraph(resume, job, job_keywords)
        closing_paragraph = self._generate_closing_paragraph(job)
        combined_paragraph = self._generate_combined_paragraph(resume, job, job_keywords)

        # Fill template
        cover_letter = template.format(
            hiring_manager=self._get_hiring_manager(job),
            job_title=job.get("title", "the position"),
            company=job.get("company", "your company"),
            name=personal.get("name", ""),
            opening_hook=opening_hook,
            experience_paragraph=experience_paragraph,
            skills_paragraph=skills_paragraph,
            closing_paragraph=closing_paragraph,
            combined_paragraph=combined_paragraph
        )

        return cover_letter

    def _extract_keywords(self, job: Dict) -> List[str]:
        """Extract keywords from job description"""
        text = (
            job.get("title", "") + " " +
            job.get("description", "") + " " +
            " ".join(job.get("requirements", []))
        )

        keywords = set()
        patterns = [
            r'\b(?:Python|JavaScript|TypeScript|Java|C\+\+|Go|Rust)\b',
            r'\b(?:React|Angular|Vue|Django|Flask|Node\.js)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes)\b',
            r'\b(?:SQL|PostgreSQL|MongoDB|Redis)\b',
            r'\b(?:Machine Learning|AI|Data Science)\b'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(matches)

        return list(keywords)

    def _get_hiring_manager(self, job: Dict) -> str:
        """Get hiring manager name or default"""
        # In production, this could look up the hiring manager
        return "Hiring Manager"

    def _generate_opening_hook(self, user: Dict, job: Dict, keywords: List[str]) -> str:
        """Generate an engaging opening hook"""
        resume = user.get("resume", {}).get("parsed", {})
        experience = resume.get("experience", [])

        # Calculate years of experience
        years = len(experience) * 2 if experience else 0

        hooks = [
            f"With {years}+ years of experience in software development, I am confident in my ability to contribute to your team.",
            f"My background in {', '.join(keywords[:3]) if keywords else 'technology'} makes me an ideal candidate for this role.",
            f"I was excited to discover this opportunity as it perfectly aligns with my passion for {keywords[0] if keywords else 'technology'}.",
        ]

        return hooks[0]

    def _generate_experience_paragraph(
        self,
        resume: Dict,
        job: Dict,
        keywords: List[str]
    ) -> str:
        """Generate paragraph highlighting relevant experience"""
        experience = resume.get("experience", [])

        if not experience:
            return "I am eager to apply my skills and passion to this role."

        recent_exp = experience[0]
        company = recent_exp.get("company", "my current company")
        title = recent_exp.get("title", "my current role")
        bullets = recent_exp.get("bullets", [])

        # Find relevant bullet
        relevant_bullet = ""
        for bullet in bullets:
            if any(k.lower() in bullet.lower() for k in keywords):
                relevant_bullet = bullet
                break

        if relevant_bullet:
            return (
                f"In my current role as {title} at {company}, I have {relevant_bullet.lower()}. "
                f"This experience has prepared me well for the challenges of the {job.get('title', 'position')} role."
            )

        return (
            f"As a {title} at {company}, I have developed strong expertise in the technologies "
            f"and practices that are central to this role."
        )

    def _generate_skills_paragraph(
        self,
        resume: Dict,
        job: Dict,
        keywords: List[str]
    ) -> str:
        """Generate paragraph highlighting relevant skills"""
        skills = resume.get("skills", {})
        technical = skills.get("technical", []) if isinstance(skills, dict) else []

        # Find matching skills
        matching = [s for s in technical if s.lower() in [k.lower() for k in keywords]]

        if matching:
            return (
                f"My technical proficiency includes {', '.join(matching[:5])}, which directly align with "
                f"the requirements for this position. I am committed to continuous learning and staying "
                f"current with industry best practices."
            )

        return (
            f"I bring a diverse skill set that includes {', '.join(technical[:5]) if technical else 'various technologies'}. "
            f"I am a quick learner and am confident in my ability to adapt to your tech stack."
        )

    def _generate_closing_paragraph(self, job: Dict) -> str:
        """Generate closing paragraph"""
        company = job.get("company", "your company")

        return (
            f"I am excited about the opportunity to contribute to {company}'s success and would welcome "
            f"the chance to discuss how my skills and experience align with your needs. Thank you for "
            f"considering my application. I look forward to speaking with you soon."
        )

    def _generate_combined_paragraph(
        self,
        resume: Dict,
        job: Dict,
        keywords: List[str]
    ) -> str:
        """Generate a combined experience/skills paragraph for concise template"""
        experience = resume.get("experience", [])
        skills = resume.get("skills", {})
        technical = skills.get("technical", []) if isinstance(skills, dict) else []

        years = len(experience) * 2 if experience else 0
        matching_skills = [s for s in technical if s.lower() in [k.lower() for k in keywords]][:4]

        return (
            f"I bring {years}+ years of professional experience with expertise in "
            f"{', '.join(matching_skills) if matching_skills else 'relevant technologies'}. "
            f"My track record of delivering results and my passion for the field make me "
            f"confident that I can make meaningful contributions to your team."
        )

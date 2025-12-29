"""Form Filler Agent - Maps user data to application forms"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput


@AgentRegistry.register
class FormFillerAgent(BaseAgent):
    """Agent responsible for filling out job application forms"""

    @property
    def name(self) -> str:
        return "FORM_FILLER_AGENT"

    @property
    def description(self) -> str:
        return "Maps user data to job application form fields"

    # Standard field mappings
    FIELD_MAPPINGS = {
        # Personal info
        "first_name": ["first name", "firstname", "given name", "fname"],
        "last_name": ["last name", "lastname", "surname", "family name", "lname"],
        "full_name": ["full name", "name", "your name", "candidate name"],
        "email": ["email", "e-mail", "email address"],
        "phone": ["phone", "telephone", "mobile", "phone number", "contact number"],
        "location": ["location", "city", "address", "current location"],
        "linkedin": ["linkedin", "linkedin url", "linkedin profile"],

        # Professional info
        "resume": ["resume", "cv", "curriculum vitae", "upload resume"],
        "cover_letter": ["cover letter", "cover_letter", "letter of interest"],
        "salary": ["salary", "expected salary", "salary expectation", "compensation"],
        "start_date": ["start date", "availability", "when can you start"],
        "work_authorization": ["work authorization", "authorized to work", "visa status"],

        # Experience
        "years_experience": ["years of experience", "experience", "years experience"],
        "current_company": ["current company", "current employer", "employer"],
        "current_title": ["current title", "job title", "current position"],

        # Education
        "degree": ["degree", "highest degree", "education level"],
        "university": ["university", "school", "institution", "college"],
        "graduation_year": ["graduation year", "year graduated", "grad year"],

        # Other
        "how_heard": ["how did you hear", "source", "referral", "how heard"],
        "portfolio": ["portfolio", "website", "personal website", "github"],
        "willing_relocate": ["relocate", "willing to relocate", "relocation"]
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute form filling tasks"""
        action = task.get("action", "")

        if action == "fill_form":
            return self._fill_form(task)
        elif action == "map_fields":
            return self._map_fields(task)
        elif action == "validate_form":
            return self._validate_form(task)
        elif action == "prepare_application":
            return self._prepare_application(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _fill_form(self, task: Dict[str, Any]) -> AgentOutput:
        """Fill a form with user data"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        form_fields = task.get("form_fields", [])
        cover_letter = task.get("cover_letter", "")
        tailored_resume = task.get("tailored_resume", "")

        if not user_id:
            return self.create_output(
                action="error",
                output_data={"error": "user_id is required"}
            )

        user = self.database.get_user(user_id)
        if not user:
            return self.create_output(
                action="error",
                output_data={"error": f"User not found: {user_id}"}
            )

        job = None
        if job_id:
            job = self.database.get_job(job_id)

        # Map fields to user data
        filled_data = self._map_user_data(user, form_fields, job)

        # Add cover letter and resume if provided
        if cover_letter:
            filled_data["cover_letter"] = cover_letter
        if tailored_resume:
            filled_data["resume"] = tailored_resume

        # Identify missing required fields
        missing_fields = self._find_missing_fields(form_fields, filled_data)

        return self.create_output(
            action="form_filled",
            output_data={
                "user_id": user_id,
                "job_id": job_id,
                "filled_data": filled_data,
                "missing_fields": missing_fields,
                "completion_percentage": self._calculate_completion(form_fields, filled_data)
            },
            next_agent="QA_AGENT" if missing_fields else None,
            pass_data={
                "user_id": user_id,
                "job_id": job_id,
                "questions": missing_fields
            } if missing_fields else None
        )

    def _map_fields(self, task: Dict[str, Any]) -> AgentOutput:
        """Map form field names to standard field types"""
        field_names = task.get("field_names", [])

        mappings = {}
        for field_name in field_names:
            mapped_field = self._identify_field_type(field_name)
            mappings[field_name] = mapped_field

        return self.create_output(
            action="fields_mapped",
            output_data={
                "mappings": mappings,
                "unmapped": [f for f, m in mappings.items() if m is None]
            }
        )

    def _validate_form(self, task: Dict[str, Any]) -> AgentOutput:
        """Validate form data before submission"""
        form_data = task.get("form_data", {})
        required_fields = task.get("required_fields", [])

        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Check required fields
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")

        # Validate specific field formats
        if "email" in form_data:
            if not self._validate_email(form_data["email"]):
                validation_results["valid"] = False
                validation_results["errors"].append("Invalid email format")

        if "phone" in form_data:
            if not self._validate_phone(form_data["phone"]):
                validation_results["warnings"].append("Phone number may be in incorrect format")

        if "linkedin" in form_data:
            if not self._validate_linkedin(form_data["linkedin"]):
                validation_results["warnings"].append("LinkedIn URL may be invalid")

        return self.create_output(
            action="form_validated",
            output_data=validation_results
        )

    def _prepare_application(self, task: Dict[str, Any]) -> AgentOutput:
        """Prepare a complete application package"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        tailored_resume = task.get("tailored_resume", "")
        cover_letter = task.get("cover_letter", "")

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

        # Prepare standard application data
        personal = user.get("personal", {})
        resume = user.get("resume", {}).get("parsed", {})

        application = {
            "personal_info": {
                "full_name": personal.get("name", ""),
                "email": personal.get("email", ""),
                "phone": personal.get("phone", ""),
                "location": personal.get("location", ""),
                "linkedin": personal.get("linkedin", "")
            },
            "professional_info": {
                "resume": tailored_resume or user.get("resume", {}).get("raw_text", ""),
                "cover_letter": cover_letter,
                "current_title": resume.get("experience", [{}])[0].get("title", "") if resume.get("experience") else "",
                "current_company": resume.get("experience", [{}])[0].get("company", "") if resume.get("experience") else "",
                "years_experience": len(resume.get("experience", [])) * 2
            },
            "education_info": {
                "degree": resume.get("education", [{}])[0].get("degree", "") if resume.get("education") else "",
                "university": resume.get("education", [{}])[0].get("institution", "") if resume.get("education") else "",
                "graduation_year": resume.get("education", [{}])[0].get("year", "") if resume.get("education") else ""
            },
            "job_info": {
                "job_id": job_id,
                "job_title": job.get("title", ""),
                "company": job.get("company", ""),
                "application_url": job.get("application_url", "")
            }
        }

        return self.create_output(
            action="application_prepared",
            output_data={
                "user_id": user_id,
                "job_id": job_id,
                "application_data": application,
                "ready_to_submit": bool(
                    application["personal_info"]["email"] and
                    application["professional_info"]["resume"]
                )
            },
            next_agent="TRACKER_AGENT",
            pass_data={
                "user_id": user_id,
                "job_id": job_id,
                "application_data": application
            }
        )

    def _map_user_data(
        self,
        user: Dict,
        form_fields: List[str],
        job: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Map user data to form fields"""
        personal = user.get("personal", {})
        resume = user.get("resume", {}).get("parsed", {})
        prefs = user.get("job_preferences", {})

        filled = {}

        for field in form_fields:
            field_type = self._identify_field_type(field)
            value = None

            if field_type == "first_name":
                name = personal.get("name", "")
                value = name.split()[0] if name else ""
            elif field_type == "last_name":
                name = personal.get("name", "")
                parts = name.split()
                value = " ".join(parts[1:]) if len(parts) > 1 else ""
            elif field_type == "full_name":
                value = personal.get("name", "")
            elif field_type == "email":
                value = personal.get("email", "")
            elif field_type == "phone":
                value = personal.get("phone", "")
            elif field_type == "location":
                value = personal.get("location", "")
            elif field_type == "linkedin":
                value = personal.get("linkedin", "")
            elif field_type == "years_experience":
                experience = resume.get("experience", [])
                value = str(len(experience) * 2) if experience else ""
            elif field_type == "current_company":
                experience = resume.get("experience", [])
                value = experience[0].get("company", "") if experience else ""
            elif field_type == "current_title":
                experience = resume.get("experience", [])
                value = experience[0].get("title", "") if experience else ""
            elif field_type == "degree":
                education = resume.get("education", [])
                value = education[0].get("degree", "") if education else ""
            elif field_type == "university":
                education = resume.get("education", [])
                value = education[0].get("institution", "") if education else ""
            elif field_type == "graduation_year":
                education = resume.get("education", [])
                value = education[0].get("year", "") if education else ""
            elif field_type == "salary":
                min_sal = prefs.get("salary_min")
                max_sal = prefs.get("salary_max")
                if min_sal and max_sal:
                    value = f"${min_sal:,} - ${max_sal:,}"
                elif min_sal:
                    value = f"${min_sal:,}+"
            elif field_type == "work_authorization":
                value = "Authorized to work"  # Default, should be in user profile

            if value:
                filled[field] = value

        return filled

    def _identify_field_type(self, field_name: str) -> Optional[str]:
        """Identify the standard field type from a field name"""
        field_lower = field_name.lower().strip()

        for field_type, aliases in self.FIELD_MAPPINGS.items():
            for alias in aliases:
                if alias in field_lower or field_lower in alias:
                    return field_type

        return None

    def _find_missing_fields(
        self,
        form_fields: List[str],
        filled_data: Dict
    ) -> List[str]:
        """Find fields that couldn't be filled"""
        return [f for f in form_fields if f not in filled_data]

    def _calculate_completion(
        self,
        form_fields: List[str],
        filled_data: Dict
    ) -> float:
        """Calculate form completion percentage"""
        if not form_fields:
            return 100.0

        filled_count = sum(1 for f in form_fields if f in filled_data and filled_data[f])
        return round((filled_count / len(form_fields)) * 100, 1)

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone format"""
        # Remove common formatting
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        return len(cleaned) >= 10 and cleaned.replace('+', '').isdigit()

    def _validate_linkedin(self, url: str) -> bool:
        """Validate LinkedIn URL"""
        return 'linkedin.com' in url.lower()

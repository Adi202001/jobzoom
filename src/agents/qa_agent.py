"""QA Agent - Answers application questions"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.base_agent import BaseAgent
from ..core.registry import AgentRegistry
from ..schemas import AgentOutput


@AgentRegistry.register
class QAAgent(BaseAgent):
    """Agent responsible for answering application questions"""

    @property
    def name(self) -> str:
        return "QA_AGENT"

    @property
    def description(self) -> str:
        return "Answers common application questions using user profile data"

    # Common question patterns and answer generators
    QUESTION_PATTERNS = {
        "work_authorization": [
            r"authorized.*work",
            r"legal.*work",
            r"visa.*status",
            r"work.*permit",
            r"employment.*eligibility"
        ],
        "relocation": [
            r"willing.*relocate",
            r"open.*relocation",
            r"relocate.*position"
        ],
        "start_date": [
            r"when.*start",
            r"availability",
            r"start.*date",
            r"earliest.*start"
        ],
        "salary_expectation": [
            r"salary.*expectation",
            r"expected.*salary",
            r"compensation.*expect",
            r"desired.*salary"
        ],
        "why_interested": [
            r"why.*interested",
            r"why.*apply",
            r"why.*want.*work",
            r"what.*interest"
        ],
        "why_leaving": [
            r"why.*leaving",
            r"reason.*leave",
            r"leaving.*current"
        ],
        "strengths": [
            r"greatest.*strength",
            r"your.*strength",
            r"best.*qualities"
        ],
        "weaknesses": [
            r"greatest.*weakness",
            r"your.*weakness",
            r"areas.*improve"
        ],
        "experience_years": [
            r"years.*experience",
            r"how.*long.*experience",
            r"experience.*years"
        ],
        "remote_preference": [
            r"remote.*work",
            r"work.*remote",
            r"hybrid.*office",
            r"on-?site.*remote"
        ],
        "referral": [
            r"how.*hear",
            r"referred.*by",
            r"learn.*about.*position"
        ],
        "travel": [
            r"willing.*travel",
            r"travel.*requirement",
            r"open.*travel"
        ]
    }

    def execute(self, task: Dict[str, Any]) -> AgentOutput:
        """Execute QA tasks"""
        action = task.get("action", "")

        if action == "answer_question":
            return self._answer_question(task)
        elif action == "answer_questions":
            return self._answer_multiple_questions(task)
        elif action == "classify_question":
            return self._classify_question(task)
        elif action == "generate_response":
            return self._generate_custom_response(task)
        else:
            return self.create_output(
                action="error",
                output_data={"error": f"Unknown action: {action}"}
            )

    def _answer_question(self, task: Dict[str, Any]) -> AgentOutput:
        """Answer a single application question"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        question = task.get("question", "")

        if not question:
            return self.create_output(
                action="error",
                output_data={"error": "question is required"}
            )

        user = self.database.get_user(user_id) if user_id else {}
        job = self.database.get_job(job_id) if job_id else {}

        # Classify the question
        question_type = self._classify_question_type(question)

        # Generate answer
        answer = self._generate_answer(question, question_type, user, job)

        return self.create_output(
            action="question_answered",
            output_data={
                "question": question,
                "question_type": question_type,
                "answer": answer,
                "confidence": self._get_confidence(question_type, user)
            }
        )

    def _answer_multiple_questions(self, task: Dict[str, Any]) -> AgentOutput:
        """Answer multiple application questions"""
        user_id = task.get("user_id")
        job_id = task.get("job_id")
        questions = task.get("questions", [])

        if not questions:
            return self.create_output(
                action="error",
                output_data={"error": "questions are required"}
            )

        user = self.database.get_user(user_id) if user_id else {}
        job = self.database.get_job(job_id) if job_id else {}

        answers = []
        for question in questions:
            question_type = self._classify_question_type(question)
            answer = self._generate_answer(question, question_type, user, job)
            answers.append({
                "question": question,
                "question_type": question_type,
                "answer": answer,
                "confidence": self._get_confidence(question_type, user)
            })

        return self.create_output(
            action="questions_answered",
            output_data={
                "user_id": user_id,
                "job_id": job_id,
                "total_questions": len(questions),
                "answers": answers
            }
        )

    def _classify_question(self, task: Dict[str, Any]) -> AgentOutput:
        """Classify a question type"""
        question = task.get("question", "")
        question_type = self._classify_question_type(question)

        return self.create_output(
            action="question_classified",
            output_data={
                "question": question,
                "type": question_type,
                "is_common": question_type is not None
            }
        )

    def _generate_custom_response(self, task: Dict[str, Any]) -> AgentOutput:
        """Generate a custom response with specific instructions"""
        user_id = task.get("user_id")
        question = task.get("question", "")
        tone = task.get("tone", "professional")
        max_length = task.get("max_length", 500)
        key_points = task.get("key_points", [])

        user = self.database.get_user(user_id) if user_id else {}

        response = self._create_custom_response(
            question, user, tone, max_length, key_points
        )

        return self.create_output(
            action="custom_response_generated",
            output_data={
                "question": question,
                "response": response,
                "word_count": len(response.split())
            }
        )

    def _classify_question_type(self, question: str) -> Optional[str]:
        """Classify question into a known type"""
        question_lower = question.lower()

        for q_type, patterns in self.QUESTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return q_type

        return None

    def _generate_answer(
        self,
        question: str,
        question_type: Optional[str],
        user: Dict,
        job: Dict
    ) -> str:
        """Generate answer based on question type and user data"""
        personal = user.get("personal", {})
        prefs = user.get("job_preferences", {})
        resume = user.get("resume", {}).get("parsed", {})

        if question_type == "work_authorization":
            return "Yes, I am authorized to work in the United States."

        elif question_type == "relocation":
            remote_pref = prefs.get("remote_preference", "any")
            if remote_pref == "remote_only":
                return "I am seeking remote positions and am not looking to relocate at this time."
            return "Yes, I am open to relocation for the right opportunity."

        elif question_type == "start_date":
            return "I am available to start within 2-4 weeks, depending on the offer timeline."

        elif question_type == "salary_expectation":
            min_sal = prefs.get("salary_min")
            max_sal = prefs.get("salary_max")
            if min_sal and max_sal:
                return (
                    f"Based on my experience and market research, I am looking for compensation "
                    f"in the range of ${min_sal:,} to ${max_sal:,}. However, I am open to "
                    f"discussing this based on the total compensation package."
                )
            elif min_sal:
                return (
                    f"I am looking for compensation of ${min_sal:,} or above, depending on "
                    f"the full benefits and growth opportunities."
                )
            return (
                "I am open to discussing compensation based on the role responsibilities "
                "and the total package offered."
            )

        elif question_type == "why_interested":
            company = job.get("company", "this company")
            title = job.get("title", "this role")
            return (
                f"I am excited about the {title} opportunity at {company} because it aligns "
                f"perfectly with my skills and career goals. The company's mission and the "
                f"innovative work being done here particularly appeal to me."
            )

        elif question_type == "why_leaving":
            return (
                "I am looking for new challenges and opportunities for professional growth. "
                "While I have valued my current position, I am excited to take on more "
                "responsibility and contribute to a new team."
            )

        elif question_type == "strengths":
            skills = resume.get("skills", {})
            technical = skills.get("technical", [])[:3] if isinstance(skills, dict) else []
            if technical:
                return (
                    f"My greatest strengths include my technical expertise in {', '.join(technical)}, "
                    f"strong problem-solving abilities, and my commitment to delivering high-quality work. "
                    f"I also excel at collaborating with cross-functional teams."
                )
            return (
                "My greatest strengths include strong problem-solving skills, attention to detail, "
                "and the ability to learn quickly. I am also known for my collaborative approach "
                "and clear communication."
            )

        elif question_type == "weaknesses":
            return (
                "I sometimes tend to be overly thorough, which can impact my speed on initial tasks. "
                "However, I've been working on finding the right balance between quality and efficiency "
                "by setting clear priorities and time limits for each task."
            )

        elif question_type == "experience_years":
            experience = resume.get("experience", [])
            years = len(experience) * 2 if experience else 0
            return f"I have approximately {years} years of professional experience in this field."

        elif question_type == "remote_preference":
            remote_pref = prefs.get("remote_preference", "any")
            if remote_pref == "remote_only":
                return "I prefer to work fully remote but am flexible for occasional in-person meetings."
            elif remote_pref == "hybrid_ok":
                return "I am comfortable with a hybrid arrangement and can work both remotely and in-office."
            return "I am flexible and can adapt to remote, hybrid, or on-site work arrangements."

        elif question_type == "referral":
            return "I discovered this opportunity through your company's careers page while researching opportunities in this field."

        elif question_type == "travel":
            return "Yes, I am willing to travel as needed for the role, including occasional trips for team meetings or client visits."

        # Default response for unknown question types
        return self._generate_generic_response(question, user, job)

    def _generate_generic_response(
        self,
        question: str,
        user: Dict,
        job: Dict
    ) -> str:
        """Generate a generic response for unrecognized questions"""
        personal = user.get("personal", {})
        name = personal.get("name", "").split()[0] if personal.get("name") else ""

        return (
            f"Thank you for the question. Based on my background and experience, "
            f"I believe I can provide valuable insights on this topic. "
            f"I would be happy to discuss this further during an interview."
        )

    def _get_confidence(self, question_type: Optional[str], user: Dict) -> str:
        """Get confidence level for the answer"""
        if question_type is None:
            return "low"

        # Check if we have user data for this question type
        prefs = user.get("job_preferences", {})
        resume = user.get("resume", {}).get("parsed", {})

        if question_type == "salary_expectation":
            if prefs.get("salary_min"):
                return "high"
            return "medium"

        if question_type == "experience_years":
            if resume.get("experience"):
                return "high"
            return "medium"

        if question_type in ["work_authorization", "start_date", "referral"]:
            return "medium"

        return "high"

    def _create_custom_response(
        self,
        question: str,
        user: Dict,
        tone: str,
        max_length: int,
        key_points: List[str]
    ) -> str:
        """Create a custom response with specific parameters"""
        personal = user.get("personal", {})
        resume = user.get("resume", {}).get("parsed", {})

        # Build response incorporating key points
        response_parts = []

        if tone == "enthusiastic":
            response_parts.append("I'm excited to address this!")
        elif tone == "professional":
            response_parts.append("Thank you for this question.")

        for point in key_points:
            response_parts.append(point)

        response = " ".join(response_parts)

        # Truncate if needed
        words = response.split()
        if len(words) > max_length // 5:  # Rough word limit
            words = words[:max_length // 5]
            response = " ".join(words) + "..."

        return response

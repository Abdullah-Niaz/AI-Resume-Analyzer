import json
import re

from django.conf import settings


class GeminiProvider:
    def __init__(self):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai is not installed. Run: pip install google-generativeai"
            )

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing in .env file.")

        genai.configure(api_key=settings.GEMINI_API_KEY)

        self.model = genai.GenerativeModel(
            getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        )

    def analyze_resume(self, resume_text, job_role, keywords):
        prompt = self.build_prompt(resume_text, job_role, keywords)

        response = self.model.generate_content(
            prompt,
            request_options={"timeout": 60},
        )

        raw_text = response.text or ""

        return self.parse_json(raw_text)

    def build_prompt(self, resume_text, job_role, keywords):
        keywords_text = ", ".join(
            keywords) if keywords else "No predefined keywords"

        return f"""
You are an expert ATS resume analyzer and technical recruiter.

Analyze the resume for this target role:

Target Role: {job_role}

Important Keywords:
{keywords_text}

Resume Text:
{resume_text[:12000]}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanation.
Do not include ```json.

JSON format:

{{
  "ats_score": 0,
  "summary_feedback": "",
  "missing_keywords": [],
  "strong_points": [],
  "weak_points": [],
  "rewritten_sections": {{
    "summary": "",
    "experience": "",
    "skills": ""
  }},
  "job_role_alignment": ""
}}
"""

    def parse_json(self, raw_text):
        cleaned = raw_text.strip()

        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(0))

            raise ValueError(
                f"Gemini did not return valid JSON: {raw_text[:500]}")


def get_ai_provider():
    return GeminiProvider()

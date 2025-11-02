import os
from app.logger import get_logger
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant")

    def write_application_email_for_role(self, candidate_name, company, role):
        """
        Generate a job-application email for `role` at `company` addressed to the hiring contact.
        Keeps it short, clearly states interest, provides 1-2 lines of fit,
        and ends with a call-to-action (ask for next steps / interview).
        """
        # Template: tailor as you need (tone, length)
        prompt_template = """
        You are an assistant that composes short, professional job-application emails.

        Candidate name: {candidate_name}
        Target company: {company}
        Role applied for: {role}

        Requirements:
        - The email should be written as the candidate (first-person).
        - Clearly state interest in the {role} role and why the candidate is a good fit (1-2 short sentences).
        - Mention 1-2 specific relevant skills or experiences matching the role (if provided).
        - Finish with a polite ask for next steps or interview availability.
        - Keep the whole email between 4–7 sentences.
        - No extra commentary, only provide the email body.

        Write the email now.
        """
        prompt = PromptTemplate.from_template(prompt_template)

        chain_email = prompt | self.llm
        resp = chain_email.invoke({
            "candidate_name": candidate_name,
            "company": company,
            "role": role,
        })
        return resp.content

    def extract_projects_and_experiences(self, company, role, job_description=None, resume_json_file="data/resume.json"):
        """
        Extract relevant projects and experiences from the resume JSON file for the given company and role.
        If job_description is provided, use it to better tailor the extraction.
        Returns a dict with `projects` and `experience` keys.
        """
        resume_data = open(resume_json_file, "r").read()
        prompt = PromptTemplate.from_template(
            """
            You've been provided with a resume in JSON format. Based on the company, role and job description (if provided), you need to extract the relevant projects and experiences from the JSON to build a tailored CV.

            Company: {company}
            Role: {role}
            Job Description: {job_description}

            Resume JSON:
            {resume_data}

            Instructions:
            Only output a valid JSON text containing the `projects` and `experience` keys.
            Each key should map to a list of relevant items extracted from the resume JSON.
            Ensure that the selected projects and experiences are highly relevant to the specified role and company.

            **Do not include any additional commentary or text or quotes or backticks outside of the JSON structure.**
            """
        )

        chain = prompt | self.llm
        res = chain.invoke({
            "company": company,
            "role": role,
            "job_description": job_description or "N/A",
            "resume_data": resume_data
        })
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Unable to parse CV JSON.")
        return res


if __name__ == "__main__":
    logger.debug("GROQ_API_KEY: %s", os.getenv("GROQ_API_KEY"))
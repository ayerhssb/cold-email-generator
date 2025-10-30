import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Bharti, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of AtliQ 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
            Remember you are Mohan, BDE at AtliQ. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content
    
    def write_mail_for_candidate(self, candidate_name, company, role, links):
        """
        Generate a personalised cold email for a candidate (using candidate/company/role)
        `links` should be a list of portfolio link metadata (as returned by Portfolio.query_links).
        """
        prompt_email = PromptTemplate.from_template(
            """
            ### CONTEXT:
            You are Mohan, a Business Development Executive at AtliQ (an AI & Software Consulting company).
            The goal is to write a short, personalized outreach email to a hiring contact at {company} for the role: {role}.
            Candidate name (recipient): {candidate_name}
            Include 1–2 short sentences describing AtliQ's relevant capabilities, and add the most relevant portfolio links:
            {link_list}

            Write a polite, concise cold email that references the job role and company. Keep it ~5–8 sentences.
            Do NOT provide any preamble, only the email content.
            """
        )
        chain_email = prompt_email | self.llm
        link_text = "\n".join([str(l) for l in (links or [])])
        res = chain_email.invoke({
            "candidate_name": candidate_name,
            "company": company,
            "role": role,
            "link_list": link_text
        })
        return res.content


    # app/chains.py (inside the same class, e.g., Chain or whatever class holds LLM helper methods)

    def write_application_email_for_role(self, candidate_name, company, role, portfolio_links):
        """
        Generate a job-application email for `role` at `company` addressed to the hiring contact.
        Keeps it short, clearly states interest, provides 1-2 lines of fit, references portfolio links,
        and ends with a call-to-action (ask for next steps / interview).
        """
        # Template: tailor as you need (tone, length)
        prompt_template = """
        You are an assistant that composes short, professional job-application emails.

        Candidate name: {candidate_name}
        Target company: {company}
        Role applied for: {role}

        Portfolio / relevant links (one per line):
        {links}

        Requirements:
        - The email should be written as the candidate (first-person).
        - Clearly state interest in the {role} role and why the candidate is a good fit (1-2 short sentences).
        - Mention 1-2 specific relevant skills or experiences matching the role (if provided).
        - Include the portfolio links in one short line.
        - Finish with a polite ask for next steps or interview availability.
        - Keep the whole email between 4–7 sentences.
        - No extra commentary, only provide the email body.

        Write the email now.
        """
        prompt = PromptTemplate.from_template(prompt_template)

        # format links into a simple bullet or inline string
        links_text = "\n".join([f"- {l}" for l in (portfolio_links or [])]) or "No portfolio links available."

        chain_email = prompt | self.llm
        resp = chain_email.invoke({
            "candidate_name": candidate_name,
            "company": company,
            "role": role,
            "links": links_text
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
    print(os.getenv("GROQ_API_KEY"))
import os, csv, uuid, json
import streamlit as st

from chains import Chain
from mailmerge import send_emails
from ResumeEditor import Resume
from app.logger import logger


def create_streamlit_app(llm: Chain):
    logger.info("create_streamlit_app called")
    st.header("Mail-Merge: generate & send personalised mails from CSV")
    role_input = st.text_input("Role you are applying for (used to craft emails):", value="Software Engineer")
    generate_btn = st.button("Generate Mails")
    send_btn = st.button("Send Mails")

    # where the CSV will be read from (use backend csv in project dir)
    base_dir = os.path.dirname(__file__)
    csv_file = os.path.join(base_dir, "test-mailmerge.csv")  # change path if needed

    # Initialize session_state container
    if "generated_mails" not in st.session_state:
        st.session_state.generated_mails = []  # list of dicts: {name,email,company,subject,body}

    # Generate drafts
    if generate_btn:
        if not os.path.exists(csv_file):
            st.error(f"CSV not found at {csv_file}. Place test-mailmerge.csv there (columns: name,email,company).")
        else:
            st.session_state.generated_mails = []
            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row.get("name", "there")
                    company = row.get("company", "")
                    email = row.get("email")
                    if not email:
                        continue

                    # create subject & body using chains helper
                    with open("data/resume.json", "r") as f:
                        resume_data = json.load(f)
                    subject = f"Regarding {role_input} opportunities at {company}"
                    resume_file = "_".join(resume_data.get("name", "").split()) + "_" + uuid.uuid4().hex + ".pdf"
                    try:
                        body = llm.write_application_email_for_role(name, company, role_input)
                        llm_data = llm.extract_projects_and_experiences(company, role_input)
                        resume = Resume(
                            education=resume_data.get("education", []),
                            experience=llm_data.get("experience", []),
                            projects=llm_data.get("projects", []),
                            skills=resume_data.get("skills", {}),
                            name=resume_data.get("name", ""),
                            phone=resume_data.get("contact", {}).get("phone", ""),
                            email=resume_data.get("contact", {}).get("email", ""),
                            linkedin=resume_data.get("contact", {}).get("linkedin", ""),
                            github=resume_data.get("contact", {}).get("github", "")
                        )
                        resume.generate_full_resume_pdf(resume_file)
                    except Exception as e:
                        logger.exception("Failed to generate email for %s at %s: %s", name, company, e)
                        body = f"Could not generate email due to: {e}"
                    st.session_state.generated_mails.append({
                        "name": name, "email": email, "company": company,
                        "subject": subject, "body": body, "resume_file": resume_file
                    })
            st.success(f"Generated {len(st.session_state.generated_mails)} drafts.")

    # Show generated drafts
    if st.session_state.generated_mails:
        st.subheader("Generated drafts")
        for i, m in enumerate(st.session_state.generated_mails):
            with st.expander(f"{m['name']} — {m['company']} ({m['email']})", expanded=False):
                st.write("Subject:", m['subject'])
                st.code(m['body'], language='markdown')

    # Send mails
    if send_btn:
        if not st.session_state.generated_mails:
            st.error("No generated mails to send. Click 'Generate Mails' first.")
        else:
            try:
                # Prepare messages in the shape mailmerge.send_emails expects
                messages = []
                for m in st.session_state.generated_mails:
                    messages.append({
                        "to": m['email'],
                        "subject": m['subject'],
                        "body": m['body'],
                        "attachments": ['pdfs/' + m['resume_file']] if m.get('resume_file') else []
                    })
                results = send_emails(messages)
                st.success(f"Sent {len(results)} emails.")
                st.write(results)
            except Exception as e:
                logger.exception("Failed to send emails: %s", e)
                st.error(f"Sending failed: {e}")


if __name__ == "__main__":
    logger.info("Starting cold-email-generator application")
    chain = Chain()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain)

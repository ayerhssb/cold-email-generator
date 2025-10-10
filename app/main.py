import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

import os
import csv
import pandas as pd
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from mailmerge import send_emails


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Automate generating & sending mails")
    url_input = st.text_input("Enter a URL:", value="https://jobs.cisco.com/jobs/ProjectDetail/Software-Engineer-C-Programming-and-Networking-5-to-9-Yrs-Chennai-Bangalore/1443134")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")
    
    
    
    st.markdown("---")
    
    
    
    st.header("Mail-Merge: generate & send personalised mails from CSV")
    role_input = st.text_input("Role you are applying for (used to craft emails):", value="Software Engineer")
    generate_btn = st.button("Generate Mails")
    send_btn = st.button("Send Mails")

    # where the CSV will be read from (use backend csv in project dir)
    base_dir = os.path.dirname(__file__)
    csv_file = os.path.join(base_dir, "test-mailmerge.csv")  # change path if needed

    # ensure portfolio loaded
    portfolio.load_portfolio()

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
                    # query portfolio links using role (simple: treat role as a skill query)
                    links = portfolio.query_links([role_input])
                    # create subject & body using chains helper
                    subject = f"Regarding {role_input} opportunities at {company}"
                    try:
                        body = llm.write_application_email_for_role(name, company, role_input, links)
                    except Exception as e:
                        body = f"Could not generate email due to: {e}"
                    st.session_state.generated_mails.append({
                        "name": name, "email": email, "company": company,
                        "subject": subject, "body": body
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
                        "body": m['body']
                    })
                results = send_emails(messages)
                st.success(f"Sent {len(results)} emails.")
                st.write(results)
            except Exception as e:
                st.error(f"Sending failed: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)


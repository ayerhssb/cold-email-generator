import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from mailmerge import send_emails
import os, csv, pandas as pd


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Automate generating & sending mails")

    # ----------------------------
    # 1️⃣ Smart CV Enhancer section
    # ----------------------------
    st.header("🧠 Smart CV Enhancer")

    uploaded_resume = st.file_uploader("Upload your Resume (PDF/DOCX)", type=["pdf", "docx"])
    uploaded_json = st.file_uploader("Upload your Projects JSON", type=["json"])
    uploaded_excel = st.file_uploader("Upload Excel/CSV for job roles", type=["xlsx", "csv"])
    target_skills = st.text_input("Enter target skills (comma-separated):")

    if st.button("Process CV"):
        if uploaded_resume and uploaded_json and uploaded_excel:
            from cv_agent import (
                read_resume, read_json_projects, read_excel_or_csv,
                score_resume_against_skills, update_resume_sections
            )

            resume_text = read_resume(uploaded_resume)
            projects, skills = read_json_projects(uploaded_json)
            df = read_excel_or_csv(uploaded_excel)

            target_skill_list = [s.strip() for s in target_skills.split(",") if s.strip()]
            score = score_resume_against_skills(resume_text, target_skill_list)
            st.write(f"Resume match score: **{score}%**")

            updated_cv_text = update_resume_sections(resume_text, projects, skills, target_skill_list)

            # store in session
            st.session_state['final_cv'] = updated_cv_text
            st.session_state['csv_df'] = df

            if updated_cv_text.strip() != resume_text.strip():
                st.success("✅ Resume updated successfully! Download the new version below:")
            else:
                st.info("No major changes detected. Using your original resume.")

            st.download_button("Download Updated CV", updated_cv_text, file_name="updated_resume.txt")

        else:
            st.error("Please upload all three files.")

    st.markdown("---")

    # ----------------------------
    # 2️⃣ Mail generation & sending
    # ----------------------------
    if 'csv_df' in st.session_state and 'final_cv' in st.session_state:
        st.header("Mail-Merge: Generate & Send Personalised Mails")

        role_input = st.text_input("Role you are applying for:", value="Software Engineer")
        generate_btn = st.button("Generate Mails")
        send_btn = st.button("Send Mails")

        portfolio.load_portfolio()

        if "generated_mails" not in st.session_state:
            st.session_state.generated_mails = []

        if generate_btn:
            df = st.session_state['csv_df']
            st.session_state.generated_mails = []
            for _, row in df.iterrows():
                name = row.get("name", "there")
                company = row.get("company", "")
                email = row.get("email")
                if not email:
                    continue
                links = portfolio.query_links([role_input])
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

        # Show drafts
        if st.session_state.generated_mails:
            st.subheader("Generated Drafts")
            for m in st.session_state.generated_mails:
                with st.expander(f"{m['name']} — {m['company']} ({m['email']})"):
                    st.write("Subject:", m['subject'])
                    st.code(m['body'], language='markdown')

        # Send mails (with CV attachment)
        if send_btn:
            try:
                messages = []
                for m in st.session_state.generated_mails:
                    messages.append({
                        "to": m['email'],
                        "subject": m['subject'],
                        "body": m['body'] + "\n\n[CV attached]",
                    })
                results = send_emails(messages)
                st.success(f"Sent {len(results)} emails successfully (CV attached).")
            except Exception as e:
                st.error(f"Sending failed: {e}")
    else:
        st.info("⬆️ Please upload your files and process CV before generating mails.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)

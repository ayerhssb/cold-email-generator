from typing import List
import subprocess

class Resume:
    def __init__(self, education: List[dict], experience: List[dict], projects: List[dict], skills: dict, name: str, phone: str, email: str, linkedin: str, github: str):
        self.education = education
        self.experience = experience
        self.projects = projects
        self.skills = skills
        self.name = name
        self.phone = phone
        self.email = email
        self.linkedin = linkedin
        self.github = github

    def get_education_entry(self, edu: dict) -> str:
        tex = rf"""
        \resumeSubheading
        {{{edu["institution"]}}}{{{edu["duration"]}}}
        {{{edu["degree"]}}}{{GPA: {edu["grade"]}}}
        """
        return tex

    def get_experience_entry(self, exp: dict) -> str:
        tex = rf"""
        \resumeSubheading
        {{{exp["organization"]}}}{{{exp["duration"]}}}
        {{{exp["role"]}}}{{{exp["location"]}}}
            \resumeItemListStart
        """
        for point in exp["description"]:
            tex += rf"""
            \resumeItem{{{point}}}
            """
        tex += r"""
            \resumeItemListEnd
        """
        return tex
    
    def get_project_entry(self, proj: dict) -> str:
        tex = rf"""
        \resumeProjectHeading
        {{\textbf{{{proj["name"]}}} $|$ \emph{{{", ".join(proj["technologies"])}}}}}{{}}
        \resumeItemListStart
        """
        for point in proj["description"]:
            tex += rf"""
            \resumeItem{{{point}}}
            """
        tex += r"""
            \resumeItemListEnd
        """
        return tex
    
    def generate_heading(self) -> str:
        tex = rf"""
        %----------HEADING----------%
        \begin{{center}}
            \textbf{{\Huge \scshape {self.name}}} \\ \vspace{{1pt}}
            \seticon{{faPhone}} \ \small {self.phone} \quad
            \href{{mailto:{self.email}}}{{\seticon{{faEnvelope}} \underline{{{self.email}}}}} \quad
            \href{{https://www.linkedin.com/in/{self.linkedin}}}{{\seticon{{faLinkedin}} \underline{{linkedin.com/in/{self.linkedin}}}}} \quad
            \href{{https://github.com/{self.github}}}{{\seticon{{faGithub}} \underline{{github.com/{self.github}}}}}
        \end{{center}}
        """
        return tex
    
    def generate_education_section(self) -> str:
        tex = rf"""
        %-----------EDUCATION-----------%
        \section{{Education}}
            \resumeSubHeadingListStart
        """
        education_entries = []
        for edu in self.education:
            education_entries.append(self.get_education_entry(edu))
        tex += "\n".join(education_entries)
        tex += r"""
            \resumeSubHeadingListEnd
        """
        return tex

    def generate_experience_section(self) -> str:
        tex = rf"""
        %-----------EXPERIENCE-----------%
        \section{{Experience}}
            \resumeSubHeadingListStart
        """
        experience_entries = []
        for exp in self.experience:
            experience_entries.append(self.get_experience_entry(exp))
        tex += "\n".join(experience_entries)
        tex += r"""
            \resumeSubHeadingListEnd
        """
        return tex

    def generate_projects_section(self) -> str:
        tex = rf"""
        %-----------PROJECTS-----------%
        \section{{Projects}}
            \resumeSubHeadingListStart
        """
        project_entries = []
        for proj in self.projects:
            project_entries.append(self.get_project_entry(proj))
        tex += "\n".join(project_entries)
        tex += r"""
            \resumeSubHeadingListEnd
        """
        return tex

    def generate_skills_section(self) -> str:
        tex = rf"""
        %-----------SKILLS-----------%
        \section{{Skills}}
            \begin{{itemize}}[leftmargin=0.15in, label={{}}]
            \small{{\item{{
        """
        # Assuming skills is a dictionary with categories as keys and list of skills as values
        for category, skills_list in self.skills.items():
            tex += rf"""
            \textbf{{{category}}}{{{": " + ", ".join(skills_list)}}}
            """
        tex += r"""
            }}
            \end{itemize}
        """
        return tex

    def generate_full_resume_latex(self) -> str:
        tex = r"""
        %-------------------------
        % Resume in Latex
        % Author : Audric Serador
        % Inspired by: https://github.com/sb2nov/resume
        % License : MIT
        %------------------------

        \documentclass[letterpaper,11pt]{article}

        \usepackage{fontawesome5}
        \usepackage{latexsym}
        \usepackage[empty]{fullpage}
        \usepackage{titlesec}
        \usepackage{marvosym}
        \usepackage[usenames,dvipsnames]{color}
        \usepackage{verbatim}
        \usepackage{enumitem}
        \usepackage[hidelinks]{hyperref}
        \usepackage{fancyhdr}
        \usepackage[english]{babel}
        \usepackage{tabularx}
        \input{glyphtounicode}



        % Custom font
        \usepackage[default]{lato}

        \pagestyle{fancy}
        \fancyhf{} % clear all header and footer fields
        \fancyfoot{}
        \renewcommand{\headrulewidth}{0pt}
        \renewcommand{\footrulewidth}{0pt}

        % Adjust margins
        \addtolength{\oddsidemargin}{-0.5in}
        \addtolength{\evensidemargin}{-0.5in}
        \addtolength{\textwidth}{1in}
        \addtolength{\topmargin}{-.5in}
        \addtolength{\textheight}{1.0in}

        \urlstyle{same}

        \raggedbottom
        \raggedright
        \setlength{\tabcolsep}{0in}

        % Sections formatting
        \titleformat{\section}{
        \vspace{-4pt}\scshape\raggedright\large
        }{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]

        % Ensure that generate pdf is machine readable/ATS parsable
        \pdfgentounicode=1

        %-------------------------%
        % Custom commands
        \begin{document}
        \newcommand{\resumeItem}[1]{
        \item\small{
            {#1 \vspace{-2pt}}
        }
        }

        \newcommand{\resumeSubheading}[4]{
        \vspace{-2pt}\item
            \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
            \textbf{#1} & #2 \\
            \textit{\small#3} & \textit{\small #4} \\
            \end{tabular*}\vspace{-7pt}
        }

        \newcommand{\resumeSubSubheading}[2]{
            \item
            \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
            \textit{\small#1} & \textit{\small #2} \\
            \end{tabular*}\vspace{-7pt}
        }

        \newcommand{\resumeProjectHeading}[2]{
            \item
            \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
            \small#1 & #2 \\
            \end{tabular*}\vspace{-7pt}
        }

        \newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

        \renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

        \newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
        \newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
        \newcommand{\resumeItemListStart}{\begin{itemize}}
        \newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

        \definecolor{Black}{RGB}{0, 0, 0}
        \newcommand{\seticon}[1]{\textcolor{Black}{\csname #1\endcsname}}

        %-------------------------------------------%
        %%%%%%  RESUME STARTS HERE  %%%%%
        """
        tex += self.generate_heading()
        tex += self.generate_education_section()
        tex += self.generate_experience_section()
        tex += self.generate_projects_section()
        tex += self.generate_skills_section()
        tex += r"""
        \end{document}
        """
        return tex

    def generate_full_resume_pdf(self, output_path: str) -> str:
        tex = self.generate_full_resume_latex()
        with open("resume.tex", "w") as f:
            f.write(tex)
        subprocess.run(["pdflatex", "resume.tex"])
        print(f"PDF resume generated as {output_path}")


if __name__ == "__main__":
    sample_education = [
        {
            "institution": "University Name",
            "degree": "Bachelor of Science in Computer Science",
            "grade": "4.00 / 4.00",
            "duration": "May 2026"
        }
    ]
    sample_experience = [
        {
            "organization": "Company Name",
            "role": "Software Engineer",
            "location": "City, Country",
            "duration": "June 2026 - Present",
            "description": [
                "Developing applications using Python and JavaScript.",
                "Collaborating with cross-functional teams to define and implement new features."
            ]
        }
    ]
    sample_projects = [
        {
            "name": "Project Name 1",
            "description": [
                "Implemented feature X using technology Y.",
                "Collaborated with team Z to enhance functionality."
            ],
            "technologies": ["React.js", "Node.js", "MongoDB"]
        }
    ]
    sample_skills = {   
        "Programming Languages": ["Python", "JavaScript", "C++"],
        "Frameworks": ["React", "Django", "Flask"],
        "Databases": ["MySQL", "MongoDB"]
    }
    
    resume = Resume(sample_education, sample_experience, sample_projects, sample_skills, "Harsh Bansal", "9821391634", "harshbansal8705@gmail.com", "harshbansal8705", "harshbansal8705")
    # print(resume.generate_education_section())
    # print(resume.generate_experience_section())
    # print(resume.generate_projects_section())
    # print(resume.generate_skills_section())
    print(resume.generate_full_resume_pdf("resume.pdf"))
# Cold Email Generator

An AI-powered cold email generation tool built with **Streamlit**.  
This app uses **Llama 3.1**, **LangChain**, and **ChromaDB** to generate personalized outreach emails by matching your portfolio to target job postings or company descriptions.

---

## Features
- Generates cold emails using LLMs (Llama 3.1 on Groq Cloud)
- sends personalized mails
- Semantic portfolio and job matching using vector embeddings
- Streamlit-based interactive dashboard

---

## Tech Stack
- **Python**
- **Streamlit**
- **LangChain**
- **Groq Cloud (Llama 3.1)**
- **ChromaDB**
- **Web Scraping utilities**

---

## ⚙️ How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayerhssb/cold-email-generator.git
   cd cold-email-generator
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate      # On Windows
   ```

2. **Add environment variables**
   rename .env.example as .anv and add your_groq_api_key

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run .\app\main.py
   ```

5. **Open in browser**
   Streamlit will automatically open a local URL like  
   👉 `http://localhost:8501`

---

## 📁 Project Structure
```
cold-email-generator/
│
├── app/main.py          # Streamlit app entry point
├── requirements.txt     # Dependencies
└── README.md
```

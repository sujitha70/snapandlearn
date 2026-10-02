# 📚 Snap & Learn — AI Vision Study Buddy & Homework Decoder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://snapandlearn-omkqpcpfnmnkxaxjgfcj2d.streamlit.app/)

> 🌐 **Live Deployed App**: [https://snapandlearn-omkqpcpfnmnkxaxjgfcj2d.streamlit.app/](https://snapandlearn-omkqpcpfnmnkxaxjgfcj2d.streamlit.app/)  
> **Snap it. Learn it. Email yourself the study notes.**  
> An intelligent educational assistant built with **Google Gemini (Vision + Chat)** and **Python SMTP (Gmail)** that analyzes photographed notes, textbook pages, math problems, and diagrams, breaks them down into intuitive step-by-step explanations, and emails a formatted revision sheet straight to the student's inbox.

---

## 🌟 Key Features

- 📸 **Multimodal Vision Analysis**: Attach or snap photos of textbook pages, handwritten notes, biology/physics diagrams, or math equations directly inside the chat interface.
- 🧑‍🏫 **Socratic & Clear AI Tutor**: Powered by Gemini with a dedicated pedagogical system prompt in `prompts.py` that keeps responses structured, encouraging, and focused strictly on learning.
- 📧 **One-Click Email Revision Sheet**: When finishing a study session, click **"Email Study Notes"** to compile all covered topics, formulas, and step-by-step breakdowns into a high-yield study guide sent via Gmail.
- 🎨 **Modern & Polished UI**: Built with Streamlit featuring responsive layouts, custom typography, LaTeX equation rendering, and session management.
- 🔒 **Secure Secrets Management**: Fully compliant with Streamlit Community Cloud and security best practices (`.gitignore` protects local secrets).

---

## 📁 Project Structure

```
snapnlearn/
├── app.py                     # Main Streamlit web application & chat flow
├── prompts.py                 # AI system prompt, persona, welcome message & summary prompt
├── requirements.txt           # Python package dependencies
├── .gitignore                 # Excludes secrets, venv, and cache from Git tracking
├── README.md                  # Project documentation & setup instructions
└── .streamlit/
    ├── secrets.toml.example   # Template for configuration & API keys
    └── secrets.toml           # (Ignored by Git) Local secrets configuration
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.9+ installed
- A free [Google AI Studio](https://aistudio.google.com) account for a Gemini API key
- A Gmail account with 2-Step Verification enabled (for free SMTP emailing)

### 2. Clone / Setup the Repository
```bash
# Navigate to the project directory
cd snapnlearn

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Open `.streamlit/secrets.toml` and fill in your credentials:
   ```toml
   # Google Gemini API Key from https://aistudio.google.com
   GEMINI_API_KEY = "AIzaSy..."

   # Gmail Address and 16-character App Password:
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "abcd efgh ijkl mnop"
   ```
   > 💡 **How to generate a Gmail App Password:**
   > 1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
   > 2. Ensure **2-Step Verification** is turned ON.
   > 3. Go to [App Passwords](https://myaccount.google.com/apppasswords).
   > 4. Create an app named `Snap & Learn` and copy the 16-character generated password into `GMAIL_APP_PASSWORD`.

### 5. Run the Application
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your repository to GitHub (ensure `.streamlit/secrets.toml` is **not** committed; `.gitignore` is already configured for this).
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"** and select your repository, branch, and `app.py` as the entrypoint.
4. Click **"Advanced settings"** -> **"Secrets"**, then paste your configuration:
   ```toml
   GEMINI_API_KEY = "your-real-gemini-key"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-16-char-app-password"
   ```
5. Click **"Deploy!"** Your app is now live with a public URL!

---

## 🧪 How to Use

1. **Onboard**: Enter your name and the email address where you want to receive your study summaries.
2. **Chat & Snap**:
   - Type any homework question or topic.
   - Click the paperclip icon in the chat bar to attach a picture of your handwritten notes, textbook problem, or diagram.
3. **Email Revision Notes**:
   - Once you have explored your questions, click the **"📧 Email Study Notes"** button in the top right.
   - Snap & Learn will compile a clean revision guide and deliver it directly to your email inbox!

---

## 📜 License
MIT License — Feel free to use and adapt for your own learning projects!

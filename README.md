# GenAI Interview Bot

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/) [![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-lightgrey)](https://platform.openai.com/) [![Google Cloud](https://img.shields.io/badge/Google%20Cloud-TTS-blue)](https://cloud.google.com/text-to-speech)

> **GenAI Interview Bot** is a professional, AI-powered platform for conducting primary-level candidate assessments using automated, adaptive interviews. Built with Django and OpenAI GPT-4o, it streamlines hiring with objective, voice-based, and time-bound evaluations.

---

## 🚀 Overview
GenAI Interview Bot enables recruiters to efficiently assess candidates through:
- Automated, objective interviews
- Adaptive, AI-generated questions
- Voice-based interaction (Google Cloud TTS)
- Automated scoring and eligibility feedback
- Secure, role-based access
- Resilience to network interruptions

---

## ✨ Features
- **AI-Powered Interviews:** Real-time question generation and adaptation via OpenAI GPT-4o-mini
- **Voice Delivery:** Google Cloud Text-to-Speech for all questions
- **Async, Time-Bound Flow:** Candidates complete interviews at their own pace within set limits
- **Automated, Transparent Scoring:** LLM-based scoring, eligibility %, and feedback
- **Recruiter Dashboard:** Manage interviews, track progress, and review analytics
- **Candidate Portal:** Simple, distraction-free experience for candidates
- **Modern, Responsive UI:** Clean, accessible design using custom CSS (no UI libraries)
- **Long-Term Storage:** Persistent record of responses and results
- **Security:** Django authentication and role-based access

---

## 🛠️ Tech Stack
- **Backend:** Django (Python)
- **Frontend:** Django Templates, Custom CSS
- **AI/ML:** OpenAI GPT-4o-mini API
- **Voice:** Google Cloud Text-to-Speech
- **Database:** Django ORM (SQLite/PostgreSQL)

---

## ⚡ Getting Started

### 1. Clone the Repository
```bash
git clone <repo-url>
cd interview_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
- `OPENAI_API_KEY` (required)
- Google Cloud TTS credentials (see Google Cloud docs)

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

### 6. Access the App
Visit [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## 👥 Usage
- **Recruiters:** Register/login, create interview sessions, send invites, review analytics/results
- **Candidates:** Register/login, complete assigned interviews, view feedback

---

## 📁 Project Structure
```
interview_bot/
├── bot/                 # Django app: views, models, interview logic
├── templates/           # HTML templates
├── static/css/          # Custom CSS (modern-style.css)
├── interview_bot/       # Django project settings, URLs
├── requirements.txt     # Python dependencies
└── README.md
```

---

## 🔒 Security & Privacy
- Role-based access (recruiter/candidate)
- No GDPR compliance required
- No OpenAI API fallback (basic error handling only)
- Handles network interruptions gracefully

---

## 📄 License
This project is for educational and demonstration purposes only.